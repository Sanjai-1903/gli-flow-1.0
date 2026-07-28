import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

GRAPH_FILE = (
    ROOT_DIR
    / "scheduler"
    / "dependency_graph.json"
)


COMPLETED_STAGES = [
    "rtl",
    "synthesis"
]


def load_graph():

    with open(GRAPH_FILE, "r") as f:
        return json.load(f)


def validate_dependencies(stages):

    results = []

    for stage in stages:

        dependencies = stage["depends_on"]

        missing = []

        for dep in dependencies:

            if dep not in COMPLETED_STAGES:
                missing.append(dep)

        results.append({
            "stage": stage["name"],
            "ready": len(missing) == 0,
            "missing_dependencies": missing
        })

    return results


def print_results(results):

    print("=" * 60)
    print("GLI-FLOW Dependency Scheduling Engine")
    print("=" * 60)

    for result in results:

        print("\n----------------------------------------")
        print(f"STAGE : {result['stage']}")

        if result["ready"]:

            print("STATUS: READY")

        else:

            print("STATUS: BLOCKED")

            print(
                f"MISSING: "
                f"{', '.join(result['missing_dependencies'])}"
            )

    print("\n========================================")


def main():

    graph = load_graph()

    results = validate_dependencies(
        graph["stages"]
    )

    print_results(results)


if __name__ == "__main__":
    main()
