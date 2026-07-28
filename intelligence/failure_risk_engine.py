from typing import Dict, Any, Optional
from failure_atlas.repository import FailureAtlasRepository
from failure_atlas.prediction.risk import FailureRiskEngine as AtlasRiskEngine


class FailureRiskEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.atlas_engine = AtlasRiskEngine(db_path)
        self.repo = FailureAtlasRepository(db_path)

    def predict_risk(self, failure_type: str) -> float:
        return self.atlas_engine.predict_risk_for_type(failure_type)

    def predict_full_risk(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        return self.atlas_engine.predict_risk(current_metrics)

    def get_risk_summary(self) -> Dict[str, float]:
        total = max(self.repo.count_entries(), 1)
        risks = {}
        for f_type in ["Timing", "Routing", "DRC", "LVS", "Power"]:
            count = self.repo.count_entries(failure_type=f_type)
            risks[f_type] = round(count / total * 100, 2)
        return risks
