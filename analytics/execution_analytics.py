import json
from collections import Counter
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = ROOT_DIR / "runs"

SIGNATURE_DB = ROOT_DIR / "failure_atlas" / "signatures.json"

OUTPUT_FILE = ROOT_DIR / "analytics" / "execution_report.json"


def load_signatures():
    with open(SIGNATURE_DB, "r") as f:
        return json.load(f)


def scan_logs(signatures):

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

                    detected.append(sig["name"])

    return detected


def generate_report():

    signatures = load_signatures()

    runs = [
        d for d in RUNS_DIR.iterdir()
        if d.is_dir()
    ]

    total_runs = len(runs)

    detected_failures = scan_logs(signatures)

    failure_counter = Counter(detected_failures)

    report = {
        "total_runs": total_runs,
        "total_detected_failures": len(detected_failures),
        "failure_statistics": dict(failure_counter)
    }

    return report


def save_report(report):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=4)


def print_report(report):

    print("=" * 60)
    print("GLI-FLOW Execution Analytics")
    print("=" * 60)

    print(f"TOTAL RUNS                : {report['total_runs']}")

    print(
        f"TOTAL DETECTED FAILURES   : "
        f"{report['total_detected_failures']}"
    )

    print("\nFAILURE STATISTICS:")

    if not report["failure_statistics"]:
        print("  No failures detected")

    else:

        for name, count in report["failure_statistics"].items():

            print(f"  {name:<35} {count}")

    print("\n========================================")
    print("[SUCCESS] Analytics generation complete")
    print("========================================")


def main():

    report = generate_report()

    save_report(report)

    print_report(report)


if __name__ == "__main__":
    main()
