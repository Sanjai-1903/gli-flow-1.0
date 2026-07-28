from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class PredictionTrainingRecord:
    run_id: str
    design_name: str
    tool: str
    stage: str
    telemetry_summary: Dict[str, Any]
    failure_fingerprint: str
    root_cause: str
    resolution: str
    trust_score: float
    outcome: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "design_name": self.design_name,
            "tool": self.tool,
            "stage": self.stage,
            "telemetry_summary": self.telemetry_summary,
            "failure_fingerprint": self.failure_fingerprint,
            "root_cause": self.root_cause,
            "resolution": self.resolution,
            "trust_score": self.trust_score,
            "outcome": self.outcome
        }
