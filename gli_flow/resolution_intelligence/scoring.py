"""Resolution confidence and trust scoring engines.

Calculates confidence based on historical success/failure data (statistical)
and trust based on engineering-relevant factors (breadth, recency, confirmations).
"""

import math
from datetime import datetime
from typing import Optional


class ResolutionScorer:

    MIN_SAMPLES = 3
    DEFAULT_CONFIDENCE = 0.0

    def calculate(self, success_count: int, failure_count: int) -> float:
        """Calculate resolution confidence as a percentage.

        Uses Bayesian-inspired smoothing to avoid overconfidence
        on very small sample sizes.

        Formula:
            confidence = (success_count + 1) / (success_count + failure_count + 2)

        This gives:
        - 0/0 → 0.50 (uncertain, no data)
        - 1/0 → 0.67 (1 success, 0 failures)
        - 5/0 → 0.86 (5 successes, 0 failures)
        - 18/2 → 0.86 (18 successes, 2 failures)
        - 0/5 → 0.14 (0 successes, 5 failures)
        """
        total = success_count + failure_count
        if total == 0:
            return self.DEFAULT_CONFIDENCE
        confidence = (success_count + 1) / (total + 2)
        return round(confidence, 4)

    def get_confidence_label(self, confidence: float) -> str:
        if confidence >= 0.80:
            return "HIGH"
        elif confidence >= 0.50:
            return "MEDIUM"
        else:
            return "LOW"

    def is_reliable(self, confidence: float, total_attempts: int) -> bool:
        return confidence >= 0.70 and total_attempts >= self.MIN_SAMPLES


class TrustScorer:
    """Evaluates how much an engineer should trust a resolution recommendation.

    Trust is calculated from 7 factors:
      1. Base confidence — statistical success rate (weight: 35%)
      2. Unique runs — breadth across different run contexts (weight: 15%)
      3. Unique designs — cross-design applicability (weight: 10%)
      4. Recency — how recently the resolution was confirmed (weight: 10%)
      5. Engineer confirmations — explicit YES from engineers (weight: 15%)
      6. Contradictory evidence — explicit NO or failed attempts (penalty: 15%)
      7. Run similarity — consistency of run characteristics (reserved, neutral in v1)
    """

    def calculate_trust(
        self,
        success_count: int,
        failure_count: int,
        unique_runs: int = 0,
        unique_designs: int = 0,
        last_seen: Optional[str] = None,
        engineer_confirmations: int = 0,
        contradictory_reports: int = 0,
    ) -> dict:
        """Compute trust score, level, and explanation string.

        Returns:
            dict with keys: trust_score (0.0-1.0), trust_level (HIGH/MEDIUM/LOW),
            trust_reason (human-readable string)
        """
        # 1. Base confidence (statistical)
        scorer = ResolutionScorer()
        base_confidence = scorer.calculate(success_count, failure_count)

        # 2. Unique runs breadth (0.0 - 1.0)
        runs_bonus = min(1.0, math.sqrt(unique_runs) / math.sqrt(20)) if unique_runs > 0 else 0.0

        # 3. Unique designs breadth (0.0 - 1.0)
        designs_bonus = min(1.0, unique_designs / 10) if unique_designs > 0 else 0.0

        # 4. Recency — linear decay over 90 days (0.0 - 1.0)
        recency_bonus = 0.0
        if last_seen:
            try:
                last = datetime.fromisoformat(last_seen)
                days_since = (datetime.utcnow() - last).days
                recency_bonus = max(0.0, 1.0 - days_since / 90.0)
            except (ValueError, TypeError):
                recency_bonus = 0.0

        # 5. Engineer confirmations (0.0 - 1.0, diminishing returns at sqrt scale)
        engineer_bonus = min(1.0, math.sqrt(engineer_confirmations) / math.sqrt(5))

        # 6. Contradiction penalty (0.0 - 1.0)
        total_feedback = engineer_confirmations + contradictory_reports
        if total_feedback > 0:
            contradiction_ratio = contradictory_reports / total_feedback
            contradiction_penalty = contradiction_ratio * min(1.0, contradictory_reports / 3.0)
        else:
            contradiction_penalty = 0.0

        # Weighted combination (weights sum to 1.0 for positive factors)
        trust_score = (
            base_confidence * 0.35
            + runs_bonus * 0.15
            + designs_bonus * 0.10
            + recency_bonus * 0.10
            + engineer_bonus * 0.15
            - contradiction_penalty * 0.15
        )

        trust_score = max(0.0, min(1.0, round(trust_score, 4)))

        # Trust level
        if trust_score >= 0.80:
            trust_level = "HIGH"
        elif trust_score >= 0.50:
            trust_level = "MEDIUM"
        else:
            trust_level = "LOW"

        # Human-readable reason
        trust_reason = self._build_reason(
            trust_level, success_count, failure_count,
            unique_runs, unique_designs, recency_bonus,
            engineer_confirmations, contradictory_reports,
        )

        return {
            "trust_score": trust_score,
            "trust_level": trust_level,
            "trust_reason": trust_reason,
        }

    def _build_reason(
        self,
        level: str,
        success_count: int,
        failure_count: int,
        unique_runs: int,
        unique_designs: int,
        recency_bonus: float,
        engineer_confirmations: int,
        contradictory_reports: int,
    ) -> str:
        parts = []
        total = success_count + failure_count

        if total == 0:
            parts.append("No data available")
        else:
            parts.append(f"{total} attempt{'s' if total != 1 else ''} ({success_count} ok, {failure_count} fail)")

        if unique_runs > 0:
            parts.append(f"across {unique_runs} run{'s' if unique_runs != 1 else ''}")
        if unique_designs > 0:
            parts.append(f"{unique_designs} design{'s' if unique_designs != 1 else ''}")

        if engineer_confirmations > 0:
            parts.append(f"confirmed by {engineer_confirmations} engineer{'s' if engineer_confirmations != 1 else ''}")
        if contradictory_reports > 0:
            parts.append(f"{contradictory_reports} contradiction{'s' if contradictory_reports != 1 else ''}")

        if recency_bonus >= 0.8:
            parts.append("recently active")
        elif recency_bonus <= 0.1 and total > 0:
            parts.append("last seen long ago")

        if level == "HIGH":
            base = "Strong evidence — "
        elif level == "MEDIUM":
            base = "Moderate evidence — "
        else:
            base = "Limited evidence — "

        return base + ", ".join(parts) + "."
