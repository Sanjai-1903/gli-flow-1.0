import json
import logging
import os
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

FAILURE_ATLAS_DIR = Path(__file__).resolve().parent


def save_failure_record(run_id, design_name, stage, error_message, log_files=None):
    failures_dir = FAILURE_ATLAS_DIR / "records"
    failures_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "run_id": run_id,
        "design_name": design_name,
        "stage": stage,
        "error": error_message,
        "timestamp": datetime.utcnow().isoformat(),
        "log_files": log_files or [],
    }
    fname = f"failure_{run_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    path = failures_dir / fname
    path.write_text(json.dumps(record, indent=2))
    logger.info(f"Failure record saved: {path}")
    return str(path)


def search_failure_web(error_message):
    query = urllib.parse.quote(f"EDA tool error: {error_message}")
    url = f"https://www.google.com/search?q={query}"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (gli-flow failure analysis)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="replace")[:5000]
    except Exception as e:
        logger.warning(f"Web search failed: {e}")
        return None


def save_failure_analysis(run_id, design_name, stage, error_message):
    records_dir = FAILURE_ATLAS_DIR / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    web_results = search_failure_web(error_message)
    analysis = {
        "run_id": run_id,
        "design_name": design_name,
        "failure_stage": stage,
        "error_message": error_message,
        "timestamp": datetime.utcnow().isoformat(),
        "web_search_results": web_results[:2000] if web_results else None,
        "possible_causes": _suggest_causes(error_message),
    }
    fname = f"analysis_{run_id}.json"
    path = records_dir / fname
    path.write_text(json.dumps(analysis, indent=2))
    logger.info(f"Failure analysis saved: {path}")
    return str(path)


def _suggest_causes(error_message):
    suggestions = []
    em = error_message.lower()
    if "oom" in em or "memory" in em or "killed" in em:
        suggestions.append("Out of memory — reduce design complexity or increase available memory")
    if "latch" in em:
        suggestions.append("Latch inferred — add default assignments in case/if statements")
    if "multiple drivers" in em:
        suggestions.append("Multiple drivers on net — fix short circuit in RTL")
    if "module" in em and "not found" in em:
        suggestions.append("Missing module — add missing RTL file or check module name")
    if "overflow" in em:
        suggestions.append("Routing congestion — reduce core utilization or add routing layers")
    if "timing" in em or "wns" in em:
        suggestions.append("Timing violation — reduce logic depth or increase clock period")
    if "drc" in em or "violation" in em:
        suggestions.append("DRC violation — check metal spacing, width, and density rules")
    if not suggestions:
        suggestions.append("Unknown failure — check logs for detailed error messages")
    return suggestions
