import json
import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent

SIGNATURE_FILE = ROOT_DIR / "failure_atlas" / "signatures.json"

RUNS_DIR = ROOT_DIR / "runs"


def load_signatures():
    signatures = []
    seen_ids = set()
    # Load from new directory structure
    signatures_dir = ROOT_DIR / "failure_atlas" / "signatures"
    if signatures_dir.exists():
        for json_file in sorted(signatures_dir.rglob("*.json")):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for entry in data:
                        sig_id = entry.get("atlas_id") or entry.get("rule_id")
                        if sig_id:
                            if sig_id not in seen_ids:
                                seen_ids.add(sig_id)
                                signatures.append(entry)
                        else:
                            signatures.append(entry)
                else:
                    sig_id = data.get("atlas_id") or data.get("rule_id")
                    if sig_id:
                        if sig_id not in seen_ids:
                            seen_ids.add(sig_id)
                            signatures.append(data)
                    else:
                        signatures.append(data)
            except (FileNotFoundError, json.JSONDecodeError):
                continue
    # Always load legacy signatures.json (merged, not fallback)
    try:
        with open(SIGNATURE_FILE, "r") as f:
            legacy = json.load(f)
            for entry in legacy:
                sig_id = entry.get("atlas_id") or entry.get("rule_id")
                if sig_id:
                    if sig_id not in seen_ids:
                        seen_ids.add(sig_id)
                        signatures.append(entry)
                else:
                    signatures.append(entry)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return signatures


def scan_file(log_file, signatures):
    findings = []

    try:
        content = log_file.read_text(errors="ignore")
        content_lower = content.lower()

        for sig in signatures:
            pattern = sig.get("observed_signature", "")
            if not pattern:
                continue

            # Try exact regex match first
            regex = re.compile(re.escape(pattern), re.IGNORECASE)
            if regex.search(content):
                sig = dict(sig)
                sig["_detection_method"] = "EXACT_MATCH"
                findings.append(sig)
                continue

            # Fallback: keyword-based matching using category + key terms
            keywords = _get_keywords(sig)
            if keywords and any(kw in content_lower for kw in keywords):
                sig = dict(sig)
                sig["_detection_method"] = "KEYWORD_FALLBACK"
                findings.append(sig)

    except Exception as e:
        log.warning(f"Failed to scan file {log_file}: {e}")

    return findings


def _get_keywords(sig):
    category = sig.get("category", "").lower()
    atlas_id = sig.get("atlas_id", "")

    keyword_map = {
        "timing": ["wns", "tns", "slack", "setup", "hold", "violat"],
        "drc": ["drc", "violation", "spacing", "width", "enclosure", "antenna"],
        "congestion": ["overflow", "congestion", "density"],
        "power": ["ir drop", "voltage", "power"],
        "logic": ["latch", "inferred", "combinatorial loop", "module.*not found"],
        "library": ["not found", "missing", "can't open"],
        "floorplan": ["aspect ratio", "core boundary", "pin.*place"],
        "routing": ["open net", "short", "unconnected"],
    }
    return keyword_map.get(category, [])


def scan_runs():
    signatures = load_signatures()

    all_findings = []

    for run_dir in RUNS_DIR.iterdir():

        if not run_dir.is_dir():
            continue

        for log_file in run_dir.rglob("*.log"):

            findings = scan_file(log_file, signatures)

            for finding in findings:
                result = {
                    "run": run_dir.name,
                    "log": str(log_file),
                    "signature": finding
                }

                all_findings.append(result)

    return all_findings


def main():
    print("=" * 60)
    print("GLI-FLOW Failure Signature Engine")
    print("=" * 60)

    findings = scan_runs()

    if not findings:
        print("[INFO] No known signatures detected")
        return

    for item in findings:

        sig = item["signature"]

        print("\n----------------------------------------")
        print(f"RUN        : {item.get('run', '?')}")
        print(f"SIGNATURE  : {sig.get('atlas_id', '?')}")
        print(f"CATEGORY   : {sig.get('category', '?')}")
        print(f"SEVERITY   : {sig.get('severity', '?')}")
        print(f"SIGNATURE  : {sig.get('observed_signature', '?')}")
        print(f"LOG FILE   : {item.get('log', '?')}")

    print("\n========================================")
    print("[COMPLETE] Signature scan finished")
    print("========================================")


if __name__ == "__main__":
    main()
