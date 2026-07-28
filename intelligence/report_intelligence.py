import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = ROOT_DIR / "runs"

SIGNATURE_FILE = (
    ROOT_DIR
    / "intelligence"
    / "warning_signatures.json"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "intelligence"
    / "latest_diagnostics.json"
)


def load_signatures():

    with open(SIGNATURE_FILE, "r") as f:
        return json.load(f)


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


def analyze_log(content, signatures):

    diagnostics = []

    for sig in signatures:

        count = content.count(
            sig["signature"]
        )

        if count > 0:

            diagnostics.append({
                "category": sig["category"],
                "severity": sig["severity"],
                "occurrences": count
            })

    return diagnostics


def save_output(diagnostics):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(diagnostics, f, indent=4)


def print_diagnostics(diagnostics):

    print("=" * 60)
    print("GLI-FLOW Semantic Report Intelligence")
    print("=" * 60)

    if not diagnostics:

        print("[SUCCESS] No significant diagnostics")

    else:

        for item in diagnostics:

            print("\n----------------------------------------")
            print(
                f"CATEGORY    : "
                f"{item['category']}"
            )

            print(
                f"SEVERITY    : "
                f"{item['severity']}"
            )

            print(
                f"OCCURRENCES : "
                f"{item['occurrences']}"
            )

    print("\n========================================")


def main():

    signatures = load_signatures()

    log_file = find_latest_log()

    if log_file is None:

        print("[ERROR] No synthesis log found")

        return

    content = log_file.read_text(
        errors="ignore"
    )

    diagnostics = analyze_log(
        content,
        signatures
    )

    save_output(diagnostics)

    print_diagnostics(diagnostics)


if __name__ == "__main__":
    main()
