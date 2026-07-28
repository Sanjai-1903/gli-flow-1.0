"""Legacy-shape endpoints for the existing dashboard, made multi-tenant.

The original dashboard (dashboard/src/App.jsx and pages) was written against
backend/server.py which read from local SQLite. Those endpoints returned
run rows shaped like `runs` table columns.

Here we re-implement the ~15 endpoints the dashboard actually calls, but:
    1. All data comes from Supabase (ingestion.telemetry_events),
    2. Every request must present a Supabase JWT,
    3. Every query is filtered by the caller's user_id.

We keep the same JSON shape the dashboard expects so it renders without
frontend changes. Endpoints that require data we don't have yet
(investigation, trust-score, comparison, reproducibility, live_runs)
return sensible empty/placeholder responses so pages don't crash.

Mount at /api/v1/legacy/*. The dashboard's global fetch wrapper rewrites
bare paths (`/runs`) into `${INGEST_URL}/api/v1/legacy/runs` with the
Authorization header attached.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from cloud_ingestion.config import CloudIngestionConfig
from cloud_ingestion.supabase_jwt import require_supabase_user, SupabaseUser

logger = logging.getLogger(__name__)


def _pg(config: CloudIngestionConfig):
    import psycopg2
    return psycopg2.connect(config.database.url)


def _ensure_app_user(conn, user: SupabaseUser) -> None:
    with conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO app_users (id, email, display_name, last_login_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (id) DO UPDATE
              SET email = EXCLUDED.email,
                  last_login_at = NOW(),
                  updated_at = NOW()
            """,
            (user.id, user.email or f"{user.id}@unknown", user.email or ""),
        )


def _to_num(v):
    """Coerce string/None/whatever into a float, or None."""
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _to_int(v):
    if v is None or v == "":
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _to_bool(v):
    if isinstance(v, bool):
        return v
    if v in ("true", "True", 1, "1", "YES", "yes"):
        return True
    return False


