import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = (
    BASE_DIR
    / "openroad_runs"
)

execution_runs = []

if RUNS_DIR.exists():

    for run in sorted(RUNS_DIR.iterdir()):

        if run.is_dir():

            log_file = run / "openroad.log"

            execution_runs.append({

                "run_name": run.name,

                "path": str(
                    run.resolve()
                ),

                "log_exists": log_file.exists(),

                "generated_at": str(
                    datetime.fromtimestamp(
                        run.stat().st_mtime
                    )
                )
            })

index = {

    "generated_at": str(
        datetime.now()
    ),

    "run_count": len(
        execution_runs
    ),

    "runs": execution_runs
}

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "execution_index.json"
)

with open(output, "w") as f:
    json.dump(
        index,
        f,
        indent=4
    )

print("=" * 60)
print("GLI-FLOW Execution Index")
print("=" * 60)
print()

print(json.dumps(
    index,
    indent=4
))

print()
print(f"[OUTPUT] {output}")
