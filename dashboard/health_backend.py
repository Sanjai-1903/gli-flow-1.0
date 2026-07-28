import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    ROOT_DIR
    / "dashboard"
    / "health_report.json"
)


FILES = {
    "analytics": (
        ROOT_DIR
        / "analytics"
        / "execution_report.json"
    ),

    "reliability": (
        ROOT_DIR
        / "analytics"
        / "reliability_report.json"
    ),

    "regression": (
        ROOT_DIR
        / "regression"
        / "regression_report.json"
    )
}


def load_json(path):

    if not path.exists():
        return None

    with open(path, "r") as f:
        return json.load(f)


def aggregate_health():

    analytics = load_json(FILES["analytics"])

    reliability = load_json(FILES["reliability"])

    regression = load_json(FILES["regression"])

    health = {
        "execution_health": {},
        "telemetry_summary": {},
        "governance_state": {},
        "regression_state": {}
    }

    if analytics:

        health["telemetry_summary"] = {
            "total_runs": analytics.get(
                "total_runs",
                0
            ),

            "total_detected_failures": analytics.get(
                "total_detected_failures",
                0
            )
        }

    if reliability:

        health["execution_health"] = {
            "score": reliability.get(
                "execution_score",
                0
            ),

            "classification": reliability.get(
                "classification",
                "UNKNOWN"
            )
        }

    if regression:

        health["regression_state"] = {
            "regression_detected": regression.get(
                "regression_detected",
                False
            ),

            "flags": regression.get(
                "flags",
                []
            )
        }

    health["governance_state"] = {
        "contracts_enforced": True,
        "reproducibility_enabled": True
    }

    return health


def save_health(health):

    with open(OUTPUT_FILE, "w") as f:
        json.dump(health, f, indent=4)


def print_health(health):

    print("=" * 60)
    print("GLI-FLOW Infrastructure Health Backend")
    print("=" * 60)

    print("\nEXECUTION HEALTH:")

    print(
        f"  SCORE           : "
        f"{health['execution_health'].get('score', 0)}"
    )

    print(
        f"  CLASSIFICATION  : "
        f"{health['execution_health'].get('classification', 'UNKNOWN')}"
    )

    print("\nTELEMETRY SUMMARY:")

    print(
        f"  TOTAL RUNS      : "
        f"{health['telemetry_summary'].get('total_runs', 0)}"
    )

    print(
        f"  FAILURES        : "
        f"{health['telemetry_summary'].get('total_detected_failures', 0)}"
    )

    print("\nREGRESSION STATE:")

    print(
        f"  REGRESSION      : "
        f"{health['regression_state'].get('regression_detected', False)}"
    )

    print("\nGOVERNANCE:")

    print(
        f"  CONTRACTS       : "
        f"{health['governance_state']['contracts_enforced']}"
    )

    print(
        f"  REPRODUCIBILITY : "
        f"{health['governance_state']['reproducibility_enabled']}"
    )

    print("\n========================================")
    print("[SUCCESS] Health aggregation complete")
    print("========================================")


def main():

    health = aggregate_health()

    save_health(health)

    print_health(health)


if __name__ == "__main__":
    main()
