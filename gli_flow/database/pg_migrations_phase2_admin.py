"""Phase 2 migration: admin flag + profile completion.

Adds to public.app_users:
    - is_admin          BOOLEAN   (master users who can see everyone's data)
    - full_name         TEXT      (captured on first login)
    - profile_complete  BOOLEAN   (has the user entered their name yet?)

Admins are seeded from the GLI_ADMIN_EMAILS env var (comma-separated) at
migration time, and re-checked on every login by the ingest server.

Idempotent — safe to re-run.
"""

import os


PHASE2_MIGRATION_SQL = """
ALTER TABLE app_users ADD COLUMN IF NOT EXISTS is_admin          BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE app_users ADD COLUMN IF NOT EXISTS full_name         TEXT;
ALTER TABLE app_users ADD COLUMN IF NOT EXISTS profile_complete  BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_app_users_is_admin ON app_users(is_admin) WHERE is_admin = TRUE;

INSERT INTO schema_version (source, version, description)
VALUES ('phase2_admin', 1, 'Add is_admin, full_name, profile_complete to app_users')
ON CONFLICT (source, version) DO NOTHING;
"""


def _admin_emails():
    raw = os.environ.get("GLI_ADMIN_EMAILS", "")
    return [e.strip().lower() for e in raw.split(",") if e.strip()]


def apply(engine) -> None:
    conn = engine._get_conn()
    cur = conn.cursor()
    try:
        for statement in PHASE2_MIGRATION_SQL.strip().split(";"):
            stmt = statement.strip()
            if not stmt or all(ln.strip().startswith("--") or not ln.strip() for ln in stmt.splitlines()):
                continue
            try:
                cur.execute(stmt + ";")
            except Exception as e:
                if "already exists" in str(e).lower():
                    continue
                raise

        # Seed admins from env. If a listed email already has a row, flip
        # is_admin; otherwise create a placeholder row that will be filled
        # in when they first sign in.
        for email in _admin_emails():
            cur.execute(
                """
                INSERT INTO app_users (id, email, display_name, is_admin, is_active)
                VALUES (gen_random_uuid(), %s, %s, TRUE, TRUE)
                ON CONFLICT (email) DO UPDATE SET is_admin = TRUE
                """,
                (email, email.split("@")[0]),
            )
    finally:
        cur.close()


def validate(engine) -> dict:
    missing = engine.validate_table_columns(
        "public", "app_users", ["is_admin", "full_name", "profile_complete"]
    )
    return {"ok": not missing, "missing_columns": missing}
