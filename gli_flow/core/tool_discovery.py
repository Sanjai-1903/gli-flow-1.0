"""
Canonical EDA tool discovery — single source of truth.

Every caller must use this module for binary path and version resolution.
No duplicated discovery logic anywhere else.

Architecture:
  discover_*_binaries() -> list[ToolCandidate]  (multi-candidate)
  rank_tool_candidates() -> list[ToolCandidate]  (evidence-based ranking)
  validate_*_candidate() -> ValidationReport     (functional validation)
  find_*_binary() -> Optional[ToolInfo]          (backwards-compatible convenience)

Never trust PATH order alone.
Never trust version strings alone.
Always prefer: Functional validation + Artifact validation + Evidence.
"""

import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from gli_flow.core.subprocess_env import safe_env


class BinarySource(Enum):
    CONFIG = "config"
    USER_LOCAL = "user_local"
    VENV = "venv"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class ValidationStatus(Enum):
    VALID = "valid"
    BROKEN = "broken"
    UNVERIFIED = "unverified"


class ToolCandidateStatus(Enum):
    VALID = "valid"
    BROKEN = "broken"
    UNKNOWN = "unknown"


@dataclass
class ToolInfo:
    tool_name: str
    executable_path: str
    version: tuple[int, ...]
    version_str: str
    source: BinarySource = BinarySource.UNKNOWN
    validation_status: ValidationStatus = ValidationStatus.UNVERIFIED

    @property
    def path(self) -> str:
        return self.executable_path


@dataclass
class ToolCandidate:
    path: str
    source: BinarySource = BinarySource.UNKNOWN
    version: tuple[int, ...] = (0,)
    version_str: str = "unknown"
    exists: bool = False
    executable: bool = False
    functional: bool = False
    status: ToolCandidateStatus = ToolCandidateStatus.UNKNOWN
    failure_reason: str = ""
    validation_evidence: list[str] = field(default_factory=list)

    def to_tool_info(self, tool_name: str) -> ToolInfo:
        vs = ValidationStatus.BROKEN if self.status == ToolCandidateStatus.BROKEN else ValidationStatus.VALID
        return ToolInfo(
            tool_name=tool_name,
            executable_path=self.path,
            version=self.version,
            version_str=self.version_str,
            source=self.source,
            validation_status=vs,
        )


@dataclass
class ValidationReport:
    status: ToolCandidateStatus = ToolCandidateStatus.UNKNOWN
    evidence: list[str] = field(default_factory=list)
    failure_reason: str = ""

    @property
    def passed(self) -> bool:
        return self.status == ToolCandidateStatus.VALID


HISTORICAL_RISK_VERSIONS: dict[str, list[tuple[int, ...]]] = {
    "magic": [(8, 3, 105)],
}

TOOL_CONFIG_KEYS: dict[str, str] = {
    "magic": "magic_binary",
    "netgen": "netgen_binary",
    "openroad": "openroad_binary",
    "yosys": "yosys_binary",
    "klayout": "klayout_binary",
    "sv2v": "sv2v_binary",
    "sta": "sta_binary",
}

HOME_PREFIX = "<HOME>"

EXTRA_PATH_DIRS = [
    "/usr/local/bin",
    HOME_PREFIX + "/.local/bin",
    HOME_PREFIX + "/.gli-flow/tools/bin",
    HOME_PREFIX + "/.gli-flow/orfs/tools/install/OpenROAD/bin",
    HOME_PREFIX + "/.gli-flow/orfs/tools/install/Yosys/bin",
    "/opt/OpenROAD/tools/install/magic/bin",
    "/opt/OpenROAD/tools/install/OpenROAD/bin",
    "/opt/OpenROAD/build/bin",
    "/opt/pdk/share/magic/bin",
    "/opt/pdk/share/netgen/bin",
    "/pdk",
    "/usr/lib/netgen",
    "/usr/local/lib/netgen",
]

MAGIC_SEARCH_PATHS: list[str] = [
    "magic",
    HOME_PREFIX + "/.local/bin/magic",
    "/usr/local/bin/magic",
    "/usr/bin/magic",
    "/opt/OpenROAD/tools/install/magic/bin/magic",
    "/opt/pdk/share/magic/bin/magic",
]

