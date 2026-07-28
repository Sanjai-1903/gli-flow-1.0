import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

QUEUE_FILE = (
    ROOT_DIR
    / "scheduler"
    / "execution_queue.json"
)


VALID_STATES = [
    "QUEUED",
    "RUNNING",
    "FAILED",
    "RETRYING",
    "COMPLETED",
    "ARCHIVED"
]


def load_queue():

    with open(QUEUE_FILE, "r") as f:
        return json.load(f)


def save_queue(queue):

    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=4)


def transition_state(queue):

    for run in queue["queued_runs"]:

        current = run["status"]

        if current == "QUEUED":

            run["status"] = "RUNNING"

        elif current == "RUNNING":

            run["status"] = "COMPLETED"

        elif current == "COMPLETED":

            run["status"] = "ARCHIVED"

    return queue


def print_queue(queue):

    print("=" * 60)
    print("GLI-FLOW Lifecycle State Engine")
    print("=" * 60)

    for item in queue["queued_runs"]:

        print("\n----------------------------------------")
        print(f"RUN ID : {item['run_id']}")
        print(f"STATE  : {item['status']}")

    print("\n========================================")


def main():

    queue = load_queue()

    queue = transition_state(queue)

    save_queue(queue)

    print_queue(queue)


if __name__ == "__main__":
    main()
