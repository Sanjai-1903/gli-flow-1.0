import json
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


def inject_failure(queue):

    if not queue["queued_runs"]:
        return queue

    queue["queued_runs"][0]["status"] = "FAILED"

    return queue


def main():

    queue = load_queue()

    queue = inject_failure(queue)

    save_queue(queue)

    print("[SUCCESS] Failure injected")


if __name__ == "__main__":
    main()