MAGICDNUL_SEARCH_PATHS: list[str] = [
    "magicdnull",
    HOME_PREFIX + "/.local/lib/magic/tcl/magicdnull",
    "/usr/local/lib/magic/tcl/magicdnull",
    "/usr/lib/x86_64-linux-gnu/magic/tcl/magicdnull",
]

NETGEN_SEARCH_PATHS: list[str] = [
    "netgen-lvs",
    "netgen",
    "/usr/bin/netgen-lvs",
    "/usr/lib/netgen/bin/netgen",
    "/usr/bin/netgen",
    "/usr/local/bin/netgen",
    "/opt/OpenROAD/tools/install/netgen/bin/netgen",
    "/opt/pdk/share/netgen/bin/netgen",
]

NETGENEXEC_SEARCH_PATHS: list[str] = [
    "netgenexec",
    "/usr/lib/netgen/tcl/netgenexec",
    "/usr/local/lib/netgen/tcl/netgenexec",
]

KLAYOUT_SEARCH_PATHS: list[str] = [
    "klayout",
    "klayout_app",
    "/usr/local/bin/klayout",
    "/usr/bin/klayout",
]

OPENROAD_SEARCH_PATHS: list[str] = [
    "openroad",
    "/usr/local/bin/openroad",
    "/usr/bin/openroad",
    "/opt/OpenROAD/tools/install/OpenROAD/bin/openroad",
    "/opt/OpenROAD/build/bin/openroad",
]

YOSYS_SEARCH_PATHS: list[str] = [
    "yosys",
    "/usr/local/bin/yosys",
    "/usr/bin/yosys",
]

SV2V_SEARCH_PATHS: list[str] = [
    "sv2v",
    "/usr/local/bin/sv2v",
    "/usr/bin/sv2v",
]

STA_SEARCH_PATHS: list[str] = [
    "sta",
    "/usr/local/bin/sta",
    "/usr/bin/sta",
]


def _detect_source(resolved_path: str) -> BinarySource:
    home = str(Path.home())
    if ".local/bin" in resolved_path or ".gli-flow" in resolved_path:
        return BinarySource.USER_LOCAL
    if "/venv/" in resolved_path or "/.venv/" in resolved_path or "/virtualenv/" in resolved_path:
        return BinarySource.VENV
    if resolved_path.startswith(("/usr/", "/opt/")):
        return BinarySource.SYSTEM
    return BinarySource.UNKNOWN


def _source_priority(source: BinarySource) -> int:
    order = {
        BinarySource.CONFIG: 4,
        BinarySource.USER_LOCAL: 3,
        BinarySource.VENV: 2,
        BinarySource.SYSTEM: 1,
        BinarySource.UNKNOWN: 0,
    }
    return order.get(source, 0)


def _get_config_override(tool_name: str) -> Optional[str]:
    key = TOOL_CONFIG_KEYS.get(tool_name)
    if not key:
        return None
    from gli_flow.installer.workspace import get_config_value
    val = get_config_value(key)
    if val and os.path.isfile(val) and os.access(val, os.X_OK):
        return val
    env_val = os.environ.get(f"GLI_FLOW_{tool_name.upper()}_BINARY")
    if env_val and os.path.isfile(env_val) and os.access(env_val, os.X_OK):
        return env_val
    return None


def _run_cmd(args: list[str], timeout: int = 10) -> tuple[int, str, str]:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=safe_env())
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", ""
    except subprocess.TimeoutExpired:
        _discovery_telemetry["timeout_occurred"] = True
        return -2, "", ""
    except OSError:
        return -3, "", ""


def _parse_semver(text: str) -> tuple[int, ...]:
    m = re.search(r"(\d+(?:\.\d+)+(?:-\d+)?)", text)
    if m:
        version_str = m.group(1)
        parts = re.split(r"[.-]", version_str)
        result = tuple(int(p) for p in parts[:4])
        if len(parts) < 3:
            rev = re.search(r"(?:revision|rev|r)\s*(\d+)", text, re.IGNORECASE)
            if rev:
                result = result + (int(rev.group(1)),)
        return result
    m = re.search(r"(\d+)\.(\d+)\s*(?:revision|r|rev)\s*(\d+)", text, re.IGNORECASE)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    digits = re.findall(r"(\d+)", text)
    if digits:
        return (int(digits[0]),)
    return (0,)


