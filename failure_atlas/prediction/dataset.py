from typing import List, Optional
from failure_atlas.repository import FailureAtlasRepository
from failure_atlas.prediction.models import PredictionTrainingRecord


class PredictionDatasetBuilder:
    """Builds prediction training datasets from historical intelligence records.

    Resolves trust_score from actual confidence and fix history,
    design_name from run context, and produces ready-to-use training records.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def build(self) -> List[PredictionTrainingRecord]:
        failures = self.repo.get_all_failures(limit=1000)
        records = []
        for f in failures:
            trust_score = f.get("confidence", 0.5)
            if f.get("fix_applied"):
                trust_score = min(1.0, trust_score + 0.15)
            success_rate_rows = self.repo.get_fix_effectiveness(min_samples=1)
            for row in success_rate_rows:
                if row["failure_type"] == f.get("failure_type", ""):
                    historical_rate = row["success_rate"] / 100.0
                    trust_score = (trust_score + historical_rate) / 2.0
                    break

            records.append(PredictionTrainingRecord(
                run_id=f["run_id"],
                design_name=f.get("design_name", f.get("run_id", "")),
                tool=f.get("tool_name", "UNKNOWN"),
                stage=f.get("tool_stage", "UNKNOWN"),
                telemetry_summary=f.get("before_metrics", {}),
                failure_fingerprint=f.get("signature", "NONE"),
                root_cause=f.get("description", "UNKNOWN"),
                resolution=f.get("fix_description", "NONE"),
                trust_score=round(trust_score, 4),
                outcome="SUCCESS" if f.get("fix_applied") else "FAILURE",
            ))
        return records
