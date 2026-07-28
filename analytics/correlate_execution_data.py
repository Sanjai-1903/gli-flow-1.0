from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

METRICS_FILE = BASE_DIR / "openroad_metrics.json"
SCORES_FILE = BASE_DIR / "run_scores.json"

with open(METRICS_FILE) as f:
    metrics = json.load(f)

with open(SCORES_FILE) as f:
    scores = json.load(f)

score_map = {
    item["run"]: item
    for item in scores
}

correlated = []

for metric in metrics:

    run_name = metric["run"]

    score_data = score_map.get(
        run_name,
        {}
    )

    combined = {
        "run": run_name,
        "status": metric.get(
            "flow_status"
        ),
        "score": score_data.get(
            "score"
        ),
        "cell_count": metric.get(
            "cell_count"
        ),
        "runtime_seconds": metric.get(
            "runtime_seconds"
        ),
        "wns": metric.get("wns"),
        "tns": metric.get("tns"),
        "power": metric.get("power")
    }

    correlated.append(combined)

output = (
    BASE_DIR
    / "execution_dataset.json"
)

with open(output, "w") as f:
    json.dump(
        correlated,
        f,
        indent=4
    )

print("=" * 60)
print("GLI-FLOW Execution Correlation Engine")
print("=" * 60)
print()

for item in correlated:
    print(item)

print()
print(f"[OUTPUT] {output.resolve()}")
