import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

QUEUE_FILE = (
    ROOT_DIR
    / "scheduler"
    / "execution_queue.json"
)

MAX_RETRIES = 3


def load_queue():

    with open(QUEUE_FILE, "r") as f:
        return json.load(f)


def save_queue(queue):

    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=4)


def initialize_retry(run):

    if "retry_count" not in run:
        run["retry_count"] = 0


def process_recovery(queue):

    for run in queue["queued_runs"]:

        initialize_retry(run)

        if run["status"] == "FAILED":

            if run["retry_count"] < MAX_RETRIES:

                run["retry_count"] += 1

                run["status"] = "RETRYING"

            else:

                run["status"] = "ARCHIVED"

        elif run["status"] == "RETRYING":

            run["status"] = "RUNNING"

    return queue


def print_results(queue):

    print("=" * 60)
    print("GLI-FLOW Recovery Orchestration Engine")
    print("=" * 60)

    for run in queue["queued_runs"]:

        print("\n----------------------------------------")
        print(f"RUN ID      : {run['run_id']}")
        print(f"STATUS      : {run['status']}")
        print(f"RETRY COUNT : {run.get('retry_count', 0)}")

    print("\n========================================")


def main():

    queue = load_queue()

    queue = process_recovery(queue)

    save_queue(queue)

    print_results(queue)


if __name__ == "__main__":
    main()