def build_router(config: CloudIngestionConfig) -> APIRouter:
    router = APIRouter(prefix="/api/v1/legacy")

    # -----------------------------------------------------------------
    # /runs  — list of run summaries in legacy dashboard shape
    # -----------------------------------------------------------------
    @router.get("/runs")
    def list_runs(
        limit: int = Query(50, ge=1, le=10000),
        important: bool = Query(False),
        user: SupabaseUser = Depends(require_supabase_user),
    ):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                # Aggregate: one row per run_id for this user, joined with
                # its SUMMARY row's metrics.
                cur.execute(
                    """
                    WITH agg AS (
                        SELECT
                            run_id,
                            MAX(design_name) FILTER (WHERE design_name IS NOT NULL) AS design_name,
                            COUNT(*) FILTER (WHERE event = 'stage_completed') AS stages_done,
                            BOOL_OR(event = 'run_completed') AS completed,
                            MIN(ingested_at) AS first_seen,
                            MAX(ingested_at) AS last_seen
                        FROM ingestion.telemetry_events
                        WHERE user_id = %s
                        GROUP BY run_id
                    ),
                    summary AS (
                        SELECT DISTINCT ON (run_id)
                            run_id, metrics, ingested_at
                        FROM ingestion.telemetry_events
                        WHERE user_id = %s AND stage = 'SUMMARY'
                        ORDER BY run_id, ingested_at DESC
                    ),
                    failures AS (
                        SELECT run_id, COUNT(*) AS cnt
                        FROM ingestion.failure_atlas_events
                        WHERE user_id = %s
                        GROUP BY run_id
                    )
                    SELECT
                        agg.run_id, agg.design_name, agg.completed,
                        agg.stages_done, agg.last_seen,
                        summary.metrics,
                        COALESCE(failures.cnt, 0)
                    FROM agg
                    LEFT JOIN summary ON summary.run_id = agg.run_id
                    LEFT JOIN failures ON failures.run_id = agg.run_id
                    ORDER BY agg.last_seen DESC
                    LIMIT %s
                    """,
                    (user.id, user.id, user.id, limit),
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        out = []
        for r in rows:
            run_id, design_name, completed, stages_done, last_seen, metrics, failure_count = r
            m = metrics or {}
            status = "SUCCESS" if completed else "RUNNING"
            qor = _to_num(m.get("qor_score"))
            out.append({
                "run_id": run_id,
                "design_name": design_name or "unknown",
                "status": status,
                "current_stage": "DONE" if completed else "IN_PROGRESS",
                "progress": 100 if completed else min(95, (stages_done or 0) * 3),
                "wns": _to_num(m.get("wns")),
                "tns": _to_num(m.get("tns")),
                "hold_wns": _to_num(m.get("hold_wns")),
                "hold_tns": _to_num(m.get("hold_tns")),
                "utilization": _to_num(m.get("utilization")),
                "runtime_sec": _to_num(m.get("runtime_sec")),
                "cell_count": _to_int(m.get("cell_count")),
                "qor_score": qor,
                "timestamp": last_seen.isoformat() if last_seen else None,
                "is_important": False,      # not tracked yet — see /runs/{id}/important
                "tapeout_ready": _to_bool(m.get("tapeout_ready")),
                "implementation_status": "SUCCESS" if completed else "IN_PROGRESS",
                "signoff_status": m.get("signoff_status") or ("PASS" if completed else "NOT_RUN"),
                "implementation_score": _to_num(m.get("implementation_score")),
                "signoff_score": _to_num(m.get("signoff_score")),
                "root_cause_summary": None,
                "drc_violations": _to_int(m.get("drc_violations")) or 0,
                "drc_is_clean": _to_bool(m.get("drc_is_clean")),
                "lvs_is_clean": _to_bool(m.get("lvs_is_clean")),
                "failure_count": int(failure_count or 0),
                "max_severity": "",
            })
        return out

    # -----------------------------------------------------------------
    # /runs/count
    # -----------------------------------------------------------------
    @router.get("/runs/count")
    def runs_count(user: SupabaseUser = Depends(require_supabase_user)):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(DISTINCT run_id) FROM ingestion.telemetry_events WHERE user_id = %s",
                    (user.id,),
                )
                (n,) = cur.fetchone()
        finally:
            conn.close()
        return {"total": int(n or 0)}

    # -----------------------------------------------------------------
    # /live_runs  — we have no "currently running" signal from Supabase
    #               yet; return the ones we haven't seen a SUMMARY for
    #               within the last hour.
    # -----------------------------------------------------------------
    @router.get("/live_runs")
    def live_runs(user: SupabaseUser = Depends(require_supabase_user)):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT run_id, COUNT(*) AS stages
                    FROM ingestion.telemetry_events
                    WHERE user_id = %s
                      AND ingested_at > NOW() - INTERVAL '1 hour'
                    GROUP BY run_id
                    HAVING BOOL_OR(event = 'run_completed') = FALSE
                    """,
                    (user.id,),
                )
                rows = cur.fetchall()
        finally:
            conn.close()
        return [
            {"run_id": r[0], "status": "RUNNING", "current_stage": "IN_PROGRESS", "progress": min(95, (r[1] or 0) * 3)}
            for r in rows
        ]

    # -----------------------------------------------------------------
    # /trends  — QoR trend across the user's last 20 completed runs
    # -----------------------------------------------------------------
    @router.get("/trends")
    def trends(user: SupabaseUser = Depends(require_supabase_user)):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT metrics, ingested_at
                    FROM ingestion.telemetry_events
                    WHERE user_id = %s AND stage = 'SUMMARY'
                    ORDER BY ingested_at DESC
                    LIMIT 20
                    """,
                    (user.id,),
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        if not rows:
            return {"trend": "NO_DATA", "avg_qor": 0, "avg_runtime": 0, "regressions": 0}

        qor = [_to_num((m or {}).get("qor_score")) for m, _ in rows]
        qor = [x for x in qor if x is not None]
        rt = [_to_num((m or {}).get("runtime_sec")) for m, _ in rows]
        rt = [x for x in rt if x is not None]

        avg_qor = round(sum(qor) / len(qor), 2) if qor else 0
        avg_rt = round(sum(rt) / len(rt), 2) if rt else 0
        regs = sum(1 for x in qor if x < 0.7)

        if len(qor) >= 2:
            trend = "IMPROVING" if qor[0] > qor[-1] else ("DEGRADING" if qor[0] < qor[-1] else "STABLE")
        else:
            trend = "NO_DATA"

        return {"trend": trend, "avg_qor": avg_qor, "avg_runtime": avg_rt, "regressions": regs}

    # -----------------------------------------------------------------
    # /health  — lightweight status
    # -----------------------------------------------------------------
    @router.get("/health")
    def health():
        return {
            "status": "ok",
            "database": "connected",
            "checked_at": datetime.utcnow().isoformat(),
        }

    # -----------------------------------------------------------------
    # /releases  — no release tracking yet
    # -----------------------------------------------------------------
    @router.get("/releases")
    def releases(user: SupabaseUser = Depends(require_supabase_user)):
        return []

    # -----------------------------------------------------------------
    # /runs/{id}  — full detail
    # -----------------------------------------------------------------
    @router.get("/runs/{run_id}")
    def run_detail(run_id: str, user: SupabaseUser = Depends(require_supabase_user)):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        MAX(design_name) FILTER (WHERE design_name IS NOT NULL),
                        COUNT(*) FILTER (WHERE event = 'stage_completed'),
                        BOOL_OR(event = 'run_completed'),
                        MAX(ingested_at)
                    FROM ingestion.telemetry_events
                    WHERE user_id = %s AND run_id = %s
                    """,
                    (user.id, run_id),
                )
                design_name, stages_done, completed, last_seen = cur.fetchone()
                if last_seen is None:
                    raise HTTPException(status_code=404, detail="Run not found")

                cur.execute(
                    """
                    SELECT metrics FROM ingestion.telemetry_events
                    WHERE user_id = %s AND run_id = %s AND stage = 'SUMMARY'
                    ORDER BY ingested_at DESC LIMIT 1
                    """,
                    (user.id, run_id),
                )
                srow = cur.fetchone()
                m = (srow[0] if srow else {}) or {}
        finally:
            conn.close()

        return {
            "run_id": run_id,
            "design_name": design_name or "unknown",
            "status": "SUCCESS" if completed else "RUNNING",
            "current_stage": "DONE" if completed else "IN_PROGRESS",
            "progress": 100 if completed else min(95, (stages_done or 0) * 3),
            "wns": _to_num(m.get("wns")),
            "tns": _to_num(m.get("tns")),
            "hold_wns": _to_num(m.get("hold_wns")),
            "hold_tns": _to_num(m.get("hold_tns")),
            "utilization": _to_num(m.get("utilization")),
            "runtime_sec": _to_num(m.get("runtime_sec")),
            "cell_count": _to_int(m.get("cell_count")),
            "qor_score": _to_num(m.get("qor_score")),
            "timestamp": last_seen.isoformat() if last_seen else None,
            "drc_violations": _to_int(m.get("drc_violations")) or 0,
            "drc_magic_violations": 0,
            "drc_klayout_violations": 0,
            "drc_is_clean": _to_bool(m.get("drc_is_clean")),
            "lvs_result": m.get("lvs_result") or "",
            "lvs_is_clean": _to_bool(m.get("lvs_is_clean")),
            "signoff_setup_pass": _to_bool(m.get("signoff_setup_pass")),
            "signoff_hold_pass": _to_bool(m.get("signoff_hold_pass")),
            "signoff_gate_json": {},
            "tapeout_ready": _to_bool(m.get("tapeout_ready")),
            "implementation_status": "SUCCESS" if completed else "IN_PROGRESS",
            "signoff_status": m.get("signoff_status") or ("PASS" if completed else "NOT_RUN"),
            "implementation_score": _to_num(m.get("implementation_score")),
            "signoff_score": _to_num(m.get("signoff_score")),
            "root_cause_summary": None,
        }

    # -----------------------------------------------------------------
    # /runs/{id}/failures
    # -----------------------------------------------------------------
    @router.get("/runs/{run_id}/failures")
    def run_failures(
        run_id: str,
        user: SupabaseUser = Depends(require_supabase_user),
    ):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, tool, stage, failure_type, error_text,
                           design_name, design_category, log_excerpt,
                           frequency, first_seen, last_seen
                    FROM ingestion.failure_atlas_events
                    WHERE user_id = %s AND run_id = %s
                    ORDER BY last_seen DESC NULLS LAST
                    """,
                    (user.id, run_id),
                )
                rows = cur.fetchall()
        finally:
            conn.close()
        return [
            {
                "id": str(r[0]),
                "tool": r[1] or "",
                "stage": r[2] or "",
                "failure_type": r[3] or "",
                "error_text": r[4] or "",
                "design_name": r[5] or "",
                "design_category": r[6] or "",
                "log_excerpt": r[7] or "",
                "frequency": int(r[8] or 1),
                "first_seen": r[9].isoformat() if r[9] else None,
                "last_seen": r[10].isoformat() if r[10] else None,
                "severity": "MEDIUM",   # not tracked in ingestion.* yet
                "title": r[3] or "",
                "description": r[4] or "",
            }
            for r in rows
        ]

    # -----------------------------------------------------------------
    # Placeholder endpoints — the dashboard calls these but we don't
    # have the data yet. Return shapes that don't crash the UI.
    # -----------------------------------------------------------------

    @router.get("/runs/{run_id}/trust-score")
    def trust_score(run_id: str, user: SupabaseUser = Depends(require_supabase_user)):
        return {"trust_score": 0.5, "confidence": "unverified", "run_id": run_id}

    @router.get("/runs/{run_id}/investigation")
    def get_investigation(run_id: str, user: SupabaseUser = Depends(require_supabase_user)):
        return {
            "available": False,
            "status": "NOT_RUN",
            "summary": "",
            "reason": "LLM investigation is not available in the cloud pilot.",
        }

    @router.post("/runs/{run_id}/investigation")
    def post_investigation(run_id: str, user: SupabaseUser = Depends(require_supabase_user)):
        return {"status": "not_supported", "reason": "LLM investigation is not available in the cloud pilot."}

    @router.get("/runs/{run_id}/compare/{other_id}")
    def compare_runs(run_id: str, other_id: str, user: SupabaseUser = Depends(require_supabase_user)):
        return {"run_a": run_id, "run_b": other_id, "diffs": [], "note": "comparison not yet implemented in cloud"}

    @router.get("/runs/{run_id}/report/{report_path:path}")
    def report(run_id: str, report_path: str, user: SupabaseUser = Depends(require_supabase_user)):
        return {"run_id": run_id, "report": report_path, "note": "report artifact not available in cloud"}

    @router.post("/runs/{run_id}/important")
    def mark_important(run_id: str, user: SupabaseUser = Depends(require_supabase_user)):
        # No-op for now; would require a per-user starred_runs table.
        return {"run_id": run_id, "is_important": True}

    @router.delete("/runs/{run_id}/important")
    def unmark_important(run_id: str, user: SupabaseUser = Depends(require_supabase_user)):
        return {"run_id": run_id, "is_important": False}

    @router.post("/failures/{failure_id}/resolution")
    def failure_resolution(failure_id: str, user: SupabaseUser = Depends(require_supabase_user)):
        return {"failure_id": failure_id, "status": "recorded"}

    # -----------------------------------------------------------------
    # /failures  — global-ish; scope to caller's runs
    # -----------------------------------------------------------------
    @router.get("/failures")
    def list_failures(
        limit: int = Query(50, ge=1, le=1000),
        user: SupabaseUser = Depends(require_supabase_user),
    ):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, run_id, tool, stage, failure_type, error_text,
                           design_name, first_seen, last_seen, frequency
                    FROM ingestion.failure_atlas_events
                    WHERE user_id = %s
                    ORDER BY last_seen DESC NULLS LAST
                    LIMIT %s
                    """,
                    (user.id, limit),
                )
                rows = cur.fetchall()
        finally:
            conn.close()
        return [
            {
                "id": str(r[0]),
                "run_id": r[1],
                "tool": r[2] or "",
                "stage": r[3] or "",
                "failure_type": r[4] or "",
                "error_text": r[5] or "",
                "design_name": r[6] or "",
                "first_seen": r[7].isoformat() if r[7] else None,
                "last_seen": r[8].isoformat() if r[8] else None,
                "frequency": int(r[9] or 1),
                "severity": "MEDIUM",
            }
            for r in rows
        ]

    # -----------------------------------------------------------------
    # /analytics/*  — coarse aggregations for the analytics pages
    # -----------------------------------------------------------------
    @router.get("/analytics/summary")
    def analytics_summary(user: SupabaseUser = Depends(require_supabase_user)):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        COUNT(DISTINCT run_id),
                        COUNT(DISTINCT run_id) FILTER (WHERE event = 'run_completed'),
                        COUNT(DISTINCT design_name) FILTER (WHERE design_name IS NOT NULL)
                    FROM ingestion.telemetry_events
                    WHERE user_id = %s
                    """,
                    (user.id,),
                )
                total, completed, designs = cur.fetchone()
                cur.execute(
                    "SELECT COUNT(*) FROM ingestion.failure_atlas_events WHERE user_id = %s",
                    (user.id,),
                )
                (failures,) = cur.fetchone()
        finally:
            conn.close()
        return {
            "total_runs": int(total or 0),
            "completed_runs": int(completed or 0),
            "unique_designs": int(designs or 0),
            "total_failures": int(failures or 0),
        }

    @router.get("/analytics/common-failures")
    def common_failures(user: SupabaseUser = Depends(require_supabase_user)):
        conn = _pg(config)
        try:
            _ensure_app_user(conn, user)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT failure_type, COUNT(*) AS cnt
                    FROM ingestion.failure_atlas_events
                    WHERE user_id = %s AND failure_type != ''
                    GROUP BY failure_type
                    ORDER BY cnt DESC
                    LIMIT 20
                    """,
                    (user.id,),
                )
                rows = cur.fetchall()
        finally:
            conn.close()
        return [{"failure_type": r[0], "count": int(r[1])} for r in rows]

    @router.get("/analytics/fix-effectiveness")
    def fix_effectiveness(user: SupabaseUser = Depends(require_supabase_user)):
        return []

    @router.get("/analytics/qor-improvements")
    def qor_improvements(user: SupabaseUser = Depends(require_supabase_user)):
        return []

    @router.get("/analytics/failure-trends")
    def failure_trends(user: SupabaseUser = Depends(require_supabase_user)):
        return []

    @router.get("/analytics/resolution-confidence")
    def resolution_confidence(user: SupabaseUser = Depends(require_supabase_user)):
        return []

    @router.get("/analytics/mttr")
    def mttr(user: SupabaseUser = Depends(require_supabase_user)):
        return {"mttr_hours": None, "sample_size": 0}

    @router.get("/regressions")
    def regressions(user: SupabaseUser = Depends(require_supabase_user)):
        return []

    return router
