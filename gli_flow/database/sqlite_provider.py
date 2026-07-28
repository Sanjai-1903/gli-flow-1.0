import sqlite3
from typing import Any, Dict, List, Optional

from gli_flow.database.database_provider import DatabaseProvider, Row
from gli_flow.database.migrations import _get_db_path, migrate_if_needed, MigrationEngine


class SQLiteProvider(DatabaseProvider):
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or _get_db_path()
        self._conn: Optional[sqlite3.Connection] = None
        self._last_cursor = None
        self._params_style = "qmark"

    def connect(self) -> None:
        if self._conn is not None:
            return
        migrate_if_needed(self.db_path)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        try:
            self._conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.OperationalError:
            self._conn.close()
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row

    def disconnect(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def close(self) -> None:
        self.disconnect()

    def _ensure_connected(self):
        if self._conn is None:
            self.connect()

    def _normalize_params(self, params: Optional[Dict[str, Any]] = None):
        if params is None:
            return ()
        if isinstance(params, dict):
            return params
        return params

    def execute(self, sql: str, params: Optional[Dict[str, Any]] = None) -> None:
        self._ensure_connected()
        self._last_cursor = self._conn.execute(sql, self._normalize_params(params))
        self._conn.commit()

    @property
    def rowcount(self) -> int:
        if self._last_cursor is not None:
            return self._last_cursor.rowcount
        return -1

    def fetchone(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Row]:
        self._ensure_connected()
        cursor = self._conn.execute(sql, self._normalize_params(params))
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetchall(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Row]:
        self._ensure_connected()
        cursor = self._conn.execute(sql, self._normalize_params(params))
        return [dict(row) for row in cursor.fetchall()]

    def fetchval(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        self._ensure_connected()
        cursor = self._conn.execute(sql, self._normalize_params(params))
        row = cursor.fetchone()
        return row[0] if row else None

    def commit(self) -> None:
        self._ensure_connected()
        self._conn.commit()

    def rollback(self) -> None:
        self._ensure_connected()
        self._conn.rollback()

    def migrate(self) -> None:
        migrate_if_needed(self.db_path)

    def validate_schema(self) -> bool:
        engine = MigrationEngine(self.db_path)
        try:
            ok, _ = engine.validate_runtime_schema()
            return ok
        finally:
            engine.close()

    @property
    def is_connected(self) -> bool:
        return self._conn is not None
