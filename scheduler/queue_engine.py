import json
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

QUEUE_FILE = (
    ROOT_DIR
    / "scheduler"
    / "execution_queue.json"
)


def load_queue():

    with open(QUEUE_FILE, "r") as f:
        return json.load(f)


def save_queue(queue):

    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=4)


def add_execution(queue, run_name):

    entry = {
        "run_id": run_name,
        "status": "QUEUED",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    queue["queued_runs"].append(entry)

    return queue


def print_queue(queue):

    print("=" * 60)
    print("GLI-FLOW Execution Queue Engine")
    print("=" * 60)

    print(
        f"TOTAL QUEUED RUNS : "
        f"{len(queue['queued_runs'])}"
    )

    for item in queue["queued_runs"]:

        print("\n----------------------------------------")
        print(f"RUN ID    : {item['run_id']}")
        print(f"STATUS    : {item['status']}")
        print(f"TIMESTAMP : {item['timestamp']}")

    print("\n========================================")


def main():

    queue = load_queue()

    run_name = (
        f"run_{len(queue['queued_runs']) + 1}"
    )

    queue = add_execution(queue, run_name)

    save_queue(queue)

    print_queue(queue)


if __name__ == "__main__":
    main()
