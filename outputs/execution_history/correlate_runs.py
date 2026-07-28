import json
import os
from datetime import datetime, timezone


RUNS_DIR = "../runs"
OUTPUT_FILE = "run_index.json"


def collect_runs():
    run_data = []

    if not os.path.exists(RUNS_DIR):
        return run_data

    for run_name in sorted(os.listdir(RUNS_DIR)):
        run_path = os.path.join(RUNS_DIR, run_name)

        if os.path.isdir(run_path):
            entry = {
                "run_id": run_name,
                "path": os.path.abspath(run_path),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "ARCHIVED"
            }

            run_data.append(entry)

    return run_data


def main():
    runs = collect_runs()

    with open(OUTPUT_FILE, "w") as f:
        json.dump(runs, f, indent=4)

    print(f"[SUCCESS] Indexed {len(runs)} runs")
    print(f"[OUTPUT] {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
