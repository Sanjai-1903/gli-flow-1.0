import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

POLICY_FILE = ROOT_DIR / "governance" / "policies.json"


def load_policies():

    with open(POLICY_FILE, "r") as f:
        return json.load(f)


def check_directories(required_dirs):

    missing = []

    for directory in required_dirs:

        path = ROOT_DIR / directory

        if not path.exists():
            missing.append(directory)

    return missing


def check_files(required_files):

    missing = []

    for file in required_files:

        path = ROOT_DIR / file

        if not path.exists():
            missing.append(file)

    return missing


def main():

    print("=" * 60)
    print("GLI-FLOW Governance Policy Engine")
    print("=" * 60)

    policies = load_policies()

    missing_dirs = check_directories(
        policies["required_directories"]
    )

    missing_files = check_files(
        policies["required_files"]
    )

    if missing_dirs:

        print("\n[MISSING DIRECTORIES]")

        for item in missing_dirs:
            print(f"  - {item}")

    if missing_files:

        print("\n[MISSING FILES]")

        for item in missing_files:
            print(f"  - {item}")

    if not missing_dirs and not missing_files:

        print("\n[SUCCESS] Governance compliance verified")

    else:

        print("\n[FAILED] Governance validation failed")

    print("\n========================================")


if __name__ == "__main__":
    main()
