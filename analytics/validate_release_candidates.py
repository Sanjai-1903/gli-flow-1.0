from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

HEALTH_FILE = (
    BASE_DIR
    / "execution_health_report.json"
)

with open(HEALTH_FILE) as f:
    health_data = json.load(f)

release_report = []

for run in health_data:

    decision = "BLOCKED"

    if (
        run["health"] == "HEALTHY"
        and run["score"] >= 80
    ):

        decision = "RELEASE_CANDIDATE"

    elif run["health"] == "WARNING":

        decision = "REVIEW_REQUIRED"

    release_report.append({
        "run": run["run"],
        "score": run["score"],
        "health": run["health"],
        "decision": decision
    })

output = (
    BASE_DIR
    / "release_validation_report.json"
)

with open(output, "w") as f:
    json.dump(
        release_report,
        f,
        indent=4
    )

print("=" * 60)
print("GLI-FLOW Release Validation Engine")
print("=" * 60)
print()

for item in release_report:
    print(item)

print()
print(f"[OUTPUT] {output.resolve()}")
