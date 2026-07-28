import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = ROOT_DIR / "runs"

SIGNATURE_DB = ROOT_DIR / "failure_atlas" / "signatures.json"

OUTPUT_FILE = ROOT_DIR / "analytics" / "reliability_report.json"


def load_signatures():

    with open(SIGNATURE_DB, "r") as f:
        return json.load(f)


def detect_failures(signatures):

    detected = []

    for run_dir in RUNS_DIR.iterdir():

        if not run_dir.is_dir():
            continue

        for log_file in run_dir.rglob("*.log"):

            try:
                content = log_file.read_text(errors="ignore")

            except Exception:
                continue

            for sig in signatures:

                if sig["match"] in content:
                    detected.append(sig)

    return detected


def calculate_score(failures):

    score = 100

    score += 20

    score += 20

    score += 20

    for failure in failures:

        score -= 15

        if failure["severity"] == "HIGH":
            score -= 25

    if score < 0:
        score = 0

    if score > 100:
        score = 100

    return score


def classify_score(score):

    if score >= 90:
        return "STABLE"

    if score >= 70:
        return "ACCEPTABLE"

    if score >= 50:
        return "RISKY"

    return "UNSTABLE"


def generate_report():

    signatures = load_signatures()

    failures = detect_failures(signatures)

    score = calculate_score(failures)

    classification = classify_score(score)

    report = {
        "execution_score": score,
        "classification": classification,
        "detected_failures": len(failures)
    }

    return report


def save_report(report):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=4)


def print_report(report):

    print("=" * 60)
    print("GLI-FLOW Reliability Scoring Engine")
    print("=" * 60)

    print(
        f"EXECUTION SCORE      : "
        f"{report['execution_score']}"
    )

    print(
        f"CLASSIFICATION       : "
        f"{report['classification']}"
    )

    print(
        f"DETECTED FAILURES    : "
        f"{report['detected_failures']}"
    )

    print("\n========================================")
    print("[SUCCESS] Reliability analysis complete")
    print("========================================")


def main():

    report = generate_report()

    save_report(report)

    print_report(report)


if __name__ == "__main__":
    main()
