import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

from gli_flow.database.factory import create_provider
from gli_flow.database.database_provider import DatabaseProvider


AUDIT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS telemetry_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    event_name TEXT DEFAULT '',
    status TEXT NOT NULL,
    reason TEXT DEFAULT '',
    payload_hash TEXT DEFAULT '',
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tal_event_type ON telemetry_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_tal_status ON telemetry_audit_log(status);
CREATE INDEX IF NOT EXISTS idx_tal_recorded ON telemetry_audit_log(recorded_at);
"""


class TelemetryAuditLog:
    EVENT_CREATED = "event_created"
    EVENT_SANITIZED = "event_sanitized"
    EVENT_UPLOADED = "event_uploaded"
    EVENT_REJECTED = "event_rejected"
    EVENT_EXPORTED = "event_exported"
    EVENT_REPLAYED = "event_replayed"

    def __init__(self, provider=None):
        if isinstance(provider, DatabaseProvider):
            self._provider = provider
        elif isinstance(provider, str):
            self._provider = create_provider(database_url=None, db_path=provider)
        else:
            self._provider = create_provider()
        self._ensure_table()

    def _ensure_table(self):
        try:
            self._provider.execute("SELECT COUNT(*) FROM telemetry_audit_log LIMIT 1")
        except Exception:
            for statement in AUDIT_TABLE_SQL.strip().split(";"):
                stmt = statement.strip()
                if stmt:
                    try:
                        self._provider.execute(stmt)
                    except Exception:
                        pass

    def record(self, event_type: str, event_name: str = "",
               status: str = "success", reason: str = "",
               payload: Optional[dict] = None):
        payload_hash = ""
        if payload:
            payload_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True, default=str).encode()
            ).hexdigest()[:16]
        self._provider.execute(
            """INSERT INTO telemetry_audit_log
               (event_type, event_name, status, reason, payload_hash, recorded_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (event_type, event_name, status, reason, payload_hash,
             datetime.now(timezone.utc).isoformat()),
        )

    def get_logs(self, limit: int = 100, offset: int = 0,
                 event_type: Optional[str] = None) -> list[dict]:
        if event_type:
            return self._provider.fetchall(
                """SELECT * FROM telemetry_audit_log
                   WHERE event_type = ? ORDER BY recorded_at DESC LIMIT ? OFFSET ?""",
                (event_type, limit, offset),
            )
        return self._provider.fetchall(
            """SELECT * FROM telemetry_audit_log
               ORDER BY recorded_at DESC LIMIT ? OFFSET ?""",
            (limit, offset),
        )

    def get_stats(self) -> dict:
        total = self._provider.fetchval("SELECT COUNT(*) FROM telemetry_audit_log") or 0
        by_type_rows = self._provider.fetchall(
            "SELECT event_type, COUNT(*) as cnt FROM telemetry_audit_log GROUP BY event_type"
        )
        by_type = {r["event_type"]: r["cnt"] for r in by_type_rows}
        rejected = self._provider.fetchval(
            "SELECT COUNT(*) FROM telemetry_audit_log WHERE status = 'rejected'"
        ) or 0
        return {
            "total_entries": total,
            "by_event_type": by_type,
            "total_rejected": rejected,
        }
