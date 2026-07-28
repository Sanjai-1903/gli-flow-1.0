import time
from concurrent.futures import ThreadPoolExecutor


TASKS = [
    "environment_validation",
    "telemetry_collection",
    "analytics_generation",
    "reliability_scoring",
    "governance_check"
]


def execute_task(task):

    print(f"[STARTED] {task}")

    time.sleep(2)

    print(f"[COMPLETED] {task}")

    return task


def main():

    print("=" * 60)
    print("GLI-FLOW Parallel Orchestration Engine")
    print("=" * 60)

    with ThreadPoolExecutor(max_workers=3) as executor:

        results = list(
            executor.map(execute_task, TASKS)
        )

    print("\n========================================")
    print("[SUCCESS] Parallel execution complete")
    print("========================================")

    print("\nEXECUTED TASKS:")

    for result in results:
        print(f"  - {result}")


if __name__ == "__main__":
    main()
