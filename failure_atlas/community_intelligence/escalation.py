import dataclasses
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from failure_atlas.ai_assistant.trigger import should_use_ai, AITriggerResult
from failure_atlas.ai_assistant.email_workflow import EmailWorkflow
from failure_atlas.community_intelligence.failure_package import FailurePackageBuilder


ESCALATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS community_escalations (
    id TEXT PRIMARY KEY,
    run_id TEXT DEFAULT '',
    failure_type TEXT NOT NULL,
    tool TEXT DEFAULT '',
    stage TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'open',
    consent_given INTEGER DEFAULT 0,
    consent_timestamp TEXT DEFAULT '',
    bharatcode_submission_id TEXT DEFAULT '',
    bharatcode_status TEXT DEFAULT '',
    ai_summary TEXT DEFAULT '',
    user_notes TEXT DEFAULT '',
    engineer_response TEXT DEFAULT '{}',
    atlas_id_created TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    sent_at TEXT DEFAULT '',
    resolved_at TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_esc_failure_type ON community_escalations(failure_type);
CREATE INDEX IF NOT EXISTS idx_esc_status ON community_escalations(status);
CREATE INDEX IF NOT EXISTS idx_esc_created ON community_escalations(created_at);
"""


@dataclasses.dataclass
class EscalationRecord:
    id: str
    run_id: str
    failure_type: str
    tool: str
    stage: str
    status: str
    consent_given: bool
    consent_timestamp: str
    bharatcode_submission_id: str
    bharatcode_status: str
    ai_summary: str
    user_notes: str
    engineer_response: dict
    atlas_id_created: str
    created_at: str
    sent_at: str
    resolved_at: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class EscalationManager:
    """Manages the lifecycle of failure escalations to GLI engineers."""

    def __init__(self, db_path: Optional[str] = None, api_key: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            from gli_flow.database.migrations import _get_db_path
            self.db_path = _get_db_path()
        self.api_key = api_key
        self._ensure_table()

    def _ensure_table(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(ESCALATION_TABLE_SQL)
        finally:
            conn.close()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_escalation(
        self,
        failure_type: str,
        tool: str = "",
        stage: str = "",
        run_id: str = "",
        ai_summary: str = "",
        user_notes: str = "",
        consent_given: bool = False,
    ) -> str:
        """Create a new escalation record. Returns escalation ID."""
        esc_id = f"ESC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT INTO community_escalations
                (id, run_id, failure_type, tool, stage, status,
                 consent_given, consent_timestamp, ai_summary, user_notes, created_at)
                VALUES (?, ?, ?, ?, ?, 'open', ?, ?, ?, ?, ?)
                """,
                (esc_id, run_id, failure_type, tool, stage,
                 int(consent_given),
                 datetime.now(timezone.utc).isoformat() if consent_given else "",
                 ai_summary, user_notes,
                 datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
            return esc_id
        finally:
            conn.close()

    def submit_escalation(
        self,
        escalation_id: str,
        failure_package: Dict[str, Any],
        consent_given: bool = False,
    ) -> Dict[str, Any]:
        """Submit an escalation via BharatCode email API."""
        if not consent_given:
            return {"status": "error", "message": "User consent required"}

        email = EmailWorkflow(api_key=self.api_key)
        result = email.submit(
            failure_metadata=failure_package.get("failure", {}),
            ai_suggestions=failure_package.get("ai_suggestions", {}),
            consent_given=consent_given,
        )

        conn = self._get_connection()
        try:
            if result.get("status") == "submitted":
                submission_id = result.get("response", {}).get("id", "")
                conn.execute(
                    """
                    UPDATE community_escalations SET
                        status = 'sent',
                        bharatcode_submission_id = ?,
                        bharatcode_status = 'submitted',
                        sent_at = ?,
                        consent_given = ?,
                        consent_timestamp = ?
                    WHERE id = ?
                    """,
                    (submission_id, datetime.now(timezone.utc).isoformat(),
                     int(consent_given),
                     datetime.now(timezone.utc).isoformat() if consent_given else "",
                     escalation_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE community_escalations SET
                        bharatcode_status = ?,
                        user_notes = ?
                    WHERE id = ?
                    """,
                    (f"error: {result.get('message', 'unknown')}",
                     json.dumps(failure_package.get("failure", {})),
                     escalation_id),
                )
            conn.commit()
        finally:
            conn.close()

        return result

    def record_engineer_response(
        self,
        escalation_id: str,
        response: Dict[str, Any],
    ) -> None:
        """Record an engineer's response and knowledge contribution."""
        conn = self._get_connection()
        try:
            conn.execute(
                """
                UPDATE community_escalations SET
                    status = 'resolved',
                    engineer_response = ?,
                    atlas_id_created = ?,
                    resolved_at = ?
                WHERE id = ?
                """,
                (json.dumps(response),
                 response.get("knowledge_contribution", {}).get("atlas_id_assigned", ""),
                 datetime.now(timezone.utc).isoformat(),
                 escalation_id),
            )
            conn.commit()
        finally:
            conn.close()

    def get_escalation(self, escalation_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM community_escalations WHERE id = ?",
                (escalation_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            result = dict(row)
            if isinstance(result.get("engineer_response"), str):
                try:
                    result["engineer_response"] = json.loads(result["engineer_response"])
                except (json.JSONDecodeError, TypeError):
                    result["engineer_response"] = {}
            result["consent_given"] = bool(result.get("consent_given"))
            return result
        finally:
            conn.close()

    def list_escalations(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            if status:
                cursor = conn.execute(
                    "SELECT * FROM community_escalations WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (status, limit, offset),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM community_escalations ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                )
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                if isinstance(d.get("engineer_response"), str):
                    try:
                        d["engineer_response"] = json.loads(d["engineer_response"])
                    except (json.JSONDecodeError, TypeError):
                        d["engineer_response"] = {}
                d["consent_given"] = bool(d.get("consent_given"))
                results.append(d)
            return results
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        conn = self._get_connection()
        try:
            open_count = conn.execute(
                "SELECT COUNT(*) FROM community_escalations WHERE status = 'open'"
            ).fetchone()[0]
            sent_count = conn.execute(
                "SELECT COUNT(*) FROM community_escalations WHERE status = 'sent'"
            ).fetchone()[0]
            resolved_count = conn.execute(
                "SELECT COUNT(*) FROM community_escalations WHERE status = 'resolved'"
            ).fetchone()[0]
            converted = conn.execute(
                "SELECT COUNT(*) FROM community_escalations WHERE atlas_id_created != ''"
            ).fetchone()[0]

            top_unknown = conn.execute(
                """
                SELECT failure_type, COUNT(*) as freq
                FROM community_escalations
                GROUP BY failure_type
                ORDER BY freq DESC
                LIMIT 10
                """
            ).fetchall()

            return {
                "open_count": open_count,
                "sent_count": sent_count,
                "resolved_count": resolved_count,
                "converted_to_signatures": converted,
                "total": open_count + sent_count + resolved_count,
                "top_unknown_failures": [dict(r) for r in top_unknown],
            }
        finally:
            conn.close()


def should_escalate(
    failure_type: str,
    signature: str = "",
    severity: str = "MEDIUM",
    confidence: float = 0.0,
    user_requested: bool = False,
) -> bool:
    """Determine if a failure should be escalated to GLI engineers.

    Escalation is allowed ONLY when:
    - No signature exists (AI trigger says use_ai=True)
    - OR no historical intelligence
    - OR user explicitly requests help

    Must NOT escalate for known signatures.
    """
    if user_requested:
        return True

    trigger = should_use_ai(
        failure_type=failure_type,
        signature=signature,
        severity=severity,
        confidence=confidence,
    )
    return trigger.use_ai
