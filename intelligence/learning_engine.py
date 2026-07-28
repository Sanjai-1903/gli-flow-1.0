from typing import Dict, Optional
from failure_atlas.repository import FailureAtlasRepository


class ContinuousLearningEngine:
    """Updates frequencies, trust scores, and risk statistics from actual outcomes.

    Reads from FailureAtlasRepository (SQLite-backed) to compute:
    - Failure type frequencies
    - Fix success rates per type
    - Risk statistics derived from historical outcomes
    """

    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)
        self.risk_stats: Dict[str, float] = {}
        self.fix_success_rates: Dict[str, float] = {}
        self.frequencies: Dict[str, int] = {}

    def update_statistics(self):
        total = max(self.repo.count_entries(), 1)

        common = self.repo.get_common_failures(limit=50)
        self.frequencies = {row["failure_type"]: row["count"] for row in common}

        effective = self.repo.get_fix_effectiveness(min_samples=1)
        self.fix_success_rates = {
            row["failure_type"]: row["success_rate"] / 100.0
            for row in effective
        }

        for f_type, count in self.frequencies.items():
            freq = count / total
            success_rate = self.fix_success_rates.get(f_type, 0.5)
            self.risk_stats[f_type] = round(freq * (1.0 - success_rate) * 100, 4)

        uncounted = self.repo.count_entries()
        for row in common:
            f_type = row["failure_type"]
            self.risk_stats[f_type] = self.risk_stats.get(f_type, 0.0)

    def get_risk_stats(self) -> Dict[str, float]:
        return self.risk_stats

    def get_frequencies(self) -> Dict[str, int]:
        return self.frequencies

    def get_fix_success_rates(self) -> Dict[str, float]:
        return self.fix_success_rates

    def get_trust_scores(self) -> Dict[str, float]:
        scores = {}
        for f_type in self.frequencies:
            count = self.frequencies[f_type]
            success_rate = self.fix_success_rates.get(f_type, 0.5)
            sample_factor = min(1.0, count / 20.0)
            scores[f_type] = round(success_rate * 0.7 + sample_factor * 0.3, 4)
        return scores
