import os
import shutil
import sys
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from gli_flow.database.migrations import migrate_if_needed, _get_db_path
from gli_flow.installer.tool_detector import detect_netgen_lib_dir, detect_netgenexec


@dataclass
class RepairActionResult:
    action: str
    success: bool
    detail: str = ""
    requires_restart: bool = False


class RepairAction(ABC):
    @abstractmethod
    def detect(self) -> bool:
        pass

    @abstractmethod
    def repair(self) -> RepairActionResult:
        pass

    @abstractmethod
    def verify(self) -> bool:
        pass


class SchemaMigrationRepair(RepairAction):
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or _get_db_path()
        self._needs_repair = False

    def detect(self) -> bool:
        try:
            migrate_if_needed(self.db_path)
            self._needs_repair = False
            return False
        except RuntimeError:
            self._needs_repair = True
            return True

    def repair(self) -> RepairActionResult:
        try:
            migrate_if_needed(self.db_path)
            return RepairActionResult("schema-migration", True,
                "All schema migrations applied successfully")
        except RuntimeError as e:
            return RepairActionResult("schema-migration", False, str(e))

    def verify(self) -> bool:
        try:
            migrate_if_needed(self.db_path)
            return True
        except RuntimeError:
            return False


class NetgenLibPathRepair(RepairAction):
    def __init__(self):
        self._needs_repair = False

    def detect(self) -> bool:
        self._needs_repair = detect_netgen_lib_dir() is None
        return self._needs_repair

    def repair(self) -> RepairActionResult:
        candidates = [
            "/usr/lib/netgen",
            "/usr/local/lib/netgen",
        ]
        for d in candidates:
            p = Path(d)
            if p.is_dir():
                for f in p.iterdir():
                    if "tclnetgen" in f.name and f.suffix in (".so", ".dylib"):
                        if d not in (os.environ.get("LD_LIBRARY_PATH", "")):
                            return RepairActionResult("netgen-lib-path", False,
                                f"Found at {d} but not in LD_LIBRARY_PATH. "
                                f"Add: export LD_LIBRARY_PATH={d}:$LD_LIBRARY_PATH",
                                requires_restart=True)
        return RepairActionResult("netgen-lib-path", False,
            "tclnetgen.so not found. Reinstall netgen: gli-flow install --force")

    def verify(self) -> bool:
        return detect_netgen_lib_dir() is not None


class PathRepair(RepairAction):
    def __init__(self, tool_name: str, expected_paths: Optional[list[str]] = None):
        self.tool_name = tool_name
        self.expected_paths = expected_paths or [
            str(Path.home() / ".local" / "bin"),
            str(Path.home() / ".gli-flow" / "tools" / "bin"),
        ]

    def detect(self) -> bool:
        return shutil.which(self.tool_name) is None

    def repair(self) -> RepairActionResult:
        found = False
        for p in self.expected_paths:
            candidate = Path(p) / self.tool_name
            if candidate.exists() and os.access(str(candidate), os.X_OK):
                found = True
                break
        if found:
            return RepairActionResult(f"path-{self.tool_name}", True,
                f"Found at {candidate}. Ensure {candidate.parent} is in your PATH",
                requires_restart=True)
        return RepairActionResult(f"path-{self.tool_name}", False,
            f"Not found. Install with: gli-flow install")

    def verify(self) -> bool:
        return shutil.which(self.tool_name) is not None


class CacheRepair(RepairAction):
    def __init__(self, cache_dirs: Optional[list[str]] = None):
        self.cache_dirs = cache_dirs or [
            str(Path.home() / ".cache" / "gli-flow"),
            str(Path.home() / ".gli-flow"),
        ]

    def detect(self) -> bool:
        return True

    def repair(self) -> RepairActionResult:
        cleaned = []
        failed = []
        for d in self.cache_dirs:
            p = Path(d)
            if p.is_dir():
                try:
                    for f in p.rglob("__pycache__"):
                        shutil.rmtree(str(f), ignore_errors=True)
                    cleaned.append(d)
                except Exception as e:
                    failed.append(f"{d}: {e}")
        if cleaned and not failed:
            return RepairActionResult("cache-clean", True,
                f"Cleaned caches in: {', '.join(cleaned)}")
        elif cleaned:
            return RepairActionResult("cache-clean", True,
                f"Partial: cleaned {', '.join(cleaned)}; failed: {', '.join(failed)}")
        return RepairActionResult("cache-clean", True,
            "No caches found to clean")

    def verify(self) -> bool:
        return True


