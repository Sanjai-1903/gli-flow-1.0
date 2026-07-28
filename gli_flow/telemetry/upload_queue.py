import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

from gli_flow.database.factory import create_provider
from gli_flow.database.database_provider import DatabaseProvider


QUEUE_DB_DIR = Path.home() / ".gli-flow"
QUEUE_DB_PATH = QUEUE_DB_DIR / "upload_queue.db"

QUEUE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS upload_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    next_retry_at TEXT,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    run_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_uq_status ON upload_queue(status);
CREATE INDEX IF NOT EXISTS idx_uq_next_retry ON upload_queue(next_retry_at);
CREATE INDEX IF NOT EXISTS idx_uq_run_id ON upload_queue(run_id);
"""


class UploadQueue:
    def __init__(self, provider=None, db_path: Optional[str] = None):
        if isinstance(provider, DatabaseProvider):
            self._provider = provider
        elif isinstance(provider, str):
            path = provider
            self._provider = create_provider(database_url=None, db_path=path)
        else:
            path = db_path or str(QUEUE_DB_PATH)
            os.makedirs(str(QUEUE_DB_DIR), exist_ok=True)
            self._provider = create_provider(database_url=None, db_path=path)
        self._ensure_table()

    def _ensure_table(self):
        try:
            self._provider.execute("SELECT COUNT(*) FROM upload_queue LIMIT 1")
        except Exception:
            for statement in QUEUE_TABLE_SQL.strip().split(";"):
                stmt = statement.strip()
                if stmt:
                    try:
                        self._provider.execute(stmt)
                    except Exception:
                        pass

    def enqueue(self, destination: str, payload: dict,
                run_id: str = "", status: str = "pending") -> int:
        now = datetime.now(timezone.utc).isoformat()
        payload_json = json.dumps(payload, default=str)
        self._provider.execute(
            """INSERT INTO upload_queue
               (destination, payload, status, created_at, run_id)
               VALUES (?, ?, ?, ?, ?)""",
            (destination, payload_json, status, now, run_id),
        )
        return self._provider.fetchval("SELECT last_insert_rowid()") or 0

    def dequeue(self, limit: int = 10) -> list[dict]:
        now = datetime.now(timezone.utc).isoformat()
        rows = self._provider.fetchall(
            """SELECT * FROM upload_queue
               WHERE status = 'pending'
                  OR (status = 'failed' AND next_retry_at IS NOT NULL AND next_retry_at <= ?)
               ORDER BY created_at ASC
               LIMIT ?""",
            (now, limit),
        )
        ids = [r["id"] for r in rows]
        if ids:
            placeholders = ",".join("?" for _ in ids)
            self._provider.execute(
                f"UPDATE upload_queue SET status = 'in_progress' WHERE id IN ({placeholders})",
                ids,
            )
        return rows

    def mark_completed(self, item_id: int):
        self._provider.execute(
            "UPDATE upload_queue SET status = 'completed' WHERE id = ?",
            (item_id,),
        )

    def mark_failed(self, item_id: int, error_message: str = "",
                    next_retry_at: Optional[str] = None):
        row = self._provider.fetchone(
            "SELECT retry_count FROM upload_queue WHERE id = ?", (item_id,)
        )
        retry_count = (row["retry_count"] if row else 0) + 1
        self._provider.execute(
            """UPDATE upload_queue
               SET status = 'failed', retry_count = ?, error_message = ?, next_retry_at = ?
               WHERE id = ?""",
            (retry_count, error_message[:500], next_retry_at, item_id),
        )

    def flush_completed(self, older_than_hours: int = 24):
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=older_than_hours)).isoformat()
        self._provider.execute(
            "DELETE FROM upload_queue WHERE status = 'completed' AND created_at < ?",
            (cutoff,),
        )

    def get_pending_count(self) -> int:
        return self._provider.fetchval(
            "SELECT COUNT(*) FROM upload_queue WHERE status IN ('pending', 'failed', 'in_progress')"
        ) or 0

    def get_queue_stats(self) -> dict:
        total = self._provider.fetchval("SELECT COUNT(*) FROM upload_queue") or 0
        by_status_rows = self._provider.fetchall(
            "SELECT status, COUNT(*) as cnt FROM upload_queue GROUP BY status"
        )
        by_status = {r["status"]: r["cnt"] for r in by_status_rows}
        by_dest_rows = self._provider.fetchall(
            "SELECT destination, COUNT(*) as cnt FROM upload_queue GROUP BY destination"
        )
        by_destination = {r["destination"]: r["cnt"] for r in by_dest_rows}
        return {
            "total": total,
            "by_status": by_status,
            "by_destination": by_destination,
        }
