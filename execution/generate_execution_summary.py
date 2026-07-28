import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INDEX = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "execution_index.json"
)

with open(INDEX) as f:
    execution_index = json.load(f)

print("=" * 60)
print("GLI-FLOW Execution Summary")
print("=" * 60)
print()

summary = []

for run in execution_index["runs"]:

    run_name = run["run_name"]

    log_exists = run["log_exists"]

    status = (
        "READY"
        if log_exists
        else "INCOMPLETE"
    )

    run_summary = {

        "run": run_name,
        "status": status,
        "log_exists": log_exists,
        "path": run["path"]
    }

    summary.append(run_summary)

    print(f"Run        : {run_name}")
    print(f"Status     : {status}")
    print(f"Log Exists : {log_exists}")
    print()

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "execution_summary.json"
)

with open(output, "w") as f:
    json.dump(
        summary,
        f,
        indent=4
    )

print("=" * 60)
print(f"[OUTPUT] {output}")
