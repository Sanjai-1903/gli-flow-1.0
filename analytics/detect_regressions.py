from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

SCORES_FILE = BASE_DIR / "run_scores.json"

with open(SCORES_FILE) as f:
    runs = json.load(f)

print("=" * 60)
print("GLI-FLOW Regression Detection Engine")
print("=" * 60)
print()

if len(runs) < 2:
    print("[INFO] Not enough runs for regression analysis")
    exit()

previous = runs[0]

for current in runs[1:]:

    previous_score = previous["score"]
    current_score = current["score"]

    delta = current_score - previous_score

    print(f"PREVIOUS : {previous['run']}")
    print(f"CURRENT  : {current['run']}")
    print(f"SCORE Δ  : {delta}")

    if delta < 0:
        print("[REGRESSION DETECTED]")

    elif delta > 0:
        print("[IMPROVEMENT DETECTED]")

    else:
        print("[NO CHANGE]")

    print("-" * 60)

    previous = current
