import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from gli_flow.database.migrations import migrate_if_needed, MigrationEngine, RUNS_MIGRATIONS, FAILURE_ATLAS_MIGRATIONS
from gli_flow.installer.tool_detector import (
    detect_tool, detect_magic, detect_magicdnull, detect_netgen, detect_netgen_lib_dir, detect_netgenexec,
    detect_yosys, detect_openroad, detect_klayout, detect_sv2v, detect_git, detect_cmake, detect_python3,
    DetectionResult, Confidence, meets_min_version,
)
from gli_flow.installer.validation import TOOL_MIN_VERSIONS
from gli_flow.installer.system import is_wsl
from gli_flow.core.tool_discovery import find_magic_binary, is_historical_risk_version


@dataclass
class ValidationItem:
    name: str
    status: str = "PASS"
    detail: str = ""
    severity: str = "info"

    @property
    def passed(self) -> bool:
        return self.status == "PASS"

    @property
    def failed(self) -> bool:
        return self.status == "FAIL"

    @property
    def warned(self) -> bool:
        return self.status == "WARN"


@dataclass
class ValidationReport:
    sections: dict[str, list[ValidationItem]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def all_pass(self) -> bool:
        for items in self.sections.values():
            for item in items:
                if item.failed:
                    return False
        return True

    @property
    def readiness(self) -> str:
        if self.all_pass:
            return "READY FOR TAPEOUT FLOW"
        fails = [item for items in self.sections.values() for item in items if item.failed]
        if fails:
            return f"NOT READY ({len(fails)} failure(s))"
        return "READY WITH WARNINGS"


class EnvironmentValidator:
    def __init__(self, db_path: Optional[str] = None, pdk_root: Optional[str] = None, orfs_root: Optional[str] = None, backend: str = "local"):
        self.db_path = db_path
        self.pdk_root = pdk_root or os.environ.get("PDK_ROOT", str(Path.home() / ".gli-flow" / "pdk"))
        self.orfs_root = orfs_root or os.environ.get("ORFS_ROOT") or str(Path.home() / ".gli-flow" / "orfs")
        self.backend = backend
        self.report = ValidationReport()

    def validate_all(self) -> ValidationReport:
        self._validate_system()
        self._validate_tools()
        self._validate_database()
        self._validate_pdk()
        self._validate_docker()
        self._validate_orfs()
        self._validate_network()
        self._validate_permissions()
        return self.report

    def _add(self, section: str, item: ValidationItem):
        if section not in self.report.sections:
            self.report.sections[section] = []
        self.report.sections[section].append(item)

    def _validate_system(self):
        platform = "unknown"
        try:
            import platform as _p
            platform = f"{_p.system()} {_p.release()}"
        except Exception:
            pass
        self._add("SYSTEM", ValidationItem("Platform", "PASS" if platform != "unknown" else "WARN", platform))
        python = detect_python3()
        py_ok = python.version and meets_min_version(python.version, "3.9")
        self._add("SYSTEM", ValidationItem(
            "Python", "PASS" if py_ok else "FAIL",
            f"{python.version} at {python.path or 'not found'}"
        ))
        wsl = is_wsl()
        self._add("SYSTEM", ValidationItem(
            "WSL2", "INFO" if wsl else "PASS",
            "Detected WSL2 environment" if wsl else "Not WSL"
        ))

    def _validate_tools(self):
        tools = [
            ("git", detect_git, "2.0"),
            ("cmake", detect_cmake, "3.10"),
            ("yosys", detect_yosys, "0.27"),
            ("openroad", detect_openroad, "2.0"),
            ("klayout", detect_klayout, "0.28"),
            ("netgen", detect_netgen, "1.5"),
            ("sv2v", detect_sv2v, "0.0"),
        ]
        for name, detector, min_ver in tools:
            result = detector()
            ver_ok = meets_min_version(result.version, min_ver) if result.exists else False
            if result.exists and ver_ok:
                status = "PASS"
                detail = f"{result.version} at {result.path} [{result.confidence.value}]"
            elif result.exists and not ver_ok:
                status = "FAIL"
                detail = f"{result.version} < min {min_ver} at {result.path} [{result.confidence.value}]"
            else:
                status = "FAIL"
                detail = result.detail
                if result.errors:
                    detail += f"; {result.errors[0]}"
            self._add("TOOLS", ValidationItem(name, status, detail))

        # Magic: use tool_discovery for canonical version-aware detection
        tb = find_magic_binary()
        if tb:
            if meets_min_version(tb.version_str, "8.3"):
                if is_historical_risk_version("magic", tb.version):
                    status = "PASS"
                    detail = f"{tb.version_str} at {tb.path} [HISTORICAL-RISK] [{tb.source.value}]"
                else:
                    status = "PASS"
                    detail = f"{tb.version_str} at {tb.path} [{tb.source.value}]"
            else:
                status = "FAIL"
                detail = f"{tb.version_str} < min 8.3 at {tb.path}"
        else:
            status = "FAIL"
            detail = "not found"
        self._add("TOOLS", ValidationItem("magic", status, detail))

        magicdnull = detect_magicdnull()
        self._add("TOOLS", ValidationItem(
            "magicdnull", "PASS" if magicdnull.exists else "FAIL",
            magicdnull.detail
        ))
        netgenexec = detect_netgenexec()
        self._add("TOOLS", ValidationItem(
            "netgenexec", "PASS" if netgenexec else "FAIL",
            f"at {netgenexec}" if netgenexec else "not found on PATH"
        ))
        tcl_lib = detect_netgen_lib_dir()
        self._add("TOOLS", ValidationItem(
            "tclnetgen.so", "PASS" if tcl_lib else "WARN",
            f"at {tcl_lib}" if tcl_lib else "not found (LVS may fail)"
        ))

    def _validate_database(self):
        try:
            migrate_if_needed(self.db_path)
            engine = MigrationEngine(self.db_path)
            runs_ok = engine.validate_schema("runs", RUNS_MIGRATIONS)
            fa_ok = engine.validate_schema("failure_atlas", FAILURE_ATLAS_MIGRATIONS)
            engine.close()
            if runs_ok and fa_ok:
                self._add("DATABASE", ValidationItem("Schema", "PASS", "All migrations applied"))
            else:
                pending = []
                if not runs_ok:
                    pending.append("runs")
                if not fa_ok:
                    pending.append("failure_atlas")
                self._add("DATABASE", ValidationItem("Schema", "FAIL", f"Pending migrations: {', '.join(pending)}"))
        except Exception as e:
            self._add("DATABASE", ValidationItem("Schema", "FAIL", str(e)))

        db_path = self.db_path or os.environ.get("GLI_FLOW_DB") or str(Path.home() / ".gli_flow" / "gli_flow.db")
        db_exists = Path(db_path).exists() if db_path else False
        self._add("DATABASE", ValidationItem(
            "File", "PASS" if db_exists else "INFO",
            db_path if db_exists else f"Will be created at {db_path}"
        ))

    def _validate_pdk(self):
        pdk_root = Path(self.pdk_root)
        if not pdk_root.exists():
            self._add("PDK", ValidationItem("PDK Root", "FAIL", f"Not found: {self.pdk_root}"))
            return
        self._add("PDK", ValidationItem("PDK Root", "PASS", str(pdk_root)))
        for pdk_name in ["sky130", "sky130A", "sky130B", "gf180mcu"]:
            pdk_dir = pdk_root / pdk_name
            if pdk_dir.exists() and any(pdk_dir.iterdir()):
                self._add("PDK", ValidationItem(f"pdk:{pdk_name}", "PASS", str(pdk_dir)))
        installed_pdks = [d.name for d in pdk_root.iterdir() if d.is_dir() and d.name.startswith(("sky", "gf"))]
        if not installed_pdks:
            self._add("PDK", ValidationItem("Installed PDKs", "WARN", "No PDKs found. Run: gli-flow install"))

    def _validate_docker(self):
        if self.backend != "docker":
            docker_path = shutil.which("docker")
            if docker_path:
                self._add("DOCKER", ValidationItem("docker", "INFO", f"at {docker_path} (not required for local mode)"))
            else:
                self._add("DOCKER", ValidationItem("docker", "INFO", "Docker not found (not required for local mode)"))
            return
        docker_path = shutil.which("docker")
        if not docker_path:
            self._add("DOCKER", ValidationItem("docker", "FAIL" if is_wsl() else "WARN",
                "Docker not found on PATH. Install Docker for containerized ORFS."))
            return
        self._add("DOCKER", ValidationItem("docker", "PASS", f"at {docker_path}"))
        rc, stdout, stderr = _run_cmd(["docker", "info"])
        if rc == 0:
            self._add("DOCKER", ValidationItem("Daemon", "PASS", "Docker daemon is running"))
        else:
            msg = stderr.strip() or "Docker daemon not running"
            if "permission denied" in msg.lower():
                msg = "Permission denied. Add user to docker group: sudo usermod -aG docker $USER"
            elif "connect" in msg.lower():
                msg = "Docker Desktop is not running. Open Docker Desktop and wait until: docker ps returns successfully."
            self._add("DOCKER", ValidationItem("Daemon", "FAIL", msg))
        if is_wsl():
            sock_paths = [
                "/var/run/docker.sock",
                "/mnt/wsl/docker-desktop/shared-sockets/guest-services/docker.proxy.sock",
            ]
            found = any(Path(s).exists() for s in sock_paths)
            self._add("DOCKER", ValidationItem(
                "WSL Socket", "PASS" if found else "WARN",
                "Docker socket found" if found else "No Docker socket detected. Ensure Docker Desktop is running."
            ))

    def _validate_orfs(self):
        orfs_root = Path(self.orfs_root)
        if not orfs_root.exists():
            self._add("ORFS", ValidationItem("Root", "FAIL", f"Not found: {self.orfs_root}"))
            return
        self._add("ORFS", ValidationItem("Root", "PASS", str(orfs_root)))
        flow_dir = orfs_root / "flow"
        if flow_dir.exists():
            self._add("ORFS", ValidationItem("Flow dir", "PASS", str(flow_dir)))
        tools_dir = orfs_root / "tools"
        if tools_dir.exists():
            install_dirs = [d.name for d in tools_dir.iterdir() if d.is_dir()]
            self._add("ORFS", ValidationItem("Tools", "PASS" if install_dirs else "WARN",
                f"Found: {', '.join(install_dirs)}" if install_dirs else "No tools installed"
            ))

    def _validate_network(self):
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self._add("NETWORK", ValidationItem("Connectivity", "PASS", "Internet reachable"))
        except (OSError, socket.gaierror):
            self._add("NETWORK", ValidationItem("Connectivity", "WARN", "No internet connectivity (offline mode)"))

    def _validate_permissions(self):
        home = Path.home()
        gli_flow_dir = home / ".gli-flow"
        if gli_flow_dir.exists():
            readable = os.access(str(gli_flow_dir), os.R_OK)
            writable = os.access(str(gli_flow_dir), os.W_OK)
            if readable and writable:
                self._add("PERMISSIONS", ValidationItem("~/.gli-flow", "PASS", "Readable and writable"))
            else:
                self._add("PERMISSIONS", ValidationItem("~/.gli-flow", "FAIL",
                    f"readable={readable}, writable={writable}"))
        pdk_root = Path(self.pdk_root)
        if pdk_root.exists():
            readable = os.access(str(pdk_root), os.R_OK)
            self._add("PERMISSIONS", ValidationItem("PDK Root", "PASS" if readable else "FAIL",
                str(pdk_root) if readable else "Not readable"))
        sudo_check = _run_cmd(["sudo", "-n", "true"])
        if sudo_check[0] == 0:
            self._add("PERMISSIONS", ValidationItem("sudo", "PASS", "Passwordless sudo available"))
        else:
            self._add("PERMISSIONS", ValidationItem("sudo", "INFO", "Password may be required for installations"))


def _run_cmd(args: list[str], timeout: int = 5) -> tuple[int, str, str]:
    import subprocess
    try:
        from gli_flow.core.subprocess_env import safe_env
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=safe_env())
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", "command not found"
    except subprocess.TimeoutExpired:
        return -2, "", "timed out"
    except OSError as e:
        return -3, "", str(e)
