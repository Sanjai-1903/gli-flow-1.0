from typing import Dict, Any, Optional
from failure_atlas.repository import FailureAtlasRepository


class YieldAnalyzer:
    def calculate_yield(self, collected: int, uploaded: int) -> float:
        return round(uploaded / collected, 4) if collected > 0 else 0.0


class AtlasCoverageAnalyzer:
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def calculate_coverage(self, known: int, unknown: int) -> float:
        total = known + unknown
        if total == 0:
            stats = self.repo.get_statistics()
            return round(min(1.0, stats.get("total_entries", 0) / 100.0), 4)
        return round(known / total, 4)


class IntelligenceQualityEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)

    def calculate_score(self, record: Dict[str, Any]) -> float:
        stats = self.repo.get_statistics()
        total = stats.get("total_entries", 0)
        if total == 0:
            return 0.0
        fix_rate = stats.get("fix_rate", 50.0) / 100.0
        sample_quality = min(1.0, total / 200.0)
        return round(fix_rate * 0.5 + sample_quality * 0.5, 4)
