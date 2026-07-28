from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = BASE_DIR / "openroad_runs"

artifact_database = []

for run in RUNS_DIR.iterdir():

    if not run.is_dir():
        continue

    artifacts = []

    for file in run.rglob("*"):

        if file.is_file():

            artifacts.append({
                "name": file.name,
                "path": str(
                    file.relative_to(
                        BASE_DIR
                    )
                ),
                "size_bytes": file.stat().st_size
            })

    artifact_database.append({
        "run": run.name,
        "artifact_count": len(
            artifacts
        ),
        "artifacts": artifacts
    })

output = (
    BASE_DIR
    / "artifact_manifest.json"
)

with open(output, "w") as f:
    json.dump(
        artifact_database,
        f,
        indent=4
    )

print("=" * 60)
print("GLI-FLOW Artifact Manifest Engine")
print("=" * 60)
print()

for run in artifact_database:

    print(
        f"{run['run']} -> "
        f"{run['artifact_count']} artifacts"
    )

print()
print(f"[OUTPUT] {output.resolve()}")
