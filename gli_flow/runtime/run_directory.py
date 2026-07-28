from pathlib import Path


class RunDirectoryManager:

    def __init__(self, run_id=None):
        if run_id:
            self.run_id = run_id
        else:
            from datetime import datetime
            self.run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.run_dir = Path("outputs/runs") / self.run_id

    def create(self):
        directories = [
            "logs",
            "reports",
            "artifacts",
            "telemetry",
            "snapshots",
        ]

        for directory in directories:
            (self.run_dir / directory).mkdir(parents=True, exist_ok=True)

        self.run_dir = self.run_dir.resolve()
        return self.run_dir
