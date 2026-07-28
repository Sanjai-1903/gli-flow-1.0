import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


RESOLUTION_CAPTURE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ai_resolution_capture (
    id TEXT PRIMARY KEY,
    investigation_id TEXT NOT NULL,
    failure_type TEXT NOT NULL,
    tool TEXT NOT NULL,
    stage TEXT DEFAULT '',
    fix_description TEXT NOT NULL,
    resolution_outcome TEXT DEFAULT '',
    design_name TEXT DEFAULT '',
    pdk TEXT DEFAULT '',
    metrics_before TEXT DEFAULT '{}',
    metrics_after TEXT DEFAULT '{}',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ai_resolution_failure ON ai_resolution_capture(failure_type);
CREATE INDEX IF NOT EXISTS idx_ai_resolution_investigation ON ai_resolution_capture(investigation_id);
"""


class ResolutionCapture:
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
            conn.executescript(RESOLUTION_CAPTURE_TABLE_SQL)
        finally:
            conn.close()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def record_resolution(
        self,
        investigation_id: str,
        failure_type: str,
        tool: str,
        fix_description: str,
        resolution_outcome: str = "",
        stage: str = "",
        design_name: str = "",
        pdk: str = "",
        metrics_before: Optional[Dict[str, Any]] = None,
        metrics_after: Optional[Dict[str, Any]] = None,
    ) -> str:
        entry_id = str(uuid.uuid4())
        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT INTO ai_resolution_capture
                (id, investigation_id, failure_type, tool, stage,
                 fix_description, resolution_outcome, design_name, pdk,
                 metrics_before, metrics_after, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (entry_id, investigation_id, failure_type, tool, stage,
                 fix_description, resolution_outcome, design_name, pdk,
                 json.dumps(metrics_before or {}),
                 json.dumps(metrics_after or {}),
                 datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
            return entry_id
        finally:
            conn.close()

    def get_captured_resolutions(self, failure_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            if failure_type:
                cursor = conn.execute(
                    "SELECT * FROM ai_resolution_capture WHERE failure_type = ? ORDER BY created_at DESC LIMIT ?",
                    (failure_type, limit),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM ai_resolution_capture ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                )
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                for field in ("metrics_before", "metrics_after"):
                    if isinstance(d.get(field), str):
                        try:
                            d[field] = json.loads(d[field])
                        except (json.JSONDecodeError, TypeError):
                            pass
                results.append(d)
            return results
        finally:
            conn.close()

    def get_resolution_count(self) -> int:
        conn = self._get_connection()
        try:
            return conn.execute("SELECT COUNT(*) FROM ai_resolution_capture").fetchone()[0]
        finally:
            conn.close()
