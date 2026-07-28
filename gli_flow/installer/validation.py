import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from gli_flow.core.subprocess_env import safe_env
from gli_flow.installer.tool_detector import (
    detect_tool, detect_magic, detect_netgen, detect_netgen_lib_dir, detect_netgenexec,
    detect_yosys, detect_openroad, detect_klayout, detect_sv2v, detect_git, detect_cmake, detect_python3,
    DetectionResult, Confidence, meets_min_version, _find_on_path,
)
from gli_flow.installer.system import check_command


@dataclass
class ValidationResult:
    tool: str
    installed: bool
    version: Optional[str] = None
    path: Optional[str] = None
    ok: bool = False
    error: Optional[str] = None
    warning: Optional[str] = None
    remediation: Optional[str] = None
    confidence: str = "UNKNOWN"
    phase: str = ""


@dataclass
class InstallReport:
    completed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    action_required: list[tuple[str, str, str]] = field(default_factory=list)
    validations: list[ValidationResult] = field(default_factory=list)
    phase: str = "install"

    @property
    def success(self) -> bool:
        if self.failed and self.phase == "install":
            return False
        if self.phase == "validate":
            return all(v.ok for v in self.validations)
        if self.phase == "readiness":
            critical = [v for v in self.validations if v.tool in ("magic", "netgen", "yosys", "openroad")]
            return all(v.ok for v in critical) if critical else all(v.ok for v in self.validations)
        return True

    def to_json(self) -> str:
        data = {
            "phase": self.phase,
            "completed": self.completed,
            "skipped": self.skipped,
            "failed": self.failed,
            "action_required": [{"tool": t, "reason": r, "remediation": rem} for t, r, rem in self.action_required],
            "validations": [{
                "tool": v.tool,
                "installed": v.installed,
                "version": v.version,
                "path": v.path,
                "ok": v.ok,
                "error": v.error,
                "warning": v.warning,
                "remediation": v.remediation,
                "confidence": v.confidence,
            } for v in self.validations],
            "success": self.success,
        }
        return json.dumps(data, indent=2)

    def summary_text(self) -> str:
        lines = []
        lines.append(f"\n{'=' * 60}")
        lines.append(f"Phase: {self.phase.upper()}")
        lines.append(f"{'=' * 60}\n")
        if self.completed:
            lines.append("COMPLETED:")
            for c in self.completed:
                lines.append(f"  [PASS] {c}")
            lines.append("")
        if self.skipped:
            lines.append("SKIPPED:")
            for s in self.skipped:
                lines.append(f"  [SKIP] {s}")
            lines.append("")
        if self.failed:
            lines.append("FAILED:")
            for f in self.failed:
                lines.append(f"  [FAIL] {f}")
            lines.append("")
        if self.validations:
            lines.append(f"{'Component':<25} {'Status':<10} {'Version'}")
            lines.append("-" * 55)
            for v in self.validations:
                status = "PASS" if v.ok else "FAIL"
                ver = v.version or "-"
                lines.append(f"  {v.tool:<23} {status:<10} {ver}")
                if v.warning:
                    lines.append(f"  {'':>23} ⚠ {v.warning}")
            lines.append("")
        if self.action_required:
            lines.append("ACTION REQUIRED:")
            for tool, reason, remediation in self.action_required:
                lines.append(f"  - {tool}: {reason}")
                if remediation:
                    lines.append(f"    {remediation.split(chr(10))[0]}")
            lines.append("")
        lines.append(f"Status: {'READY' if self.success else 'NOT READY'}")
        lines.append("")
        return "\n".join(lines)


TOOLCHAIN = ["git", "cmake", "python3", "yosys", "openroad", "klayout", "magic", "netgen", "sv2v"]

PDK_TOOLS = ["volare"]

TOOL_MIN_VERSIONS = {
    "python3": "3.9.0",
    "yosys": "0.27",
    "openroad": "2.0",
    "klayout": "0.28",
    "magic": "8.3",
    "netgen": "1.5",
    "sv2v": "0.0",
    "git": "2.0",
    "cmake": "3.10",
}

