import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

HEALTH_REPORT = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "execution_health_v3.json"
)

with open(HEALTH_REPORT) as f:
    health_report = json.load(f)

results = []

print("=" * 60)
print("GLI-FLOW Reliability Intelligence V2")
print("=" * 60)
print()

for run in health_report:

    health = run["health"]

    score = 0
    confidence = "LOW"

    if health == "HEALTHY":

        score = 95
        confidence = "HIGH"

    elif health == "WARNING":

        score = 65
        confidence = "MEDIUM"

    elif health == "FAILED":

        score = 20
        confidence = "LOW"

    else:

        score = 0
        confidence = "LOW"

    result = {

        "run": run["run"],
        "status": run["status"],
        "health": run["health"],
        "reliability_score": score,
        "confidence": confidence
    }

    results.append(result)

    print(f"{run['run']}")
    print(f"  Status      : {run['status']}")
    print(f"  Health      : {run['health']}")
    print(f"  Score       : {score}")
    print(f"  Confidence  : {confidence}")
    print()

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "reliability_report_v2.json"
)

with open(output, "w") as f:
    json.dump(
        results,
        f,
        indent=4
    )

print("=" * 60)
print(f"[OUTPUT] {output}")
