import json
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

WORKER_FILE = (
    ROOT_DIR
    / "scheduler"
    / "workers.json"
)

DISPATCH_FILE = (
    ROOT_DIR
    / "scheduler"
    / "remote_dispatch.json"
)


TASKS = [
    "synthesis",
    "routing",
    "signoff"
]


def load_json(path):

    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def dispatch_tasks(workers, dispatch_db):

    for task in TASKS:

        assigned = False

        for worker in workers["workers"]:

            if (
                task in worker["capabilities"]
            ):

                entry = {
                    "task": task,
                    "worker": worker["worker_id"],
                    "timestamp": (
                        datetime.now(timezone.utc).isoformat()
                    ),
                    "status": "DISPATCHED"
                }

                dispatch_db["dispatch_log"].append(entry)

                assigned = True

                break

        if not assigned:

            dispatch_db["dispatch_log"].append({
                "task": task,
                "worker": "UNAVAILABLE",
                "timestamp": (
                    datetime.now(timezone.utc).isoformat()
                ),
                "status": "FAILED_DISPATCH"
            })

    return dispatch_db


def print_dispatch(dispatch_db):

    print("=" * 60)
    print("GLI-FLOW Remote Execution Protocol")
    print("=" * 60)

    for item in dispatch_db["dispatch_log"]:

        print("\n----------------------------------------")
        print(f"TASK      : {item['task']}")
        print(f"WORKER    : {item['worker']}")
        print(f"STATUS    : {item['status']}")
        print(f"TIMESTAMP : {item['timestamp']}")

    print("\n========================================")


def main():

    workers = load_json(WORKER_FILE)

    dispatch_db = load_json(DISPATCH_FILE)

    dispatch_db = dispatch_tasks(
        workers,
        dispatch_db
    )

    save_json(DISPATCH_FILE, dispatch_db)

    print_dispatch(dispatch_db)


if __name__ == "__main__":
    main()
