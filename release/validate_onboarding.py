import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

required_docs = [

    "README.md",

    "docs/setup/installation.md",
    "docs/setup/quickstart.md",

    "docs/reproducibility_validation.md",

    ".github/workflows/ci.yml"
]

results = []

overall_status = "CONSISTENT"

print("=" * 60)
print("GLI-FLOW Onboarding Validation")
print("=" * 60)
print()

for item in required_docs:

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

    "onboarding_status":
        overall_status,

    "checks":
        results
}

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "onboarding_validation_report.json"
)

with open(output, "w") as f:
    json.dump(
        report,
        f,
        indent=4
    )

print("=" * 60)
print(f"Onboarding Status : {overall_status}")
print(f"[OUTPUT] {output}")
