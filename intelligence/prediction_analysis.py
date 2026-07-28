from typing import Dict, Any, List, Optional
from failure_atlas.repository import FailureAtlasRepository
from failure_atlas.prediction.similarity import ExecutionSimilarityEngine


class SimilarityEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.engine = ExecutionSimilarityEngine(db_path)

    def find_similar(self, features: Dict[str, Any]) -> List[str]:
        results = self.engine.find_similar(features, top_n=5)
        return [r["run_id"] for r in results if r["similarity"] > 0.3]


class ConfidenceEngine:
    def measure_confidence(self, prediction: Any) -> float:
        repo = FailureAtlasRepository()
        stats = repo.get_statistics()
        if stats["total_entries"] > 0:
            fix_rate = stats.get("fix_rate", 50.0) / 100.0
            sample_factor = min(1.0, stats["total_entries"] / 100.0)
            return round(0.5 + fix_rate * 0.3 + sample_factor * 0.2, 4)
        return 0.5


class ExplainabilityEngine:
    def explain(self, prediction: Any) -> str:
        if isinstance(prediction, dict):
            reasons = []
            for key, val in prediction.items():
                if isinstance(val, dict) and val.get("risk", 0) > 50:
                    reasons.append(f"High {key} risk ({val['risk']:.0f}%)")
            if reasons:
                return "; ".join(reasons)
        return "No dominant risk factors detected."


class PredictionQualityEngine:
    def evaluate(self, predictions: List[Any], actuals: List[Any]) -> Dict[str, float]:
        repo = FailureAtlasRepository()
        stats = repo.get_statistics()
        total = stats.get("total_entries", 0)
        if total == 0:
            return {"precision": 0.0, "recall": 0.0, "coverage": 0.0}
        total_fixed = stats.get("fixed_entries", 0)
        precision = total_fixed / max(total, 1)
        recall = total_fixed / max(total, 1)
        all_failures = max(repo.get_failure_count(), 1)
        atlas_coverage = total / max(total + all_failures, 1)
        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "coverage": round(min(1.0, total / 100.0), 4),
        }
