"""Repository for resolution_patterns table — single source of truth.

Tracks what fixes actually solved failures across runs.
"""

import json
import math
import uuid
from datetime import datetime
from typing import Optional

from gli_flow.resolution_intelligence.models import ResolutionPattern, ResolutionFeedback


TABLE_NAME = "resolution_patterns"
FEEDBACK_TABLE = "resolution_feedback"


class ResolutionRepository:

    def __init__(self, conn):
        self.conn = conn

    def upsert_pattern(self, pattern: ResolutionPattern) -> str:
        from gli_flow.resolution_intelligence.scoring import ResolutionScorer, TrustScorer
        now = datetime.utcnow().isoformat()
        if not pattern.id:
            pattern.id = str(uuid.uuid4())
        if not pattern.first_seen:
            pattern.first_seen = now
        pattern.last_seen = now
        pattern.updated_at = now

        scorer = ResolutionScorer()
        pattern.confidence = scorer.calculate(pattern.success_count, pattern.failure_count)

        trust_scorer = TrustScorer()
        trust_result = trust_scorer.calculate_trust(
            success_count=pattern.success_count,
            failure_count=pattern.failure_count,
            unique_runs=pattern.unique_runs,
            unique_designs=pattern.unique_designs,
            last_seen=pattern.last_seen,
            engineer_confirmations=pattern.engineer_confirmations,
            contradictory_reports=pattern.contradictory_reports,
        )
        pattern.trust_score = trust_result["trust_score"]
        pattern.trust_level = trust_result["trust_level"]
        pattern.trust_reason = trust_result["trust_reason"]

        self.conn.execute(
            f"""
            INSERT INTO {TABLE_NAME} (
                id, failure_fingerprint, failure_type, root_cause,
                resolution, resolution_type, success_count, failure_count,
                confidence, first_seen, last_seen, created_at, updated_at,
                unique_runs, unique_designs, engineer_confirmations,
                contradictory_reports, trust_score, trust_level, trust_reason,
                tracked_run_ids, tracked_design_names
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, datetime('now')), ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                success_count = excluded.success_count,
                failure_count = excluded.failure_count,
                confidence = excluded.confidence,
                last_seen = excluded.last_seen,
                updated_at = excluded.updated_at,
                root_cause = COALESCE(NULLIF(excluded.root_cause, ''), resolution_patterns.root_cause),
                resolution_type = COALESCE(NULLIF(excluded.resolution_type, ''), resolution_patterns.resolution_type),
                unique_runs = excluded.unique_runs,
                unique_designs = excluded.unique_designs,
                engineer_confirmations = excluded.engineer_confirmations,
                contradictory_reports = excluded.contradictory_reports,
                trust_score = excluded.trust_score,
                trust_level = excluded.trust_level,
                trust_reason = excluded.trust_reason,
                tracked_run_ids = excluded.tracked_run_ids,
                tracked_design_names = excluded.tracked_design_names
            """,
            (
                pattern.id, pattern.failure_fingerprint, pattern.failure_type,
                pattern.root_cause, pattern.resolution, pattern.resolution_type,
                pattern.success_count, pattern.failure_count,
                pattern.confidence, pattern.first_seen, pattern.last_seen,
                pattern.created_at, pattern.updated_at,
                pattern.unique_runs, pattern.unique_designs,
                pattern.engineer_confirmations, pattern.contradictory_reports,
                pattern.trust_score, pattern.trust_level, pattern.trust_reason,
                pattern.tracked_run_ids, pattern.tracked_design_names,
            ),
        )
        self.conn.commit()
        return pattern.id

    def find_by_fingerprint(self, fingerprint: str) -> list[ResolutionPattern]:
        cursor = self.conn.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE failure_fingerprint = ? ORDER BY confidence DESC, success_count DESC",
            (fingerprint,),
        )
        return [self._row_to_pattern(r) for r in cursor.fetchall()]

    def find_by_failure_type(self, failure_type: str, limit: int = 20) -> list[ResolutionPattern]:
        cursor = self.conn.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE failure_type = ? ORDER BY confidence DESC, success_count DESC LIMIT ?",
            (failure_type, limit),
        )
        return [self._row_to_pattern(r) for r in cursor.fetchall()]

    def find_by_resolution(self, resolution: str, limit: int = 20) -> list[ResolutionPattern]:
        cursor = self.conn.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE resolution LIKE ? ORDER BY confidence DESC LIMIT ?",
            (f"%{resolution}%", limit),
        )
        return [self._row_to_pattern(r) for r in cursor.fetchall()]

    def get_top_resolved(self, limit: int = 10) -> list[ResolutionPattern]:
        cursor = self.conn.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE success_count > 0 ORDER BY trust_score DESC, confidence DESC, success_count DESC LIMIT ?",
            (limit,),
        )
        return [self._row_to_pattern(r) for r in cursor.fetchall()]

    def get_top_unresolved(self, limit: int = 10) -> list[ResolutionPattern]:
        cursor = self.conn.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE success_count = 0 AND failure_count > 0 ORDER BY failure_count DESC LIMIT ?",
            (limit,),
        )
        return [self._row_to_pattern(r) for r in cursor.fetchall()]

    def get_pattern(self, pattern_id: str) -> Optional[ResolutionPattern]:
        cursor = self.conn.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE id = ?",
            (pattern_id,),
        )
        row = cursor.fetchone()
        return self._row_to_pattern(row) if row else None

    def get_timeline(self, fingerprint: str) -> list[dict]:
        cursor = self.conn.execute(
            f"SELECT first_seen, last_seen, success_count, failure_count, confidence, resolution, "
            f"trust_score, trust_level "
            f"FROM {TABLE_NAME} WHERE failure_fingerprint = ? ORDER BY last_seen DESC",
            (fingerprint,),
        )
        return [dict(r) for r in cursor.fetchall()]

    def increment_success(
        self, pattern_id: str,
        run_id: Optional[str] = None,
        design_name: Optional[str] = None,
    ) -> None:
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return
        pattern.success_count += 1

        if run_id:
            tracked = json.loads(pattern.tracked_run_ids or "[]")
            if run_id not in tracked:
                tracked.append(run_id)
                pattern.tracked_run_ids = json.dumps(tracked)
                pattern.unique_runs = len(tracked)

        if design_name:
            tracked_designs = json.loads(pattern.tracked_design_names or "[]")
            if design_name not in tracked_designs:
                tracked_designs.append(design_name)
                pattern.tracked_design_names = json.dumps(tracked_designs)
                pattern.unique_designs = len(tracked_designs)

        self.upsert_pattern(pattern)

    def increment_failure(
        self, pattern_id: str,
        run_id: Optional[str] = None,
    ) -> None:
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return
        pattern.failure_count += 1
        self.upsert_pattern(pattern)

    def record_feedback(
        self, pattern_id: str, run_id: str, feedback_type: str,
        design_name: Optional[str] = None,
    ) -> str:
        feedback_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            f"INSERT INTO {FEEDBACK_TABLE} (id, pattern_id, run_id, feedback_type, created_at) "
            f"VALUES (?, ?, ?, ?, ?)",
            (feedback_id, pattern_id, run_id, feedback_type, now),
        )
        self.conn.commit()

        pattern = self.get_pattern(pattern_id)
        if pattern:
            if feedback_type == "confirmed":
                pattern.success_count += 1
                pattern.engineer_confirmations += 1
                if run_id:
                    tracked = json.loads(pattern.tracked_run_ids or "[]")
                    if run_id not in tracked:
                        tracked.append(run_id)
                        pattern.tracked_run_ids = json.dumps(tracked)
                        pattern.unique_runs = len(tracked)
                if design_name:
                    tracked_designs = json.loads(pattern.tracked_design_names or "[]")
                    if design_name not in tracked_designs:
                        tracked_designs.append(design_name)
                        pattern.tracked_design_names = json.dumps(tracked_designs)
                        pattern.unique_designs = len(tracked_designs)
            else:
                pattern.failure_count += 1
                pattern.contradictory_reports += 1
            self.upsert_pattern(pattern)

        return feedback_id

    def get_feedback(self, pattern_id: str) -> list[ResolutionFeedback]:
        cursor = self.conn.execute(
            f"SELECT * FROM {FEEDBACK_TABLE} WHERE pattern_id = ? ORDER BY created_at DESC",
            (pattern_id,),
        )
        return [ResolutionFeedback(**dict(r)) for r in cursor.fetchall()]

    def get_candidates(self, min_confidence: float = 0.7, min_occurrences: int = 3) -> list:
        cursor = self.conn.execute(
            f"SELECT failure_fingerprint, failure_type, resolution, confidence, "
            f"(success_count + failure_count) AS occurrence_count, "
            f"first_seen, last_seen, trust_score, trust_level, trust_reason "
            f"FROM {TABLE_NAME} "
            f"WHERE confidence >= ? AND (success_count + failure_count) >= ? "
            f"AND NOT EXISTS (SELECT 1 FROM failure_atlas_entries "
            f"  WHERE failure_atlas_entries.signature = resolution_patterns.failure_fingerprint "
            f"  AND failure_atlas_entries.detection_classification = 'VERIFIED') "
            f"ORDER BY trust_score DESC, confidence DESC, occurrence_count DESC",
            (min_confidence, min_occurrences),
        )
        return [dict(r) for r in cursor.fetchall()]

    def get_summary_stats(self) -> dict:
        cursor = self.conn.execute(
            f"SELECT "
            f"COUNT(*) AS total_patterns, "
            f"COALESCE(SUM(success_count), 0) AS total_successes, "
            f"COALESCE(SUM(failure_count), 0) AS total_failures, "
            f"COALESCE(AVG(confidence), 0) AS avg_confidence, "
            f"COALESCE(AVG(trust_score), 0) AS avg_trust_score, "
            f"SUM(CASE WHEN trust_level = 'HIGH' THEN 1 ELSE 0 END) AS high_trust_count, "
            f"SUM(CASE WHEN trust_level = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_trust_count, "
            f"SUM(CASE WHEN trust_level = 'LOW' THEN 1 ELSE 0 END) AS low_trust_count "
            f"FROM {TABLE_NAME}"
        )
        row = dict(cursor.fetchone())
        total = row["total_successes"] + row["total_failures"]
        row["overall_success_rate"] = round(row["total_successes"] / total * 100, 1) if total > 0 else 0.0
        row["avg_confidence"] = round(row["avg_confidence"], 2)
        row["avg_trust_score"] = round(row["avg_trust_score"], 4)
        return row

    def get_trust_summary(self) -> dict:
        cursor = self.conn.execute(
            f"SELECT "
            f"COUNT(*) AS total_patterns, "
            f"SUM(CASE WHEN trust_level = 'HIGH' THEN 1 ELSE 0 END) AS high_count, "
            f"SUM(CASE WHEN trust_level = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_count, "
            f"SUM(CASE WHEN trust_level = 'LOW' THEN 1 ELSE 0 END) AS low_count, "
            f"COALESCE(AVG(trust_score), 0) AS avg_trust_score "
            f"FROM {TABLE_NAME}"
        )
        return dict(cursor.fetchone())

    def _row_to_pattern(self, row) -> ResolutionPattern:
        d = dict(row)
        return ResolutionPattern(
            id=d.get("id", ""),
            failure_fingerprint=d.get("failure_fingerprint", ""),
            failure_type=d.get("failure_type", ""),
            root_cause=d.get("root_cause"),
            resolution=d.get("resolution", ""),
            resolution_type=d.get("resolution_type"),
            success_count=d.get("success_count", 0),
            failure_count=d.get("failure_count", 0),
            confidence=d.get("confidence", 0.0),
            first_seen=d.get("first_seen"),
            last_seen=d.get("last_seen"),
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
            unique_runs=d.get("unique_runs", 0),
            unique_designs=d.get("unique_designs", 0),
            engineer_confirmations=d.get("engineer_confirmations", 0),
            contradictory_reports=d.get("contradictory_reports", 0),
            trust_score=d.get("trust_score", 0.0),
            trust_level=d.get("trust_level", "LOW"),
            trust_reason=d.get("trust_reason", ""),
            tracked_run_ids=d.get("tracked_run_ids", "[]"),
            tracked_design_names=d.get("tracked_design_names", "[]"),
        )
