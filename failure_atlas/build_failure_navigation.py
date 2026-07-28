import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REPORTS_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

navigation = {

    "failure_detections": None,
    "remediation_report": None,
    "failure_index": None,
    "failure_trend_report": None,
    "failure_snapshot": None
}

report_mapping = {

    "failure_detections":
        "failure_detections.json",

    "remediation_report":
        "remediation_report.json",

    "failure_index":
        "failure_index.json",

    "failure_trend_report":
        "failure_trend_report.json",

    "failure_snapshot":
        "failure_snapshot.json"
}

def main():
    print("=" * 60)
    print("GLI-FLOW Failure Navigation")
    print("=" * 60)
    print()

    for key, filename in report_mapping.items():

        path = (
            REPORTS_DIR
            / filename
        )

        if path.exists():

            navigation[key] = str(
                path.resolve()
            )

            print(f"[FOUND] {key}")

        else:

            print(f"[MISSING] {key}")

    output = (
        REPORTS_DIR
        / "failure_navigation.json"
    )

    with open(output, "w") as f:
        json.dump(
            navigation,
            f,
            indent=4
        )

    print()
    print("=" * 60)
    print(f"[OUTPUT] {output}")


if __name__ == "__main__":
    main()
