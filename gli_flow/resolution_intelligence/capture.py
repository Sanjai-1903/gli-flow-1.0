"""Fix capture — records potential fix relationships when runs recover.

When a run transitions FAILED → PASS/SUCCESS, captures:
- Before: Failure fingerprint from failures on the run
- After: The successful run context
- Relationship: What changed between the two
"""

import json
import logging
from datetime import datetime
from typing import Optional

from gli_flow.resolution_intelligence.models import ResolutionPattern
from gli_flow.resolution_intelligence.repository import ResolutionRepository
from gli_flow.resolution_intelligence.scoring import ResolutionScorer, TrustScorer

logger = logging.getLogger(__name__)


class ResolutionCapture:

    def __init__(self, conn):
        self.repo = ResolutionRepository(conn)
        self.scorer = ResolutionScorer()
        self.trust_scorer = TrustScorer()

    def capture_from_run_recovery(
        self,
        failed_run_id: str,
        successful_run_id: str,
        failure_fingerprint: str,
        failure_type: str,
        resolution: str,
        resolution_type: Optional[str] = None,
        root_cause: Optional[str] = None,
        design_name: Optional[str] = None,
    ) -> Optional[str]:
        """Record a potential fix when a run recovers from failure.

        Called when the pipeline detects a FAILED → PASS transition.
        Links the failure fingerprint to the resolution that apparently fixed it.
        """
        existing = self.repo.find_by_fingerprint(failure_fingerprint)
        for pat in existing:
            if pat.resolution == resolution:
                self.repo.increment_success(pat.id, run_id=successful_run_id, design_name=design_name)
                logger.info(
                    "Incremented success for pattern %s (%s → %s)",
                    pat.id, failure_fingerprint, resolution,
                )
                return pat.id

        pattern = ResolutionPattern(
            id="",
            failure_fingerprint=failure_fingerprint,
            failure_type=failure_type,
            root_cause=root_cause,
            resolution=resolution,
            resolution_type=resolution_type,
            success_count=1,
            failure_count=0,
            confidence=0.0,
            unique_runs=1 if successful_run_id else 0,
            unique_designs=1 if design_name else 0,
            tracked_run_ids=json.dumps([successful_run_id]) if successful_run_id else "[]",
            tracked_design_names=json.dumps([design_name]) if design_name else "[]",
        )
        pattern.confidence = self.scorer.calculate(pattern.success_count, pattern.failure_count)
        pattern_id = self.repo.upsert_pattern(pattern)
        logger.info(
            "Created new resolution pattern %s (%s → %s) with %s runs, %s designs",
            pattern_id, failure_fingerprint, resolution,
            pattern.unique_runs, pattern.unique_designs,
        )
        return pattern_id

    def capture_failed_attempt(
        self,
        failure_fingerprint: str,
        failure_type: str,
        resolution: str,
        root_cause: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> Optional[str]:
        """Record that a resolution attempt failed for this fingerprint."""
        existing = self.repo.find_by_fingerprint(failure_fingerprint)
        for pat in existing:
            if pat.resolution == resolution:
                self.repo.increment_failure(pat.id)
                return pat.id

        pattern = ResolutionPattern(
            id="",
            failure_fingerprint=failure_fingerprint,
            failure_type=failure_type,
            root_cause=root_cause,
            resolution=resolution,
            success_count=0,
            failure_count=1,
            confidence=0.0,
        )
        pattern.confidence = self.scorer.calculate(pattern.success_count, pattern.failure_count)
        pattern_id = self.repo.upsert_pattern(pattern)
        return pattern_id
