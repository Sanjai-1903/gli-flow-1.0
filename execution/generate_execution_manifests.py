import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = (
    BASE_DIR
    / "openroad_runs"
)

print("=" * 60)
print("GLI-FLOW Execution Manifest Generator")
print("=" * 60)
print()

generated = 0

for run in RUNS_DIR.iterdir():

    if not run.is_dir():
        continue

    log_file = run / "openroad.log"

    status = "UNKNOWN"

    if log_file.exists():

        log_text = log_file.read_text()

        if "[SUCCESS]" in log_text:
            status = "SUCCESS"

        elif "[FAILED]" in log_text:
            status = "FAILED"

    manifest = {

        "run_name": run.name,

        "generated_at": str(
            datetime.fromtimestamp(
                run.stat().st_mtime
            )
        ),

        "log_file": str(
            log_file.resolve()
        ),

        "log_exists": log_file.exists(),

        "execution_status": status
    }

    output = (
        run
        / "execution_manifest.json"
    )

    with open(output, "w") as f:
        json.dump(
            manifest,
            f,
            indent=4
        )

    generated += 1

    print(f"[GENERATED] {run.name}")

print()
print("=" * 60)
print(f"Generated {generated} manifests")