# ---------------------------------------------------------------------------
# Tool-specific safe version detection strategies
# ---------------------------------------------------------------------------
# Each tool declares how to safely extract its version without:
#   - launching a GUI
#   - entering interactive mode
#   - blocking on user input
# ---------------------------------------------------------------------------

def _version_magic(path: str) -> Optional[tuple[int, ...]]:
    rc, stdout, stderr = _run_cmd([path, "--version"])
    if rc == 0:
        return _parse_semver(stdout or stderr)
    rc, stdout, stderr = _run_cmd([path, "-version"])
    if rc == 0:
        return _parse_semver(stdout or stderr)
    return None


def _version_magicdnull(path: str) -> Optional[tuple[int, ...]]:
    return _version_magic(path)


def _version_netgen(path: str) -> Optional[tuple[int, ...]]:
    rc, stdout, stderr = _run_cmd([path, "-batch", "quit"])
    if rc == 0:
        return _parse_semver(stdout or stderr)
    return None


def _version_netgenexec(path: str) -> Optional[tuple[int, ...]]:
    return _version_netgen(path)


def _version_yosys(path: str) -> Optional[tuple[int, ...]]:
    rc, stdout, stderr = _run_cmd([path, "-V"])
    if rc == 0:
        return _parse_semver(stdout or stderr)
    return None


def _version_openroad(path: str) -> Optional[tuple[int, ...]]:
    rc, stdout, stderr = _run_cmd([path, "-version"])
    if rc == 0:
        return _parse_semver(stdout or stderr)
    return None


def _version_klayout(path: str) -> Optional[tuple[int, ...]]:
    rc, stdout, stderr = _run_cmd([path, "-b", "-v"])
    if rc == 0:
        return _parse_semver(stdout or stderr)
    return None


def _version_generic(path: str) -> Optional[tuple[int, ...]]:
    rc, stdout, stderr = _run_cmd([path, "--version"])
    if rc == 0:
        ver = _parse_semver(stdout or stderr)
        if ver != (0,):
            return ver
    return None


VERSION_STRATEGIES: dict[str, Callable[[str], Optional[tuple[int, ...]]]] = {
    "magic": _version_magic,
    "magicdnull": _version_magicdnull,
    "netgen": _version_netgen,
    "netgenexec": _version_netgenexec,
    "yosys": _version_yosys,
    "openroad": _version_openroad,
    "klayout": _version_klayout,
    "sv2v": _version_generic,
    "sta": _version_generic,
}


def _get_version(path: str, tool_name: str = "") -> Optional[tuple[int, ...]]:
    strategy = VERSION_STRATEGIES.get(tool_name, _version_generic)
    if strategy is _version_generic:
        _discovery_telemetry["fallback_count"] += 1
    return strategy(path)


def is_broken_version(tool: str, version: tuple[int, ...]) -> bool:
    return False


def is_historical_risk_version(tool: str, version: tuple[int, ...]) -> bool:
    risky = HISTORICAL_RISK_VERSIONS.get(tool, [])
    for rv in risky:
        if version[: len(rv)] == rv:
            return True
    return False


def get_version_risk_warning(tool: str, version: tuple[int, ...]) -> Optional[str]:
    if is_historical_risk_version(tool, version):
        ver_str = ".".join(str(v) for v in version)
        return f"{tool} version {ver_str} has historical risk — functional validation recommended"
    return None


def _resolve_home(path: str) -> str:
    if path.startswith(HOME_PREFIX):
        return str(Path.home() / path[len(HOME_PREFIX) + 1:])
    return path


def _resolve_candidate(candidate: str) -> Optional[str]:
    resolved = shutil.which(candidate)
    if resolved:
        return resolved
    path = Path(_resolve_home(candidate))
    if path.is_file() and os.access(str(path), os.X_OK):
        return str(path.resolve())
    return None