class BrokenBinaryRepair(RepairAction):
    """Repair a broken binary by renaming it (e.g., magic -> magic.broken).

    Detects if a binary at a higher-PATH-priority location is broken
    while a valid binary exists at a lower-priority location.
    Renames the broken binary to disable it.
    """

    def __init__(self, tool_name: str, broken_path: str, valid_path: str):
        self.tool_name = tool_name
        self.broken_path = broken_path
        self.valid_path = valid_path
        self.backup_path = broken_path + ".broken"

    def detect(self) -> bool:
        broken = Path(self.broken_path)
        valid = Path(self.valid_path)
        return (
            broken.exists()
            and valid.exists()
            and os.access(str(valid), os.X_OK)
        )

    def repair(self) -> RepairActionResult:
        broken = Path(self.broken_path)
        backup = Path(self.backup_path)
        if backup.exists():
            return RepairActionResult(
                f"broken-binary-{self.tool_name}", False,
                f"Backup already exists: {self.backup_path}. Remove it first manually.",
            )
        try:
            broken.rename(backup)
            return RepairActionResult(
                f"broken-binary-{self.tool_name}", True,
                f"Renamed {self.broken_path} -> {self.backup_path}. "
                f"Valid binary at {self.valid_path} will now be used.",
            )
        except OSError as e:
            return RepairActionResult(
                f"broken-binary-{self.tool_name}", False,
                f"Failed to rename {self.broken_path}: {e}",
            )

    def verify(self) -> bool:
        return not Path(self.broken_path).exists()


class PathShadowingRepair(RepairAction):
    """Detect and repair PATH shadowing where a broken local binary shadows
    a valid system binary.

    This is the canonical repair for the 'magic version 0' failure
    pattern where ~/.local/bin/magic is a broken wrapper that shadows
    /usr/bin/magic.
    """

    def __init__(self, tool_name: str = "magic"):
        self.tool_name = tool_name
        self.broken_path: Optional[str] = None
        self.valid_path: Optional[str] = None

    def detect(self) -> bool:
        from gli_flow.core.tool_discovery import (
            discover_magic_binaries,
            validate_magic_candidate,
            rank_tool_candidates,
        )
        candidates = discover_magic_binaries()
        for c in candidates:
            from gli_flow.core.tool_discovery import validate_magic_candidate
            report = validate_magic_candidate(c)
            c.status = report.status
            c.failure_reason = report.failure_reason
            c.validation_evidence = report.evidence
            c.functional = report.passed

        broken = [c for c in candidates if c.status.value == "broken"]
        valid = [c for c in candidates if c.status.value == "valid"]

        if broken and valid:
            self.broken_path = broken[0].path
            self.valid_path = valid[0].path
            return True

        # Also detect via simple existence check
        home_local = Path.home() / ".local" / "bin" / self.tool_name
        system_bin = Path("/usr/bin") / self.tool_name
        if home_local.exists() and system_bin.exists():
            self.broken_path = str(home_local)
            self.valid_path = str(system_bin)
            return True

        return False

    def repair(self) -> RepairActionResult:
        if not self.broken_path or not self.valid_path:
            return RepairActionResult(
                f"path-shadowing-{self.tool_name}", False,
                "No broken/valid pair detected",
            )
        broken = Path(self.broken_path)
        backup = broken.with_suffix(broken.suffix + ".broken")
        if backup.exists():
            return RepairActionResult(
                f"path-shadowing-{self.tool_name}", False,
                f"Backup already exists: {backup}. Skipping.",
            )
        try:
            broken.rename(backup)
            return RepairActionResult(
                f"path-shadowing-{self.tool_name}", True,
                f"Renamed {self.broken_path} -> {backup}. "
                f"Valid binary at {self.valid_path} is now exposed.",
            )
        except OSError as e:
            return RepairActionResult(
                f"path-shadowing-{self.tool_name}", False,
                f"Failed to rename: {e}",
            )

    def verify(self) -> bool:
        if self.broken_path:
            return not Path(self.broken_path).exists()
        return True


