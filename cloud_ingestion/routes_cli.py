"""FastAPI routes for the device-flow login and CLI token management.

Endpoints:

    POST /api/v1/cli/device/authorize      (no auth) — CLI starts login
    POST /api/v1/cli/device/poll           (no auth) — CLI checks approval
    POST /api/v1/cli/device/approve        (Supabase JWT) — browser approves

    GET  /api/v1/tokens/list               (Supabase JWT)
    POST /api/v1/tokens/create             (Supabase JWT)
    POST /api/v1/tokens/revoke             (Supabase JWT)

All persistent state lives in Postgres tables:
    public.app_users
    public.user_cli_tokens
    public.pending_device_authorizations
"""

from __future__ import annotations

import logging
import os
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from cloud_ingestion.config import CloudIngestionConfig
from cloud_ingestion.auth import hash_token, TOKEN_PREFIX
from cloud_ingestion.supabase_jwt import require_supabase_user, SupabaseUser

logger = logging.getLogger(__name__)


# ---------------- Helpers ----------------

def _pg(config: CloudIngestionConfig):
    import psycopg2
    return psycopg2.connect(config.database.url)


def _admin_emails():
    raw = os.environ.get("GLI_ADMIN_EMAILS", "")
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


def _ensure_app_user(conn, user: SupabaseUser) -> None:
    """Upsert the caller into app_users on every JWT-verified request.

    This is the seam between Supabase's auth.users and our public.app_users
    mirror — we don't need a database trigger, we just sync on demand.

    Also re-asserts admin status from GLI_ADMIN_EMAILS on every login, so
    adding an email to that env var promotes them on their next request.
    """
    is_admin = (user.email or "").strip().lower() in _admin_emails()
    with conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO app_users (id, email, display_name, last_login_at, is_admin)
            VALUES (%s, %s, %s, NOW(), %s)
            ON CONFLICT (id) DO UPDATE
              SET email = EXCLUDED.email,
                  last_login_at = NOW(),
                  updated_at = NOW(),
                  is_admin = app_users.is_admin OR EXCLUDED.is_admin
            """,
            (user.id, user.email or f"{user.id}@unknown", user.email or "", is_admin),
        )


def _is_admin(conn, user_id: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT is_admin FROM app_users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        return bool(row and row[0])


def _gen_token() -> str:
    """Generate a raw CLI token: 'gfp_' + 40 URL-safe chars."""
    return TOKEN_PREFIX + secrets.token_urlsafe(30)  # ~40 chars


def _gen_user_code() -> str:
    """Human-friendly 8-char code, avoiding ambiguous glyphs (0/O/I/1)."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(8))


def _gen_device_code() -> str:
    """Secret 43-char code held only by the CLI."""
    return secrets.token_urlsafe(32)


def _prefix(t: str) -> str:
    return t[:12] if len(t) > 12 else t


# ---------------- Pydantic bodies ----------------

class DeviceAuthorizeIn(BaseModel):
    pass


class DevicePollIn(BaseModel):
    device_code: str


class DeviceApproveIn(BaseModel):
    user_code: str
    deny: bool = False


class TokenCreateIn(BaseModel):
    name: str = "CLI token"


class ProfileIn(BaseModel):
    full_name: str


class TokenRevokeIn(BaseModel):
    token_id: str


# ---------------- Router factory ----------------

