from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from failure_atlas.repository import FailureAtlasRepository
from failure_atlas.correlation_engine import get_correlation_data


@dataclass
class CorrelationEngine:
    """Correlates telemetry with failure patterns using FailureAtlasRepository data."""

    db_path: Optional[str] = None

    def __post_init__(self):
        self.repo = FailureAtlasRepository(db_path=self.db_path)

    def correlate(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        failure_type = telemetry.get("failure_type", "UNKNOWN")
        correlation = get_correlation_data(failure_type)
        correlation["current_telemetry"] = {
            "wns": telemetry.get("wns"),
            "tns": telemetry.get("tns"),
            "utilization": telemetry.get("utilization"),
            "drc_violations": telemetry.get("drc_violations"),
        }
        return correlation

    def correlate_by_id(self, failure_id: str) -> Dict[str, Any]:
        entry = self.repo.get_failure_by_id(failure_id)
        if not entry:
            return {"error": "Failure not found"}
        return get_correlation_data(entry.get("failure_type", "UNKNOWN"))