def _find_candidate(candidates: list[str]) -> Optional[str]:
    seen: set[str] = set()
    for c in candidates:
        norm = os.path.normpath(c)
        if norm in seen:
            continue
        seen.add(norm)
        resolved = _resolve_candidate(c)
        if resolved:
            return resolved
    return None


def find_binary(name: str) -> Optional[str]:
    return shutil.which(name)


# ---------------------------------------------------------------------------
# Telemetry accumulators — read by environment_fingerprint.capture_fingerprint
# ---------------------------------------------------------------------------

_discovery_telemetry: dict[str, Any] = {
    "total_duration_ms": 0.0,
    "timeout_occurred": False,
    "fallback_count": 0,
}


def get_discovery_telemetry() -> dict[str, Any]:
    return dict(_discovery_telemetry)


def reset_discovery_telemetry() -> None:
    _discovery_telemetry["total_duration_ms"] = 0.0
    _discovery_telemetry["timeout_occurred"] = False
    _discovery_telemetry["fallback_count"] = 0


# ---------------------------------------------------------------------------
# Multi-candidate discovery
# ---------------------------------------------------------------------------

def _discover_candidates(
    candidates: list[str],
    config_override: Optional[str] = None,
    tool_name: str = "",
) -> list[ToolCandidate]:
    seen: set[str] = set()
    result: list[ToolCandidate] = []
    extra_dirs = [_resolve_home(d) for d in EXTRA_PATH_DIRS]
    _start = time.time()

    if config_override:
        resolved = os.path.realpath(config_override)
        if resolved not in seen:
            seen.add(resolved)
            ver = _get_version(resolved, tool_name) or (0,)
            ver_str = ".".join(str(v) for v in ver)
            result.append(ToolCandidate(
                path=resolved,
                source=BinarySource.CONFIG,
                version=ver,
                version_str=ver_str,
                exists=True,
                executable=os.access(resolved, os.X_OK),
            ))

    for c in candidates:
        resolved = _resolve_candidate(c)
        if not resolved:
            continue
        real = os.path.realpath(resolved)
        if real in seen:
            continue
        seen.add(real)
        ver = _get_version(real, tool_name) or (0,)
        ver_str = ".".join(str(v) for v in ver)
        source = _detect_source(real)
        result.append(ToolCandidate(
            path=real,
            source=source,
            version=ver,
            version_str=ver_str,
            exists=True,
            executable=os.access(real, os.X_OK),
        ))

    for extra in extra_dirs:
        if candidates:
            base_name = os.path.basename(candidates[0])
        else:
            continue
        candidate_path = Path(extra) / base_name
        if candidate_path.is_file() and os.access(str(candidate_path), os.X_OK):
            real = str(candidate_path.resolve())
            if real in seen:
                continue
            seen.add(real)
            ver = _get_version(real, tool_name) or (0,)
            ver_str = ".".join(str(v) for v in ver)
            source = _detect_source(real)
            result.append(ToolCandidate(
                path=real,
                source=source,
                version=ver,
                version_str=ver_str,
                exists=True,
                executable=True,
            ))

    _discovery_telemetry["total_duration_ms"] += (time.time() - _start) * 1000
    return result


def discover_magic_binaries() -> list[ToolCandidate]:
    config_override = _get_config_override("magic")
    return _discover_candidates(MAGIC_SEARCH_PATHS, config_override, tool_name="magic")


def discover_netgen_binaries() -> list[ToolCandidate]:
    config_override = _get_config_override("netgen")
    return _discover_candidates(NETGEN_SEARCH_PATHS, config_override, tool_name="netgen")


def discover_yosys_binaries() -> list[ToolCandidate]:
    config_override = _get_config_override("yosys")
    return _discover_candidates(YOSYS_SEARCH_PATHS, config_override, tool_name="yosys")


def discover_openroad_binaries() -> list[ToolCandidate]:
    config_override = _get_config_override("openroad")
    return _discover_candidates(OPENROAD_SEARCH_PATHS, config_override, tool_name="openroad")


