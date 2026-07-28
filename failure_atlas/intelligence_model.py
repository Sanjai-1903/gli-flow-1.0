from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class ExecutionIntelligenceRecord:
    """Canonical training unit for GLI-SDI and Large Circuit Models."""
    event_type: str
    tool: str
    stage: str
    severity: str
    fingerprint: str
    timestamp: str
    failure_context: dict[str, Any]
    root_cause_analysis: dict[str, Any]
    resolution: dict[str, Any]
    trust_score: float
    outcome: str # e.g., SUCCESS, FAILED
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "tool": self.tool,
            "stage": self.stage,
            "severity": self.severity,
            "fingerprint": self.fingerprint,
            "timestamp": self.timestamp,
            "failure_context": self.failure_context,
            "root_cause_analysis": self.root_cause_analysis,
            "resolution": self.resolution,
            "trust_score": self.trust_score,
            "outcome": self.outcome
        }
