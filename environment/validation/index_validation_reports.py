import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent

REPORTS_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

validation_reports = []

for report in REPORTS_DIR.glob("*.json"):

    validation_reports.append({

        "report_name": report.name,
        "path": str(report.resolve()),
        "generated_at": str(
            datetime.fromtimestamp(
                report.stat().st_mtime
            )
        )
    })

index = {

    "generated_at": str(
        datetime.now()
    ),

    "report_count": len(
        validation_reports
    ),

    "reports": validation_reports
}

output = (
    REPORTS_DIR
    / "validation_report_index.json"
)

with open(output, "w") as f:
    json.dump(
        index,
        f,
        indent=4
    )

print("=" * 60)
print("GLI-FLOW Validation Report Index")
print("=" * 60)
print()

print(json.dumps(
    index,
    indent=4
))

print()
print(f"[OUTPUT] {output}")
