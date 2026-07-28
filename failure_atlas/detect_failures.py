import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RUNS_DIR = BASE_DIR / "openroad_runs"
SIGNATURES_FILE = BASE_DIR / "failure_atlas" / "signatures.json"


def load_signatures():
    with open(SIGNATURES_FILE) as f:
        return json.load(f)


def detect_failures_in_log(log_path, signatures=None):
    if signatures is None:
        signatures = load_signatures()
    log_text = Path(log_path).read_text(errors="ignore")
    results = []
    for sig in signatures:
        pattern = sig["observed_signature"]
        if pattern in log_text:
            results.append({
                "run": Path(log_path).parent.name,
                "failure_id": sig["atlas_id"],
                "failure_type": sig["category"],
                "severity": sig["severity"],
                "matched_signature": pattern,
                "description": sig["remediation"],
            })
    return results


def main():
    signatures = load_signatures()
    detections = []

    print("=" * 60)
    print("GLI-FLOW Failure Detection Engine")
    print("=" * 60)
    print()

    for run in RUNS_DIR.iterdir():
        if not run.is_dir():
            continue
        log_file = run / "openroad.log"
        if not log_file.exists():
            continue
        results = detect_failures_in_log(log_file, signatures)
        detections.extend(results)
        for d in results:
            print(f"[DETECTED] {d['run']}")
            print(f"  Failure ID : {d['failure_id']}")
            print(f"  Severity   : {d['severity']}")
            print()

    output = BASE_DIR / "outputs" / "reports" / "failure_detections.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(detections, f, indent=4)

    print("=" * 60)
    print(f"[OUTPUT] {output}")


if __name__ == "__main__":
    main()