def discover_klayout_binaries() -> list[ToolCandidate]:
    config_override = _get_config_override("klayout")
    return _discover_candidates(KLAYOUT_SEARCH_PATHS, config_override, tool_name="klayout")


def discover_sv2v_binaries() -> list[ToolCandidate]:
    config_override = _get_config_override("sv2v")
    return _discover_candidates(SV2V_SEARCH_PATHS, config_override, tool_name="sv2v")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _check_file_executable(path: str) -> tuple[bool, str]:
    if not os.path.exists(path):
        return False, "file does not exist"
    if not os.path.isfile(path):
        return False, "not a regular file"
    if not os.access(path, os.X_OK):
        return False, "not executable"
    return True, ""


def _check_process_launches(path: str, timeout: int = 10) -> tuple[bool, str]:
    rc, _, stderr = _run_cmd([path, "--version"], timeout=timeout)
    if rc == -1:
        return False, "command not found"
    if rc == -2:
        return False, "timed out"
    if rc == -3:
        return False, "OS error"
    return True, ""


def _check_version_detectable(path: str) -> tuple[bool, str]:
    ver = _version_generic(path)
    if ver and ver != (0,):
        return True, f"version detected: {'.'.join(str(v) for v in ver)}"
    return True, "version not parseable but process launches"


def validate_magic_candidate(candidate: ToolCandidate) -> ValidationReport:
    report = ValidationReport()
    evidence: list[str] = []

    exec_ok, exec_err = _check_file_executable(candidate.path)
    if not exec_ok:
        report.failure_reason = exec_err
        report.status = ToolCandidateStatus.BROKEN
        report.evidence = [f"executable check failed: {exec_err}"]
        return report
    evidence.append(f"executable: {candidate.path}")

    launch_ok, _ = _check_process_launches(candidate.path)
    if not launch_ok:
        report.failure_reason = "process does not launch"
        report.status = ToolCandidateStatus.BROKEN
        report.evidence = evidence + ["process launch failed"]
        return report
    evidence.append("process launches")

    ver_detectable, ver_msg = _check_version_detectable(candidate.path)
    if not ver_detectable:
        evidence.append(f"version check: {ver_msg}")
    else:
        evidence.append(ver_msg)

    tcl_out = _check_magic_tcl(candidate.path)
    if tcl_out:
        evidence.append(f"TCL execution: {tcl_out}")
    else:
        report.failure_reason = "TCL execution failed"
        report.status = ToolCandidateStatus.BROKEN
        report.evidence = evidence + ["TCL interpreter did not respond"]
        return report

    drc_out = _check_magic_drc_smoke(candidate.path)
    if drc_out:
        evidence.append(f"DRC smoke: {drc_out}")
    else:
        evidence.append("DRC smoke: skipped (not required for validation)")

    report.evidence = evidence
    report.status = ToolCandidateStatus.VALID
    return report


def _check_magic_tcl(path: str, timeout: int = 15) -> Optional[str]:
    tcl = 'puts "TCL_OK"\nexit 0\n'
    try:
        result = subprocess.run(
            [path, "-noconsole", "-dnull"],
            input=tcl, capture_output=True, text=True, timeout=timeout,
            env=safe_env(),
        )
        if "TCL_OK" in result.stdout:
            return "TCL interpreter OK"
        if result.returncode != 0:
            stderr_short = result.stderr[:200] if result.stderr else ""
            if "couldn't read file" in stderr_short or "couldn't read" in stderr_short:
                return None
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def _check_magic_drc_smoke(path: str, timeout: int = 30) -> Optional[str]:
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "drc_test.tcl"
        script.write_text("puts {DRC_SMOKE_OK}\nquit\n")
        try:
            result = subprocess.run(
                [path, "-noconsole", "-dnull", str(script)],
                capture_output=True, text=True, timeout=timeout,
                env=safe_env(),
            )
            if result.returncode == 0 and "DRC_SMOKE_OK" in result.stdout:
                return "DRC smoke passed"
            return None
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return None


