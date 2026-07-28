from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_FILE = (
    BASE_DIR
    / "execution_dataset.json"
)

TIMELINE_FILE = (
    BASE_DIR
    / "execution_timeline.json"
)

ARTIFACT_FILE = (
    BASE_DIR
    / "artifact_manifest.json"
)

with open(DATASET_FILE) as f:
    dataset = json.load(f)

with open(TIMELINE_FILE) as f:
    timeline = json.load(f)

with open(ARTIFACT_FILE) as f:
    artifacts = json.load(f)

timeline_map = {
    item["run"]: item
    for item in timeline
}

artifact_map = {
    item["run"]: item
    for item in artifacts
}

graph = []

for run in dataset:

    run_name = run["run"]

    node = {
        "run": run_name,

        "relationships": {

            "timeline": timeline_map.get(
                run_name
            ),

            "artifacts": artifact_map.get(
                run_name
            ),

            "metrics": {
                "score": run.get("score"),
                "status": run.get("status"),
                "cell_count": run.get(
                    "cell_count"
                ),
                "runtime_seconds": run.get(
                    "runtime_seconds"
                )
            }
        }
    }

    graph.append(node)

output = (
    BASE_DIR
    / "execution_provenance_graph.json"
)

with open(output, "w") as f:
    json.dump(
        graph,
        f,
        indent=4
    )

print("=" * 60)
print("GLI-FLOW Provenance Graph Engine")
print("=" * 60)
print()

for node in graph:
    print(node["run"])

print()
print(f"[OUTPUT] {output.resolve()}")
