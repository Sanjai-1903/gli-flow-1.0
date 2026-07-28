from typing import List
from intelligence.recommendation_record import RecommendationRecord

class ResolutionRankingEngine:
    def rank_fixes(self, recommendations: List[RecommendationRecord]) -> List[RecommendationRecord]:
        # Rank by historical success rate and trust score
        return sorted(
            recommendations, 
            key=lambda x: (x.historical_success_rate * 0.7 + x.trust_score * 0.3), 
            reverse=True
        )
