import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any


FEEDBACK_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ai_investigation_feedback (
    id TEXT PRIMARY KEY,
    investigation_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL,
    resolved BOOLEAN DEFAULT 0,
    comment TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    run_id TEXT DEFAULT '',
    failure_type TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_investigation ON ai_investigation_feedback(investigation_id);
"""


class FeedbackEntry:
    def __init__(
        self,
        investigation_id: str,
        feedback_type: str,
        resolved: bool = False,
        comment: str = "",
        run_id: str = "",
        failure_type: str = "",
    ):
        self.id = str(uuid.uuid4())
        self.investigation_id = investigation_id
        self.feedback_type = feedback_type
        self.resolved = resolved
        self.comment = comment
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.run_id = run_id
        self.failure_type = failure_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "investigation_id": self.investigation_id,
            "feedback_type": self.feedback_type,
            "resolved": self.resolved,
            "comment": self.comment,
            "created_at": self.created_at,
            "run_id": self.run_id,
            "failure_type": self.failure_type,
        }


class FeedbackStore:
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
            conn.executescript(FEEDBACK_TABLE_SQL)
        finally:
            conn.close()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def record_feedback(
        self,
        investigation_id: str,
        feedback_type: str,
        resolved: bool = False,
        comment: str = "",
        run_id: str = "",
        failure_type: str = "",
    ) -> str:
        entry = FeedbackEntry(
            investigation_id=investigation_id,
            feedback_type=feedback_type,
            resolved=resolved,
            comment=comment,
            run_id=run_id,
            failure_type=failure_type,
        )
        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT INTO ai_investigation_feedback
                (id, investigation_id, feedback_type, resolved, comment, created_at, run_id, failure_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (entry.id, entry.investigation_id, entry.feedback_type,
                 int(entry.resolved), entry.comment, entry.created_at,
                 entry.run_id, entry.failure_type),
            )
            conn.commit()
            return entry.id
        finally:
            conn.close()

    def get_feedback_for_investigation(self, investigation_id: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM ai_investigation_feedback WHERE investigation_id = ? ORDER BY created_at DESC",
                (investigation_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_feedback_summary(self, failure_type: Optional[str] = None) -> Dict[str, Any]:
        conn = self._get_connection()
        try:
            base = "SELECT COUNT(*) FROM ai_investigation_feedback"
            params = []
            if failure_type:
                base += " WHERE failure_type = ?"
                params.append(failure_type)
            total = conn.execute(base, params).fetchone()[0]

            helpful = conn.execute(
                "SELECT COUNT(*) FROM ai_investigation_feedback WHERE feedback_type = 'helpful'",
            ).fetchone()[0]

            resolved = conn.execute(
                "SELECT COUNT(*) FROM ai_investigation_feedback WHERE resolved = 1",
            ).fetchone()[0]

            return {
                "total_feedback": total,
                "helpful_count": helpful,
                "resolved_count": resolved,
            }
        finally:
            conn.close()
