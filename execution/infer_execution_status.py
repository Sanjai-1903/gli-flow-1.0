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
print("GLI-FLOW Execution Status Intelligence")
print("=" * 60)
print()

status_report = []

for run in execution_index["runs"]:

    run_path = Path(run["path"])

    log_file = run_path / "openroad.log"

    status = "UNKNOWN"

    if not log_file.exists():

        status = "INCOMPLETE"

    else:

        log_text = log_file.read_text()

        if "[SUCCESS]" in log_text:

            status = "SUCCESS"

        elif "[FAILED]" in log_text:

            status = "FAILED"

        else:

            status = "UNKNOWN"

    result = {

        "run": run["run_name"],
        "status": status
    }

    status_report.append(result)

    print(f"{run['run_name']}")
    print(f"  Status : {status}")
    print()

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "execution_status_report.json"
)

with open(output, "w") as f:
    json.dump(
        status_report,
        f,
        indent=4
    )

print("=" * 60)
print(f"[OUTPUT] {output}")
