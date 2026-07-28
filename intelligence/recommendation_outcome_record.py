from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime

@dataclass
class RecommendationOutcomeRecord:
    recommendation_id: str
    run_id: str
    failure_type: str
    recommendation: str
    trust_level: float
    accepted: bool
    rejected: bool
    outcome: str # e.g., "SUCCESS", "FAILURE"
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RecommendationFailureRecord:
    recommendation_id: str
    run_id: str
    failure_type: str
    recommendation: str
