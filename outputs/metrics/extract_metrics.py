import json
import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = ROOT_DIR / "runs"

OUTPUT_DIR = ROOT_DIR / "metrics"

OUTPUT_FILE = OUTPUT_DIR / "latest_metrics.json"


def find_latest_log():

    run_dirs = sorted(
        [
            d for d in RUNS_DIR.iterdir()
            if d.is_dir()
        ],
        reverse=True
    )

    for run_dir in run_dirs:

        log_file = run_dir / "synthesis.log"

        if log_file.exists():
            return log_file

    return None


def extract_metrics(log_content):

    metrics = {
        "wire_count": None,
        "cell_count": None,
        "warnings": 0,
        "errors": 0
    }

    wire_match = re.search(
        r"Number of wires:\s+(\d+)",
        log_content
    )

    if wire_match:
        metrics["wire_count"] = int(
            wire_match.group(1)
        )

    cell_match = re.search(
        r"Number of cells:\s+(\d+)",
        log_content
    )

    if cell_match:
        metrics["cell_count"] = int(
            cell_match.group(1)
        )

    metrics["warnings"] = len(
        re.findall(r"Warning:", log_content)
    )

    metrics["errors"] = len(
        re.findall(r"ERROR", log_content)
    )

    return metrics


def save_metrics(metrics):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(metrics, f, indent=4)


def print_metrics(metrics):

    print("=" * 60)
    print("GLI-FLOW Metrics Extraction Engine")
    print("=" * 60)

    print(
        f"WIRE COUNT : {metrics['wire_count']}"
    )

    print(
        f"CELL COUNT : {metrics['cell_count']}"
    )

    print(
        f"WARNINGS   : {metrics['warnings']}"
    )

    print(
        f"ERRORS     : {metrics['errors']}"
    )

    print("\n========================================")
    print("[SUCCESS] Metrics extraction complete")
    print("========================================")


def main():

    log_file = find_latest_log()

    if log_file is None:

        print("[ERROR] No synthesis log found")

        return

    content = log_file.read_text(
        errors="ignore"
    )

    metrics = extract_metrics(content)

    save_metrics(metrics)

    print_metrics(metrics)


if __name__ == "__main__":
    main()
