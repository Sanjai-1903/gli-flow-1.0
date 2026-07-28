import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

ANALYTICS_DIR = ROOT_DIR / "analytics"

OUTPUT_FILE = (
    ROOT_DIR
    / "regression"
    / "regression_report.json"
)


def load_reliability():

    reliability_file = (
        ANALYTICS_DIR
        / "reliability_report.json"
    )

    if not reliability_file.exists():
        return None

    with open(reliability_file, "r") as f:
        return json.load(f)


def analyze_regression(reliability):

    regression_flags = []

    if reliability is None:

        regression_flags.append(
            "Missing reliability report"
        )

        return regression_flags

    score = reliability.get("execution_score", 0)

    classification = reliability.get(
        "classification",
        "UNKNOWN"
    )

    if score < 70:

        regression_flags.append(
            "Execution score below stability threshold"
        )

    if classification in ["RISKY", "UNSTABLE"]:

        regression_flags.append(
            f"Environment classified as {classification}"
        )

    return regression_flags


def generate_report(flags):

    report = {
        "regression_detected": len(flags) > 0,
        "flags": flags
    }

    return report


def save_report(report):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=4)


def print_report(report):

    print("=" * 60)
    print("GLI-FLOW Deterministic Regression Engine")
    print("=" * 60)

    if report["regression_detected"]:

        print("[REGRESSION DETECTED]\n")

        for flag in report["flags"]:
            print(f"  - {flag}")

    else:

        print("[SUCCESS] No regressions detected")

    print("\n========================================")


def main():

    reliability = load_reliability()

    flags = analyze_regression(reliability)

    report = generate_report(flags)

    save_report(report)

    print_report(report)


if __name__ == "__main__":
    main()
