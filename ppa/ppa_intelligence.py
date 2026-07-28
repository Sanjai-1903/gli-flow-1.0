import json
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

METRICS_FILE = (
    ROOT_DIR
    / "metrics"
    / "latest_metrics.json"
)

HISTORY_FILE = (
    ROOT_DIR
    / "ppa"
    / "metrics_history.json"
)


def load_json(path):

    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def append_metrics(history, metrics):

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "wire_count": metrics["wire_count"],
        "cell_count": metrics["cell_count"],
        "warnings": metrics["warnings"],
        "errors": metrics["errors"]
    }

    history["runs"].append(entry)

    return history


def compare_runs(history):

    if len(history["runs"]) < 2:

        return [
            "Insufficient historical data"
        ]

    latest = history["runs"][-1]

    previous = history["runs"][-2]

    analysis = []

    if latest["cell_count"] > previous["cell_count"]:

        analysis.append(
            "Cell count increased"
        )

    elif latest["cell_count"] < previous["cell_count"]:

        analysis.append(
            "Cell count decreased"
        )

    if latest["warnings"] > previous["warnings"]:

        analysis.append(
            "Warnings increased"
        )

    if latest["errors"] > previous["errors"]:

        analysis.append(
            "Errors increased"
        )

    if not analysis:

        analysis.append(
            "No significant PPA regressions detected"
        )

    return analysis


def print_analysis(history, analysis):

    latest = history["runs"][-1]

    print("=" * 60)
    print("GLI-FLOW PPA Intelligence Engine")
    print("=" * 60)

    print(
        f"TOTAL RUNS TRACKED : "
        f"{len(history['runs'])}"
    )

    print(
        f"LATEST CELL COUNT  : "
        f"{latest['cell_count']}"
    )

    print(
        f"LATEST WIRE COUNT  : "
        f"{latest['wire_count']}"
    )

    print("\nANALYSIS:")

    for item in analysis:

        print(f"  - {item}")

    print("\n========================================")
    print("[SUCCESS] PPA correlation complete")
    print("========================================")


def main():

    metrics = load_json(METRICS_FILE)

    history = load_json(HISTORY_FILE)

    history = append_metrics(
        history,
        metrics
    )

    save_json(HISTORY_FILE, history)

    analysis = compare_runs(history)

    print_analysis(history, analysis)


if __name__ == "__main__":
    main()
