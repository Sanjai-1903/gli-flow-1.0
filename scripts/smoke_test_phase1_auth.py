#!/usr/bin/env python3
"""End-to-end smoke test for the Phase 1-4 stack, runnable locally.

What it validates, in order:

    1. Phase 1 migration is applied (all required tables + columns exist)
    2. We can create a fake user + issue a CLI token directly in the DB
    3. The ingest server (running locally) accepts uploads with that token
    4. The upload lands in Supabase with the correct user_id attached
    5. Unauthenticated / wrong-token uploads are rejected with 401

Prerequisites:
    - GLI_DATABASE_URL set to your Supabase Postgres URL
    - The ingest server running locally, pointed at the same DB:
        export GLI_DATABASE_URL="postgresql://..."
        uvicorn cloud_ingestion.server:create_app --factory --port 8100 &
    - Or pass a custom URL with --ingest-url

Usage:
    export GLI_DATABASE_URL="postgresql://..."
    python3 scripts/smoke_test_phase1_auth.py
"""

from __future__ import annotations

import argparse
import hashlib
import os
import secrets
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import httpx  # noqa: E402
import psycopg2  # noqa: E402


TOKEN_PREFIX = "gfp_"


def gen_token() -> str:
    return TOKEN_PREFIX + secrets.token_urlsafe(30)


