import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

MEMORY_FILE = (
    ROOT_DIR
    / "intelligence"
    / "learning_memory.json"
)

POLICY_FILE = (
    ROOT_DIR
    / "intelligence"
    / "orchestration_policy.json"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "intelligence"
    / "adaptive_orchestration_report.json"
)


def load_json(path):

    with open(path, "r") as f:
        return json.load(f)


def analyze_patterns(memory, policy):

    report = []

    policies = policy["optimization_policies"]

    for pattern in memory["execution_patterns"]:

        classification = pattern[
            "classification"
        ]

        orchestration_action = policies.get(
            classification,
            "UNKNOWN"
        )

        report.append({
            "classification": classification,
            "execution_score": (
                pattern["execution_score"]
            ),
            "recommended_action": (
                orchestration_action
            )
        })

    return report


def save_output(report):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=4)


def print_results(report):

    print("=" * 60)
    print("GLI-FLOW Adaptive Orchestration")
    print("=" * 60)

    if not report:

        print(
            "[INFO] No orchestration intelligence available"
        )

    else:

        for item in report:

            print("\n----------------------------------------")

            print(
                f"CLASSIFICATION : "
                f"{item['classification']}"
            )

            print(
                f"EXECUTION SCORE: "
                f"{item['execution_score']}"
            )

            print(
                f"ORCHESTRATION  : "
                f"{item['recommended_action']}"
            )

    print("\n========================================")
    print("[SUCCESS] Adaptive orchestration complete")
    print("========================================")


def main():

    memory = load_json(
        MEMORY_FILE
    )

    policy = load_json(
        POLICY_FILE
    )

    report = analyze_patterns(
        memory,
        policy
    )

    save_output(report)

    print_results(report)


if __name__ == "__main__":
    main()
