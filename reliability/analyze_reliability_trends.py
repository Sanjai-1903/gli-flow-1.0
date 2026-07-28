import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent

REPORT = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "reliability_report_v2.json"
)

with open(REPORT) as f:
    reliability = json.load(f)

scores = [
    r["reliability_score"]
    for r in reliability
]

confidences = [
    r["confidence"]
    for r in reliability
]

health_states = [
    r["health"]
    for r in reliability
]

average_score = 0

if scores:
    average_score = (
        sum(scores)
        / len(scores)
    )

confidence_distribution = Counter(
    confidences
)

health_distribution = Counter(
    health_states
)

trend_report = {

    "average_reliability_score":
        average_score,

    "confidence_distribution":
        dict(confidence_distribution),

    "health_distribution":
        dict(health_distribution)
}

print("=" * 60)
print("GLI-FLOW Reliability Trend Intelligence")
print("=" * 60)
print()

print(
    f"Average Reliability : "
    f"{average_score:.2f}"
)

print()

print("Confidence Distribution")
print("------------------------------")

for key, value in confidence_distribution.items():

    print(f"{key} : {value}")

print()

print("Health Distribution")
print("------------------------------")

for key, value in health_distribution.items():

    print(f"{key} : {value}")

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "reliability_trend_report.json"
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
