import os
import json


class TelemetryManager:

    def __init__(self, run_dir):

        self.run_dir = run_dir

        self.telemetry_dir = os.path.join(
            run_dir,
            "telemetry"
        )

        os.makedirs(
            self.telemetry_dir,
            exist_ok=True
        )

    def export_metrics(self, metrics):

        output_file = os.path.join(
            self.telemetry_dir,
            "metrics.json"
        )

        with open(output_file, "w") as f:

            json.dump(
                metrics,
                f,
                indent=4
            )

    def export_stage_data(
        self,
        stage_name,
        data
    ):

        output_file = os.path.join(
            self.telemetry_dir,
            f"{stage_name}.json"
        )

        with open(output_file, "w") as f:

            json.dump(
                data,
                f,
                indent=4
            )
