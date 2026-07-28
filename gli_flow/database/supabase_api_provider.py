import os
import json
import time
import urllib.request
import urllib.error

from gli_flow.database.database_provider import DatabaseProvider


class SupabaseApiProvider(DatabaseProvider):
    """DatabaseProvider that routes SQL through the Supabase Management API.

    Uses the /v1/projects/{ref}/database/query endpoint with a personal
    access token.  Bypasses the need for direct PostgreSQL connectivity.
    """

    def __init__(self, project_ref: str, api_token: str):
        self._project_ref = project_ref
        self._api_token = api_token
        self._base = "https://api.supabase.com/v1"
        self._connected = True

    @staticmethod
    def _escape(val) -> str:
        if val is None:
            return "NULL"
        if isinstance(val, bool):
            return "TRUE" if val else "FALSE"
        if isinstance(val, (int, float)):
            return str(val)
        if isinstance(val, str):
            return "'" + val.replace("'", "''") + "'"
        return "'" + json.dumps(val, default=str).replace("'", "''") + "'"

    def _query(self, sql: str, params: tuple = ()) -> list:
        import re
        if params:
            param_list = list(params)
            i = 0
            def replacer(m):
                nonlocal i
                if i >= len(param_list):
                    return m.group(0)
                val = self._escape(param_list[i])
                i += 1
                return val
            sql = re.sub(r"\?|%s", replacer, sql)

        body = json.dumps({"query": sql}).encode()
        req = urllib.request.Request(
            f"{self._base}/projects/{self._project_ref}/database/query",
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_token}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Origin": "https://supabase.com",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                return data if isinstance(data, list) else [data]
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"API error {e.code}: {body[:300]}") from e

    def connect(self):
        self._connected = True

    def disconnect(self):
        self._connected = False

    def close(self):
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def execute(self, sql: str, params: tuple = ()):
        self._query(sql, params)

    def fetchone(self, sql: str, params: tuple = ()) -> dict | None:
        rows = self._query(sql, params)
        if rows and len(rows) > 0:
            return rows[0]
        return None

    def fetchall(self, sql: str, params: tuple = ()) -> list[dict]:
        return self._query(sql, params)

    def fetchval(self, sql: str, params: tuple = (), column: int = 0):
        row = self.fetchone(sql, params)
        if row:
            vals = list(row.values())
            if column < len(vals):
                return vals[column]
            return vals[0]
        return None

    def commit(self):
        pass

    def rollback(self):
        pass

    def migrate(self):
        pass

    def validate_schema(self) -> list[str]:
        rows = self.fetchall(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        return [r["table_name"] for r in rows]

    def __repr__(self):
        return f"<SupabaseApiProvider project={self._project_ref}>"
