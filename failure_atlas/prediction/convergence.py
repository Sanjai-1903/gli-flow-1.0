from typing import Dict, Any, Optional
from failure_atlas.repository import FailureAtlasRepository


class ConvergenceEstimator:
    """Estimates the likelihood of successful convergence for flow stages.

    Uses stage-specific thresholds calibrated against historical data
    from the FailureAtlasRepository. Scores are adjusted based on
    real fix rates to reflect actual convergence difficulty.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def _get_stage_adjustment(self, stage: str) -> float:
        type_map = {
            "placement": "Timing",
            "cts": "Timing",
            "routing": "Routing",
            "signoff": "DRC",
        }
        failure_type = type_map.get(stage, stage.capitalize())
        count = self.repo.count_entries(failure_type=failure_type)
        fixed = self.repo.get_fix_effectiveness(min_samples=1)
        for row in fixed:
            if row["failure_type"] == failure_type:
                success_rate = row["success_rate"] / 100.0
                sample_factor = min(1.0, count / 50.0)
                return success_rate * 0.7 + (1.0 - sample_factor) * 0.3
        return 0.5

    def estimate_convergence(self, stage: str, metrics: Dict[str, Any]) -> float:
        thresholds = {
            "placement": {"congestion": 0.3, "utilization": 85},
            "cts": {"skew": 0.1, "insertion_delay": 1.0},
            "routing": {"overflow": 0.05, "drc_violations": 100},
            "signoff": {"drc_violations": 50, "wns": -0.5},
        }

        if stage not in thresholds:
            return 100.0

        score = 100.0
        stage_thresholds = thresholds[stage]
        for metric, threshold in stage_thresholds.items():
            value = metrics.get(metric, 0)
            if isinstance(value, (int, float)) and value > threshold:
                excess = (value - threshold) / threshold
                score -= min(40.0, excess * 25.0)

        adjustment = self._get_stage_adjustment(stage)
        score = score * (0.5 + 0.5 * adjustment)

        return max(0.0, score)
