import json
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

DIAGNOSTIC_FILE = (
    ROOT_DIR
    / "intelligence"
    / "latest_diagnostics.json"
)

METRICS_FILE = (
    ROOT_DIR
    / "metrics"
    / "latest_metrics.json"
)

HISTORY_FILE = (
    ROOT_DIR
    / "intelligence"
    / "anomaly_history.json"
)


def load_json(path):

    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def append_history(history, diagnostics, metrics):

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "diagnostics": diagnostics,
        "metrics": metrics
    }

    history["history"].append(entry)

    return history


def analyze_anomalies(history):

    if len(history["history"]) < 2:

        return [
            "Insufficient history for anomaly detection"
        ]

    latest = history["history"][-1]

    previous = history["history"][-2]

    anomalies = []

    latest_warnings = sum(
        item["occurrences"]
        for item in latest["diagnostics"]
    )

    previous_warnings = sum(
        item["occurrences"]
        for item in previous["diagnostics"]
    )

    if latest_warnings > previous_warnings:

        anomalies.append(
            "Warning activity increased"
        )

    latest_cells = latest["metrics"]["cell_count"]

    previous_cells = previous["metrics"]["cell_count"]

    if latest_cells > previous_cells:

        anomalies.append(
            "Cell count increased unexpectedly"
        )

    latest_errors = latest["metrics"]["errors"]

    previous_errors = previous["metrics"]["errors"]

    if latest_errors > previous_errors:

        anomalies.append(
            "Execution errors increased"
        )

    if not anomalies:

        anomalies.append(
            "No significant anomalies detected"
        )

    return anomalies


def print_results(history, anomalies):

    print("=" * 60)
    print("GLI-FLOW Cross-Run Anomaly Engine")
    print("=" * 60)

    print(
        f"TOTAL RUNS ANALYZED : "
        f"{len(history['history'])}"
    )

    print("\nANOMALY ANALYSIS:")

    for item in anomalies:

        print(f"  - {item}")

    print("\n========================================")
    print("[SUCCESS] Cross-run analysis complete")
    print("========================================")


def main():

    diagnostics = load_json(
        DIAGNOSTIC_FILE
    )

    metrics = load_json(
        METRICS_FILE
    )

    history = load_json(
        HISTORY_FILE
    )

    history = append_history(
        history,
        diagnostics,
        metrics
    )

    save_json(
        HISTORY_FILE,
        history
    )

    anomalies = analyze_anomalies(
        history
    )

    print_results(
        history,
        anomalies
    )


if __name__ == "__main__":
    main()
