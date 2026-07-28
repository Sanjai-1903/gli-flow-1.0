import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent

REPORT = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "regression_report.json"
)

with open(REPORT) as f:
    regressions = json.load(f)

statuses = [
    r["regression_status"]
    for r in regressions
]

status_distribution = Counter(
    statuses
)

trend_report = {

    "total_comparisons":
        len(regressions),

    "status_distribution":
        dict(status_distribution)
}

print("=" * 60)
print("GLI-FLOW Regression Trend Intelligence")
print("=" * 60)
print()

print(
    f"Total Comparisons : "
    f"{len(regressions)}"
)

print()

print("Regression Distribution")
print("------------------------------")

for key, value in status_distribution.items():

    print(f"{key} : {value}")

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "regression_trend_report.json"
)

with open(output, "w") as f:
    json.dump(
        trend_report,
        f,
        indent=4
    )

print()
print("=" * 60)
print(f"[OUTPUT] {output}")
