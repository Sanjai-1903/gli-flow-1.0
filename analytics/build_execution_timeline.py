from pathlib import Path
import json
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = BASE_DIR / "openroad_runs"

timeline = []

for run in RUNS_DIR.iterdir():

    if not run.is_dir():
        continue

    timestamp_str = run.name.replace(
        "openroad_run_",
        ""
    )

    try:

        timestamp = datetime.strptime(
            timestamp_str,
            "%Y%m%d_%H%M%S"
        )

    except (ValueError, OSError):
        continue

    timeline.append({
        "run": run.name,
        "timestamp": str(timestamp)
    })

timeline = sorted(
    timeline,
    key=lambda x: x["timestamp"]
)

output = (
    BASE_DIR
    / "execution_timeline.json"
)

with open(output, "w") as f:
    json.dump(
        timeline,
        f,
        indent=4
    )

print("=" * 60)
print("GLI-FLOW Execution Timeline Engine")
print("=" * 60)
print()

for item in timeline:
    print(item)

print()
print(f"[OUTPUT] {output.resolve()}")
