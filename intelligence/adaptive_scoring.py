import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

POLICY_FILE = (
    ROOT_DIR
    / "intelligence"
    / "scoring_policy.json"
)

DIAGNOSTIC_FILE = (
    ROOT_DIR
    / "intelligence"
    / "latest_diagnostics.json"
)

ANOMALY_FILE = (
    ROOT_DIR
    / "intelligence"
    / "anomaly_history.json"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "intelligence"
    / "execution_confidence.json"
)


def load_json(path):

    with open(path, "r") as f:
        return json.load(f)


def calculate_score(policy, diagnostics, anomalies):

    score = policy["base_score"]

    weights = policy["severity_weights"]

    for item in diagnostics:

        severity = item["severity"]

        occurrences = item["occurrences"]

        penalty = (
            weights[severity]
            * occurrences
        )

        score -= penalty

    if len(anomalies["history"]) > 1:

        score -= (
            policy["anomaly_penalty"]
        )

    if score < 0:
        score = 0

    return score


def classify_score(score):

    if score >= 90:
        return "HIGH_CONFIDENCE"

    if score >= 70:
        return "MODERATE_CONFIDENCE"

    if score >= 50:
        return "LOW_CONFIDENCE"

    return "UNSTABLE_EXECUTION"


def save_output(data):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=4)


def print_results(data):

    print("=" * 60)
    print("GLI-FLOW Adaptive Execution Scoring")
    print("=" * 60)

    print(
        f"EXECUTION SCORE : "
        f"{data['score']}"
    )

    print(
        f"CLASSIFICATION  : "
        f"{data['classification']}"
    )

    print("\n========================================")
    print("[SUCCESS] Adaptive scoring complete")
    print("========================================")


def main():

    policy = load_json(
        POLICY_FILE
    )

    diagnostics = load_json(
        DIAGNOSTIC_FILE
    )

    anomalies = load_json(
        ANOMALY_FILE
    )

    score = calculate_score(
        policy,
        diagnostics,
        anomalies
    )

    classification = classify_score(
        score
    )

    output = {
        "score": score,
        "classification": classification
    }

    save_output(output)

    print_results(output)


if __name__ == "__main__":
    main()
