import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

SNAPSHOT_DIR = ROOT_DIR / "snapshots"

OUTPUT_FILE = ROOT_DIR / "replay" / "replay_index.json"


def discover_snapshots():

    snapshots = []

    if not SNAPSHOT_DIR.exists():
        return snapshots

    for snapshot in SNAPSHOT_DIR.iterdir():

        if snapshot.is_dir():

            snapshot_info = {
                "snapshot": snapshot.name,
                "path": str(snapshot),
                "contains_manifests": (
                    snapshot / "manifests"
                ).exists(),

                "contains_telemetry": (
                    snapshot / "telemetry"
                ).exists(),

                "contains_analytics": (
                    snapshot / "analytics"
                ).exists(),

                "contains_failure_atlas": (
                    snapshot / "failure_atlas"
                ).exists()
            }

            snapshots.append(snapshot_info)

    return snapshots


def save_index(data):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=4)


def print_results(data):

    print("=" * 60)
    print("GLI-FLOW Replay Infrastructure Engine")
    print("=" * 60)

    print(f"[SNAPSHOTS FOUND] {len(data)}")

    for item in data:

        print("\n----------------------------------------")
        print(f"SNAPSHOT : {item['snapshot']}")
        print(f"MANIFESTS: {item['contains_manifests']}")
        print(f"TELEMETRY: {item['contains_telemetry']}")
        print(f"ANALYTICS: {item['contains_analytics']}")
        print(f"FAILURES : {item['contains_failure_atlas']}")

    print("\n========================================")
    print("[SUCCESS] Replay index generated")
    print("========================================")


def main():

    snapshots = discover_snapshots()

    save_index(snapshots)

    print_results(snapshots)


if __name__ == "__main__":
    main()
