from typing import Dict, Any, List, Optional
from intelligence.prediction_outcome_record import PredictionOutcomeRecord
from failure_atlas.repository import FailureAtlasRepository


class OutcomeCaptureService:
    def capture(self, run_id: str, prediction: Dict[str, Any], actual: Dict[str, Any]) -> PredictionOutcomeRecord:
        return PredictionOutcomeRecord(
            run_id=run_id,
            prediction_timestamp=prediction["timestamp"],
            timing_risk_predicted=prediction.get("timing", 0.0),
            routing_risk_predicted=prediction.get("routing", 0.0),
            drc_risk_predicted=prediction.get("drc", 0.0),
            lvs_risk_predicted=prediction.get("lvs", 0.0),
            power_risk_predicted=prediction.get("power", 0.0),
            tapeout_readiness_predicted=prediction.get("readiness", 0.0),
            actual_outcomes=actual,
            prediction_confidence=prediction.get("confidence", 0.5),
        )


class AccuracyEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def calculate_accuracy(self, outcomes: List[PredictionOutcomeRecord]) -> Dict[str, float]:
        if outcomes:
            correct = sum(
                1 for o in outcomes
                if abs(o.timing_risk_predicted - float(o.actual_outcomes.get("timing", 0))) < 0.2
            )
            precision = correct / len(outcomes)
            recall = correct / len(outcomes)
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            return {
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
            }
        stats = self.repo.get_statistics()
        total = stats.get("total_entries", 0)
        if total == 0:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        fix_rate = stats.get("fix_rate", 50.0) / 100.0
        sample_adj = min(1.0, total / 100.0)
        return {
            "precision": round(fix_rate * sample_adj, 4),
            "recall": round(fix_rate * sample_adj, 4),
            "f1": round(fix_rate * sample_adj, 4),
        }


class CalibrationEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def compute_brier_score(self, outcomes: List[PredictionOutcomeRecord]) -> float:
        if not outcomes:
            return 0.5
        errors = [
            (o.prediction_confidence - float(o.actual_outcomes.get("outcome", 0))) ** 2
            for o in outcomes
        ]
        return round(sum(errors) / len(errors), 4)