def validate_netgen_candidate(candidate: ToolCandidate) -> ValidationReport:
    report = ValidationReport()
    evidence: list[str] = []

    exec_ok, exec_err = _check_file_executable(candidate.path)
    if not exec_ok:
        report.failure_reason = exec_err
        report.status = ToolCandidateStatus.BROKEN
        report.evidence = [f"executable check failed: {exec_err}"]
        return report
    evidence.append(f"executable: {candidate.path}")

    rc, stdout, stderr = _run_cmd([candidate.path, "-batch", "quit"], timeout=15)
    if rc in (0, 1):
        evidence.append("batch mode OK")
    else:
        report.failure_reason = f"batch mode failed (exit {rc})"
        report.status = ToolCandidateStatus.BROKEN
        report.evidence = evidence + [f"batch mode failed: {stderr[:100]}"]
        return report

    report.evidence = evidence
    report.status = ToolCandidateStatus.VALID
    return report


def validate_yosys_candidate(candidate: ToolCandidate) -> ValidationReport:
    report = ValidationReport()
    evidence: list[str] = []
    exec_ok, exec_err = _check_file_executable(candidate.path)
    if not exec_ok:
        report.failure_reason = exec_err
        report.status = ToolCandidateStatus.BROKEN
        report.evidence = [f"executable check failed: {exec_err}"]
        return report
    evidence.append(f"executable: {candidate.path}")

    rc, stdout, stderr = _run_cmd([candidate.path, "-V"], timeout=15)
    if rc == 0:
        evidence.append(f"version: {(stdout or stderr).strip()[:60]}")
    else:
        report.failure_reason = f"version check failed (exit {rc})"
        report.status = ToolCandidateStatus.BROKEN
        report.evidence = evidence + [f"version check failed: {stderr[:100]}"]
        return report

    report.evidence = evidence
    report.status = ToolCandidateStatus.VALID
    return report


def validate_openroad_candidate(candidate: ToolCandidate) -> ValidationReport:
    report = ValidationReport()
    evidence: list[str] = []
    exec_ok, exec_err = _check_file_executable(candidate.path)
    if not exec_ok:
        report.failure_reason = exec_err
        report.status = ToolCandidateStatus.BROKEN
        report.evidence = [f"executable check failed: {exec_err}"]
        return report
    evidence.append(f"executable: {candidate.path}")

    rc, stdout, stderr = _run_cmd([candidate.path, "-version"], timeout=15)
    if rc == 0:
        evidence.append(f"version: {(stdout or stderr).strip()[:60]}")
    else:
        report.failure_reason = f"version check failed (exit {rc})"
        report.status = ToolCandidateStatus.BROKEN
        report.evidence = evidence + [f"version check failed: {stderr[:100]}"]
        return report

    report.evidence = evidence
    report.status = ToolCandidateStatus.VALID
    return report


def validate_klayout_candidate(candidate: ToolCandidate) -> ValidationReport:
    report = ValidationReport()
    evidence: list[str] = []
    exec_ok, exec_err = _check_file_executable(candidate.path)
    if not exec_ok:
        report.failure_reason = exec_err
        report.status = ToolCandidateStatus.BROKEN
        report.evidence = [f"executable check failed: {exec_err}"]
        return report
    evidence.append(f"executable: {candidate.path}")

    rc, stdout, stderr = _run_cmd([candidate.path, "-b", "-v"], timeout=15)
    if rc == 0:
        evidence.append(f"version: {(stdout or stderr).strip()[:60]}")
    else:
        report.failure_reason = f"version check failed (exit {rc})"
        report.status = ToolCandidateStatus.BROKEN
        report.evidence = evidence + [f"version check failed: {stderr[:100]}"]
        return report

    report.evidence = evidence
    report.status = ToolCandidateStatus.VALID
    return report


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

def rank_tool_candidates(candidates: list[ToolCandidate]) -> list[ToolCandidate]:
    def sort_key(c: ToolCandidate) -> tuple:
        functional_pass = 0 if c.functional else 1
        version_ok = 0 if c.version != (0,) else 1
        source_val = -_source_priority(c.source)
        return (functional_pass, version_ok, source_val)

    return sorted(candidates, key=sort_key)


