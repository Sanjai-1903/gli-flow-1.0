import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

WORKER_FILE = (
    ROOT_DIR
    / "scheduler"
    / "workers.json"
)


TASK_QUEUE = [
    "synthesis",
    "routing"
]


def load_workers():

    with open(WORKER_FILE, "r") as f:
        return json.load(f)


def assign_tasks(worker_db):

    assignments = []

    for task in TASK_QUEUE:

        assigned = False

        for worker in worker_db["workers"]:

            if (
                task in worker["capabilities"]
                and worker["status"] == "IDLE"
            ):

                worker["status"] = "BUSY"

                assignments.append({
                    "task": task,
                    "worker": worker["worker_id"]
                })

                assigned = True

                break

        if not assigned:

            assignments.append({
                "task": task,
                "worker": "UNASSIGNED"
            })

    return assignments


def print_results(assignments):

    print("=" * 60)
    print("GLI-FLOW Worker Abstraction Engine")
    print("=" * 60)

    for item in assignments:

        print("\n----------------------------------------")
        print(f"TASK   : {item['task']}")
        print(f"WORKER : {item['worker']}")

    print("\n========================================")


def main():

    workers = load_workers()

    assignments = assign_tasks(workers)

    print_results(assignments)


if __name__ == "__main__":
    main()
