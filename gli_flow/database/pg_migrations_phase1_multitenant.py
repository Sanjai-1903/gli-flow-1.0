"""Phase 1 migration: multi-tenant foundation.

Adds:
    - public.app_users              (mirrors Supabase auth.users)
    - public.user_cli_tokens        (long-lived Bearer tokens for CLI)
    - user_id column on 5 tables:
        ingestion.telemetry_events
        ingestion.failure_atlas_events
        ingestion.upload_audit
        ingestion.consent_records
        public.runs
    - a legacy placeholder user, backfilled onto existing rows
    - RLS enabled on all 7 new/altered tables (permissive for now; policies
      tighten in Phase 4 once the ingest server passes user_id)

Idempotent — safe to re-run.

Reference: multi-tenant plan in project notes.
"""

# Deterministic UUID for the "legacy" placeholder user that owns any rows
# written before authentication was enforced. Chosen once, never changes.
LEGACY_USER_ID = "00000000-0000-0000-0000-000000000001"


PHASE1_MIGRATION_SQL = f"""
-- ---------------------------------------------------------------------------
-- 1. New tables: app_users, user_cli_tokens
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS app_users (
    id            UUID        PRIMARY KEY,
    email         TEXT        NOT NULL UNIQUE,
    display_name  TEXT,
    avatar_url    TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    is_active     BOOLEAN     NOT NULL DEFAULT TRUE,
    metadata      JSONB       NOT NULL DEFAULT '{{}}'
);

CREATE INDEX IF NOT EXISTS idx_app_users_email ON app_users(email);

CREATE TABLE IF NOT EXISTS user_cli_tokens (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID        NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    token_hash    TEXT        NOT NULL UNIQUE,
    token_prefix  TEXT        NOT NULL,
    name          TEXT        NOT NULL DEFAULT 'CLI token',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at  TIMESTAMPTZ,
    revoked_at    TIMESTAMPTZ,
    user_agent    TEXT,
    created_ip    TEXT
);

CREATE INDEX IF NOT EXISTS idx_user_cli_tokens_user_id ON user_cli_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_user_cli_tokens_hash    ON user_cli_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_user_cli_tokens_active
    ON user_cli_tokens(user_id) WHERE revoked_at IS NULL;

-- Device-flow authorizations (short-lived; used by `gli-flow login`)
CREATE TABLE IF NOT EXISTS pending_device_authorizations (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    device_code   TEXT        NOT NULL UNIQUE,
    user_code     TEXT        NOT NULL UNIQUE,
    user_id       UUID        REFERENCES app_users(id),
    token_id      UUID        REFERENCES user_cli_tokens(id),
    access_token  TEXT,
    status        TEXT        NOT NULL DEFAULT 'pending',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at    TIMESTAMPTZ NOT NULL,
    approved_at   TIMESTAMPTZ,
    consumed_at   TIMESTAMPTZ,
    user_agent    TEXT,
    ip_address    TEXT
);

CREATE INDEX IF NOT EXISTS idx_pda_device_code ON pending_device_authorizations(device_code);
CREATE INDEX IF NOT EXISTS idx_pda_user_code   ON pending_device_authorizations(user_code);
CREATE INDEX IF NOT EXISTS idx_pda_status      ON pending_device_authorizations(status);
CREATE INDEX IF NOT EXISTS idx_pda_expires_at  ON pending_device_authorizations(expires_at);

-- ---------------------------------------------------------------------------
-- 2. Legacy placeholder user (owns rows written before auth was enforced)
-- ---------------------------------------------------------------------------

INSERT INTO app_users (id, email, display_name, is_active, metadata)
VALUES (
    '{LEGACY_USER_ID}',
    'legacy@gli-flow.local',
    'Legacy (pre-auth uploads)',
    FALSE,
    '{{"reserved": true, "purpose": "backfill placeholder"}}'
)
ON CONFLICT (id) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 3. Add user_id to per-user tables (nullable, backfilled to legacy user)
-- ---------------------------------------------------------------------------

ALTER TABLE ingestion.telemetry_events
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES app_users(id);

ALTER TABLE ingestion.failure_atlas_events
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES app_users(id);

ALTER TABLE ingestion.upload_audit
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES app_users(id);

ALTER TABLE ingestion.consent_records
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES app_users(id);

ALTER TABLE runs
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES app_users(id);

-- Backfill: any existing row gets the legacy placeholder user.
UPDATE ingestion.telemetry_events      SET user_id = '{LEGACY_USER_ID}' WHERE user_id IS NULL;
UPDATE ingestion.failure_atlas_events  SET user_id = '{LEGACY_USER_ID}' WHERE user_id IS NULL;
UPDATE ingestion.upload_audit          SET user_id = '{LEGACY_USER_ID}' WHERE user_id IS NULL;
UPDATE ingestion.consent_records       SET user_id = '{LEGACY_USER_ID}' WHERE user_id IS NULL;
UPDATE runs                            SET user_id = '{LEGACY_USER_ID}' WHERE user_id IS NULL;

CREATE INDEX IF NOT EXISTS idx_te_user_id  ON ingestion.telemetry_events(user_id);
CREATE INDEX IF NOT EXISTS idx_fae_user_id ON ingestion.failure_atlas_events(user_id);
CREATE INDEX IF NOT EXISTS idx_ua_user_id  ON ingestion.upload_audit(user_id);
CREATE INDEX IF NOT EXISTS idx_cr_user_id  ON ingestion.consent_records(user_id);
CREATE INDEX IF NOT EXISTS idx_runs_user_id ON runs(user_id);

-- ---------------------------------------------------------------------------
-- 4. RLS: enable on tenant tables. Policies read auth.uid() (Supabase) so
--    logged-in users only see their own rows. The Postgres superuser role
--    used by the ingest server bypasses RLS, so writes still work.
-- ---------------------------------------------------------------------------

ALTER TABLE app_users                     ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_cli_tokens               ENABLE ROW LEVEL SECURITY;
ALTER TABLE runs                          ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingestion.telemetry_events    ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingestion.failure_atlas_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingestion.upload_audit        ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingestion.consent_records     ENABLE ROW LEVEL SECURITY;

-- Drop-then-create so re-running the migration refreshes policies.
DROP POLICY IF EXISTS app_users_self_read       ON app_users;
DROP POLICY IF EXISTS user_cli_tokens_self_read ON user_cli_tokens;
DROP POLICY IF EXISTS user_cli_tokens_self_write ON user_cli_tokens;
DROP POLICY IF EXISTS runs_self_read            ON runs;
DROP POLICY IF EXISTS te_self_read              ON ingestion.telemetry_events;
DROP POLICY IF EXISTS fae_self_read             ON ingestion.failure_atlas_events;
DROP POLICY IF EXISTS ua_self_read              ON ingestion.upload_audit;
DROP POLICY IF EXISTS cr_self_read              ON ingestion.consent_records;

CREATE POLICY app_users_self_read ON app_users
    FOR SELECT USING (id = auth.uid());

CREATE POLICY user_cli_tokens_self_read ON user_cli_tokens
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY user_cli_tokens_self_write ON user_cli_tokens
    FOR ALL USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

CREATE POLICY runs_self_read ON runs
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY te_self_read ON ingestion.telemetry_events
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY fae_self_read ON ingestion.failure_atlas_events
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY ua_self_read ON ingestion.upload_audit
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY cr_self_read ON ingestion.consent_records
    FOR SELECT USING (user_id = auth.uid());

-- ---------------------------------------------------------------------------
-- 5. Record migration in schema_version
-- ---------------------------------------------------------------------------

INSERT INTO schema_version (source, version, description)
VALUES ('phase1_multitenant', 1, 'Add app_users, user_cli_tokens, user_id columns, RLS')
ON CONFLICT (source, version) DO NOTHING;
"""


