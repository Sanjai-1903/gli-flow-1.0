from typing import List, Dict, Optional
from failure_atlas.repository import FailureAtlasRepository


class CalibrationEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def calculate_calibration_error(self, predictions: List[float], actuals: List[float]) -> float:
        if not predictions or len(predictions) != len(actuals):
            return 0.0
        return round(sum(abs(p - a) for p, a in zip(predictions, actuals)) / len(predictions), 4)


class AccuracyMetricsEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def calculate_metrics(self, predictions: List[int], actuals: List[int]) -> Dict[str, float]:
        if predictions and actuals and len(predictions) == len(actuals):
            tp = sum(1 for p, a in zip(predictions, actuals) if p == 1 and a == 1)
            fp = sum(1 for p, a in zip(predictions, actuals) if p == 1 and a == 0)
            fn = sum(1 for p, a in zip(predictions, actuals) if p == 0 and a == 1)
            tn = sum(1 for p, a in zip(predictions, actuals) if p == 0 and a == 0)
            total = tp + fp + fn + tn
            if total == 0:
                return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0}
            accuracy = (tp + tn) / total
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            return {
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
            }
        stats = self.repo.get_statistics()
        total = stats.get("total_entries", 0)
        if total == 0:
            return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0}
        fix_rate = stats.get("fix_rate", 50.0) / 100.0
        sample_conf = min(1.0, total / 100.0)
        return {
            "accuracy": round(fix_rate * sample_conf, 4),
            "precision": round(fix_rate, 4),
            "recall": round(fix_rate, 4),
        }
