import json
import os
from typing import Any, Dict, List, Optional
from contextlib import contextmanager
from threading import local

from gli_flow.database.database_provider import DatabaseProvider, Row


_thread_local = local()


def _get_pg_module():
    try:
        import psycopg2
        import psycopg2.extras
        return psycopg2, psycopg2.extras, None
    except ImportError:
        pass
    try:
        import psycopg
        return psycopg, psycopg, None
    except ImportError:
        pass
    raise ImportError(
        "Neither psycopg2 nor psycopg (3) is installed. "
        "Install one: pip install psycopg2-binary"
    )


class PostgresProvider(DatabaseProvider):
    def __init__(self, database_url: Optional[str] = None, min_connections: int = 1, max_connections: int = 5):
        self.database_url = database_url or os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL must be set for PostgresProvider. "
                "Set it via constructor or DATABASE_URL environment variable."
            )
        self._conn = None
        self._params_style = "pyformat"
        self._min_connections = min_connections
        self._max_connections = max_connections
        self._pool = None

    def _get_pool(self):
        if self._pool is None:
            psycopg2, extras, _ = _get_pg_module()
            try:
                from psycopg2 import pool as pg_pool
                self._pool = pg_pool.ThreadedConnectionPool(
                    self._min_connections,
                    self._max_connections,
                    self.database_url,
                )
            except (ImportError, AttributeError):
                pass
        return self._pool

    def _get_conn(self):
        pool = self._get_pool()
        if pool:
            return pool.getconn()
        if self._conn is None or self._conn.closed:
            self.connect()
        return self._conn

    def _put_conn(self, conn):
        pool = self._get_pool()
        if pool:
            pool.putconn(conn)

    def connect(self) -> None:
        psycopg2, extras, _ = _get_pg_module()
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self.database_url)
            self._conn.autocommit = False

    def disconnect(self) -> None:
        if self._pool:
            self._pool.closeall()
            self._pool = None
        if self._conn and not self._conn.closed:
            self._conn.close()
            self._conn = None

    def close(self) -> None:
        self.disconnect()

    def _normalize_params(self, params: Optional[Dict[str, Any]] = None):
        if params is None:
            return ()
        if isinstance(params, (list, tuple)):
            return params
        return params

    def execute(self, sql: str, params: Optional[Dict[str, Any]] = None) -> None:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, self._normalize_params(params))
            conn.commit()
        finally:
            self._put_conn(conn)

    def _row_to_dict(self, row, cursor) -> Row:
        if row is None:
            return None
        return Row(zip([d[0] for d in cursor.description], row))

    def fetchone(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Row]:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, self._normalize_params(params))
                row = cur.fetchone()
                if row is None:
                    return None
                return Row(zip([d[0] for d in cur.description], row))
        finally:
            self._put_conn(conn)

    def fetchall(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Row]:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, self._normalize_params(params))
                rows = cur.fetchall()
                if not rows:
                    return []
                cols = [d[0] for d in cur.description]
                return [Row(zip(cols, row)) for row in rows]
        finally:
            self._put_conn(conn)

    def fetchval(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, self._normalize_params(params))
                row = cur.fetchone()
                return row[0] if row else None
        finally:
            self._put_conn(conn)

    def commit(self) -> None:
        conn = self._get_conn()
        try:
            conn.commit()
        finally:
            self._put_conn(conn)

    def rollback(self) -> None:
        conn = self._get_conn()
        try:
            conn.rollback()
        finally:
            self._put_conn(conn)

    def migrate(self) -> None:
        from gli_flow.database.pg_migrations import PGMigrationEngine
        engine = PGMigrationEngine(self.database_url)
        engine.migrate()

    def validate_schema(self) -> bool:
        from gli_flow.database.pg_migrations import PGMigrationEngine
        engine = PGMigrationEngine(self.database_url)
        try:
            return engine.validate_all_tables()
        finally:
            engine.close()

    @property
    def is_connected(self) -> bool:
        if self._conn:
            try:
                cur = self._conn.cursor()
                cur.execute("SELECT 1")
                cur.close()
                return True
            except Exception:
                return False
        return False
