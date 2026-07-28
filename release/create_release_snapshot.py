import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

REPORTS_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

snapshot = {

    "generated_at": str(
        datetime.now()
    ),

    "release_reports": {}
}

report_files = [

    "release_manifest.json",
    "release_validation_report_v2.json"
]

print("=" * 60)
print("GLI-FLOW Release Snapshot")
print("=" * 60)
print()

for report_name in report_files:

    report_path = (
        REPORTS_DIR
        / report_name
    )

    if report_path.exists():

        with open(report_path) as f:

            snapshot["release_reports"][
                report_name
            ] = json.load(f)

        print(f"[CAPTURED] {report_name}")

    else:

        print(f"[MISSING] {report_name}")

output = (
    REPORTS_DIR
    / "release_snapshot_v2.json"
)

with open(output, "w") as f:
    json.dump(
        snapshot,
        f,
        indent=4
    )

print()
print("=" * 60)
print(f"[OUTPUT] {output}")
