import json
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

HEALTH_FILE = (
    ROOT_DIR
    / "dashboard"
    / "health_report.json"
)

TREND_FILE = (
    ROOT_DIR
    / "trends"
    / "historical_trends.json"
)


def load_health():

    if not HEALTH_FILE.exists():
        return None

    with open(HEALTH_FILE, "r") as f:
        return json.load(f)


def load_existing_trends():

    if not TREND_FILE.exists():
        return []

    with open(TREND_FILE, "r") as f:
        return json.load(f)


def append_trend(trends, health):

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "execution_score": (
            health["execution_health"].get(
                "score",
                0
            )
        ),

        "classification": (
            health["execution_health"].get(
                "classification",
                "UNKNOWN"
            )
        ),

        "total_runs": (
            health["telemetry_summary"].get(
                "total_runs",
                0
            )
        ),

        "failures": (
            health["telemetry_summary"].get(
                "total_detected_failures",
                0
            )
        ),

        "regression_detected": (
            health["regression_state"].get(
                "regression_detected",
                False
            )
        )
    }

    trends.append(entry)

    return trends


def save_trends(trends):

    with open(TREND_FILE, "w") as f:
        json.dump(trends, f, indent=4)


def print_summary(trends):

    latest = trends[-1]

    print("=" * 60)
    print("GLI-FLOW Historical Trend Engine")
    print("=" * 60)

    print(
        f"TOTAL SNAPSHOTS TRACKED : "
        f"{len(trends)}"
    )

    print(
        f"LATEST SCORE            : "
        f"{latest['execution_score']}"
    )

    print(
        f"LATEST CLASSIFICATION   : "
        f"{latest['classification']}"
    )

    print(
        f"TOTAL RUNS              : "
        f"{latest['total_runs']}"
    )

    print(
        f"FAILURES                : "
        f"{latest['failures']}"
    )

    print(
        f"REGRESSION DETECTED     : "
        f"{latest['regression_detected']}"
    )

    print("\n========================================")
    print("[SUCCESS] Trend analysis updated")
    print("========================================")


def main():

    health = load_health()

    if health is None:

        print("[ERROR] Missing health report")

        return

    trends = load_existing_trends()

    trends = append_trend(trends, health)

    save_trends(trends)

    print_summary(trends)


if __name__ == "__main__":
    main()
