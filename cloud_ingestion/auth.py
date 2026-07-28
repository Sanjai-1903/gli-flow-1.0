"""Bearer token authentication for the ingest server.

Tokens are issued by the web app and stored in public.user_cli_tokens with a
SHA-256 hash (never plaintext). The ingest server:

    1. Reads Authorization: Bearer <token> from the request
    2. Hashes the token
    3. Looks it up in user_cli_tokens
    4. Confirms it isn't revoked
    5. Bumps last_used_at
    6. Returns the associated user_id

If auth is disabled (dev mode), returns a fixed dev user_id so uploads still
work locally without needing Supabase.
"""

from __future__ import annotations

import hashlib
import logging
import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)


# Same UUID the Phase 1 migration used for the legacy placeholder user.
DEV_USER_ID = os.environ.get(
    "GLI_DEV_USER_ID",
    "00000000-0000-0000-0000-000000000001",
)

TOKEN_PREFIX = "gfp_"  # gli-flow personal token, printed in the CLI


def hash_token(raw_token: str) -> str:
    """Hash a raw token with SHA-256. This is what we store in the DB."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def extract_bearer(request: Request) -> Optional[str]:
    """Extract the raw Bearer token from an incoming request, or None."""
    header = request.headers.get("Authorization", "")
    if not header.lower().startswith("bearer "):
        return None
    return header.split(" ", 1)[1].strip() or None


class TokenValidator:
    """Validates Bearer tokens against user_cli_tokens.

    Works against both Postgres (production) and SQLite (dev). The SQLite
    path is only for local dev — in that case we usually run with
    auth.enabled=False and skip validation entirely.
    """

    def __init__(self, config):
        self.config = config
        self._backend = (
            "postgres"
            if config.database.url.startswith(("postgresql://", "postgres://"))
            else "sqlite"
        )

    def _pg(self):
        import psycopg2
        return psycopg2.connect(self.config.database.url)

    def _sq(self):
        # Dev mode SQLite path (same as IngestionDatabase). We create the
        # table if missing so `gli-flow login --token ...` can be tested
        # against a local server too.
        url = self.config.database.url
        path = url[len("sqlite:///"):] if url.startswith("sqlite:///") else "/tmp/cloud_ingestion_dev.db"
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_cli_tokens (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                token_prefix TEXT NOT NULL,
                name TEXT NOT NULL DEFAULT 'CLI token',
                created_at TEXT NOT NULL,
                last_used_at TEXT,
                revoked_at TEXT
            )
        """)
        conn.commit()
        return conn

    def validate(self, raw_token: str) -> Optional[str]:
        """Return the user_id for the token, or None if invalid/revoked."""
        if not raw_token:
            return None
        h = hash_token(raw_token)
        now = datetime.now(timezone.utc)

        if self._backend == "postgres":
            c = self._pg()
            try:
                with c, c.cursor() as cur:
                    cur.execute(
                        "SELECT user_id, revoked_at FROM user_cli_tokens "
                        "WHERE token_hash = %s",
                        (h,),
                    )
                    row = cur.fetchone()
                    if not row:
                        return None
                    user_id, revoked_at = row
                    if revoked_at is not None:
                        return None
                    cur.execute(
                        "UPDATE user_cli_tokens SET last_used_at = %s "
                        "WHERE token_hash = %s",
                        (now, h),
                    )
                    return str(user_id)
            except Exception as e:
                logger.error("Token validation failed: %s", e)
                return None
            finally:
                c.close()

        # SQLite dev path
        c = self._sq()
        try:
            row = c.execute(
                "SELECT user_id, revoked_at FROM user_cli_tokens WHERE token_hash = ?",
                (h,),
            ).fetchone()
            if not row:
                return None
            if row["revoked_at"] is not None:
                return None
            c.execute(
                "UPDATE user_cli_tokens SET last_used_at = ? WHERE token_hash = ?",
                (now.isoformat(), h),
            )
            c.commit()
            return row["user_id"]
        except Exception as e:
            logger.error("Token validation (sqlite) failed: %s", e)
            return None
        finally:
            c.close()


def make_auth_dependency(config):
    """Build a FastAPI dependency that returns user_id or 401s.

    When auth.enabled=False (dev), returns DEV_USER_ID without any DB lookup
    so localhost testing keeps working.
    """
    validator = TokenValidator(config)

    def _dep(request: Request) -> str:
        if not config.auth.enabled:
            return DEV_USER_ID
        raw = extract_bearer(request)
        if not raw:
            raise HTTPException(
                status_code=401,
                detail="Missing Authorization: Bearer <token>",
            )
        user_id = validator.validate(raw)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or revoked token")
        return user_id

    return _dep
