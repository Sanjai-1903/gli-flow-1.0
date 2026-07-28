import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REPORTS_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

navigation = {

    "package_manifest": None,
    "package_validation_report": None,
    "package_snapshot": None
}

report_mapping = {

    "package_manifest":
        "package_manifest.json",

    "package_validation_report":
        "package_validation_report.json",

    "package_snapshot":
        "package_snapshot.json"
}

print("=" * 60)
print("GLI-FLOW Package Navigation")
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
    / "package_navigation.json"
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
