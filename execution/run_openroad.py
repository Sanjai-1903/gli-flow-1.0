import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = BASE_DIR / "openroad_runs"
RUNS_DIR.mkdir(exist_ok=True)

def run_flow():

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    run_dir = RUNS_DIR / f"openroad_run_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    log_file = run_dir / "openroad.log"

    command = [
        "librelane",
        "--version"
    ]

    with open(log_file, "w") as log:

        result = subprocess.run(

            command,

            stdout=log,
            stderr=log,
            text=True
        )

    return result.returncode, log_file

def main():

    print("=" * 60)
    print("GLI-FLOW OpenROAD Integration")
    print("=" * 60)
    print()

    code, log_file = run_flow()

    print(f"LOG FILE : {log_file}")
    print()

    if code == 0:

        print("[SUCCESS] OpenROAD flow completed")

        with open(log_file, "a") as f:
            f.write(
                "\n[SUCCESS] OpenROAD flow completed\n"
            )

    else:

        print("[FAILED] OpenROAD flow failed")

        with open(log_file, "a") as f:
            f.write(
                "\n[FAILED] OpenROAD flow failed\n"
            )

    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
