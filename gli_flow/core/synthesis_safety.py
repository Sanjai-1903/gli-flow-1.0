"""
Synthesis safety checks.
These checks block the flow when silicon-fatal conditions are detected.
"""

import re
import subprocess
import shutil
import logging
from pathlib import Path
from typing import List, Tuple
from gli_flow.core.exceptions import SynthesisSafetyError
from gli_flow.core.subprocess_env import safe_env

log = logging.getLogger(__name__)


def check_synthesis_log(log_path: str) -> List[dict]:
    """Parse synthesis log for TAPEOUT_BLOCKING conditions."""
    try:
        content = Path(log_path).read_text(errors='ignore')
    except FileNotFoundError:
        return []

    issues = []

    # ── LATCH INFERENCE ──────────────────────────────
    latch_count = len(re.findall(r"Latch inferred|inferring latch", content, re.IGNORECASE))

    if latch_count > 0:
        signal_matches = re.findall(
            r"Latch inferred for signal ['\"]?([^\s'\"\\n]+)",
            content, re.IGNORECASE
        )
        signal_list = ", ".join(signal_matches[:5]) if signal_matches else "check synthesis log"
        raise SynthesisSafetyError(
            check="LATCH_INFERRED",
            detail=(
                f"{latch_count} latch(es) inferred in synthesis.\n"
                f"Signals: {signal_list}\n"
                f"Latches cause unpredictable hold violations in silicon that timing analysis cannot detect."
            ),
            fix=(
                "Add a default assignment in every if/case branch to prevent latch inference.\n"
                "Example: default: out = 1'b0;\n"
                "Or use always_ff (SystemVerilog) to force register inference."
            )
        )

    # ── MULTI-DRIVER NETS ────────────────────────────
    md_count = len(re.findall(r"multiple drivers", content, re.IGNORECASE))

    if md_count > 0:
        raise SynthesisSafetyError(
            check="MULTI_DRIVER_NET",
            detail=(
                f"{md_count} multi-driver net(s) detected.\n"
                f"Multiple drivers on a net = short circuit in silicon."
            ),
            fix=(
                "Find nets driven by more than one always block or assign statement.\n"
                "Each net must have exactly one driver.\n"
                "Use a mux or priority encoder to combine multiple sources."
            )
        )

    # ── MISSING MODULES (already blackboxed) ─────────
    bb_matches = re.findall(
        r"Module ['\"]?([^\s'\"]+)['\"]? not found.*blackbox|"
        r"blackboxing module ['\"]?([^\s'\"]+)",
        content, re.IGNORECASE
    )
    bb_modules = [m[0] or m[1] for m in bb_matches if m[0] or m[1]]

    if bb_modules:
        module_list = ", ".join(bb_modules[:5])
        raise SynthesisSafetyError(
            check="MISSING_MODULE_BLACKBOXED",
            detail=(
                f"Module(s) not found and blackboxed during synthesis: {module_list}\n"
                f"Your GDS will be missing this logic."
            ),
            fix=(
                f"Add the missing module source files to rtl_files in gli_manifest.yaml.\n"
                f"Missing: {module_list}"
            )
        )

    # ── UNDRIVEN SIGNALS (warning only) ──────────────
    undriven_count = len(re.findall(r"undriven|no driver", content, re.IGNORECASE))
    if undriven_count > 0:
        issues.append({
            "type": "UNDRIVEN_SIGNAL",
            "severity": "WARNING",
            "count": undriven_count,
            "message": f"{undriven_count} undriven signal(s) detected. Check synthesis log."
        })
        log.warning(f"Synthesis: {undriven_count} undriven signals detected (not blocking)")

    return issues


def pre_synthesis_hierarchy_check(
    rtl_files: List[str],
    top_module: str,
    include_paths: List[str] = None,
    run_dir: Path = None
) -> Tuple[bool, List[str]]:
    """Run Yosys hierarchy check before synthesis."""
    from gli_flow.core.tool_discovery import find_yosys_binary
    yosys_tb = find_yosys_binary()
    yosys_path = yosys_tb.path if yosys_tb else None
    if not yosys_path:
        return True, []

    inc_args = ""
    if include_paths:
        for p in include_paths:
            inc_args += f"-I{p} "

    read_cmds = ""
    for f in rtl_files:
        read_cmds += f"read_verilog {inc_args}{f}; "

    check_script = f"{read_cmds}hierarchy -check -top {top_module}; check -noinit"

    check_log_path = None
    if run_dir:
        check_log_path = run_dir / "logs" / "pre_synth_check.log"
        check_log_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [yosys_path, "-p", check_script, "-l", str(check_log_path) if run_dir else "/dev/null"],
        capture_output=True,
        text=True,
        env=safe_env(),
        timeout=120
    )

    output = result.stdout + result.stderr

    missing = re.findall(r"Module ['\"]?([A-Za-z0-9_]+)['\"]? not found", output)
    if missing:
        module_list = ", ".join(set(missing))
        raise SynthesisSafetyError(
            check="MISSING_MODULES",
            detail=(
                f"Module(s) not found: {module_list}\n"
                f"Synthesis would blackbox these modules producing an incomplete GDS."
            ),
            fix=(
                f"Add source files for: {module_list}\n"
                f"Update rtl_files in gli_manifest.yaml"
            )
        )

    multi = re.findall(r"multiple drivers on net ([^\s]+)", output, re.IGNORECASE)
    if multi:
        net_list = ", ".join(multi[:5])
        raise SynthesisSafetyError(
            check="MULTI_DRIVER_NET",
            detail=(
                f"Multiple drivers on net(s): {net_list}\n"
                f"This is a short circuit in silicon."
            ),
            fix="Each net must have exactly one driver. Use a mux to combine sources."
        )

    warnings = re.findall(r"Warning:([^\n]+)", output)
    return True, warnings
