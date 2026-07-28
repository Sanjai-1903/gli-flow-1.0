from typing import Dict, Any, Optional
from failure_atlas.repository import FailureAtlasRepository
from failure_atlas.prediction.readiness import TapeoutReadinessPredictor
from failure_atlas.prediction.convergence import ConvergenceEstimator


class ReadinessPredictor:
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path)
        self.readiness_predictor = TapeoutReadinessPredictor(db_path)

    def predict_readiness(self, features: Dict[str, Any]) -> float:
        result = self.readiness_predictor.predict_readiness(features)
        tapeout_score = result.get("TapeoutReady", 0.0)
        return round(tapeout_score / 100.0, 4)


class ConvergencePredictor:
    def __init__(self, db_path: Optional[str] = None):
        self.estimator = ConvergenceEstimator(db_path)
        self.repo = FailureAtlasRepository(db_path)

    def predict_convergence(self, features: Dict[str, Any]) -> float:
        stage = features.get("stage", "routing")
        base = self.estimator.estimate_convergence(stage, features)
        stats = self.repo.get_statistics()
        total = stats.get("total_entries", 0)
        if total == 0:
            return round(base / 100.0, 4)
        fixed_rate = stats.get("fix_rate", 0.0) / 100.0
        adjusted = base * (0.6 + 0.4 * fixed_rate)
        return round(min(1.0, adjusted / 100.0), 4)
