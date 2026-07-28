import json
import os


class TelemetryManager:

    def __init__(self, run_dir):
        self.run_dir = run_dir
        self.telemetry_dir = os.path.join(run_dir, "telemetry")
        os.makedirs(self.telemetry_dir, exist_ok=True)
        self._environment_events: list[dict] = []

    def _export_json(self, filename, data):
        output_file = os.path.join(self.telemetry_dir, filename)
        try:
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            print(f"[WARN] Failed to write telemetry {filename}: {e}")

    def export_metrics(self, metrics):
        self._export_json("metrics.json", metrics)

    def export_stage_data(self, stage_name, data):
        safe_name = stage_name.lower().replace(" ", "_")
        self._export_json(f"{safe_name}.json", data)

    def record_environment_event(self, event_type: str, tool: str, detail: str):
        """Record an environment resilience event for telemetry.

        Event types:
          tool_shadowing — broken local binary shadows valid system binary
          broken_wrapper — Tcl wrapper references missing file
          repair_invocation — user invoked a repair action
          repair_success — repair completed successfully
          repair_failure — repair failed
        """
        import time
        event = {
            "type": event_type,
            "tool": tool,
            "detail": detail,
            "timestamp": time.time(),
        }
        self._environment_events.append(event)

    def export_environment_events(self):
        """Write collected environment events to telemetry."""
        if self._environment_events:
            self._export_json("environment_events.json", {
                "event_count": len(self._environment_events),
                "events": self._environment_events,
            })
