import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATUS_REPORT = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "execution_status_report.json"
)

with open(STATUS_REPORT) as f:
    status_report = json.load(f)

health_report = []

print("=" * 60)
print("GLI-FLOW Execution Health")
print("=" * 60)
print()

for run in status_report:

    status = run["status"]

    health = "UNKNOWN"

    if status == "SUCCESS":
        health = "HEALTHY"

    elif status == "FAILED":
        health = "FAILED"

    elif status == "INCOMPLETE":
        health = "WARNING"

    result = {

        "run": run["run"],
        "status": status,
        "health": health
    }

    health_report.append(result)

    print(f"{run['run']}")
    print(f"  Status : {status}")
    print(f"  Health : {health}")
    print()

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "execution_health_v2.json"
)

with open(output, "w") as f:
    json.dump(
        health_report,
        f,
        indent=4
    )

print("=" * 60)
print(f"[OUTPUT] {output}")
