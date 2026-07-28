import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

included_components = [

    "environment",
    "execution",
    "failure_atlas",
    "reliability",
    "regression",
    "release",
    "packaging",
    "docs"
]

artifact_count = 0

for component in included_components:

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

    "package_id":
        f"gli-flow-package-{datetime.now().strftime('%Y%m%d_%H%M%S')}",

    "generated_at":
        str(datetime.now()),

    "package_type":
        "PORTABLE_DISTRIBUTION",

    "included_components":
        included_components,

    "artifact_count":
        artifact_count,

    "distribution_status":
        "READY"
}

print("=" * 60)
print("GLI-FLOW Distribution Manifest")
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
    / "package_manifest.json"
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