class DashboardNodeModulesRepair(RepairAction):
    def detect(self) -> bool:
        dashboard_dir = Path(__file__).resolve().parent.parent.parent / "dashboard"
        node_modules = dashboard_dir / "node_modules"
        return not node_modules.exists() or not any(node_modules.iterdir())

    def repair(self) -> RepairActionResult:
        dashboard_dir = Path(__file__).resolve().parent.parent.parent / "dashboard"
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(dashboard_dir),
                capture_output=True, text=True, timeout=120,
                env={**os.environ, "HOME": str(Path.home())},
            )
            if result.returncode == 0:
                return RepairActionResult("dashboard-node-modules", True,
                    "Dashboard npm dependencies installed")
            return RepairActionResult("dashboard-node-modules", False,
                f"npm install failed: {result.stderr[:200]}")
        except FileNotFoundError:
            return RepairActionResult("dashboard-node-modules", False,
                "npm not found on PATH")
        except subprocess.TimeoutExpired:
            return RepairActionResult("dashboard-node-modules", False,
                "npm install timed out after 120s")

    def verify(self) -> bool:
        dashboard_dir = Path(__file__).resolve().parent.parent.parent / "dashboard"
        node_modules = dashboard_dir / "node_modules"
        return node_modules.exists() and any(node_modules.iterdir())


class ToolInstallRepair(RepairAction):
    def __init__(self, tool_name: str, installer_module_path: str):
        self.tool_name = tool_name
        self.installer_module_path = installer_module_path
        self.module = None

    def detect(self) -> bool:
        return shutil.which(self.tool_name) is None

    def _get_module(self):
        if self.module is not None:
            return self.module
        import importlib
        self.module = importlib.import_module(self.installer_module_path)
        return self.module

    def repair(self) -> RepairActionResult:
        try:
            from gli_flow.installer.system import detect_platform
            mod = self._get_module()
            info = detect_platform()
            ok, msg = mod.install(info)
            if ok:
                return RepairActionResult(f"install-{self.tool_name}", True,
                    f"{self.tool_name}: {msg}")
            return RepairActionResult(f"install-{self.tool_name}", False,
                f"{self.tool_name}: {msg}")
        except Exception as e:
            return RepairActionResult(f"install-{self.tool_name}", False, str(e))

    def verify(self) -> bool:
        return shutil.which(self.tool_name) is not None


class CmakeInstallRepair(RepairAction):
    def detect(self) -> bool:
        return shutil.which("cmake") is None

    def repair(self) -> RepairActionResult:
        try:
            from gli_flow.installer.system import run_sudo
            if shutil.which("apt-get"):
                ok = run_sudo(["apt-get", "install", "-y", "cmake"], "Installing cmake")
                if ok:
                    return RepairActionResult("install-cmake", True, "cmake installed via apt")
            if shutil.which("brew"):
                result = subprocess.run(
                    ["brew", "install", "cmake"],
                    capture_output=True, text=True, timeout=300,
                )
                if result.returncode == 0:
                    return RepairActionResult("install-cmake", True, "cmake installed via brew")
            return RepairActionResult("install-cmake", False,
                "Could not install cmake. Install manually: sudo apt-get install cmake")
        except Exception as e:
            return RepairActionResult("install-cmake", False, str(e))

    def verify(self) -> bool:
        return shutil.which("cmake") is not None


class OpenRoadInstallRepair(RepairAction):
    def detect(self) -> bool:
        return shutil.which("openroad") is None

    def repair(self) -> RepairActionResult:
        try:
            from gli_flow.installer import openroad as or_mod
            from gli_flow.installer.system import detect_platform
            info = detect_platform()
            ok, msg = or_mod.install(info)
            if ok:
                return RepairActionResult("install-openroad", True, f"openroad: {msg}")
            return RepairActionResult("install-openroad", False,
                f"openroad installation failed: {msg}")
        except Exception as e:
            return RepairActionResult("install-openroad", False, str(e))

    def verify(self) -> bool:
        return shutil.which("openroad") is not None


class Sv2vInstallRepair(RepairAction):
    def detect(self) -> bool:
        return shutil.which("sv2v") is None

    def repair(self) -> RepairActionResult:
        try:
            from gli_flow.installer import sv2v as sv_mod
            from gli_flow.installer.system import detect_platform
            info = detect_platform()
            ok, msg = sv_mod.install(info)
            if ok:
                return RepairActionResult("install-sv2v", True, f"sv2v: {msg}")
            return RepairActionResult("install-sv2v", False,
                f"sv2v installation failed: {msg}")
        except Exception as e:
            return RepairActionResult("install-sv2v", False, str(e))

    def verify(self) -> bool:
        return shutil.which("sv2v") is not None


