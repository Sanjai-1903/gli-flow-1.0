import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

required_paths = [

    "environment",
    "execution",
    "failure_atlas",
    "reliability",
    "regression",
    "release",
    "packaging",
    "outputs",
    "docs",

    ".github/workflows/ci.yml",

    "docs/architecture/output_architecture.md",
    "docs/architecture/report_governance.md",
    "docs/architecture/repository_evolution.md"
]

results = []

overall_status = "CONSISTENT"

print("=" * 60)
print("GLI-FLOW Structure Validation")
print("=" * 60)
print()

for item in required_paths:

    path = BASE_DIR / item

    exists = path.exists()

    results.append({

        "path": item,
        "exists": exists
    })

    print(f"{item}")
    print(f"  Exists : {exists}")
    print()

    if not exists:
        overall_status = "INCONSISTENT"

report = {

    "generated_at":
        str(datetime.now()),

    "structure_status":
        overall_status,

    "checks":
        results
}

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "structure_validation_report.json"
)

with open(output, "w") as f:
    json.dump(
        report,
        f,
        indent=4
    )

print("=" * 60)
print(f"Structure Status : {overall_status}")
print(f"[OUTPUT] {output}")
