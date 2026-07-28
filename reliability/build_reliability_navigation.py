import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REPORTS_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

navigation = {

    "execution_health": None,
    "reliability_report": None,
    "reliability_trend_report": None,
    "reliability_snapshot": None
}

report_mapping = {

    "execution_health":
        "execution_health_v3.json",

    "reliability_report":
        "reliability_report_v2.json",

    "reliability_trend_report":
        "reliability_trend_report.json",

    "reliability_snapshot":
        "reliability_snapshot.json"
}

print("=" * 60)
print("GLI-FLOW Reliability Navigation")
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
    / "reliability_navigation.json"
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
