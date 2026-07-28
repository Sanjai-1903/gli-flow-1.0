import json
from datetime import datetime
from typing import Any, Dict
from failure_atlas.intelligence_model import ExecutionIntelligenceRecord

class TelemetryNormalizer:
    """Converts heterogeneous telemetry data into a unified ExecutionIntelligenceRecord."""
    
    @staticmethod
    def normalize(event_data: Dict[str, Any]) -> ExecutionIntelligenceRecord:
        # Example mapping logic
        # In a real scenario, this would map fields based on event types.
        return ExecutionIntelligenceRecord(
            event_type=event_data.get("event", "UNKNOWN"),
            tool=event_data.get("tool", "UNKNOWN"),
            stage=event_data.get("stage", "UNKNOWN"),
            severity=event_data.get("severity", "MEDIUM"),
            fingerprint=event_data.get("signature") or event_data.get("fingerprint", "NONE"),
            timestamp=event_data.get("created_at") or datetime.now().isoformat(),
            failure_context=event_data.get("details", {}),
            root_cause_analysis=event_data.get("root_cause", {}),
            resolution=event_data.get("resolution", {}),
            trust_score=event_data.get("trust_score", 0.0),
            outcome=event_data.get("outcome", "UNKNOWN")
        )