EXPECTED_PHASE1_TABLES = {
    "public": ["app_users", "user_cli_tokens", "pending_device_authorizations"],
}

EXPECTED_PHASE1_COLUMNS = {
    ("ingestion", "telemetry_events"):      ["user_id"],
    ("ingestion", "failure_atlas_events"):  ["user_id"],
    ("ingestion", "upload_audit"):          ["user_id"],
    ("ingestion", "consent_records"):       ["user_id"],
    ("public",    "runs"):                  ["user_id"],
}


def apply(engine) -> None:
    """Apply Phase 1 migration using a PGMigrationEngine instance.

    Each statement runs separately so a benign 'already exists' on one
    ALTER doesn't abort the transaction and skip the rest.

    RLS/policy statements need Supabase's 'auth' schema (auth.uid()) to
    exist. On a plain Postgres without Supabase Auth those will fail —
    we swallow that specific error so local dev keeps working.
    """
    conn = engine._get_conn()
    cur = conn.cursor()
    # Strip -- line comments up front so a `;` inside a comment doesn't
    # confuse the naive split-on-semicolon parser.
    stripped_sql = "\n".join(
        line.split("--", 1)[0] if line.lstrip().startswith("--") or "--" in line
        else line
        for line in PHASE1_MIGRATION_SQL.splitlines()
    )
    try:
        for statement in stripped_sql.strip().split(";"):
            stmt = statement.strip()
            if not stmt:
                continue
            non_comment = [ln for ln in stmt.splitlines() if ln.strip()]
            if not non_comment:
                continue
            try:
                cur.execute(stmt + ";")
            except Exception as e:
                msg = str(e).lower()
                # Idempotent-safe skips
                if "already exists" in msg:
                    continue
                # auth schema only exists on Supabase; skip policies elsewhere
                if 'schema "auth" does not exist' in msg or "auth.uid()" in msg:
                    continue
                raise
    finally:
        cur.close()


def validate(engine) -> dict:
    """Return {'ok': bool, 'missing_tables': [...], 'missing_columns': [...]}."""
    missing_tables = []
    for schema, tables in EXPECTED_PHASE1_TABLES.items():
        for table in tables:
            if not engine.validate_table_exists(schema, table):
                missing_tables.append(f"{schema}.{table}")

    missing_columns = []
    for (schema, table), cols in EXPECTED_PHASE1_COLUMNS.items():
        missing = engine.validate_table_columns(schema, table, cols)
        for col in missing:
            missing_columns.append(f"{schema}.{table}.{col}")

    return {
        "ok": not missing_tables and not missing_columns,
        "missing_tables": missing_tables,
        "missing_columns": missing_columns,
    }
