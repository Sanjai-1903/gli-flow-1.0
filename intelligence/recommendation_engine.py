from typing import Dict, Any, List, Optional
from intelligence.recommendation_record import RecommendationRecord
from intelligence.warehouse import TelemetryWarehouse
from failure_atlas.repository import FailureAtlasRepository
from gli_flow.resolution_intelligence.repository import ResolutionRepository
from gli_flow.resolution_intelligence.scoring import ResolutionScorer, TrustScorer
from gli_flow.database.migrations import _get_db_path
import sqlite3

DESIGN_CLASS_RECOMMENDATION_TEMPLATES = {
    "CPU": [
        "Optimize clock frequency for critical control paths",
        "Check branch predictor and pipeline stall logic",
        "Review register file power and timing",
    ],
    "DSP": [
        "Optimize multiply-accumulate chain timing",
        "Check bit-width truncation for area savings",
        "Review pipeline balancing in datapath",
    ],
    "Accelerator": [
        "Optimize data movement between compute and memory",
        "Check weight stationary vs. dataflow architecture",
        "Review systolic array timing closure",
    ],
    "Memory-heavy": [
        "Check SRAM macro placement and aspect ratio",
        "Review memory BIST and repair logic",
        "Optimize memory power gating",
    ],
    "Controller": [
        "Optimize FSM encoding for area",
        "Check reset and enable tree timing",
        "Review control path vs. datapath partitioning",
    ],
    "Interconnect": [
        "Optimize bus width for throughput",
        "Check crossbar arbitration logic",
        "Review I/O pad placement and ESD protection",
    ],
}


class RecommendationEngine:
    def __init__(self, warehouse: Optional[TelemetryWarehouse] = None):
        self.warehouse = warehouse or TelemetryWarehouse()
        self.repo = FailureAtlasRepository()
        conn = sqlite3.connect(_get_db_path())
        self.resolution_repo = ResolutionRepository(conn)
        self.scorer = ResolutionScorer()
        self.trust_scorer = TrustScorer()

    def get_design_class_recommendations(self, design_name: str) -> List[str]:
        try:
            conn = sqlite3.connect(_get_db_path())
            row = conn.execute(
                "SELECT classification FROM design_profiles WHERE design_name = ?",
                (design_name,)
            ).fetchone()
            conn.close()
            if row and row[0]:
                return DESIGN_CLASS_RECOMMENDATION_TEMPLATES.get(row[0], DESIGN_CLASS_RECOMMENDATION_TEMPLATES["Controller"])
        except Exception:
            pass
        return DESIGN_CLASS_RECOMMENDATION_TEMPLATES["Controller"]

    def get_recommendation(self, failure_type: str) -> RecommendationRecord:
        patterns = self.resolution_repo.find_by_failure_type(failure_type, limit=5)
        if patterns:
            best = patterns[0]
            total = best.success_count + best.failure_count
            success_rate = best.success_count / total if total > 0 else 0.0
            return RecommendationRecord(
                failure=failure_type,
                root_cause=best.root_cause or "Unknown",
                recommended_fix=best.resolution,
                historical_success_rate=round(success_rate, 4),
                trust_score=best.trust_score,
                outcome="SUCCESS" if best.success_count > best.failure_count else "PENDING",
            )

        similar = self.repo.similar_failures(failure_type)
        if similar:
            best = similar[0]
            return RecommendationRecord(
                failure=failure_type,
                root_cause="Derived from similar failures",
                recommended_fix=best.get("fix_type", "Manual Review"),
                historical_success_rate=best.get("success_rate", 0.0) / 100.0,
                trust_score=0.6,
                outcome="SUCCESS" if best.get("success_rate", 0) > 50 else "PENDING",
            )

        successes = self.warehouse.get_successful_recommendations(failure_type)
        if successes:
            from collections import Counter
            fixes = Counter([r.recommendation for r in successes])
            best_fix = fixes.most_common(1)[0][0]
            return RecommendationRecord(failure_type, "Known", best_fix, 1.0, 1.0, "SUCCESS")

        return RecommendationRecord(failure_type, "UNKNOWN", "Manual Review", 0.0, 0.0, "PENDING")

    def get_recommendations_by_evidence(self, failure_type: str) -> List[Dict[str, Any]]:
        similar = self.repo.similar_failures(failure_type, limit=10)
        results = []
        for s in similar:
            success_rate = s.get("success_rate", 0) / 100.0
            sample_size = s.get("sample_size", 0)
            trust = self.trust_scorer.calculate_trust(
                success_count=int(success_rate * sample_size),
                failure_count=sample_size - int(success_rate * sample_size),
                unique_runs=sample_size,
                unique_designs=max(1, sample_size // 3),
            )
            results.append({
                "fix_type": s.get("fix_type", "Unknown"),
                "success_rate": success_rate,
                "sample_size": sample_size,
                "trust_score": trust["trust_score"],
                "trust_level": trust["trust_level"],
                "trust_reason": trust["trust_reason"],
            })
        return results

    def explain(self, rec: RecommendationRecord) -> str:
        return (
            f"Fix '{rec.recommended_fix}' is recommended because it successfully resolved "
            f"{rec.failure} in previous runs "
            f"(success rate: {rec.historical_success_rate:.0%}, "
            f"trust: {rec.trust_score:.2f})."
        )