def build_router(config: CloudIngestionConfig) -> APIRouter:
    router = APIRouter()

    device_ttl_sec = int(os.environ.get("GLI_DEVICE_FLOW_TTL_SEC", "900"))  # 15 min
    poll_interval_sec = int(os.environ.get("GLI_DEVICE_FLOW_POLL_SEC", "5"))
    verification_uri = (
        os.environ.get("GLI_WEB_URL", "https://gli-flow.vercel.app").rstrip("/")
        + "/cli/device"
    )

    # ---------- Device flow ----------

    @router.post("/api/v1/cli/device/authorize")
    def device_authorize(_body: DeviceAuthorizeIn, request: Request):
        device_code = _gen_device_code()
        user_code = _gen_user_code()
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=device_ttl_sec)
        ua = request.headers.get("User-Agent", "")[:200]
        ip = request.client.host if request.client else ""

        conn = _pg(config)
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO pending_device_authorizations
                        (device_code, user_code, status, expires_at, user_agent, ip_address)
                    VALUES (%s, %s, 'pending', %s, %s, %s)
                    """,
                    (device_code, user_code, expires, ua, ip),
                )
        finally:
            conn.close()

        return {
            "device_code": device_code,
            "user_code": user_code,
            "verification_uri": verification_uri,
            "expires_in": device_ttl_sec,
            "interval": poll_interval_sec,
        }

    @router.post("/api/v1/cli/device/poll")
    def device_poll(body: DevicePollIn):
        conn = _pg(config)
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT status, user_id, access_token, expires_at, consumed_at
                    FROM pending_device_authorizations
                    WHERE device_code = %s
                    """,
                    (body.device_code,),
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=400, detail={"error": "invalid_grant"})
                status, user_id, access_token, expires_at, consumed_at = row

                now = datetime.now(timezone.utc)
                if expires_at and expires_at < now:
                    raise HTTPException(status_code=400, detail={"error": "expired_token"})

                if status == "denied":
                    raise HTTPException(status_code=400, detail={"error": "access_denied"})

                if status != "approved" or not access_token:
                    raise HTTPException(status_code=400, detail={"error": "authorization_pending"})

                if consumed_at is not None:
                    # Already picked up once — refuse to hand out again.
                    raise HTTPException(status_code=400, detail={"error": "invalid_grant"})

                # Consume: clear access_token and mark consumed. Look up email.
                cur.execute(
                    "UPDATE pending_device_authorizations SET consumed_at = %s, access_token = NULL "
                    "WHERE device_code = %s",
                    (now, body.device_code),
                )
                cur.execute("SELECT email FROM app_users WHERE id = %s", (user_id,))
                email_row = cur.fetchone()
                email = email_row[0] if email_row else ""
        finally:
            conn.close()

        return {
            "access_token": access_token,
            "user_id": str(user_id),
            "email": email,
            "token_type": "Bearer",
        }

    @router.post("/api/v1/cli/device/approve")
    def device_approve(
        body: DeviceApproveIn,
        user: SupabaseUser = Depends(require_supabase_user),
    ):
        user_code = body.user_code.strip().upper()
        now = datetime.now(timezone.utc)

        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn, conn.cursor() as cur:
                cur.execute(
                    "SELECT id, status, expires_at FROM pending_device_authorizations "
                    "WHERE user_code = %s",
                    (user_code,),
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Unknown code")
                pda_id, status, expires_at = row
                if expires_at and expires_at < now:
                    raise HTTPException(status_code=400, detail="Code expired")
                if status != "pending":
                    raise HTTPException(status_code=400, detail=f"Already {status}")

                if body.deny:
                    cur.execute(
                        "UPDATE pending_device_authorizations SET status='denied' WHERE id=%s",
                        (pda_id,),
                    )
                    return {"status": "denied"}

                # Issue a token: store hash, hand back raw via poll.
                raw_token = _gen_token()
                th = hash_token(raw_token)
                cur.execute(
                    """
                    INSERT INTO user_cli_tokens (user_id, token_hash, token_prefix, name)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (user.id, th, _prefix(raw_token), f"Device login {now.strftime('%Y-%m-%d %H:%M')}"),
                )
                (token_id,) = cur.fetchone()

                cur.execute(
                    """
                    UPDATE pending_device_authorizations
                    SET status='approved', user_id=%s, token_id=%s, access_token=%s,
                        approved_at=%s
                    WHERE id=%s
                    """,
                    (user.id, token_id, raw_token, now, pda_id),
                )
        finally:
            conn.close()

        return {"status": "approved"}

    # ---------- Token management ----------

    @router.get("/api/v1/tokens/list")
    def tokens_list(user: SupabaseUser = Depends(require_supabase_user)):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, token_prefix, name, created_at, last_used_at, revoked_at
                    FROM user_cli_tokens
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    """,
                    (user.id,),
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        return {
            "tokens": [
                {
                    "id": str(r[0]),
                    "token_prefix": r[1],
                    "name": r[2],
                    "created_at": r[3].isoformat() if r[3] else None,
                    "last_used_at": r[4].isoformat() if r[4] else None,
                    "revoked_at": r[5].isoformat() if r[5] else None,
                }
                for r in rows
            ]
        }

    @router.post("/api/v1/tokens/create")
    def tokens_create(
        body: TokenCreateIn,
        user: SupabaseUser = Depends(require_supabase_user),
    ):
        raw_token = _gen_token()
        th = hash_token(raw_token)
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn, conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_cli_tokens (user_id, token_hash, token_prefix, name)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, created_at
                    """,
                    (user.id, th, _prefix(raw_token), body.name or "CLI token"),
                )
                token_id, created_at = cur.fetchone()
        finally:
            conn.close()

        return {
            "id": str(token_id),
            "access_token": raw_token,           # only ever returned here
            "token_prefix": _prefix(raw_token),
            "name": body.name or "CLI token",
            "created_at": created_at.isoformat(),
        }

    @router.post("/api/v1/tokens/revoke")
    def tokens_revoke(
        body: TokenRevokeIn,
        user: SupabaseUser = Depends(require_supabase_user),
    ):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn, conn.cursor() as cur:
                cur.execute(
                    "UPDATE user_cli_tokens SET revoked_at = NOW() "
                    "WHERE id = %s AND user_id = %s "
                    "RETURNING id",
                    (body.token_id, user.id),
                )
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Token not found")
        finally:
            conn.close()
        return {"status": "revoked"}

    # ---------- Profile (name capture on first login) ----------

    @router.get("/api/v1/profile")
    def profile_get(user: SupabaseUser = Depends(require_supabase_user)):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT email, display_name, full_name, profile_complete, is_admin "
                    "FROM app_users WHERE id = %s",
                    (user.id,),
                )
                row = cur.fetchone()
        finally:
            conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "user_id": user.id,
            "email": row[0],
            "display_name": row[1],
            "full_name": row[2],
            "profile_complete": bool(row[3]),
            "is_admin": bool(row[4]),
        }

    @router.post("/api/v1/profile")
    def profile_set(
        body: ProfileIn,
        user: SupabaseUser = Depends(require_supabase_user),
    ):
        name = (body.full_name or "").strip()
        if not name:
            raise HTTPException(status_code=400, detail="Name cannot be empty")
        if len(name) > 120:
            name = name[:120]
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn, conn.cursor() as cur:
                cur.execute(
                    "UPDATE app_users SET full_name = %s, display_name = %s, "
                    "profile_complete = TRUE, updated_at = NOW() WHERE id = %s",
                    (name, name, user.id),
                )
        finally:
            conn.close()
        return {"status": "ok", "full_name": name, "profile_complete": True}

    # ---------- Admin (master user: view everyone) ----------

    @router.get("/api/v1/admin/users")
    def admin_users(user: SupabaseUser = Depends(require_supabase_user)):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            if not _is_admin(conn, user.id):
                raise HTTPException(status_code=403, detail="Admin only")
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        u.id, u.email, u.full_name, u.display_name,
                        u.is_admin, u.created_at, u.last_login_at,
                        COALESCE(rc.run_count, 0) AS run_count,
                        COALESCE(ec.event_count, 0) AS event_count,
                        rc.last_run_at
                    FROM app_users u
                    LEFT JOIN (
                        SELECT user_id,
                               COUNT(DISTINCT run_id) AS run_count,
                               MAX(ingested_at) AS last_run_at
                        FROM ingestion.telemetry_events
                        GROUP BY user_id
                    ) rc ON rc.user_id = u.id
                    LEFT JOIN (
                        SELECT user_id, COUNT(*) AS event_count
                        FROM ingestion.telemetry_events
                        GROUP BY user_id
                    ) ec ON ec.user_id = u.id
                    WHERE u.is_active = TRUE
                    ORDER BY rc.last_run_at DESC NULLS LAST, u.created_at DESC
                    """,
                )
                rows = cur.fetchall()
        finally:
            conn.close()
        return {
            "users": [
                {
                    "user_id": str(r[0]),
                    "email": r[1],
                    "full_name": r[2],
                    "display_name": r[3],
                    "is_admin": bool(r[4]),
                    "created_at": r[5].isoformat() if r[5] else None,
                    "last_login_at": r[6].isoformat() if r[6] else None,
                    "run_count": int(r[7] or 0),
                    "event_count": int(r[8] or 0),
                    "last_run_at": r[9].isoformat() if r[9] else None,
                }
                for r in rows
            ]
        }

    @router.get("/api/v1/admin/runs")
    def admin_runs(
        limit: int = 200,
        user: SupabaseUser = Depends(require_supabase_user),
    ):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            if not _is_admin(conn, user.id):
                raise HTTPException(status_code=403, detail="Admin only")
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        te.run_id,
                        te.user_id,
                        u.email,
                        u.full_name,
                        MAX(te.design_name) FILTER (WHERE te.design_name IS NOT NULL) AS design_name,
                        BOOL_OR(te.event = 'run_completed') AS completed,
                        COUNT(*) FILTER (WHERE te.event = 'stage_completed') AS stages,
                        MAX(te.ingested_at) AS last_seen
                    FROM ingestion.telemetry_events te
                    JOIN app_users u ON u.id = te.user_id
                    GROUP BY te.run_id, te.user_id, u.email, u.full_name
                    ORDER BY MAX(te.ingested_at) DESC
                    LIMIT %s
                    """,
                    (min(max(limit, 1), 2000),),
                )
                rows = cur.fetchall()
        finally:
            conn.close()
        return {
            "runs": [
                {
                    "run_id": r[0],
                    "user_id": str(r[1]),
                    "user_email": r[2],
                    "user_name": r[3],
                    "design_name": r[4] or "unknown",
                    "completed": bool(r[5]),
                    "stages_completed": int(r[6] or 0),
                    "last_seen": r[7].isoformat() if r[7] else None,
                }
                for r in rows
            ]
        }

    @router.get("/api/v1/admin/runs/{run_id}")
    def admin_run_detail(
        run_id: str,
        owner_id: str,
        user: SupabaseUser = Depends(require_supabase_user),
    ):
        """Full detail of ANY user's run. Admin only.

        owner_id is the user_id who owns the run (from the admin runs list),
        so we can look it up without the caller's own user filter.
        """
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            if not _is_admin(conn, user.id):
                raise HTTPException(status_code=403, detail="Admin only")
            with conn.cursor() as cur:
                # Owner info
                cur.execute(
                    "SELECT email, full_name, display_name FROM app_users WHERE id = %s",
                    (owner_id,),
                )
                owner = cur.fetchone()

                # Summary metrics
                cur.execute(
                    """
                    SELECT metrics FROM ingestion.telemetry_events
                    WHERE user_id = %s AND run_id = %s AND stage = 'SUMMARY'
                    ORDER BY ingested_at DESC LIMIT 1
                    """,
                    (owner_id, run_id),
                )
                srow = cur.fetchone()
                summary = (srow[0] if srow else {}) or {}

                # All events
                cur.execute(
                    """
                    SELECT tool, stage, event, design_name, metrics,
                           recorded_at, ingested_at
                    FROM ingestion.telemetry_events
                    WHERE user_id = %s AND run_id = %s
                    ORDER BY ingested_at DESC
                    """,
                    (owner_id, run_id),
                )
                rows = cur.fetchall()
                if not rows:
                    raise HTTPException(status_code=404, detail="Run not found")
        finally:
            conn.close()

        return {
            "run_id": run_id,
            "owner": {
                "user_id": owner_id,
                "email": owner[0] if owner else None,
                "full_name": owner[1] if owner else None,
                "display_name": owner[2] if owner else None,
            },
            "summary_metrics": summary,
            "events": [
                {
                    "tool": r[0], "stage": r[1], "event": r[2],
                    "design_name": r[3], "metrics": r[4],
                    "recorded_at": r[5].isoformat() if r[5] else None,
                    "ingested_at": r[6].isoformat() if r[6] else None,
                }
                for r in rows
            ],
            "count": len(rows),
        }

    # ---------- Runs (per-user summary for the dashboard) ----------

    @router.get("/api/v1/runs")
    def runs_list(
        user: SupabaseUser = Depends(require_supabase_user),
        limit: int = 50,
    ):
        """Return the caller's most recent runs, one row per run_id.

        Aggregates from ingestion.telemetry_events. For each run we surface:
          - run_id, design_name, first/last event timestamps
          - stages_completed (count of stage_completed events)
          - qor_score / wns / cell_count if present in the SUMMARY row's metrics
          - a boolean run_completed if we've seen the SUMMARY row
        """
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        run_id,
                        MAX(design_name) FILTER (WHERE design_name IS NOT NULL) AS design_name,
                        COUNT(*) FILTER (WHERE event = 'stage_completed') AS stages_completed,
                        BOOL_OR(event = 'run_completed') AS run_completed,
                        MIN(ingested_at) AS first_seen,
                        MAX(ingested_at) AS last_seen,
                        (
                            SELECT metrics FROM ingestion.telemetry_events te2
                            WHERE te2.run_id = te.run_id
                              AND te2.user_id = te.user_id
                              AND te2.stage = 'SUMMARY'
                            ORDER BY te2.ingested_at DESC LIMIT 1
                        ) AS summary_metrics
                    FROM ingestion.telemetry_events te
                    WHERE user_id = %s
                    GROUP BY run_id, user_id
                    ORDER BY MAX(ingested_at) DESC
                    LIMIT %s
                    """,
                    (user.id, min(max(limit, 1), 500)),
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        out = []
        for r in rows:
            summary = r[6] or {}
            out.append({
                "run_id": r[0],
                "design_name": r[1] or "unknown",
                "stages_completed": r[2],
                "run_completed": bool(r[3]),
                "first_seen": r[4].isoformat() if r[4] else None,
                "last_seen": r[5].isoformat() if r[5] else None,
                "qor_score": summary.get("qor_score"),
                "wns": summary.get("wns"),
                "cell_count": summary.get("cell_count"),
                "runtime_sec": summary.get("runtime_sec"),
            })
        return {"runs": out, "count": len(out)}

    @router.get("/api/v1/runs/{run_id}")
    def run_detail(
        run_id: str,
        user: SupabaseUser = Depends(require_supabase_user),
    ):
        """Return every telemetry event for one run, most recent first."""
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT tool, stage, event, design_name, metrics,
                           recorded_at, ingested_at
                    FROM ingestion.telemetry_events
                    WHERE user_id = %s AND run_id = %s
                    ORDER BY ingested_at DESC
                    """,
                    (user.id, run_id),
                )
                rows = cur.fetchall()
                if not rows:
                    raise HTTPException(status_code=404, detail="Run not found")
        finally:
            conn.close()

        return {
            "run_id": run_id,
            "events": [
                {
                    "tool": r[0],
                    "stage": r[1],
                    "event": r[2],
                    "design_name": r[3],
                    "metrics": r[4],
                    "recorded_at": r[5].isoformat() if r[5] else None,
                    "ingested_at": r[6].isoformat() if r[6] else None,
                }
                for r in rows
            ],
            "count": len(rows),
        }

    return router
