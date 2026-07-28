import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

CONTRACT_FILE = (
    ROOT_DIR
    / "contracts"
    / "execution_contract_v1.json"
)


def load_contract():

    with open(CONTRACT_FILE, "r") as f:
        return json.load(f)


def validate_requirements(contract):

    requirements = contract["execution_requirements"]

    validation_results = {}

    validation_results["manifests"] = (
        ROOT_DIR / "manifests"
    ).exists()

    validation_results["telemetry"] = (
        ROOT_DIR / "telemetry"
    ).exists()

    validation_results["snapshots"] = (
        ROOT_DIR / "snapshots"
    ).exists()

    validation_results["analytics"] = (
        ROOT_DIR / "analytics"
    ).exists()

    validation_results["failure_atlas"] = (
        ROOT_DIR / "failure_atlas"
    ).exists()

    return validation_results


def print_results(results):

    print("=" * 60)
    print("GLI-FLOW Execution Contract Engine")
    print("=" * 60)

    all_passed = True

    for item, status in results.items():

        if status:

            print(f"[PASS] {item}")

        else:

            print(f"[FAIL] {item}")

            all_passed = False

    print("\n========================================")

    if all_passed:

        print("[SUCCESS] Execution contract satisfied")

    else:

        print("[FAILED] Contract validation failed")

    print("========================================")


def main():

    contract = load_contract()

    results = validate_requirements(contract)

    print_results(results)


if __name__ == "__main__":
    main()
