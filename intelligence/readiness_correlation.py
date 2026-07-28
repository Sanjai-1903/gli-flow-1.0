from typing import Dict, Any, Optional
from failure_atlas.repository import FailureAtlasRepository


class ReadinessCorrelationEngine:
    """Correlates telemetry metrics with readiness outcomes using real Failure Atlas data."""

    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def correlate(self, telemetry: Dict[str, Any], readiness_data: Dict[str, Any]) -> Dict[str, Any]:
        wns = telemetry.get("wns", 0.0)
        tns = telemetry.get("tns", 0.0)
        utilization = telemetry.get("utilization", 50)

        stats = self.repo.get_statistics()
        fix_rate = stats.get("fix_rate", 50.0) / 100.0
        total = stats.get("total_entries", 0)

        readiness_score = readiness_data.get("TapeoutReady", 0)
        timing_sensitivity = abs(wns) * 10 if wns and wns < 0 else 0
        congestion_risk = utilization / 100.0 if utilization > 70 else 0

        correlation = {
            "readiness_score": readiness_score,
            "fix_rate_context": fix_rate,
            "total_entries_context": total,
            "timing_sensitivity": round(timing_sensitivity, 2),
            "congestion_risk": round(congestion_risk, 2),
            "telemetry_readiness_gap": round(
                max(0, timing_sensitivity + congestion_risk * 50 - readiness_score), 2
            ),
            "evidence_based_adjustment": round(
                readiness_score * (0.7 + 0.3 * fix_rate), 2
            ),
        }
        return correlation
