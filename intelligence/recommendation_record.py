from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class RecommendationRecord:
    failure: str
    root_cause: str
    recommended_fix: str
    historical_success_rate: float
    trust_score: float
    outcome: str
