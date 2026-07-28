import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DETECTIONS = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "failure_detections.json"
)

SIGNATURES = (
    BASE_DIR
    / "failure_atlas"
    / "signatures.json"
)

def main():
    try:
        with open(DETECTIONS) as f:
            detections = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        detections = []

    try:
        with open(SIGNATURES) as f:
            signatures = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        signatures = []

    remediation_report = []

    print("=" * 60)
    print("GLI-FLOW Remediation Engine")
    print("=" * 60)
    print()

    for detection in detections:

        failure_id = detection.get("failure_id", "?")

        for signature in signatures:

            if signature.get("atlas_id") == failure_id:

                remediation = {
                    "run": detection.get("run", "?"),
                    "failure_id": failure_id,
                    "severity": signature.get("severity", "UNKNOWN"),
                    "description": signature.get("description", "No description"),
                    "recommended_actions": signature.get("remediation", "No remediation available"),
                }

                remediation_report.append(remediation)

                print(f"[REMEDIATION] {failure_id}")
                print(f"  Run : {detection.get('run', '?')}")
                print()

    output = (
        BASE_DIR
        / "outputs"
        / "reports"
        / "remediation_report.json"
    )

    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        json.dump(
            remediation_report,
            f,
            indent=4
        )

    print("=" * 60)
    print(f"[OUTPUT] {output}")


if __name__ == "__main__":
    main()
