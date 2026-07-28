from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_FILE = (
    BASE_DIR
    / "execution_dataset.json"
)

with open(DATASET_FILE) as f:
    dataset = json.load(f)

health_report = []

for run in dataset:

    score = run.get("score", 0)
    status = run.get("status")

    if status != "SUCCESS":

        health = "FAILED"

    elif score >= 80:

        health = "HEALTHY"

    elif score >= 60:

        health = "WARNING"

    else:

        health = "CRITICAL"

    health_report.append({
        "run": run["run"],
        "score": score,
        "health": health
    })

output = (
    BASE_DIR
    / "execution_health_report.json"
)

with open(output, "w") as f:
    json.dump(
        health_report,
        f,
        indent=4
    )

print("=" * 60)
print("GLI-FLOW Execution Health Engine")
print("=" * 60)
print()

for item in health_report:
    print(item)

print()
print(f"[OUTPUT] {output.resolve()}")
