import json
import sqlite3
from typing import Optional, List, Dict, Any


DATASET_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS community_unknown_dataset (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool TEXT NOT NULL,
    failure_type TEXT NOT NULL,
    signature TEXT DEFAULT '',
    frequency INTEGER DEFAULT 1,
    ai_helpfulness TEXT DEFAULT 'unknown',
    resolution_outcome TEXT DEFAULT '',
    consent_given INTEGER DEFAULT 0,
    escalation_id TEXT DEFAULT '',
    last_seen TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ud_failure ON community_unknown_dataset(failure_type);
CREATE INDEX IF NOT EXISTS idx_ud_tool ON community_unknown_dataset(tool);
CREATE INDEX IF NOT EXISTS idx_ud_freq ON community_unknown_dataset(frequency DESC);
"""


class UnknownFailureDataset:
    """Internal dataset of unknown failures.

    This becomes training data for:
    - Future Failure Atlas entries
    - Future GLI-SDI (Supervised Design Intelligence)
    - Future LCM (Lifecycle Management)
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            from gli_flow.database.migrations import _get_db_path
            self.db_path = _get_db_path()
        self._ensure_table()

    def _ensure_table(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(DATASET_TABLE_SQL)
        finally:
            conn.close()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def record_unknown_failure(
        self,
        tool: str,
        failure_type: str,
        signature: str = "",
        ai_helpfulness: str = "unknown",
        consent_given: bool = False,
        escalation_id: str = "",
    ) -> None:
        """Record or increment an unknown failure instance."""
        from datetime import datetime, timezone

        conn = self._get_connection()
        try:
            existing = conn.execute(
                "SELECT id, frequency FROM community_unknown_dataset WHERE tool = ? AND failure_type = ? AND signature = ?",
                (tool, failure_type, signature),
            ).fetchone()

            if existing:
                conn.execute(
                    """
                    UPDATE community_unknown_dataset SET
                        frequency = frequency + 1,
                        last_seen = ?
                    WHERE id = ?
                    """,
                    (datetime.now(timezone.utc).isoformat(), existing["id"]),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO community_unknown_dataset
                    (tool, failure_type, signature, frequency, ai_helpfulness, resolution_outcome,
                     consent_given, escalation_id, last_seen)
                    VALUES (?, ?, ?, 1, ?, '', ?, ?, ?)
                    """,
                    (tool, failure_type, signature, ai_helpfulness,
                     int(consent_given), escalation_id,
                     datetime.now(timezone.utc).isoformat()),
                )
            conn.commit()
        finally:
            conn.close()

    def update_resolution(
        self,
        tool: str,
        failure_type: str,
        signature: str,
        resolution_outcome: str,
    ) -> None:
        conn = self._get_connection()
        try:
            conn.execute(
                """
                UPDATE community_unknown_dataset SET
                    resolution_outcome = ?
                WHERE tool = ? AND failure_type = ? AND signature = ?
                """,
                (resolution_outcome, tool, failure_type, signature),
            )
            conn.commit()
        finally:
            conn.close()

    def update_ai_helpfulness(
        self,
        failure_type: str,
        helpful: bool,
    ) -> None:
        conn = self._get_connection()
        try:
            conn.execute(
                """
                UPDATE community_unknown_dataset SET
                    ai_helpfulness = ?
                WHERE failure_type = ?
                """,
                ("helpful" if helpful else "not_helpful", failure_type),
            )
            conn.commit()
        finally:
            conn.close()

    def get_dataset(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT * FROM community_unknown_dataset
                ORDER BY frequency DESC, last_seen DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                d["consent_given"] = bool(d.get("consent_given"))
                results.append(d)
            return results
        finally:
            conn.close()

    def get_top_unknown(self, limit: int = 10) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT tool, failure_type, SUM(frequency) as total_freq,
                       COUNT(*) as variants
                FROM community_unknown_dataset
                GROUP BY tool, failure_type
                ORDER BY total_freq DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """Return failure types with no resolution outcome recorded."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT failure_type, COUNT(*) as freq
                FROM community_unknown_dataset
                WHERE resolution_outcome = '' OR resolution_outcome IS NULL
                GROUP BY failure_type
                ORDER BY freq DESC
                LIMIT 20
                """
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def export_for_training(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Export dataset suitable for ML training."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT tool, failure_type, signature, frequency,
                       ai_helpfulness, resolution_outcome
                FROM community_unknown_dataset
                ORDER BY frequency DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
