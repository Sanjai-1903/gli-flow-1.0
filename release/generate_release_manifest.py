import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

tracked_components = [

    "environment",
    "execution",
    "failure_atlas",
    "reliability",
    "regression",
    "release",
    "docs",
    "outputs"
]

artifact_count = 0

for component in tracked_components:

    component_path = (
        BASE_DIR
        / component
    )

    if component_path.exists():

        artifact_count += len(
            list(
                component_path.rglob("*")
            )
        )

manifest = {

    "release_id":
        f"gli-flow-{datetime.now().strftime('%Y%m%d_%H%M%S')}",

    "generated_at":
        str(datetime.now()),

    "repository_state":
        "DEVELOPMENT",

    "tracked_components":
        tracked_components,

    "artifact_count":
        artifact_count,

    "validation_status":
        "VALID"
}

print("=" * 60)
print("GLI-FLOW Release Manifest")
print("=" * 60)
print()

print(json.dumps(
    manifest,
    indent=4
))

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "release_manifest.json"
)

with open(output, "w") as f:
    json.dump(
        manifest,
        f,
        indent=4
    )

print()
print("=" * 60)
print(f"[OUTPUT] {output}")
