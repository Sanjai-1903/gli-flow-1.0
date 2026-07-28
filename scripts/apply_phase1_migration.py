#!/usr/bin/env python3
"""Apply Phase 1 multi-tenant migration to Supabase (or any Postgres).

Reads DATABASE_URL from:
    1. --url CLI arg
    2. GLI_DATABASE_URL env var
    3. SUPABASE_URL env var
    4. DATABASE_URL env var

Usage:
    export GLI_DATABASE_URL="postgresql://postgres.xxx:PASSWORD@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"
    python scripts/apply_phase1_migration.py

    # or:
    python scripts/apply_phase1_migration.py --url "postgresql://..."

Idempotent — safe to re-run.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def resolve_url(cli_url: str | None) -> str:
    for candidate in (
        cli_url,
        os.environ.get("GLI_DATABASE_URL"),
        os.environ.get("SUPABASE_URL"),
        os.environ.get("DATABASE_URL"),
    ):
        if candidate:
            return candidate
    print("ERROR: no database URL provided.")
    print("Set GLI_DATABASE_URL (or SUPABASE_URL / DATABASE_URL), or pass --url.")
    sys.exit(2)


def redact(url: str) -> str:
    """Hide the password portion when printing."""
    if "://" not in url or "@" not in url:
        return url
    scheme, rest = url.split("://", 1)
    creds, host = rest.split("@", 1)
    if ":" in creds:
        user, _pw = creds.split(":", 1)
        return f"{scheme}://{user}:***@{host}"
    return url


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Postgres connection URL")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Skip apply; just check what's currently in the DB.",
    )
    args = parser.parse_args()

    url = resolve_url(args.url)
    print(f"Target database: {redact(url)}")

    from gli_flow.database.pg_migrations import PGMigrationEngine
    from gli_flow.database import pg_migrations_phase1_multitenant as phase1

    engine = PGMigrationEngine(url)

    if not args.validate_only:
        print("Applying Phase 1 migration (multi-tenant foundation)...")
        # Full migrate() runs base tables + ingestion + phase1. Base tables
        # already exist on Supabase from the earlier setup, so this is a no-op
        # for them and only the Phase 1 statements do meaningful work.
        engine.migrate()
        print("  applied.")

    print("Validating Phase 1 schema...")
    result = phase1.validate(engine)
    if result["ok"]:
        print("  OK: all Phase 1 tables and columns present.")
    else:
        print("  MISSING:")
        for t in result["missing_tables"]:
            print(f"    - table:  {t}")
        for c in result["missing_columns"]:
            print(f"    - column: {c}")

    # Extra visibility: show current per-user row counts
    conn = engine._get_conn()
    cur = conn.cursor()
    print("\nRow counts (should be non-zero if Phase 1 applied and legacy backfill ran):")
    for label, sql in [
        ("app_users",                       "SELECT COUNT(*) FROM app_users"),
        ("user_cli_tokens",                 "SELECT COUNT(*) FROM user_cli_tokens"),
        ("runs w/ user_id",                 "SELECT COUNT(*) FROM runs WHERE user_id IS NOT NULL"),
        ("ingestion.telemetry_events w/ user_id",     "SELECT COUNT(*) FROM ingestion.telemetry_events WHERE user_id IS NOT NULL"),
        ("ingestion.failure_atlas_events w/ user_id", "SELECT COUNT(*) FROM ingestion.failure_atlas_events WHERE user_id IS NOT NULL"),
        ("ingestion.upload_audit w/ user_id",         "SELECT COUNT(*) FROM ingestion.upload_audit WHERE user_id IS NOT NULL"),
        ("ingestion.consent_records w/ user_id",      "SELECT COUNT(*) FROM ingestion.consent_records WHERE user_id IS NOT NULL"),
    ]:
        try:
            cur.execute(sql)
            (n,) = cur.fetchone()
            print(f"  {label}: {n}")
        except Exception as e:
            print(f"  {label}: ERROR ({e})")
    cur.close()
    engine.close()

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
