from typing import Dict, Optional
from failure_atlas.repository import FailureAtlasRepository


class PredictionReadinessEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def compute_score(self, metrics: Dict[str, float]) -> float:
        stats = self.repo.get_statistics()
        total = stats.get("total_entries", 0)
        if total == 0:
            return 0.0
        fix_rate = stats.get("fix_rate", 50.0)
        num_types = self.repo.get_common_failures(limit=100)
        type_coverage = min(100.0, len(num_types) * 10.0)
        score = fix_rate * 0.5 + type_coverage * 0.3 + min(100.0, total) * 0.2
        return round(min(100.0, score), 2)


def generate_calibration_report():
    print("Generating Prediction Calibration Report...")
    repo = FailureAtlasRepository()
    stats = repo.get_statistics()
    common = repo.get_common_failures(limit=10)
    print(f"  Total entries: {stats.get('total_entries', 0)}")
    print(f"  Fix rate: {stats.get('fix_rate', 0)}%")
    print(f"  Failure type coverage: {len(common)} types")
    print("Calibration report generated.")