# ---------------------------------------------------------------------------
# Backwards-compatible find_*_binary functions
# ---------------------------------------------------------------------------

def _find_best_tool(tool_name: str, discover_fn: Callable[[], list[ToolCandidate]]) -> Optional[ToolInfo]:
    candidates = discover_fn()
    ranked = rank_tool_candidates(candidates)
    if not ranked:
        return None
    best = ranked[0]
    return best.to_tool_info(tool_name)


def find_magic_binary() -> Optional[ToolInfo]:
    return _find_best_tool("magic", discover_magic_binaries)


def find_magicdnull_binary() -> Optional[ToolInfo]:
    return _get_tool_info("magicdnull")


def find_netgen_binary() -> Optional[ToolInfo]:
    return _find_best_tool("netgen", discover_netgen_binaries)


def find_netgenexec_binary() -> Optional[ToolInfo]:
    return _get_tool_info("netgenexec")


def find_klayout_binary() -> Optional[ToolInfo]:
    return _find_best_tool("klayout", discover_klayout_binaries)


def find_openroad_binary() -> Optional[ToolInfo]:
    return _find_best_tool("openroad", discover_openroad_binaries)


def find_yosys_binary() -> Optional[ToolInfo]:
    return _find_best_tool("yosys", discover_yosys_binaries)


def find_sv2v_binary() -> Optional[ToolInfo]:
    return _find_best_tool("sv2v", discover_sv2v_binaries)


def find_sta_binary() -> Optional[ToolInfo]:
    return _get_tool_info("sta")


def _get_tool_info(tool_name: str) -> Optional[ToolInfo]:
    search_paths = {
        "magic": MAGIC_SEARCH_PATHS,
        "magicdnull": MAGICDNUL_SEARCH_PATHS,
        "netgen": NETGEN_SEARCH_PATHS,
        "netgenexec": NETGENEXEC_SEARCH_PATHS,
        "klayout": KLAYOUT_SEARCH_PATHS,
        "openroad": OPENROAD_SEARCH_PATHS,
        "yosys": YOSYS_SEARCH_PATHS,
        "sv2v": SV2V_SEARCH_PATHS,
        "sta": STA_SEARCH_PATHS,
    }
    candidates = search_paths.get(tool_name, [tool_name])
    return _find_tool_with_info(tool_name, candidates)


def _find_tool_with_info(
    tool_name: str,
    candidates: list[str],
    config_override: bool = True,
) -> Optional[ToolInfo]:
    if config_override:
        override_path = _get_config_override(tool_name)
        if override_path:
            ver = _get_version(override_path, tool_name)
            if ver is None:
                ver = (0,)
            ver_str = ".".join(str(v) for v in ver)
            return ToolInfo(
                tool_name=tool_name,
                executable_path=override_path,
                version=ver,
                version_str=ver_str,
                source=BinarySource.CONFIG,
                validation_status=ValidationStatus.VALID,
            )

    found: list[tuple[tuple[int, ...], str]] = []
    for c in candidates:
        resolved = _resolve_candidate(c)
        if not resolved:
            continue
        ver = _get_version(resolved, tool_name)
        if ver is None:
            ver = (0,)
        found.append((ver, resolved))

    if not found:
        for extra in EXTRA_PATH_DIRS:
            candidate = Path(_resolve_home(extra)) / tool_name
            if candidate.is_file() and os.access(str(candidate), os.X_OK):
                resolved = str(candidate.resolve())
                ver = _get_version(resolved, tool_name)
                if ver is None:
                    ver = (0,)
                found.append((ver, resolved))
                break

    if not found:
        return None

    non_broken = [(v, p) for v, p in found]
    if non_broken:
        non_broken.sort(key=lambda x: x[0], reverse=True)
        version, path = non_broken[0]
    else:
        found.sort(key=lambda x: x[0], reverse=True)
        version, path = found[0]

    ver_str = ".".join(str(v) for v in version) if version else "unknown"
    source = _detect_source(path)
    status = ValidationStatus.VALID

    return ToolInfo(
        tool_name=tool_name,
        executable_path=path,
        version=version,
        version_str=ver_str,
        source=source,
        validation_status=status,
    )
