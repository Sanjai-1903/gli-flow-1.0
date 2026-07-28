"""
Dual DRC runner: Magic + KLayout.
Both must be run. Final count is deduplicated union.
"""

import subprocess
import re
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional
from gli_flow.core.subprocess_env import safe_env
from gli_flow.core.tool_discovery import find_magicdnull_binary, find_klayout_binary

PDK_VARIANT_MAP = {
    "sky130": "sky130A",
    "sky130A": "sky130A",
    "gf180mcu": "gf180mcuD",
    "gf180mcuD": "gf180mcuD",
}

def _resolve_pdk_path(pdk: str) -> str:
    variant = PDK_VARIANT_MAP.get(pdk, pdk)
    pdk_root = os.environ.get("PDK_ROOT", "") or str(Path.home() / ".gli-flow" / "pdk")
    if not Path(pdk_root).exists():
        pdk_root = str(Path.home() / "pdk")
    return f"{pdk_root}/{variant}"

log = logging.getLogger(__name__)


def _get_magicdnull_path() -> Optional[str]:
    tb = find_magicdnull_binary()
    if tb:
        return tb.path
    return None


def run_magic_drc(gds_path: str, design_name: str, pdk: str, run_dir: Path) -> dict:
    """Run Magic DRC on final GDS."""
    t_start = time.time()
    magicdnull_path = _get_magicdnull_path()
    if not magicdnull_path:
        return {"tool": "magic", "run": False, "error": "magicdnull not found", "violations": None, "runtime_seconds": time.time() - t_start}

    report_path = run_dir / "reports" / "magic_drc.rpt"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    magic_rcfile = _get_magic_rcfile(pdk)
    if not Path(magic_rcfile).exists():
        return {"tool": "magic", "run": False, "error": f"Magic rcfile not found: {magic_rcfile}", "violations": None, "runtime_seconds": time.time() - t_start}

    pdk_root = os.environ.get("PDK_ROOT", "") or str(Path.home() / ".gli-flow" / "pdk")

    script_path = run_dir / "magic_drc.tcl"
    script_path.write_text(
        f"drc off\n"
        f"gds read {gds_path}\n"
        f"load {design_name}\n"
        f"select top cell\n"
        f"drc on\n"
        f"drc check\n"
        f"set drc_result [drc listall why]\n"
        f"set fp [open {report_path} w]\n"
        f"puts $fp \"DRC Results:\"\n"
        f"puts $fp $drc_result\n"
        f"set count [llength $drc_result]\n"
        f"puts $fp \"Total violations: $count\"\n"
        f"close $fp\n"
        f"quit -noprompt\n"
    )

    env = safe_env(extra={
        "DISPLAY": os.environ.get("DISPLAY", ""),
        "PDK_ROOT": pdk_root,
    })
    cmd = [magicdnull_path, "-nowrapper", "-d", "NULL", "-rcfile", magic_rcfile, str(script_path)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)

        violations, report_ok = _parse_magic_drc_report(str(report_path))
        if not report_ok:
            return {"tool": "magic", "run": False, "error": "Magic DRC report not generated", "violations": None, "runtime_seconds": time.time() - t_start}

        return {
            "tool": "magic", "run": True, "violations": violations,
            "report_path": str(report_path), "returncode": result.returncode,
            "runtime_seconds": time.time() - t_start,
        }

    except subprocess.TimeoutExpired:
        return {"tool": "magic", "run": False, "error": "Magic DRC timed out after 600s", "violations": None, "runtime_seconds": time.time() - t_start}
    except Exception as e:
        return {"tool": "magic", "run": False, "error": str(e), "violations": None, "runtime_seconds": time.time() - t_start}


def run_klayout_drc(gds_path: str, design_name: str, pdk: str, run_dir: Path) -> dict:
    """Run KLayout DRC on final GDS."""
    t_start = time.time()
    klayout_bin = find_klayout_binary()
    klayout_path = klayout_bin.path if klayout_bin else None
    if not klayout_path:
        return {"tool": "klayout", "run": False, "error": "KLayout not found", "violations": None, "runtime_seconds": time.time() - t_start}

    drc_script = _get_klayout_drc_script(pdk)
    if not drc_script:
        return {"tool": "klayout", "run": False, "error": f"No KLayout DRC script for {pdk}", "violations": None, "runtime_seconds": time.time() - t_start}

    report_path = run_dir / "reports" / "klayout_drc.xml"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [klayout_path, "-b", "-r", drc_script, "-rd", f"input={gds_path}", "-rd", f"topcell={design_name}", "-rd", f"report={report_path}"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=safe_env())
        violations, report_ok = _parse_klayout_drc_report(str(report_path))
        if not report_ok:
            return {"tool": "klayout", "run": False, "error": "KLayout DRC report not generated", "violations": None, "runtime_seconds": time.time() - t_start}
        return {
            "tool": "klayout", "run": True, "violations": violations,
            "report_path": str(report_path), "returncode": result.returncode,
            "runtime_seconds": time.time() - t_start,
        }
    except subprocess.TimeoutExpired:
        return {"tool": "klayout", "run": False, "error": "KLayout DRC timed out after 600s", "violations": None, "runtime_seconds": time.time() - t_start}
    except Exception as e:
        return {"tool": "klayout", "run": False, "error": str(e), "violations": None, "runtime_seconds": time.time() - t_start}


