import subprocess
from pathlib import Path
from datetime import datetime


ROOT_DIR = Path(__file__).resolve().parent.parent

DESIGN_DIR = (
    ROOT_DIR
    / "execution"
    / "test_design"
)

RUN_DIR = (
    ROOT_DIR
    / "runs"
    / f"synth_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)

RUN_DIR.mkdir(parents=True, exist_ok=True)


def run_synthesis():

    yosys_script = DESIGN_DIR / "synth.ys"

    log_file = RUN_DIR / "synthesis.log"

    command = [
        "yosys",
        str(yosys_script)
    ]

    with open(log_file, "w") as log:

        result = subprocess.run(
            command,
            cwd=DESIGN_DIR,
            stdout=log,
            stderr=log
        )

    return result.returncode, log_file


def print_results(code, log_file):

    print("=" * 60)
    print("GLI-FLOW Real Synthesis Execution")
    print("=" * 60)

    print(f"LOG FILE : {log_file}")

    if code == 0:

        print("\n[SUCCESS] Synthesis completed")

    else:

        print("\n[FAILED] Synthesis failed")

    print("\n========================================")


def main():

    code, log_file = run_synthesis()

    print_results(code, log_file)


if __name__ == "__main__":
    main()
