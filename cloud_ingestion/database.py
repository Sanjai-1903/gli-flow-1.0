"""Ingestion DB — SQLite (dev) or Postgres (prod), chosen by config.database.url.

Every write now records a user_id (from Bearer-token auth). Reads and stats
remain global for now; per-user filtering happens in the dashboard via RLS.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone

from cloud_ingestion.config import CloudIngestionConfig


SQLITE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS telemetry_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    run_id TEXT NOT NULL, tool TEXT NOT NULL, stage TEXT NOT NULL,
    event TEXT NOT NULL, design_name TEXT,
    metrics TEXT DEFAULT '{}', details TEXT,
    recorded_at TEXT NOT NULL, ingested_at TEXT NOT NULL,
    source_ip TEXT, upload_batch_id TEXT
);
CREATE TABLE IF NOT EXISTS failure_atlas_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    run_id TEXT NOT NULL, tool TEXT NOT NULL, stage TEXT NOT NULL,
    failure_type TEXT NOT NULL, error_text TEXT,
    design_name TEXT, design_category TEXT, log_excerpt TEXT,
    frequency INTEGER DEFAULT 1,
    first_seen TEXT, last_seen TEXT, ingested_at TEXT NOT NULL,
    upload_batch_id TEXT
);
CREATE TABLE IF NOT EXISTS upload_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    run_id TEXT NOT NULL, batch_id TEXT NOT NULL,
    telemetry_count INTEGER DEFAULT 0, failures_count INTEGER DEFAULT 0,
    escalations_count INTEGER DEFAULT 0,
    source_version TEXT, client_ip TEXT,
    status TEXT NOT NULL DEFAULT 'accepted', error_message TEXT,
    ingested_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS consent_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    run_id TEXT NOT NULL, consent_given INTEGER NOT NULL DEFAULT 0,
    consent_timestamp TEXT, recorded_at TEXT NOT NULL
);
"""


def _is_postgres(url):
    return url.startswith("postgresql://") or url.startswith("postgres://")


