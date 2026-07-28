import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, Any


TELEMETRY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS community_telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    escalation_id TEXT DEFAULT '',
    failure_type TEXT DEFAULT '',
    tool TEXT DEFAULT '',
    atlas_id TEXT DEFAULT '',
    details TEXT DEFAULT '{}',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ct_event ON community_telemetry(event);
CREATE INDEX IF NOT EXISTS idx_ct_esc ON community_telemetry(escalation_id);
"""


class EscalationTelemetry:
    """Tracks escalation lifecycle events for the Community Intelligence Network."""

    EVENTS = {
        "escalation_created",
        "escalation_sent",
        "escalation_resolved",
        "knowledge_created",
        "signature_created",
        "unknown_failure_detected",
        "ai_investigation_run",
        "failure_atlas_miss",
        "dashboard_view",
    }

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
            conn.executescript(TELEMETRY_TABLE_SQL)
        finally:
            conn.close()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def record(
        self,
        event: str,
        escalation_id: str = "",
        failure_type: str = "",
        tool: str = "",
        atlas_id: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        if event not in self.EVENTS:
            return

        import json
        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT INTO community_telemetry
                (event, escalation_id, failure_type, tool, atlas_id, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (event, escalation_id, failure_type, tool, atlas_id,
                 json.dumps(details or {}),
                 datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
        finally:
            conn.close()

    def get_event_count(self, event: Optional[str] = None) -> int:
        conn = self._get_connection()
        try:
            if event:
                return conn.execute(
                    "SELECT COUNT(*) FROM community_telemetry WHERE event = ?",
                    (event,),
                ).fetchone()[0]
            return conn.execute(
                "SELECT COUNT(*) FROM community_telemetry"
            ).fetchone()[0]
        finally:
            conn.close()

    def get_event_breakdown(self) -> Dict[str, int]:
        conn = self._get_connection()
        try:
            rows = conn.execute(
                "SELECT event, COUNT(*) as cnt FROM community_telemetry GROUP BY event"
            ).fetchall()
            return {row["event"]: row["cnt"] for row in rows}
        finally:
            conn.close()

    def get_events(self, limit: int = 100, offset: int = 0) -> list[dict]:
        conn = self._get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM community_telemetry ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
