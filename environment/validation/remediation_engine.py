import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

REPORT = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "environment_validation_report.json"
)

DB = (
    BASE_DIR
    / "environment"
    / "validation"
    / "remediation_db.json"
)

with open(REPORT) as f:
    validation_report = json.load(f)

with open(DB) as f:
    remediation_db = json.load(f)

print("=" * 60)
print("GLI-FLOW Environment Remediation")
print("=" * 60)
print()

for tool in validation_report:

    tool_name = tool["tool"]
    status = tool["status"]

    print(f"{tool_name}: {status}")

    if status == "MISSING":

        fixes = remediation_db.get(
            tool_name,
            {}
        ).get(
            "missing",
            []
        )

        print("Suggested Fixes:")

        for fix in fixes:
            print(f" - {fix}")

    print()
