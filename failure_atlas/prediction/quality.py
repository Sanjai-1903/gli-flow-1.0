import json
import os
from typing import Dict, Any, Optional
from failure_atlas.repository import FailureAtlasRepository


class PredictionQualityEngine:
    """Tracks prediction accuracy and confidence calibration.

    Stores prediction-vs-actual outcomes for accuracy calculation
    and provides quality metrics derived from real Failure Atlas data.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path)

    def record_outcome(self, prediction: Dict[str, Any], actual_outcome: str):
        outcome_record = {
            "prediction": prediction,
            "actual_outcome": actual_outcome,
            "correct": prediction.get("outcome") == actual_outcome,
        }
        history_path = self._get_history_path()
        history = []
        if os.path.exists(history_path):
            with open(history_path) as f:
                history = json.load(f)
        history.append(outcome_record)
        if len(history) > 1000:
            history = history[-1000:]
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)

    def _get_history_path(self) -> str:
        from pathlib import Path
        return str(Path.home() / ".gli_flow" / "prediction_history.json")

    def get_quality_score(self) -> float:
        stats = self.repo.get_statistics()
        total = stats.get("total_entries", 0)
        if total == 0:
            return 0.0
        fix_rate = stats.get("fix_rate", 50.0) / 100.0
        sample_confidence = min(1.0, total / 200.0)
        return round(fix_rate * 0.6 + sample_confidence * 0.4, 4)

    def get_accuracy(self) -> float:
        history_path = self._get_history_path()
        if not os.path.exists(history_path):
            return 0.0
        with open(history_path) as f:
            history = json.load(f)
        if not history:
            return 0.0
        correct = sum(1 for h in history if h.get("correct"))
        return round(correct / len(history), 4)