class IngestionDatabase:
    def __init__(self, config):
        self.config = config
        self._backend = "postgres" if _is_postgres(config.database.url) else "sqlite"

    @property
    def _db_path(self):
        url = self.config.database.url
        if url.startswith("sqlite:///"):
            p = url[len("sqlite:///"):]
            d = os.path.dirname(p)
            if d: os.makedirs(d, exist_ok=True)
            return p
        return "/tmp/cloud_ingestion_dev.db"

    def _pg(self):
        import psycopg2
        return psycopg2.connect(self.config.database.url)

    def _sq(self):
        c = sqlite3.connect(self._db_path, check_same_thread=False)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL")
        return c

    def initialize(self):
        if self._backend == "postgres":
            c = self._pg()
            try:
                with c.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='ingestion' AND table_name IN ('telemetry_events','failure_atlas_events','upload_audit','consent_records')")
                    (n,) = cur.fetchone()
                    if n < 4: raise RuntimeError(f"Ingestion schema missing tables ({n}/4).")
            finally: c.close()
            return
        c = self._sq()
        try:
            c.executescript(SQLITE_SCHEMA_SQL); c.commit()
        finally: c.close()

    def insert_telemetry_events(self, events, batch_id, source_ip="", user_id=None):
        if not events: return 0
        now = datetime.now(timezone.utc)
        if self._backend == "postgres":
            import psycopg2.extras
            rows = [{"user_id":user_id,"run_id":ev.get("run_id") or "","tool":ev.get("tool") or "","stage":ev.get("stage") or "","event":ev.get("event") or "","design_name":ev.get("design_name"),"metrics":json.dumps(ev.get("metrics",{}),default=str),"details":json.dumps(ev.get("details"),default=str) if ev.get("details") is not None else None,"recorded_at":ev.get("recorded_at") or now.isoformat(),"ingested_at":now,"source_ip":source_ip,"batch_id":batch_id} for ev in events]
            c = self._pg()
            try:
                with c, c.cursor() as cur:
                    psycopg2.extras.execute_batch(cur, "INSERT INTO ingestion.telemetry_events (user_id,run_id,tool,stage,event,design_name,metrics,details,recorded_at,ingested_at,source_ip,upload_batch_id) VALUES (%(user_id)s,%(run_id)s,%(tool)s,%(stage)s,%(event)s,%(design_name)s,%(metrics)s::jsonb,%(details)s::jsonb,%(recorded_at)s,%(ingested_at)s,%(source_ip)s,%(batch_id)s)", rows)
                return len(rows)
            finally: c.close()
        c = self._sq()
        try:
            for ev in events:
                c.execute("INSERT INTO telemetry_events (user_id,run_id,tool,stage,event,design_name,metrics,details,recorded_at,ingested_at,source_ip,upload_batch_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(user_id,ev.get("run_id") or "",ev.get("tool") or "",ev.get("stage") or "",ev.get("event") or "",ev.get("design_name"),json.dumps(ev.get("metrics",{}),default=str),json.dumps(ev.get("details"),default=str),ev.get("recorded_at") or now.isoformat(),now.isoformat(),source_ip,batch_id))
            c.commit()
            return len(events)
        finally: c.close()

    def insert_failure_entries(self, entries, batch_id, user_id=None):
        if not entries: return 0
        now = datetime.now(timezone.utc)
        if self._backend == "postgres":
            import psycopg2.extras
            rows = [{"user_id":user_id,"run_id":e.get("run_id") or "","tool":e.get("tool") or "","stage":e.get("stage") or "","failure_type":e.get("failure_type") or "","error_text":e.get("error_text"),"design_name":e.get("design_name"),"design_category":e.get("design_category"),"log_excerpt":e.get("log_excerpt"),"frequency":e.get("frequency") or 1,"first_seen":e.get("first_seen"),"last_seen":e.get("last_seen"),"ingested_at":now,"batch_id":batch_id} for e in entries]
            c = self._pg()
            try:
                with c, c.cursor() as cur:
                    psycopg2.extras.execute_batch(cur, "INSERT INTO ingestion.failure_atlas_events (user_id,run_id,tool,stage,failure_type,error_text,design_name,design_category,log_excerpt,frequency,first_seen,last_seen,ingested_at,upload_batch_id) VALUES (%(user_id)s,%(run_id)s,%(tool)s,%(stage)s,%(failure_type)s,%(error_text)s,%(design_name)s,%(design_category)s,%(log_excerpt)s,%(frequency)s,%(first_seen)s,%(last_seen)s,%(ingested_at)s,%(batch_id)s)", rows)
                return len(rows)
            finally: c.close()
        c = self._sq()
        try:
            for e in entries:
                c.execute("INSERT INTO failure_atlas_events (user_id,run_id,tool,stage,failure_type,error_text,design_name,design_category,log_excerpt,frequency,first_seen,last_seen,ingested_at,upload_batch_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(user_id,e.get("run_id") or "",e.get("tool") or "",e.get("stage") or "",e.get("failure_type") or "",e.get("error_text"),e.get("design_name"),e.get("design_category"),e.get("log_excerpt"),e.get("frequency") or 1,e.get("first_seen"),e.get("last_seen"),now.isoformat(),batch_id))
            c.commit()
            return len(entries)
        finally: c.close()

    def record_upload_audit(self, run_id, batch_id, telemetry_count, failures_count, escalations_count, source_version="", client_ip="", status="accepted", error_message="", user_id=None):
        now = datetime.now(timezone.utc)
        if self._backend == "postgres":
            c = self._pg()
            try:
                with c, c.cursor() as cur:
                    cur.execute("INSERT INTO ingestion.upload_audit (user_id,run_id,batch_id,telemetry_count,failures_count,escalations_count,source_version,client_ip,status,error_message,ingested_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",(user_id,run_id,batch_id,telemetry_count,failures_count,escalations_count,source_version,client_ip,status,error_message,now))
                    return cur.fetchone()[0]
            finally: c.close()
        c = self._sq()
        try:
            cur = c.execute("INSERT INTO upload_audit (user_id,run_id,batch_id,telemetry_count,failures_count,escalations_count,source_version,client_ip,status,error_message,ingested_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(user_id,run_id,batch_id,telemetry_count,failures_count,escalations_count,source_version,client_ip,status,error_message,now.isoformat()))
            c.commit()
            return cur.lastrowid or 0
        finally: c.close()

    def record_consent(self, run_id, consent_given, consent_timestamp="", user_id=None):
        now = datetime.now(timezone.utc)
        if self._backend == "postgres":
            c = self._pg()
            try:
                with c, c.cursor() as cur:
                    cur.execute("INSERT INTO ingestion.consent_records (user_id,run_id,consent_given,consent_timestamp,recorded_at) VALUES (%s,%s,%s,%s,%s)",(user_id,run_id,consent_given,consent_timestamp,now))
            finally: c.close()
            return
        c = self._sq()
        try:
            c.execute("INSERT INTO consent_records (user_id,run_id,consent_given,consent_timestamp,recorded_at) VALUES (?,?,?,?,?)",(user_id,run_id,1 if consent_given else 0,consent_timestamp,now.isoformat()))
            c.commit()
        finally: c.close()

    def get_stats(self, user_id=None):
        """Aggregate stats. If user_id given, scope to that user."""
        if self._backend == "postgres":
            c = self._pg()
            try:
                with c.cursor() as cur:
                    s = {}
                    if user_id:
                        cur.execute("SELECT COUNT(*) FROM ingestion.telemetry_events WHERE user_id = %s", (user_id,)); s["total_telemetry_events"] = cur.fetchone()[0]
                        cur.execute("SELECT COUNT(*) FROM ingestion.failure_atlas_events WHERE user_id = %s", (user_id,)); s["total_failure_atlas_entries"] = cur.fetchone()[0]
                        cur.execute("SELECT COUNT(*) FROM ingestion.upload_audit WHERE user_id = %s", (user_id,)); s["total_uploads"] = cur.fetchone()[0]
                        cur.execute("SELECT COUNT(DISTINCT run_id) FROM ingestion.upload_audit WHERE user_id = %s", (user_id,)); s["unique_runs"] = cur.fetchone()[0]
                        cur.execute("SELECT COUNT(DISTINCT design_name) FROM ingestion.failure_atlas_events WHERE user_id = %s", (user_id,)); s["unique_designs"] = cur.fetchone()[0]
                    else:
                        cur.execute("SELECT COUNT(*) FROM ingestion.telemetry_events"); s["total_telemetry_events"] = cur.fetchone()[0]
                        cur.execute("SELECT COUNT(*) FROM ingestion.failure_atlas_events"); s["total_failure_atlas_entries"] = cur.fetchone()[0]
                        cur.execute("SELECT COUNT(*) FROM ingestion.upload_audit"); s["total_uploads"] = cur.fetchone()[0]
                        cur.execute("SELECT COUNT(DISTINCT run_id) FROM ingestion.upload_audit"); s["unique_runs"] = cur.fetchone()[0]
                        cur.execute("SELECT COUNT(DISTINCT design_name) FROM ingestion.failure_atlas_events"); s["unique_designs"] = cur.fetchone()[0]
                    s["db_size_bytes"] = 0
                    return s
            finally: c.close()
        c = self._sq()
        try:
            s = {}
            if user_id:
                s["total_telemetry_events"] = c.execute("SELECT COUNT(*) FROM telemetry_events WHERE user_id = ?", (user_id,)).fetchone()[0]
                s["total_failure_atlas_entries"] = c.execute("SELECT COUNT(*) FROM failure_atlas_events WHERE user_id = ?", (user_id,)).fetchone()[0]
                s["total_uploads"] = c.execute("SELECT COUNT(*) FROM upload_audit WHERE user_id = ?", (user_id,)).fetchone()[0]
                s["unique_runs"] = c.execute("SELECT COUNT(DISTINCT run_id) FROM upload_audit WHERE user_id = ?", (user_id,)).fetchone()[0]
                s["unique_designs"] = c.execute("SELECT COUNT(DISTINCT design_name) FROM failure_atlas_events WHERE user_id = ?", (user_id,)).fetchone()[0]
            else:
                s["total_telemetry_events"] = c.execute("SELECT COUNT(*) FROM telemetry_events").fetchone()[0]
                s["total_failure_atlas_entries"] = c.execute("SELECT COUNT(*) FROM failure_atlas_events").fetchone()[0]
                s["total_uploads"] = c.execute("SELECT COUNT(*) FROM upload_audit").fetchone()[0]
                s["unique_runs"] = c.execute("SELECT COUNT(DISTINCT run_id) FROM upload_audit").fetchone()[0]
                s["unique_designs"] = c.execute("SELECT COUNT(DISTINCT design_name) FROM failure_atlas_events").fetchone()[0]
            try: s["db_size_bytes"] = os.path.getsize(self._db_path)
            except OSError: s["db_size_bytes"] = 0
            return s
        finally: c.close()

    def close(self): pass
