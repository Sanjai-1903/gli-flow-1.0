"""Atlas candidate generation — promotes high-confidence patterns to Failure Atlas.

If an unknown failure has been seen many times and the same resolution
repeatedly succeeds, creates a Failure Atlas candidate for engineer review.
Never auto-promotes — always requires human review.
"""

import json
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class AtlasCandidateGenerator:

    def __init__(self, conn):
        self.conn = conn

    def generate_candidates(self, min_confidence: float = 0.75, min_occurrences: int = 3) -> list[dict]:
        """Find high-confidence resolution patterns not yet in Failure Atlas.

        Returns candidates that need engineer review before promotion.
        """
        from gli_flow.resolution_intelligence.repository import ResolutionRepository
        repo = ResolutionRepository(self.conn)
        return repo.get_candidates(
            min_confidence=min_confidence,
            min_occurrences=min_occurrences,
        )

    def promote_to_atlas(self, candidate: dict, reviewer_notes: str = "") -> Optional[str]:
        """Promote a resolution candidate to a Failure Atlas entry.

        Requires explicit engineer action — never auto-promotes.
        """
        from failure_atlas.repository import FailureAtlasRepository

        repo = FailureAtlasRepository()
        try:
            entry_id = repo.insert_entry({
                "run_id": "",
                "failure_type": candidate.get("failure_type", "UNKNOWN"),
                "severity": "MEDIUM",
                "title": f"Resolution Candidate: {candidate.get('resolution', '')[:80]}",
                "description": (
                    f"Auto-detected resolution pattern:\n"
                    f"Resolution: {candidate.get('resolution', '')}\n"
                    f"Confidence: {candidate.get('confidence', 0):.0%}\n"
                    f"Occurrences: {candidate.get('occurrence_count', 0)}\n"
                    f"First seen: {candidate.get('first_seen', '')}\n"
                    f"Last seen: {candidate.get('last_seen', '')}\n"
                    f"Reviewer notes: {reviewer_notes}"
                ),
                "recommended_fix": candidate.get("resolution", ""),
                "confidence": min(candidate.get("confidence", 0.5), 1.0),
                "signature": candidate.get("failure_fingerprint", ""),
                "domain": candidate.get("failure_type", "").split("_")[0] if "_" in candidate.get("failure_type", "") else "",
                "category": "resolution_candidate",
                "evidence": json.dumps({
                    "source": "resolution_intelligence",
                    "occurrence_count": candidate.get("occurrence_count", 0),
                    "confidence": candidate.get("confidence", 0),
                    "reviewer_notes": reviewer_notes,
                }),
                "detected_at": datetime.utcnow().isoformat(),
                "entry_level": "WARNING",
                "detection_classification": "HEURISTIC",
            })
            logger.info("Promoted candidate to Failure Atlas entry %s: %s", entry_id, candidate.get("resolution", ""))
            return entry_id
        finally:
            repo.close()