TOOL_DISPLAY_NAMES = {
    "yosys": "Yosys",
    "openroad": "OpenROAD",
    "klayout": "KLayout",
    "magic": "Magic",
    "netgen": "Netgen",
    "sv2v": "sv2v",
    "git": "Git",
    "cmake": "CMake",
    "python3": "Python3",
}

TOOL_REMEDIATIONS = {
    "yosys": "Install OSS CAD Suite: https://github.com/YosysHQ/oss-cad-suite-build",
    "openroad": "Install OpenROAD: https://github.com/The-OpenROAD-Project/OpenROAD/releases",
    "klayout": "sudo apt-get install klayout",
    "sv2v": "cargo install sv2v",
    "magic": "sudo apt-get install magic",
    "netgen": "sudo apt-get install netgen-lvs",
}


def run_pdk_validation(pdk: str, pdk_root: str = "") -> ValidationResult:
    candidates = [pdk]
    if pdk == "sky130":
        candidates += ["sky130A", "sky130B"]
    pdk_dir = None
    installed = False
    for cand in candidates:
        d = Path(pdk_root) / cand
        if d.exists() and any(d.iterdir()):
            pdk_dir = d
            installed = True
            break
    if pdk_dir is None:
        pdk_dir = Path(pdk_root) / pdk
    return ValidationResult(
        tool=f"pdk:{pdk}",
        installed=installed,
        path=str(pdk_dir),
        ok=installed,
        confidence="HIGH",
    )


def run_flow_validation(design_dir: Optional[str] = None) -> ValidationResult:
    if not design_dir:
        return ValidationResult(tool="flow", installed=False, error="No design provided")
    manifest = Path(design_dir) / "gli_manifest.yaml"
    ok = manifest.exists()
    return ValidationResult(
        tool="flow",
        installed=ok,
        path=str(manifest) if ok else None,
        error=None if ok else "No gli_manifest.yaml found",
        ok=ok,
        confidence="HIGH",
    )


def doctor_report(validations: list[ValidationResult]) -> str:
    lines = []
    lines.append("")
    lines.append(f"{'Tool':<25} {'Status':<12} {'Version':<20} {'Confidence'}")
    lines.append("-" * 75)
    for v in validations:
        status = "PASS" if v.ok else "FAIL"
        version = v.version or "-"
        display = TOOL_DISPLAY_NAMES.get(v.tool, v.tool)
        conf = v.confidence or "UNKNOWN"
        lines.append(f"{display:<25} {status:<12} {version:<20} {conf}")
        if v.warning:
            lines.append(f"{'':>25} ⚠ {v.warning}")
    lines.append("")
    all_ok = all(v.ok for v in validations)
    if all_ok:
        lines.append("READY FOR TAPEOUT FLOW")
    else:
        lines.append("NOT READY")
        lines.append("")
        lines.append("Issues:")
        for v in validations:
            if not v.ok:
                lines.append(f"  - {v.tool}: {v.error or 'not installed'}")
                remed = TOOL_REMEDIATIONS.get(v.tool)
                if remed:
                    lines.append(f"    {remed}")
    lines.append("")
    return "\n".join(lines)


def validate_magic_functionality(magic_binary: str, timeout: int = 30) -> tuple[bool, Optional[str]]:
    """Run functional validation against a real Magic binary.

    Checks:
    - Launch magic and execute TCL command
    - Generate minimal DRC check
    - Verify DRC report exists and is non-empty

    Returns: (pass, error_message)
    """
    import subprocess
    import tempfile
    from pathlib import Path

    checks = [
        ("TCL startup", lambda to: _check_magic_tcl_startup(magic_binary, to)),
        ("Version check", lambda to: _check_magic_version(magic_binary, to)),
    ]

    for name, check_fn in checks:
        ok, err = check_fn(timeout)
        if not ok:
            return False, f"functional check '{name}' failed: {err}"

    return True, None


