from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from failure_atlas.repository import FailureAtlasRepository
from failure_atlas.prediction.similarity import ExecutionSimilarityEngine


@dataclass
class PredictionTrainingRecord:
    features: Dict[str, Any]
    target: Dict[str, Any]


class PredictionDatasetBuilder:
    """Builds prediction training datasets from real Failure Atlas records.

    Resolves design_name via repository, computes trust_score from
    confidence and fix_rate, and produces training records
    suitable for GLI-SDI model training.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)
        self.similarity = ExecutionSimilarityEngine(db_path)

    def build(self) -> List[PredictionTrainingRecord]:
        records = []
        entries = self.repo.get_all_failures(limit=1000)
        for entry in entries:
            before = entry.get("before_metrics", {})
            if isinstance(before, str):
                import json
                before = json.loads(before)

            trust_score = entry.get("confidence", 0.5)
            if entry.get("fix_applied"):
                trust_score = min(1.0, trust_score + 0.2)

            records.append(PredictionTrainingRecord(
                features=before,
                target={
                    "outcome": "SUCCESS" if entry.get("fix_applied") else "FAILURE",
                    "failure_type": entry.get("failure_type", "UNKNOWN"),
                    "severity": entry.get("severity", "MEDIUM"),
                    "trust_score": trust_score,
                },
            ))
        return records

    def build_single(self, record) -> PredictionTrainingRecord:
        return PredictionTrainingRecord(
            features=record.telemetry_summary,
            target={"outcome": record.outcome},
        )
