import psutil
import time


TASKS = [
    {
        "name": "synthesis",
        "priority": 1,
        "estimated_memory_mb": 500
    },

    {
        "name": "floorplan",
        "priority": 2,
        "estimated_memory_mb": 700
    },

    {
        "name": "routing",
        "priority": 3,
        "estimated_memory_mb": 1200
    }
]


def print_system_resources():

    cpu = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()

    print("\nSYSTEM RESOURCES:")
    print(f"CPU USAGE       : {cpu}%")

    print(
        f"MEMORY USAGE    : "
        f"{memory.percent}%"
    )

    print(
        f"AVAILABLE RAM   : "
        f"{round(memory.available / (1024**3), 2)} GB"
    )


def schedule_tasks():

    print("\nTASK SCHEDULING:")

    sorted_tasks = sorted(
        TASKS,
        key=lambda x: x["priority"]
    )

    for task in sorted_tasks:

        print("\n----------------------------------------")
        print(f"TASK      : {task['name']}")

        print(
            f"PRIORITY  : {task['priority']}"
        )

        print(
            f"EST MEMORY: "
            f"{task['estimated_memory_mb']} MB"
        )

        print("STATUS    : SCHEDULED")

        time.sleep(1)


def main():

    print("=" * 60)
    print("GLI-FLOW Resource Management Engine")
    print("=" * 60)

    print_system_resources()

    schedule_tasks()

    print("\n========================================")
    print("[SUCCESS] Resource scheduling complete")
    print("========================================")


if __name__ == "__main__":
    main()
