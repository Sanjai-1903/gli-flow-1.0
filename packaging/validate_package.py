import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

required_components = [

    "environment",
    "execution",
    "failure_atlas",
    "reliability",
    "regression",
    "release",
    "packaging",
    "docs"
]

validation = {

    "generated_at":
        str(datetime.now()),

    "distribution_status":
        "READY",

    "checks": []
}

print("=" * 60)
print("GLI-FLOW Package Validation")
print("=" * 60)
print()

for component in required_components:

    path = BASE_DIR / component

    exists = path.exists()

    result = {

        "component": component,
        "exists": exists
    }

    validation["checks"].append(result)

    print(f"{component}")
    print(f"  Exists : {exists}")
    print()

    if not exists:
        validation["distribution_status"] = "INVALID"

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "package_validation_report.json"
)

with open(output, "w") as f:
    json.dump(
        validation,
        f,
        indent=4
    )

print("=" * 60)
print(f"[OUTPUT] {output}")
