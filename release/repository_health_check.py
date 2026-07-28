import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

required_paths = [

    ".github/workflows/ci.yml",
    "CONTRIBUTING.md",
    "README.md",
    "environment",
    "execution",
    "failure_atlas",
    "reliability",
    "regression",
    "release",
    "docs"
]

results = []

overall_status = "HEALTHY"

print("=" * 60)
print("GLI-FLOW Repository Health Check")
print("=" * 60)
print()

for item in required_paths:

    path = BASE_DIR / item

    exists = path.exists()

    result = {

        "path": item,
        "exists": exists
    }

    results.append(result)

    print(f"{item}")
    print(f"  Exists : {exists}")
    print()

    if not exists:
        overall_status = "WARNING"

report = {

    "generated_at":
        str(datetime.now()),

    "repository_health":
        overall_status,

    "checks":
        results
}

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "repository_health_report.json"
)

with open(output, "w") as f:
    json.dump(
        report,
        f,
        indent=4
    )

print("=" * 60)
print(f"Repository Health : {overall_status}")
print(f"[OUTPUT] {output}")