def hash_token(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def ok(msg: str) -> None:
    print(f"  \033[32m✓\033[0m {msg}")


def fail(msg: str) -> None:
    print(f"  \033[31m✗\033[0m {msg}")
    sys.exit(1)


def step(n: int, title: str) -> None:
    print(f"\n[{n}] {title}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db-url", default=os.environ.get("GLI_DATABASE_URL"))
    ap.add_argument("--ingest-url", default=os.environ.get("GLI_INGEST_URL", "http://localhost:8100"))
    args = ap.parse_args()

    if not args.db_url:
        fail("Set GLI_DATABASE_URL to your Supabase URL, or pass --db-url.")

    print(f"Database:   {args.db_url.split('@')[-1] if '@' in args.db_url else args.db_url}")
    print(f"Ingest:     {args.ingest_url}")

    # ---- 1. Migration applied? ----
    step(1, "Verify Phase 1 migration is applied")
    conn = psycopg2.connect(args.db_url)
    conn.autocommit = True
    cur = conn.cursor()

    required = [
        ("public", "app_users"),
        ("public", "user_cli_tokens"),
        ("public", "pending_device_authorizations"),
    ]
    for schema, table in required:
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
            "WHERE table_schema=%s AND table_name=%s)",
            (schema, table),
        )
        if not cur.fetchone()[0]:
            fail(f"Missing table {schema}.{table} — run scripts/apply_phase1_migration.py first")
        ok(f"table {schema}.{table} exists")

    for schema, table, col in [
        ("ingestion", "telemetry_events", "user_id"),
        ("ingestion", "upload_audit", "user_id"),
        ("public", "runs", "user_id"),
    ]:
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM information_schema.columns "
            "WHERE table_schema=%s AND table_name=%s AND column_name=%s)",
            (schema, table, col),
        )
        if not cur.fetchone()[0]:
            fail(f"Missing column {schema}.{table}.{col}")
        ok(f"column {schema}.{table}.{col} exists")

    # ---- 2. Create test user + token ----
    step(2, "Create a test user + issue a CLI token")
    test_user_id = str(uuid.uuid4())
    test_email = f"smoketest+{secrets.token_hex(4)}@gli-flow.local"
    raw_token = gen_token()
    th = hash_token(raw_token)

    cur.execute(
        "INSERT INTO app_users (id, email, display_name, is_active) "
        "VALUES (%s, %s, %s, TRUE)",
        (test_user_id, test_email, "Smoke Test User"),
    )
    cur.execute(
        "INSERT INTO user_cli_tokens (user_id, token_hash, token_prefix, name) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        (test_user_id, th, raw_token[:12], "smoke-test-token"),
    )
    token_row_id = cur.fetchone()[0]
    ok(f"created user {test_email[:40]}... id={test_user_id[:8]}...")
    ok(f"issued token {raw_token[:16]}... (id={token_row_id})")

    # ---- 3. Reject anonymous upload ----
    step(3, "Ingest server rejects anonymous upload with 401")
    payload = {
        "run_id": f"smoke_test_{secrets.token_hex(4)}",
        "source_version": "smoke-test",
        "telemetry_events": [{
            "run_id": "will-be-overridden",
            "tool": "gli-flow",
            "stage": "SMOKE",
            "event": "smoke_event",
            "design_name": "smoketest",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }],
        "failure_atlas_entries": [],
        "escalations": [],
    }
    try:
        resp = httpx.post(f"{args.ingest_url}/api/v1/telemetry", json=payload, timeout=15.0)
    except Exception as e:
        fail(f"Could not reach ingest server at {args.ingest_url}: {e}")
    if resp.status_code != 401:
        fail(f"Expected 401 for anonymous upload, got {resp.status_code}: {resp.text[:120]}")
    ok(f"anonymous upload rejected: 401")

    # ---- 4. Reject wrong token ----
    step(4, "Ingest server rejects a bogus token with 401")
    bogus = f"Bearer {TOKEN_PREFIX}deadbeef" * 3
    resp = httpx.post(
        f"{args.ingest_url}/api/v1/telemetry",
        json=payload,
        headers={"Authorization": bogus},
        timeout=15.0,
    )
    if resp.status_code != 401:
        fail(f"Expected 401 for bogus token, got {resp.status_code}")
    ok("bogus token rejected: 401")

    # ---- 5. Accept valid token ----
    step(5, "Ingest server accepts our valid token")
    payload["run_id"] = f"smoke_test_{secrets.token_hex(4)}"
    for ev in payload["telemetry_events"]:
        ev["run_id"] = payload["run_id"]
    resp = httpx.post(
        f"{args.ingest_url}/api/v1/telemetry",
        json=payload,
        headers={"Authorization": f"Bearer {raw_token}"},
        timeout=15.0,
    )
    if resp.status_code != 200:
        fail(f"Expected 200, got {resp.status_code}: {resp.text[:200]}")
    body = resp.json()
    ok(f"upload accepted: {body.get('telemetry_accepted', 0)} events")

    # ---- 6. Row present in Supabase with correct user_id ----
    step(6, "Row is in ingestion.telemetry_events with our user_id")
    cur.execute(
        "SELECT user_id, run_id, event FROM ingestion.telemetry_events "
        "WHERE run_id = %s ORDER BY id DESC LIMIT 1",
        (payload["run_id"],),
    )
    row = cur.fetchone()
    if not row:
        fail(f"No row found for run_id={payload['run_id']}")
    ok(f"row user_id={row[0]} matches test_user_id={test_user_id}: "
       + ("YES" if str(row[0]) == test_user_id else "NO — MISMATCH"))
    if str(row[0]) != test_user_id:
        fail("user_id was not attributed correctly!")

    # ---- 7. Whoami works ----
    step(7, "/api/v1/whoami returns our user_id")
    resp = httpx.get(
        f"{args.ingest_url}/api/v1/whoami",
        headers={"Authorization": f"Bearer {raw_token}"},
        timeout=10.0,
    )
    if resp.status_code != 200:
        fail(f"whoami failed: {resp.status_code}")
    body = resp.json()
    if body.get("user_id") != test_user_id:
        fail(f"whoami user_id mismatch: {body.get('user_id')} vs {test_user_id}")
    ok(f"whoami: user_id={body.get('user_id')}")

    # ---- 8. Revoke the token; upload now fails ----
    step(8, "Revoke token; upload now 401s")
    cur.execute(
        "UPDATE user_cli_tokens SET revoked_at = NOW() WHERE id = %s",
        (token_row_id,),
    )
    resp = httpx.post(
        f"{args.ingest_url}/api/v1/telemetry",
        json=payload,
        headers={"Authorization": f"Bearer {raw_token}"},
        timeout=15.0,
    )
    if resp.status_code != 401:
        fail(f"Revoked token still accepted (got {resp.status_code})!")
    ok("revoked token rejected: 401")

    # ---- 9. Cleanup ----
    step(9, "Cleanup test data")
    cur.execute("DELETE FROM ingestion.telemetry_events WHERE user_id = %s", (test_user_id,))
    cur.execute("DELETE FROM ingestion.upload_audit WHERE user_id = %s", (test_user_id,))
    cur.execute("DELETE FROM user_cli_tokens WHERE user_id = %s", (test_user_id,))
    cur.execute("DELETE FROM app_users WHERE id = %s", (test_user_id,))
    ok("cleanup complete")

    cur.close()
    conn.close()

    print("\n\033[32mAll smoke tests passed.\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
