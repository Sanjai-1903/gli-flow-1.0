import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REPORT = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "reliability_report_v2.json"
)

with open(REPORT) as f:
    reliability = json.load(f)

comparisons = []

print("=" * 60)
print("GLI-FLOW Regression Intelligence")
print("=" * 60)
print()

for i in range(len(reliability) - 1):

    baseline = reliability[i]
    comparison = reliability[i + 1]

    baseline_score = baseline[
        "reliability_score"
    ]

    comparison_score = comparison[
        "reliability_score"
    ]

    delta = (
        comparison_score
        - baseline_score
    )

    status = "UNCHANGED"

    if delta > 0:
        status = "IMPROVED"

    elif delta < 0:
        status = "REGRESSED"

    result = {

        "baseline_run":
            baseline["run"],

        "comparison_run":
            comparison["run"],

        "metric":
            "reliability_score",

        "baseline_value":
            baseline_score,

        "comparison_value":
            comparison_score,

        "delta":
            delta,

        "regression_status":
            status
    }

    comparisons.append(result)

    print(
        f"{baseline['run']}"
        f" -> "
        f"{comparison['run']}"
    )

    print(f"  Delta  : {delta}")
    print(f"  Status : {status}")
    print()

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "regression_report.json"
)

with open(output, "w") as f:
    json.dump(
        comparisons,
        f,
        indent=4
    )

print("=" * 60)
print(f"[OUTPUT] {output}")
