import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = (
    BASE_DIR
    / "openroad_runs"
)

results = []

print("=" * 60)
print("GLI-FLOW Health Inference Engine")
print("=" * 60)
print()

for run_dir in sorted(RUNS_DIR.iterdir()):

    if not run_dir.is_dir():
        continue

    run_name = run_dir.name

    log_file = run_dir / "openroad.log"

    status = "UNKNOWN"
    health = "UNKNOWN"

    if log_file.exists():

        log_content = log_file.read_text()

        if "SUCCESS" in log_content:
            status = "SUCCESS"
            health = "HEALTHY"

        elif "ERROR" in log_content:
            status = "FAILED"
            health = "FAILED"

        elif "WARNING" in log_content:
            status = "WARNING"
            health = "WARNING"

    result = {

        "run": run_name,
        "status": status,
        "health": health
    }

    results.append(result)

    print(f"{run_name}")
    print(f"  Status : {status}")
    print(f"  Health : {health}")
    print()

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "execution_health_v3.json"
)

with open(output, "w") as f:
    json.dump(
        results,
        f,
        indent=4
    )

print("=" * 60)
print(f"[OUTPUT] {output}")
