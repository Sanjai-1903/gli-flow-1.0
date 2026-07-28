import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REPORTS_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

navigation = {

    "regression_report": None,
    "regression_trend_report": None,
    "regression_snapshot": None
}

report_mapping = {

    "regression_report":
        "regression_report.json",

    "regression_trend_report":
        "regression_trend_report.json",

    "regression_snapshot":
        "regression_snapshot.json"
}

print("=" * 60)
print("GLI-FLOW Regression Navigation")
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
    / "regression_navigation.json"
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
