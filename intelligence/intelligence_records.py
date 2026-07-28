from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ExecutionIntelligenceRecord:
    failure: str
    root_cause: str
    resolution: str
    trust_score: float
    telemetry_summary: Dict[str, Any]
    outcome: str
