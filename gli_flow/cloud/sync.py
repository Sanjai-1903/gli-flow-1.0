"""Offline-first sync engine.

Design goals:
    - `gli-flow run` always writes locally, whether online or not.
    - `gli-flow sync` (and the daemon) drain any local runs that haven't
      been uploaded to the cloud yet.
    - Successfully synced runs are retained on disk for 7 days (so the
      student can inspect their own JSON), then purged.

State: ~/.gli-flow/sync.db (SQLite)
    sync_state(
        run_id       PK,
        run_dir,               -- absolute path on disk
        status,                -- 'pending' | 'synced' | 'failed'
        synced_at,
        error_message,
        attempt_count,
        last_attempt_at,
        purged_at              -- when local files were deleted
    )
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import httpx

from gli_flow.cloud import auth as cloud_auth

logger = logging.getLogger(__name__)


SYNC_DIR = Path.home() / ".gli-flow"
SYNC_DB = SYNC_DIR / "sync.db"

DEFAULT_RUNS_ROOT = Path(os.environ.get("GLI_RUNS_ROOT", "outputs/runs"))
RETENTION_DAYS = int(os.environ.get("GLI_RETENTION_DAYS", "7"))
DAEMON_INTERVAL_SEC = int(os.environ.get("GLI_SYNC_INTERVAL_SEC", "60"))
MAX_RETRY_COUNT = int(os.environ.get("GLI_SYNC_MAX_RETRIES", "20"))

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sync_state (
    run_id           TEXT PRIMARY KEY,
    run_dir          TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'pending',
    synced_at        TEXT,
    error_message    TEXT,
    attempt_count    INTEGER NOT NULL DEFAULT 0,
    last_attempt_at  TEXT,
    purged_at        TEXT,
    created_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_state(status);
CREATE INDEX IF NOT EXISTS idx_sync_synced_at ON sync_state(synced_at);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    SYNC_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SYNC_DB), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    return conn


# ---------- Payload construction (mirrors upload_run.py) ----------

def _flatten_metrics(d):
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, (int, float, str, bool)) or v is None:
            out[k] = v
    return out


def build_payload(run_dir: Path) -> Optional[dict]:
    """Read a run directory and produce an UploadPayload dict.

    Returns None if the run directory has no telemetry to upload.
    """
    if not run_dir.is_dir():
        return None
    tele_dir = run_dir / "telemetry"
    if not tele_dir.is_dir():
        return None

    metrics_path = tele_dir / "metrics.json"
    metrics = {}
    if metrics_path.exists():
        try:
            metrics = json.loads(metrics_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    design_name = metrics.get("design_name", "unknown") if metrics else "unknown"
    pdk = metrics.get("pdk", "") if metrics else ""
    now_iso = _now_iso()

    telemetry_events = []
    for stage_file in sorted(tele_dir.glob("*.json")):
        if stage_file.name == "metrics.json":
            continue
        try:
            stage_data = json.loads(stage_file.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        telemetry_events.append({
            "run_id": run_dir.name,
            "tool": "gli-flow",
            "stage": stage_file.stem.upper(),
            "event": "stage_completed",
            "design_name": design_name,
            "metrics": _flatten_metrics(stage_data),
            "recorded_at": now_iso,
        })

    if metrics:
        telemetry_events.append({
            "run_id": run_dir.name,
            "tool": "gli-flow",
            "stage": "SUMMARY",
            "event": "run_completed",
            "design_name": design_name,
            "metrics": _flatten_metrics(metrics.get("metrics", {})),
            "details": {"pdk": pdk, "pdk_variant": metrics.get("pdk_variant", "")},
            "recorded_at": now_iso,
        })

    failure_entries = []
    ai_path = run_dir / "ai_explanation.json"
    if ai_path.exists():
        try:
            ai = json.loads(ai_path.read_text())
            if ai.get("summary") or ai.get("likely_cause"):
                failure_entries.append({
                    "run_id": run_dir.name,
                    "tool": "gli-flow",
                    "stage": "UNKNOWN",
                    "failure_type": "AI_EXPLANATION",
                    "error_text": (ai.get("summary") or "")[:1000],
                    "design_name": design_name,
                    "last_seen": now_iso,
                    "detected_at": now_iso,
                })
        except (json.JSONDecodeError, OSError):
            pass

    if not telemetry_events and not failure_entries:
        return None

    return {
        "run_id": run_dir.name,
        "source_version": "gli-flow-cli/sync-1.0",
        "telemetry_events": telemetry_events,
        "failure_atlas_entries": failure_entries,
        "escalations": [],
    }


# ---------- Sync engine ----------

class SyncEngine:
    def __init__(
        self,
        runs_root: Path = DEFAULT_RUNS_ROOT,
        retention_days: int = RETENTION_DAYS,
    ):
        self.runs_root = Path(runs_root).resolve()
        self.retention_days = retention_days

    def _discover_new_runs(self, conn: sqlite3.Connection) -> int:
        """Scan the runs root and INSERT any newly-seen runs as 'pending'."""
        if not self.runs_root.is_dir():
            return 0
        known = {row["run_id"] for row in conn.execute("SELECT run_id FROM sync_state")}
        added = 0
        for entry in self.runs_root.iterdir():
            if not entry.is_dir():
                continue
            if entry.name in known:
                continue
            # Only enqueue runs that actually have telemetry
            if not (entry / "telemetry").is_dir():
                continue
            conn.execute(
                "INSERT INTO sync_state (run_id, run_dir, status, created_at) VALUES (?, ?, 'pending', ?)",
                (entry.name, str(entry), _now_iso()),
            )
            added += 1
        conn.commit()
        return added

    def _pending_rows(self, conn: sqlite3.Connection):
        return list(conn.execute(
            "SELECT * FROM sync_state WHERE status IN ('pending','failed') "
            "AND attempt_count < ? ORDER BY created_at ASC",
            (MAX_RETRY_COUNT,),
        ))

    def sync_once(self, dry_run: bool = False) -> dict:
        """One-shot: discover new runs, then attempt to sync every pending row.

        Returns { attempted, synced, failed, skipped }.
        """
        conn = _connect()
        try:
            self._discover_new_runs(conn)
            rows = self._pending_rows(conn)
            attempted = 0
            synced = 0
            failed = 0
            skipped = 0

            try:
                auth_state = cloud_auth.load_auth()
                ingest_url = auth_state.ingest_url
                token = auth_state.token
            except cloud_auth.NotLoggedInError:
                if dry_run:
                    # Still show what would be attempted
                    ingest_url = cloud_auth.DEFAULT_INGEST_URL
                    token = None
                else:
                    raise

            with httpx.Client(timeout=60.0) as client:
                for row in rows:
                    attempted += 1
                    run_dir = Path(row["run_dir"])
                    payload = build_payload(run_dir)
                    if payload is None:
                        skipped += 1
                        continue
                    if dry_run:
                        logger.info(
                            "[dry-run] would POST run=%s (events=%d failures=%d)",
                            row["run_id"],
                            len(payload.get("telemetry_events", [])),
                            len(payload.get("failure_atlas_entries", [])),
                        )
                        skipped += 1
                        continue
                    try:
                        headers = {"Authorization": f"Bearer {token}"}
                        resp = client.post(
                            ingest_url.rstrip("/") + "/api/v1/telemetry",
                            json=payload,
                            headers=headers,
                        )
                        resp.raise_for_status()
                        conn.execute(
                            "UPDATE sync_state SET status='synced', synced_at=?, "
                            "attempt_count=attempt_count+1, last_attempt_at=?, error_message=NULL "
                            "WHERE run_id=?",
                            (_now_iso(), _now_iso(), row["run_id"]),
                        )
                        conn.commit()
                        synced += 1
                    except Exception as e:
                        msg = f"{type(e).__name__}: {e}"[:500]
                        conn.execute(
                            "UPDATE sync_state SET status='failed', attempt_count=attempt_count+1, "
                            "last_attempt_at=?, error_message=? WHERE run_id=?",
                            (_now_iso(), msg, row["run_id"]),
                        )
                        conn.commit()
                        failed += 1
                        logger.warning("Sync failed for run=%s: %s", row["run_id"], msg)

            return {"attempted": attempted, "synced": synced, "failed": failed, "skipped": skipped}
        finally:
            conn.close()

    def run_daemon(self):
        """Sync forever, sleeping DAEMON_INTERVAL_SEC between passes."""
        while True:
            try:
                stats = self.sync_once()
                if stats["attempted"] > 0:
                    logger.info(
                        "sync pass: attempted=%d synced=%d failed=%d skipped=%d",
                        stats["attempted"], stats["synced"], stats["failed"], stats["skipped"],
                    )
            except cloud_auth.NotLoggedInError:
                logger.warning("Daemon: not logged in; stopping.")
                return
            except KeyboardInterrupt:
                logger.info("Daemon: interrupt; stopping.")
                return
            except Exception as e:
                logger.warning("Daemon: transient error: %s", e)
            try:
                # Also purge every pass
                self.purge_old_synced()
            except Exception as e:
                logger.warning("Daemon: purge error: %s", e)
            time.sleep(DAEMON_INTERVAL_SEC)

    # ---------- Retention ----------

    def purge_old_synced(self) -> int:
        """Delete on-disk run dirs for runs synced > retention_days ago.

        Returns number of directories deleted.
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(days=self.retention_days)).isoformat()
        conn = _connect()
        try:
            rows = list(conn.execute(
                "SELECT run_id, run_dir FROM sync_state "
                "WHERE status='synced' AND synced_at IS NOT NULL AND synced_at <= ? "
                "AND purged_at IS NULL",
                (cutoff,),
            ))
            deleted = 0
            for row in rows:
                run_dir = Path(row["run_dir"])
                try:
                    if run_dir.is_dir():
                        shutil.rmtree(run_dir)
                        deleted += 1
                    conn.execute(
                        "UPDATE sync_state SET purged_at=? WHERE run_id=?",
                        (_now_iso(), row["run_id"]),
                    )
                except OSError as e:
                    logger.warning("Purge failed for %s: %s", run_dir, e)
            conn.commit()
            return deleted
        finally:
            conn.close()

    # ---------- Introspection ----------

    def queue_stats(self) -> dict:
        conn = _connect()
        try:
            total = conn.execute("SELECT COUNT(*) FROM sync_state").fetchone()[0]
            by_status = {
                row["status"]: row["cnt"]
                for row in conn.execute("SELECT status, COUNT(*) AS cnt FROM sync_state GROUP BY status")
            }
            return {"total": total, "by_status": by_status}
        finally:
            conn.close()

    def retention_stats(self) -> dict:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=self.retention_days)).isoformat()
        conn = _connect()
        try:
            on_disk = conn.execute(
                "SELECT COUNT(*) FROM sync_state WHERE status='synced' AND purged_at IS NULL"
            ).fetchone()[0]
            eligible = conn.execute(
                "SELECT COUNT(*) FROM sync_state "
                "WHERE status='synced' AND synced_at <= ? AND purged_at IS NULL",
                (cutoff,),
            ).fetchone()[0]
            return {
                "synced_runs_on_disk": on_disk,
                "eligible_for_purge": eligible,
                "retention_days": self.retention_days,
            }
        finally:
            conn.close()


# ---------- Hook for orchestrator ----------

def notify_run_completed(run_id: str, run_dir: Optional[Path] = None) -> None:
    """Called at end of `gli-flow run`. Enqueue the run and best-effort sync.

    Never raises — the run has already succeeded on disk; sync is opportunistic.
    """
    try:
        conn = _connect()
        try:
            if run_dir is None:
                run_dir = DEFAULT_RUNS_ROOT / run_id
            run_dir = Path(run_dir).resolve()
            conn.execute(
                "INSERT OR IGNORE INTO sync_state (run_id, run_dir, status, created_at) "
                "VALUES (?, ?, 'pending', ?)",
                (run_id, str(run_dir), _now_iso()),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        logger.debug("notify_run_completed enqueue failed: %s", e)
        return

    # Try to sync inline, but never block or error out.
    try:
        if cloud_auth.is_logged_in():
            SyncEngine().sync_once()
    except Exception as e:
        logger.debug("notify_run_completed sync failed (will retry): %s", e)
