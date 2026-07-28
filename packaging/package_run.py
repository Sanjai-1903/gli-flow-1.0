import os
import tarfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = ROOT_DIR / "runs"

OUTPUT_DIR = ROOT_DIR / "packaging" / "artifacts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def package_run(run_dir):
    run_name = run_dir.name

    output_file = OUTPUT_DIR / f"{run_name}.tar.gz"

    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(run_dir, arcname=run_name)

    print(f"[PACKAGED] {output_file}")


def main():
    print("=" * 60)
    print("GLI-FLOW Deterministic Run Packager")
    print("=" * 60)

    run_dirs = sorted(
        [
            d for d in RUNS_DIR.iterdir()
            if d.is_dir()
        ]
    )

    if not run_dirs:
        print("[INFO] No runs found")
        return

    for run_dir in run_dirs:
        package_run(run_dir)

    print("=" * 60)
    print("[SUCCESS] Packaging complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
