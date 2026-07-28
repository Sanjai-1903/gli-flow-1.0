from typing import Dict, Any, List, Optional
from failure_atlas.repository import FailureAtlasRepository
from failure_atlas.prediction.similarity import ExecutionSimilarityEngine


DESIGN_CLASS_READINESS_BASELINE = {
    "CPU":         0.50,
    "DSP":         0.45,
    "Accelerator": 0.40,
    "Memory-heavy":0.35,
    "Controller":  0.60,
    "Interconnect":0.55,
}


class TapeoutReadinessPredictor:
    """Estimates probability of tapeout success based on historical outcomes of similar runs.

    Readiness derives from:
    - Historical outcome rates per stage for similar runs
    - Overall fix rate from Failure Atlas
    - Trust-weighted aggregation
    - Design-class baseline (simpler designs start with higher readiness)
    """

    def __init__(self, db_path: Optional[str] = None):
        self.similarity_engine = ExecutionSimilarityEngine(db_path)
        self.repo = FailureAtlasRepository(db_path)

    def _get_design_class(self, design_name: str) -> Optional[str]:
        try:
            import sqlite3
            conn = sqlite3.connect(self.repo.db_path)
            row = conn.execute(
                "SELECT classification FROM design_profiles WHERE design_name = ?",
                (design_name,)
            ).fetchone()
            conn.close()
            if row and row[0]:
                return row[0]
        except Exception:
            pass
        return None

    def _get_stage_outcome(self, run_id: str) -> Dict[str, float]:
        entries = self.repo.get_failures_for_run(run_id)
        if not entries:
            return {"Implementation": 1.0, "Signoff": 1.0, "TapeoutReady": 1.0}
        severity_scores = {"INFO": 1.0, "LOW": 0.9, "MEDIUM": 0.6, "HIGH": 0.3, "CRITICAL": 0.0, "TAPEOUT_BLOCKING": 0.0}
        impl_score = 1.0
        signoff_score = 1.0
        tapeout_score = 1.0
        for e in entries:
            sev = e.get("severity", "MEDIUM").upper()
            penalty = severity_scores.get(sev, 0.6)
            e_level = e.get("entry_level", "FAILURE")
            if e.get("fix_applied"):
                penalty = min(1.0, penalty + 0.3)
            if e_level == "FAILURE":
                tapeout_score = min(tapeout_score, penalty)
                if sev in ("HIGH", "CRITICAL", "TAPEOUT_BLOCKING"):
                    signoff_score = min(signoff_score, penalty * 0.5)
            impl_score = min(impl_score, penalty)
        return {
            "Implementation": impl_score,
            "Signoff": signoff_score if signoff_score < 1.0 else impl_score,
            "TapeoutReady": tapeout_score if tapeout_score < 1.0 else signoff_score,
        }

    def predict_readiness(self, current_metrics: Dict[str, Any], design_name: Optional[str] = None) -> Dict[str, float]:
        similar_runs = self.similarity_engine.find_similar(current_metrics, design_name=design_name)
        if not similar_runs:
            baseline = 0.0
            if design_name:
                cls = self._get_design_class(design_name)
                baseline = DESIGN_CLASS_READINESS_BASELINE.get(cls, 0.30)
            return {
                "Implementation": round(baseline * 100, 2),
                "Signoff": round(baseline * 100, 2),
                "TapeoutReady": round(baseline * 80, 2),
            }

        design_baseline = 0.5
        if design_name:
            cls = self._get_design_class(design_name)
            design_baseline = DESIGN_CLASS_READINESS_BASELINE.get(cls, 0.50)

        success_counts = {"Implementation": 0.0, "Signoff": 0.0, "TapeoutReady": 0.0}
        total_weight = 0.0

        for run in similar_runs:
            weight = run.get("similarity", 0.5)
            total_weight += weight
            outcomes = self._get_stage_outcome(run["run_id"])
            for stage in success_counts:
                success_counts[stage] += outcomes.get(stage, 0.5) * weight

        overall_stats = self.repo.get_statistics()
        fix_rate = overall_stats.get("fix_rate", 50.0) / 100.0

        result = {}
        for stage in success_counts:
            weighted = (success_counts[stage] / total_weight) if total_weight > 0 else 0.0
            blended = weighted * 0.5 + fix_rate * 0.25 + design_baseline * 0.25
            result[stage] = round(blended * 100, 2)

        return result
