import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

TREND_FILE = (
    ROOT_DIR
    / "trends"
    / "historical_trends.json"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "trends"
    / "predictive_report.json"
)


def load_trends():

    if not TREND_FILE.exists():
        return []

    with open(TREND_FILE, "r") as f:
        return json.load(f)


def analyze_trends(trends):

    warnings = []

    if len(trends) < 2:

        warnings.append(
            "Insufficient trend history for prediction"
        )

        return warnings

    latest = trends[-1]

    previous = trends[-2]

    latest_score = latest["execution_score"]

    previous_score = previous["execution_score"]

    if latest_score < previous_score:

        warnings.append(
            "Execution reliability decreasing"
        )

    if latest["regression_detected"]:

        warnings.append(
            "Recent regression activity detected"
        )

    if latest["failures"] > previous["failures"]:

        warnings.append(
            "Failure frequency increasing"
        )

    return warnings


def generate_report(warnings):

    return {
        "prediction_warnings": warnings,
        "risk_detected": len(warnings) > 0
    }


def save_report(report):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=4)


def print_report(report):

    print("=" * 60)
    print("GLI-FLOW Predictive Diagnostics Engine")
    print("=" * 60)

    if report["risk_detected"]:

        print("\n[RISK WARNINGS]\n")

        for warning in report["prediction_warnings"]:

            print(f"  - {warning}")

    else:

        print("[SUCCESS] No predictive instability detected")

    print("\n========================================")


def main():

    trends = load_trends()

    warnings = analyze_trends(trends)

    report = generate_report(warnings)

    save_report(report)

    print_report(report)


if __name__ == "__main__":
    main()
