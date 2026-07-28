from typing import Dict, Any, List, Optional
from failure_atlas.prediction.similarity import ExecutionSimilarityEngine
from failure_atlas.repository import FailureAtlasRepository


DESIGN_CLASS_RISK_PRIORS = {
    "CPU":        {"Timing": 35.0, "Routing": 20.0, "DRC": 20.0, "LVS": 10.0, "Power": 15.0},
    "DSP":        {"Timing": 40.0, "Routing": 25.0, "DRC": 15.0, "LVS": 10.0, "Power": 10.0},
    "Accelerator":{"Timing": 25.0, "Routing": 35.0, "DRC": 15.0, "LVS": 10.0, "Power": 15.0},
    "Memory-heavy":{"Timing": 15.0, "Routing": 20.0, "DRC": 35.0, "LVS": 15.0, "Power": 15.0},
    "Controller": {"Timing": 20.0, "Routing": 25.0, "DRC": 25.0, "LVS": 15.0, "Power": 15.0},
    "Interconnect":{"Timing": 25.0, "Routing": 35.0, "DRC": 15.0, "LVS": 10.0, "Power": 15.0},
}


class FailureRiskEngine:
    """Predicts risk of various failure types based on historical similarities and trust-weighted Failure Atlas data.

    Risk = historical failure frequency + similar run outcomes + design-class priors + trust weighting.
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

    def predict_risk(self, current_metrics: Dict[str, Any], design_name: Optional[str] = None) -> Dict[str, Any]:
        similar_runs = self.similarity_engine.find_similar(current_metrics, design_name=design_name)
        total_historical = max(self.repo.count_entries(), 1)

        risk_data = {
            "Timing": {"risk": 0.0, "reason": []},
            "Routing": {"risk": 0.0, "reason": []},
            "DRC": {"risk": 0.0, "reason": []},
            "LVS": {"risk": 0.0, "reason": []},
            "Power": {"risk": 0.0, "reason": []},
        }

        design_class_priors = None
        if design_name:
            cls = self._get_design_class(design_name)
            if cls:
                design_class_priors = DESIGN_CLASS_RISK_PRIORS.get(cls)

        historical_freq = {}
        for f_type in risk_data:
            count = self.repo.count_entries(failure_type=f_type)
            historical_freq[f_type] = count / total_historical

        if not similar_runs:
            for f_type in risk_data:
                base = historical_freq.get(f_type, 0.0) * 100
                if design_class_priors:
                    base = base * 0.5 + design_class_priors.get(f_type, 15.0) * 0.5
                risk_data[f_type]["risk"] = round(base, 2)
            return risk_data

        total_trust = 0.0
        for run in similar_runs:
            trust_weight = run.get("similarity", 0.5)
            total_trust += trust_weight

            failures = self.repo.get_failures_for_run(run["run_id"])
            for f in failures:
                f_type = f.get("failure_type", "UNKNOWN")
                if f_type in risk_data:
                    risk_data[f_type]["risk"] += (100.0 * trust_weight)
                    signature = f.get("signature")
                    if signature and signature not in risk_data[f_type]["reason"]:
                        risk_data[f_type]["reason"].append(signature)

        for f_type in risk_data:
            similar_risk = (risk_data[f_type]["risk"] / total_trust) if total_trust > 0 else 0.0
            freq_risk = historical_freq.get(f_type, 0.0) * 100
            blended = similar_risk * 0.5 + freq_risk * 0.25
            if design_class_priors:
                blended = blended + design_class_priors.get(f_type, 15.0) * 0.25
            else:
                blended = blended + freq_risk * 0.25
            risk_data[f_type]["risk"] = round(blended, 2)

        return risk_data

    def predict_risk_for_type(self, failure_type: str) -> float:
        total = max(self.repo.count_entries(), 1)
        type_count = self.repo.count_entries(failure_type=failure_type)
        freq_risk = type_count / total

        similar = self.repo.search_entries(failure_type=failure_type, limit=50)
        similar_outcomes = 0.0
        for s in similar:
            if s.get("fix_applied"):
                similar_outcomes += 1.0
        similar_risk = (1.0 - similar_outcomes / max(len(similar), 1)) if similar else 0.5

        return round(freq_risk * 0.6 + similar_risk * 0.4, 4)
