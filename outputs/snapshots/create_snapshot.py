import shutil
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent

SNAPSHOT_ROOT = ROOT_DIR / "outputs" / "snapshots"


TARGETS = [
    "manifests",
    "outputs/analytics",
    "outputs/telemetry",
    "failure_atlas",
    "outputs/execution_history"
]


def create_snapshot_dir():

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    snapshot_dir = SNAPSHOT_ROOT / f"snapshot_{timestamp}"

    snapshot_dir.mkdir(parents=True, exist_ok=True)

    return snapshot_dir


def copy_targets(snapshot_dir):

    for target in TARGETS:

        source = ROOT_DIR / target

        if source.exists():

            destination = snapshot_dir / target

            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True
            )

            print(f"[SNAPSHOT] {target}")

        else:

            print(f"[SKIPPED] {target} not found")


def main():

    print("=" * 60)
    print("GLI-FLOW Deterministic Snapshot Engine")
    print("=" * 60)

    snapshot_dir = create_snapshot_dir()

    copy_targets(snapshot_dir)

    print("\n========================================")
    print(f"[SUCCESS] Snapshot created")
    print(f"LOCATION : {snapshot_dir}")
    print("========================================")


if __name__ == "__main__":
    main()
