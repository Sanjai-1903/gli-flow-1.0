import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

DETECTIONS = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "failure_detections.json"
)

def main():
    try:
        with open(DETECTIONS) as f:
            detections = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        detections = []

    failure_index = {

        "generated_at": str(
            datetime.now()
        ),

        "failure_count": len(
            detections
        ),

        "failures": detections
    }

    print("=" * 60)
    print("GLI-FLOW Failure Index")
    print("=" * 60)
    print()

    print(f"Detected Failures : {len(detections)}")
    print()

    for failure in detections:

        print(f"{failure.get('failure_id', '?')}")
        print(f"  Run      : {failure.get('run', '?')}")
        print(f"  Severity : {failure.get('severity', '?')}")
        print()

    output = (
        BASE_DIR
        / "outputs"
        / "reports"
        / "failure_index.json"
    )

    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        json.dump(
            failure_index,
            f,
            indent=4
        )

    print("=" * 60)
    print(f"[OUTPUT] {output}")


if __name__ == "__main__":
    main()
