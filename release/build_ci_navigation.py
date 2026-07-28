import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REPORTS_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

navigation = {

    "ci_observability_report": None,
    "repository_health_report": None,
    "ci_snapshot": None
}

report_mapping = {

    "ci_observability_report":
        "ci_observability_report.json",

    "repository_health_report":
        "repository_health_report.json",

    "ci_snapshot":
        "ci_snapshot.json"
}

print("=" * 60)
print("GLI-FLOW CI Navigation")
print("=" * 60)
print()

for key, filename in report_mapping.items():

    path = (
        REPORTS_DIR
        / filename
    )

    if path.exists():

        navigation[key] = str(
            path.resolve()
        )

        print(f"[FOUND] {key}")

    else:

        print(f"[MISSING] {key}")

output = (
    REPORTS_DIR
    / "ci_navigation.json"
)

with open(output, "w") as f:
    json.dump(
        navigation,
        f,
        indent=4
    )

print()
print("=" * 60)
print(f"[OUTPUT] {output}")
