from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

SCORES_FILE = BASE_DIR / "run_scores.json"
METRICS_FILE = BASE_DIR / "openroad_metrics.json"

with open(SCORES_FILE) as f:
    scores = json.load(f)

with open(METRICS_FILE) as f:
    metrics = json.load(f)

metrics_map = {
    item["run"]: item
    for item in metrics
}

best_run = max(
    scores,
    key=lambda x: x["score"]
)

worst_run = min(
    scores,
    key=lambda x: x["score"]
)

print("=" * 60)
print("GLI-FLOW Run Comparison Engine")
print("=" * 60)
print()

print("[BEST RUN]")
print(best_run)
print(metrics_map.get(best_run["run"]))

print()

print("[WORST RUN]")
print(worst_run)
print(metrics_map.get(worst_run["run"]))

print()

delta = (
    best_run["score"]
    - worst_run["score"]
)

print(f"[SCORE GAP] {delta}")
