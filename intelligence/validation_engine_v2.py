from typing import List
from intelligence.recommendation_outcome_record import RecommendationOutcomeRecord

class ValidationEngine:
    def __init__(self):
        self.outcomes: List[RecommendationOutcomeRecord] = []
        self.trust_scores: Dict[str, float] = {}

    def track_outcome(self, record: RecommendationOutcomeRecord):
        self.outcomes.append(record)
        # Update trust
        if record.accepted:
            if record.outcome == "SUCCESS":
                self.trust_scores[record.recommendation] = self.trust_scores.get(record.recommendation, 0.5) + 0.1
            else:
                self.trust_scores[record.recommendation] = self.trust_scores.get(record.recommendation, 0.5) - 0.2

    def calculate_effectiveness(self) -> Dict[str, float]:
        accepted = [r for r in self.outcomes if r.accepted]
        successes = [r for r in accepted if r.outcome == "SUCCESS"]
        return {
            "acceptance_rate": len(accepted) / len(self.outcomes) if self.outcomes else 0,
            "success_rate": len(successes) / len(accepted) if accepted else 0
        }