class NetgenInstallRepair(RepairAction):
    def detect(self) -> bool:
        return shutil.which("netgen-lvs") is None and shutil.which("netgen") is None

    def repair(self) -> RepairActionResult:
        try:
            from gli_flow.installer import netgen as ng_mod
            from gli_flow.installer.system import detect_platform
            info = detect_platform()
            ok, msg = ng_mod.install(info)
            if ok:
                return RepairActionResult("install-netgen", True, f"netgen: {msg}")
            return RepairActionResult("install-netgen", False,
                f"netgen installation failed: {msg}")
        except Exception as e:
            return RepairActionResult("install-netgen", False, str(e))

    def verify(self) -> bool:
        return shutil.which("netgen-lvs") is not None or shutil.which("netgen") is not None


class PdkInstallRepair(RepairAction):
    def __init__(self, pdk_name: str = "sky130"):
        self.pdk_name = pdk_name
        self.pdk_root = str(Path.home() / ".gli-flow" / "pdk")

    def detect(self) -> bool:
        pdk_path = Path(self.pdk_root)
        if not pdk_path.exists():
            return True
        installed = [d for d in pdk_path.iterdir() if d.is_dir() and d.name.startswith(("sky", "gf"))]
        return len(installed) == 0

    def repair(self) -> RepairActionResult:
        try:
            from gli_flow.installer import pdk as pdk_mod
            ok = pdk_mod.install_pdk(self.pdk_name, self.pdk_root, force=False)
            if ok:
                return RepairActionResult("install-pdk", True,
                    f"PDK {self.pdk_name} installed to {self.pdk_root}")
            return RepairActionResult("install-pdk", False,
                f"PDK {self.pdk_name} installation failed")
        except Exception as e:
            return RepairActionResult("install-pdk", False, str(e))

    def verify(self) -> bool:
        pdk_path = Path(self.pdk_root)
        if not pdk_path.exists():
            return False
        installed = [d for d in pdk_path.iterdir() if d.is_dir() and d.name.startswith(("sky", "gf"))]
        return len(installed) > 0


class OrfsInstallRepair(RepairAction):
    def __init__(self):
        self.orfs_root = str(Path.home() / ".gli-flow" / "orfs")

    def detect(self) -> bool:
        return not Path(self.orfs_root).exists()

    def repair(self) -> RepairActionResult:
        try:
            from gli_flow.installer import orfs as orfs_mod
            ok = orfs_mod.install(self.orfs_root, force=False)
            if ok:
                return RepairActionResult("install-orfs", True,
                    f"ORFS installed to {self.orfs_root}")
            return RepairActionResult("install-orfs", False, "ORFS installation failed")
        except Exception as e:
            return RepairActionResult("install-orfs", False, str(e))

    def verify(self) -> bool:
        return Path(self.orfs_root).exists()


REPAIR_REGISTRY: list[type[RepairAction]] = [
    SchemaMigrationRepair,
    NetgenLibPathRepair,
    CacheRepair,
]


def get_repair_actions(db_path: Optional[str] = None) -> list[RepairAction]:
    actions: list[RepairAction] = []
    for cls in REPAIR_REGISTRY:
        try:
            if cls == SchemaMigrationRepair:
                actions.append(cls(db_path=db_path))
            else:
                actions.append(cls())
        except Exception:
            pass
    for tool in ["magic", "netgen", "yosys", "openroad", "klayout"]:
        actions.append(PathRepair(tool))
    actions.append(DashboardNodeModulesRepair())
    actions.append(CmakeInstallRepair())
    actions.append(OpenRoadInstallRepair())
    actions.append(Sv2vInstallRepair())
    actions.append(NetgenInstallRepair())
    actions.append(PdkInstallRepair())
    actions.append(OrfsInstallRepair())
    return actions


def run_repairs(db_path: Optional[str] = None) -> list[RepairActionResult]:
    results: list[RepairActionResult] = []
    for action in get_repair_actions(db_path):
        try:
            if action.detect():
                result = action.repair()
                if result.success:
                    verified = action.verify()
                    if not verified:
                        result = RepairActionResult(result.action, False,
                            f"Repair applied but verification failed: {result.detail}")
                results.append(result)
            else:
                results.append(RepairActionResult(
                    type(action).__name__, True, "No repair needed"))
        except Exception as e:
            results.append(RepairActionResult(
                type(action).__name__, False, str(e)))
    return results


def repair_path_shadowing(tool_name: str = "magic") -> RepairActionResult:
    """Convenience function for gli-flow doctor --repair-magic."""
    repair = PathShadowingRepair(tool_name=tool_name)
    if not repair.detect():
        return RepairActionResult(
            f"path-shadowing-{tool_name}", False,
            "No path shadowing detected",
        )
    return repair.repair()