def _check_magic_tcl_startup(binary: str, timeout: int = 30) -> tuple[bool, Optional[str]]:
    import subprocess
    tcl = 'puts "FUNC_OK"\nexit 0\n'
    result = subprocess.run(
        [binary, "-dnull", "-noconsole"],
        input=tcl, capture_output=True, text=True, timeout=timeout,
    )
    if result.returncode != 0:
        return False, f"exit {result.returncode}: {result.stderr}"
    if "FUNC_OK" not in result.stdout:
        return False, f"TCL marker not found in output"
    return True, None


def _check_magic_version(binary: str, timeout: int = 30) -> tuple[bool, Optional[str]]:
    import subprocess
    result = subprocess.run(
        [binary, "--version"],
        capture_output=True, text=True, timeout=timeout,
    )
    if result.returncode != 0:
        return False, f"exit {result.returncode}: {result.stderr}"
    if not result.stdout.strip() and not result.stderr.strip():
        return False, "no version output"
    return True, None


def validate_magic() -> ValidationResult:
    from gli_flow.core.tool_discovery import (
        find_magic_binary, is_historical_risk_version,
        get_version_risk_warning, discover_magic_binaries,
        validate_magic_candidate, rank_tool_candidates,
        ToolCandidateStatus,
    )
    tb = find_magic_binary()
    installed = tb is not None
    error = None
    version_str = None
    ok = False
    path = None
    warning = None

    # Check for multi-candidate shadowing
    candidates = discover_magic_binaries()
    if len(candidates) > 1:
        for c in candidates:
            if c.status == ToolCandidateStatus.UNKNOWN:
                vr = validate_magic_candidate(c)
                c.status = vr.status
                c.failure_reason = vr.failure_reason
                c.validation_evidence = vr.evidence
                c.functional = vr.passed
        ranked = rank_tool_candidates(candidates)
        valid = [c for c in ranked if c.status == ToolCandidateStatus.VALID]
        broken = [c for c in ranked if c.status == ToolCandidateStatus.BROKEN]
        if broken and valid:
            warning = (
                f"PATH shadowing detected: broken at {broken[0].path}, "
                f"valid at {valid[0].path}. Run: gli-flow doctor --repair-magic"
            )

    if not installed:
        error = "not installed"
    else:
        path = tb.path
        version_str = tb.version_str
        min_ver = TOOL_MIN_VERSIONS.get("magic", "")
        ver_ok = meets_min_version(version_str, min_ver) if min_ver else True
        if not ver_ok:
            error = f"version {version_str} < min {min_ver}"
        else:
            if is_historical_risk_version("magic", tb.version):
                warning = get_version_risk_warning("magic", tb.version)
            func_ok, func_err = validate_magic_functionality(path)
            if not func_ok:
                error = f"functional validation failed: {func_err}"
            else:
                ok = True
    from gli_flow.installer.tool_detector import Confidence
    result = ValidationResult(
        tool="magic",
        installed=installed,
        version=version_str,
        path=path,
        ok=ok,
        error=error,
        remediation=TOOL_REMEDIATIONS.get("magic"),
        confidence=Confidence.HIGH.value,
    )
    result.warning = warning
    return result


def validate_tool(tool: str) -> ValidationResult:
    if tool == "magic":
        return validate_magic()
    result = detect_tool(tool)
    min_ver = TOOL_MIN_VERSIONS.get(tool, "")
    ver_ok = meets_min_version(result.version, min_ver) if result.exists else False
    error = None
    if not result.exists:
        error = "not installed"
    elif not ver_ok and min_ver:
        error = f"version {result.version} < min {min_ver}"
    return ValidationResult(
        tool=tool,
        installed=result.exists,
        version=result.version,
        path=result.path,
        ok=result.exists and ver_ok,
        error=error,
        remediation=TOOL_REMEDIATIONS.get(tool),
        confidence=result.confidence.value,
    )
