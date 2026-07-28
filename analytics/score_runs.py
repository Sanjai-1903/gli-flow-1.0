from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

METRICS_FILE = BASE_DIR / "openroad_metrics.json"

with open(METRICS_FILE) as f:
    runs = json.load(f)

scored_runs = []

for run in runs:

    score = 0

    if run["flow_status"] == "SUCCESS":
        score += 50

    if run["cell_count"]:
        score += min(
            run["cell_count"],
            20
        )

    if run["runtime_seconds"]:

        runtime_bonus = max(
            0,
            20 - int(run["runtime_seconds"])
        )

        score += runtime_bonus

    if run["wns"] is not None:

        if run["wns"] >= 0:
            score += 20
        else:
            score += max(
                0,
                20 + int(run["wns"] * 10)
            )

    scored_runs.append({
        "run": run["run"],
        "score": score,
        "status": run["flow_status"]
    })

output = BASE_DIR / "run_scores.json"

with open(output, "w") as f:
    json.dump(
        scored_runs,
        f,
        indent=4
    )

print("=" * 60)
print("GLI-FLOW Execution Scoring Engine")
print("=" * 60)
print()

for run in scored_runs:
    print(run)

print()
print(f"[OUTPUT] {output.resolve()}")
