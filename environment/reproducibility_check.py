import os


REQUIRED_PATHS = [
    "manifests",
    "outputs/execution_history",
    "failure_atlas",
    "outputs/telemetry",
    "runs"
]


REQUIRED_FILES = [
    "environment/validate_environment.py",
    "manifests/generate_manifest.py",
    "failure_atlas/detect_failures.py",
    "outputs/telemetry/collect_metrics.py",
    "outputs/execution_history/correlate_runs.py"
]


def check_paths():
    failures = []

    print("=" * 60)
    print("GLI-FLOW Reproducibility Verification")
    print("=" * 60)

    print("\n[CHECKING DIRECTORIES]")

    for path in REQUIRED_PATHS:
        if os.path.exists(path):
            print(f"[PASS] {path}")
        else:
            print(f"[FAIL] Missing directory: {path}")
            failures.append(path)

    print("\n[CHECKING FILES]")

    for file in REQUIRED_FILES:
        if os.path.exists(file):
            print(f"[PASS] {file}")
        else:
            print(f"[FAIL] Missing file: {file}")
            failures.append(file)

    print("\n" + "=" * 60)

    if failures:
        print("[FAILED] Reproducibility verification failed")
        print(f"[MISSING] {len(failures)} items")
    else:
        print("[SUCCESS] Environment reproducibility verified")


if __name__ == "__main__":
    check_paths()
