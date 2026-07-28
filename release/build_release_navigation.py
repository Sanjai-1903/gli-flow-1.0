import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REPORTS_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

navigation = {

    "release_manifest": None,
    "release_validation_report": None,
    "release_snapshot": None
}

report_mapping = {

    "release_manifest":
        "release_manifest.json",

    "release_validation_report":
        "release_validation_report_v2.json",

    "release_snapshot":
        "release_snapshot_v2.json"
}

print("=" * 60)
print("GLI-FLOW Release Navigation")
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
    / "release_navigation.json"
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
