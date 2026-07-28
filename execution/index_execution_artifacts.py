import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = (
    BASE_DIR
    / "openroad_runs"
)

artifact_index = []

print("=" * 60)
print("GLI-FLOW Artifact Indexer")
print("=" * 60)
print()

for run in RUNS_DIR.iterdir():

    if not run.is_dir():
        continue

    artifacts = []

    for item in run.iterdir():

        artifacts.append({

            "name": item.name,
            "type": (
                "directory"
                if item.is_dir()
                else "file"
            )
        })

    entry = {

        "run": run.name,
        "artifact_count": len(artifacts),
        "artifacts": artifacts
    }

    artifact_index.append(entry)

    print(f"{run.name}")
    print(f"  Artifacts : {len(artifacts)}")
    print()

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "execution_artifact_index.json"
)

with open(output, "w") as f:
    json.dump(
        artifact_index,
        f,
        indent=4
    )

print("=" * 60)
print(f"[OUTPUT] {output}")