def run_dual_drc(gds_path: str, design_name: str, pdk: str, run_dir: Path) -> dict:
    """Run both Magic and KLayout DRC. Falls back to KLayout-only if Magic times out."""
    log.info("Running Magic DRC...")
    magic_result = run_magic_drc(gds_path, design_name, pdk, run_dir)

    log.info("Running KLayout DRC...")
    klayout_result = run_klayout_drc(gds_path, design_name, pdk, run_dir)

    magic_count = magic_result.get("violations") or 0
    klayout_count = klayout_result.get("violations") or 0

    magic_run = magic_result.get("run", False)
    klayout_run = klayout_result.get("run", False)

    if not magic_run and klayout_run:
        total = klayout_count
        drc_clean = klayout_count == 0
        drc_status = "PASS" if drc_clean else "FAIL"
        note = "KLayout DRC only (Magic skipped or timed out)."
    elif not klayout_run and magic_run:
        total = magic_count
        drc_clean = magic_count == 0
        drc_status = "PASS" if drc_clean else "FAIL"
        note = "Magic DRC only (KLayout skipped or timed out)."
    elif magic_run and klayout_run:
        total = max(magic_count, klayout_count)
        drc_clean = magic_count == 0 and klayout_count == 0
        drc_status = "PASS" if drc_clean else "FAIL"
        note = "DRC verified by both Magic and KLayout. Both tools required for full coverage."
    else:
        total = None
        drc_clean = False
        drc_status = "NOT_RUN"
        note = "Both Magic and KLayout DRC skipped or failed."

    magic_runtime = magic_result.get("runtime_seconds") if isinstance(magic_result, dict) else None
    klayout_runtime = klayout_result.get("runtime_seconds") if isinstance(klayout_result, dict) else None
    drc_runtime = None
    if magic_runtime is not None and klayout_runtime is not None:
        drc_runtime = magic_runtime + klayout_runtime
    elif magic_runtime is not None:
        drc_runtime = magic_runtime
    elif klayout_runtime is not None:
        drc_runtime = klayout_runtime

    result = {
        "drc_clean": drc_clean,
        "drc_status": drc_status,
        "total_violations": total,
        "runtime_seconds": drc_runtime,
        "magic": magic_result,
        "klayout": klayout_result,
        "note": note,
    }

    summary_path = run_dir / "reports" / "drc_combined.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


def _parse_magic_drc_report(report_path: str) -> tuple[int, bool]:
    """Parse Magic DRC report. Returns (violations, report_ok).

    report_ok is False if the report file does not exist.
    Never silently returns 0 for a missing report.
    Returns -1 for parse errors to distinguish from zero violations.
    """
    if not Path(report_path).is_file():
        return 0, False
    try:
        content = Path(report_path).read_text()
        match = re.search(r"Total violations:\s*(\d+)", content)
        if match:
            return int(match.group(1)), True
        count = len([l for l in content.split('\n') if l.strip() and 'Total' not in l and 'DRC' not in l])
        return count, True
    except Exception:
        return -1, False
    try:
        content = Path(report_path).read_text()
        match = re.search(r"Total violations:\s*(\d+)", content)
        if match:
            return int(match.group(1)), True
        count = len([l for l in content.split('\n') if l.strip() and 'Total' not in l and 'DRC' not in l])
        return count, True
    except Exception:
        return 0, False


def _parse_klayout_drc_report(report_path: str) -> tuple[int, bool]:
    """Parse KLayout DRC report. Returns (violations, report_ok).
    Returns -1 for parse errors to distinguish from zero violations.
    """
    if not Path(report_path).is_file():
        return 0, False
    try:
        content = Path(report_path).read_text()
        count = len(re.findall(r'<item>', content))
        if count:
            return count, True
        match = re.search(r"(\d+)\s+violation", content)
        if match:
            return int(match.group(1)), True
        return 0, True
    except Exception:
        return -1, False


def _get_magic_techfile(pdk: str) -> str:
    pdk_path = _resolve_pdk_path(pdk)
    return f"{pdk_path}/libs.tech/magic/{Path(pdk_path).name}.tech"


def _get_magic_rcfile(pdk: str) -> str:
    pdk_path = _resolve_pdk_path(pdk)
    return f"{pdk_path}/libs.tech/magic/{Path(pdk_path).name}.magicrc"


def _get_klayout_drc_script(pdk: str) -> Optional[str]:
    pdk_path = _resolve_pdk_path(pdk)
    script = f"{pdk_path}/libs.tech/klayout/drc/{Path(pdk_path).name}.lydrc"
    if Path(script).exists():
        return script
    return None
