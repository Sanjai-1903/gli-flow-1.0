from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime

@dataclass
class PredictionOutcomeRecord:
    run_id: str
    prediction_timestamp: datetime
    timing_risk_predicted: float
    routing_risk_predicted: float
    drc_risk_predicted: float
    lvs_risk_predicted: float
    power_risk_predicted: float
    tapeout_readiness_predicted: float
    actual_outcomes: Dict[str, Any]
    prediction_confidence: float
