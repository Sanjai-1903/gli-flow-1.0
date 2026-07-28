import json
import os
from typing import Optional
from pathlib import Path

from intelligence.recommendation_record import RecommendationRecord
from failure_atlas.repository import FailureAtlasRepository


class RecommendationTracker:
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def track_outcome(self, rec: RecommendationRecord, accepted: bool, successful: bool):
        entry = {
            "failure": rec.failure,
            "root_cause": rec.root_cause,
            "recommended_fix": rec.recommended_fix,
            "historical_success_rate": rec.historical_success_rate,
            "trust_score": rec.trust_score,
            "accepted": accepted,
            "successful": successful,
        }
        history_path = self._get_history_path()
        history = []
        if os.path.exists(history_path):
            with open(history_path) as f:
                history = json.load(f)
        history.append(entry)
        if len(history) > 1000:
            history = history[-1000:]
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)

        if successful:
            self.repo.get_fix_effectiveness()

    def _get_history_path(self) -> str:
        return str(Path.home() / ".gli_flow" / "recommendation_tracker.json")


class RecommendationQualityEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def measure_quality(self, records: list) -> float:
        stats = self.repo.get_statistics()
        total = stats.get("total_entries", 0)
        if total == 0:
            return 0.0
        fix_rate = stats.get("fix_rate", 0.0) / 100.0
        sample_quality = min(1.0, total / 50.0)
        return round(fix_rate * 0.6 + sample_quality * 0.4, 4)
