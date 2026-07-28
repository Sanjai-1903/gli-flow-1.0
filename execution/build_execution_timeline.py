import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

INDEX = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "execution_index.json"
)

with open(INDEX) as f:
    execution_index = json.load(f)

timeline = []

for run in execution_index["runs"]:

    generated_at = run["generated_at"]

    timeline.append({

        "run": run["run_name"],
        "generated_at": generated_at,
        "path": run["path"]
    })

timeline = sorted(

    timeline,

    key=lambda x:
    x["generated_at"]
)

print("=" * 60)
print("GLI-FLOW Execution Timeline")
print("=" * 60)
print()

for item in timeline:

    print(f"{item['generated_at']}")
    print(f"  Run : {item['run']}")
    print()

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "execution_timeline_v2.json"
)

with open(output, "w") as f:
    json.dump(
        timeline,
        f,
        indent=4
    )

print("=" * 60)
print(f"[OUTPUT] {output}")
