from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class TelemetryNormalizer:
    def normalize(self, raw_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation to convert to unified schema
        return {
            "event_type": raw_telemetry.get("type"),
            "tool": raw_telemetry.get("tool"),
            "stage": raw_telemetry.get("stage"),
            "severity": raw_telemetry.get("severity"),
            "fingerprint": raw_telemetry.get("fingerprint"),
            "timestamp": raw_telemetry.get("timestamp"),
            "raw": raw_telemetry
        }
