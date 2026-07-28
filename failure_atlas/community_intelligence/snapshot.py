import json
import os
from datetime import datetime
from typing import Optional


class DatasetSnapshot:
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            from gli_flow.database.migrations import _get_db_path
            self.db_path = _get_db_path()

    def create(self, output_path: Optional[str] = None) -> dict:
        from failure_atlas.community_intelligence.export import TelemetryExporter

        exporter = TelemetryExporter(self.db_path)
        snapshot = exporter.export_dataset_snapshot()

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(snapshot, f, indent=2, default=str)

        return snapshot
