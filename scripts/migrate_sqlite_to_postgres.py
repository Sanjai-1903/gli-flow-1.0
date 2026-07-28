#!/usr/bin/env python3
"""
SQLite → PostgreSQL Migration Tool.

Migrates all data from a SQLite database to PostgreSQL (Supabase).

Usage:
    # Dry run (validate only, no writes)
    python scripts/migrate_sqlite_to_postgres.py --dry-run

    # Full migration with resume support
    DATABASE_URL=postgresql://... python scripts/migrate_sqlite_to_postgres.py --confirm

    # Single table migration
    python scripts/migrate_sqlite_to_postgres.py --table runs --confirm

    # Resume from checkpoint
    python scripts/migrate_sqlite_to_postgres.py --confirm --resume

Environment:
    DATABASE_URL    = target PostgreSQL connection string (required for --confirm)
    GLI_FLOW_DB     = source SQLite database path (optional, defaults to ~/.gli_flow/gli_flow.db)
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CHECKPOINT_FILE = "migration_checkpoint.json"
REPORT_FILE = "migration_report.json"

MIGRATION_ORDER = [
    "schema_version",
    "runs",
    "failure_atlas_entries",
    "ai_investigation_feedback",
    "ai_resolution_capture",
    "community_escalations",
    "community_telemetry",
    "community_unknown_dataset",
    "resolution_patterns",
    "resolution_feedback",
    "execution_intelligence",
    "feedback_records",
    "user_journey_events",
    "resolution_tracking",
    "telemetry_audit_log",
    "design_features",
    "design_profiles",
    "telemetry_execution_records",
    "telemetry_recommendation_records",
    "upload_queue",
]

BATCH_SIZE = 500

TIMESTAMP_COLUMNS = {
    "runs": ["timestamp", "created_at", "updated_at", "important_marked_at",
             "llm_investigation_timestamp"],
    "failure_atlas_entries": ["detected_at", "created_at", "first_seen", "last_seen"],
    "resolution_patterns": ["first_seen", "last_seen", "created_at", "updated_at"],
    "resolution_feedback": ["created_at"],
    "community_escalations": ["created_at", "sent_at", "resolved_at"],
    "community_telemetry": ["created_at"],
    "community_unknown_dataset": ["last_seen"],
    "ai_investigation_feedback": ["created_at"],
    "ai_resolution_capture": ["created_at"],
    "execution_intelligence": ["timestamp"],
    "feedback_records": ["created_at", "updated_at"],
    "user_journey_events": ["created_at"],
    "resolution_tracking": ["suggested_at", "accepted_at", "rejected_at", "created_at"],
    "telemetry_audit_log": ["recorded_at"],
    "design_features": ["created_at"],
    "design_profiles": ["created_at", "updated_at"],
    "telemetry_execution_records": ["created_at"],
    "telemetry_recommendation_records": ["timestamp"],
    "upload_queue": ["created_at", "next_retry_at"],
    "schema_version": ["applied_at"],
}

BOOLEAN_COLUMNS = {
    "runs": ["drc_is_clean", "lvs_is_clean", "signoff_setup_pass",
             "signoff_hold_pass", "tapeout_ready", "is_important",
             "llm_investigation_available", "regression"],
    "failure_atlas_entries": ["fix_applied", "regression_detected"],
    "community_escalations": ["consent_given"],
    "community_unknown_dataset": ["consent_given"],
    "ai_investigation_feedback": ["resolved"],
    "resolution_tracking": ["success_verified"],
    "feedback_records": [],
    "telemetry_recommendation_records": ["accepted", "rejected"],
}

JSON_COLUMNS = {
    "runs": ["signoff_gate_json", "tags", "llm_investigation_failed_attempts"],
    "failure_atlas_entries": ["recommended_fix", "evidence", "before_metrics",
                               "after_metrics", "artifact_snapshot", "execution_snapshot",
                               "timing_snapshot", "utilization_snapshot",
                               "congestion_snapshot", "runtime_snapshot"],
    "community_escalations": ["engineer_response"],
    "community_telemetry": ["details"],
    "resolution_patterns": ["tracked_run_ids", "tracked_design_names"],
    "design_features": ["fanout_histogram"],
    "telemetry_execution_records": ["telemetry_summary"],
    "feedback_records": ["tool_versions", "telemetry_health_summary"],
    "user_journey_events": ["details"],
    "execution_intelligence": ["failure_context", "root_cause_analysis", "resolution"],
    "upload_queue": ["payload"],
}


class MigrationCheckpointer:
    def __init__(self, checkpoint_file: str = CHECKPOINT_FILE):
        self.checkpoint_file = checkpoint_file
        self.state: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if Path(self.checkpoint_file).exists():
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {"completed_tables": [], "in_progress": None, "last_row": {}}

    def save(self):
        with open(self.checkpoint_file, "w") as f:
            json.dump(self.state, f, indent=2, default=str)

    def is_table_completed(self, table: str) -> bool:
        return table in self.state["completed_tables"]

    def mark_table_started(self, table: str):
        self.state["in_progress"] = table

    def mark_table_completed(self, table: str):
        if table not in self.state["completed_tables"]:
            self.state["completed_tables"].append(table)
        self.state["in_progress"] = None
        self.state["last_row"].pop(table, None)
        self.save()

    def get_last_row(self, table: str) -> Optional[str]:
        return self.state["last_row"].get(table)

    def set_last_row(self, table: str, last_id: str):
        self.state["last_row"][table] = last_id
        self.save()

    def clear(self):
        self.state = {"completed_tables": [], "in_progress": None, "last_row": {}}


class MigrationReporter:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def add_result(self, table: str, source_count: int, dest_count: int,
                   status: str, error: Optional[str] = None,
                   duration_sec: float = 0.0):
        self.results.append({
            "table": table,
            "source_count": source_count,
            "dest_count": dest_count,
            "match": source_count == dest_count if dest_count is not None else False,
            "status": status,
            "error": error,
            "duration_sec": round(duration_sec, 2),
        })

    def generate_report(self) -> Dict[str, Any]:
        total_duration = time.time() - self.start_time
        success_count = sum(1 for r in self.results if r["status"] == "OK")
        fail_count = sum(1 for r in self.results if r["status"] == "FAILED")
        skip_count = sum(1 for r in self.results if r["status"] == "SKIPPED")
        return {
            "migration_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_duration_sec": round(total_duration, 2),
            "tables_total": len(self.results),
            "tables_succeeded": success_count,
            "tables_failed": fail_count,
            "tables_skipped": skip_count,
            "results": self.results,
            "overall_status": "SUCCESS" if fail_count == 0 else "PARTIAL",
        }

    def save(self, filepath: str = REPORT_FILE):
        report = self.generate_report()
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nMigration report saved to: {filepath}")
        return report


def get_sqlite_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_pg_connection(database_url: str):
    import psycopg2
    return psycopg2.connect(database_url)


def get_row_count(conn, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def parse_timestamp(val: Any) -> Any:
    if val is None or val == "":
        return None
    try:
        dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
        return dt.isoformat()
    except (ValueError, TypeError):
        return val


def transform_row(table: str, row: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(row)
    for col in TIMESTAMP_COLUMNS.get(table, []):
        if col in result:
            result[col] = parse_timestamp(result[col])
    for col in BOOLEAN_COLUMNS.get(table, []):
        if col in result:
            val = result[col]
            if isinstance(val, int):
                result[col] = bool(val)
            elif isinstance(val, str):
                result[col] = val.lower() in ("1", "true", "yes")
    for col in JSON_COLUMNS.get(table, []):
        if col in result and isinstance(result[col], str):
            try:
                result[col] = json.loads(result[col]) if result[col] else None
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def get_columns(conn, table: str) -> List[str]:
    cursor = conn.execute(f"SELECT * FROM {table} LIMIT 0")
    return [desc[0] for desc in cursor.description]


def get_pg_columns(cur, table: str, schema: str = "public") -> List[str]:
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
        (schema, table),
    )
    return [row[0] for row in cur.fetchall()]


def get_primary_key(conn, table: str) -> Optional[str]:
    try:
        cursor = conn.execute(f"SELECT * FROM {table} LIMIT 0")
        desc = cursor.description
        for i, d in enumerate(desc):
            if d[0].lower() in ("id", "run_id", "design_name"):
                return d[0]
        return desc[0][0]
    except Exception:
        return None


def migrate_table(sqlite_path: str, pg_url: str, table: str,
                  dry_run: bool = False, resume: bool = False,
                  checkpointer: Optional[MigrationCheckpointer] = None,
                  reporter: Optional[MigrationReporter] = None) -> Tuple[int, int, str]:
    sqlite_conn = get_sqlite_connection(sqlite_path)
    pg_conn = get_pg_connection(pg_url)
    pg_cur = pg_conn.cursor()
    t_start = time.time()

    try:
        source_count = get_row_count(sqlite_conn, table)
        if source_count == 0:
            msg = f"  {table}: source is empty (0 rows)"
            if reporter:
                reporter.add_result(table, 0, 0, "SKIPPED", duration_sec=time.time() - t_start)
            return 0, 0, "SKIPPED"

        pg_count_before = get_row_count(pg_conn, table)

        pk = get_primary_key(sqlite_conn, table)
        columns = get_columns(sqlite_conn, table)

        if resume and checkpointer and checkpointer.is_table_completed(table):
            msg = f"  {table}: already completed (resume)"
            return source_count, source_count, "SKIPPED"

        last_id = None
        if resume and checkpointer:
            last_id = checkpointer.get_last_row(table)

        if not dry_run:
            checkpointer and checkpointer.mark_table_started(table)

        offset = 0
        migrated = 0
        sqlite_columns = columns

        pg_columns = get_pg_columns(pg_cur, table)
        common_cols = [c for c in sqlite_columns if c in pg_columns]

        placeholders = ", ".join(f"%({c})s" for c in common_cols)
        col_names = ", ".join(common_cols)
        insert_sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

        if last_id and pk:
            row = sqlite_conn.execute(
                f"SELECT rowid FROM {table} WHERE {pk} = ?", (last_id,)
            ).fetchone()
            if row:
                offset = row[0]

        while True:
            rows = sqlite_conn.execute(
                f"SELECT * FROM {table} LIMIT {BATCH_SIZE} OFFSET {offset}"
            ).fetchall()

            if not rows:
                break

            if not dry_run:
                for row in rows:
                    row_dict = transform_row(table, dict(row))
                    filtered = {c: row_dict.get(c) for c in common_cols}
                    try:
                        pg_cur.execute(insert_sql, filtered)
                    except Exception as e:
                        pg_conn.rollback()
                        raise
                pg_conn.commit()

            migrated += len(rows)
            offset += BATCH_SIZE

            if pk and not dry_run:
                last_row = rows[-1]
                checkpointer and checkpointer.set_last_row(table, str(last_row[pk]))

            if dry_run:
                print(f"  {table}: would migrate {len(rows)} rows (batch at offset {offset - BATCH_SIZE})", flush=True)

        pg_count_after = get_row_count(pg_conn, table) if not dry_run else source_count
        match = source_count == pg_count_after

        status = "OK" if (match or dry_run) else "ROW_MISMATCH"
        if dry_run:
            status = "DRY_RUN"

        if not dry_run:
            checkpointer and checkpointer.mark_table_completed(table)

        duration = time.time() - t_start
        msg = f"  {table}: {source_count} source → {pg_count_after if not dry_run else '?'} dest | {status} | {duration:.1f}s"

        if reporter:
            reporter.add_result(table, source_count,
                                pg_count_after if not dry_run else None,
                                status, duration_sec=duration)

        return source_count, pg_count_after if not dry_run else source_count, status

    except Exception as e:
        pg_conn and pg_conn.rollback()
        duration = time.time() - t_start
        error_msg = str(e)
        print(f"  {table}: FAILED — {error_msg}", file=sys.stderr)
        if reporter:
            reporter.add_result(table, 0, 0, "FAILED", error=error_msg, duration_sec=duration)
        return 0, 0, "FAILED"
    finally:
        sqlite_conn.close()
        pg_conn and pg_conn.close()


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite database to PostgreSQL")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, no writes")
    parser.add_argument("--confirm", action="store_true", help="Execute migration")
    parser.add_argument("--table", type=str, help="Single table to migrate")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--sqlite-path", type=str, help="Source SQLite database path")
    parser.add_argument("--pg-url", type=str, help="Target PostgreSQL URL")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help=f"Batch size (default: {BATCH_SIZE})")
    args = parser.parse_args()

    if not args.dry_run and not args.confirm:
        parser.error("Specify --dry-run (validate) or --confirm (execute)")

    sqlite_path = args.sqlite_path or os.environ.get("GLI_FLOW_DB") or str(Path.home() / ".gli_flow" / "gli_flow.db")
    pg_url = args.pg_url or os.environ.get("DATABASE_URL")

    if args.confirm and not pg_url:
        parser.error("DATABASE_URL must be set for --confirm")

    global BATCH_SIZE
    if args.batch_size:
        BATCH_SIZE = args.batch_size

    if not Path(sqlite_path).exists():
        print(f"ERROR: SQLite database not found at {sqlite_path}", file=sys.stderr)
        sys.exit(1)

    if args.confirm:
        try:
            import psycopg2
            test_conn = psycopg2.connect(pg_url)
            test_conn.close()
        except ImportError:
            print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Cannot connect to PostgreSQL: {e}", file=sys.stderr)
            sys.exit(1)

    checkpointer = MigrationCheckpointer() if args.resume else None
    reporter = MigrationReporter() if args.confirm or args.dry_run else None

    if args.resume:
        print(f"Resuming from checkpoint...")
        print(f"  Completed: {checkpointer.state['completed_tables']}")

    tables_to_migrate = [args.table] if args.table else MIGRATION_ORDER

    print(f"{'DRY RUN' if args.dry_run else 'MIGRATION'} — {sqlite_path} → {pg_url or '(dry-run)'}")
    print(f"Tables to process: {len(tables_to_migrate)}")
    print()

    total_source = 0
    total_dest = 0
    failed_tables = []

    for table in tables_to_migrate:
        if checkpointer and checkpointer.is_table_completed(table):
            print(f"  {table}: already completed (skipping)")
            continue

        print(f"→ {table}...", flush=True)
        src, dst, status = migrate_table(
            sqlite_path, pg_url, table,
            dry_run=args.dry_run,
            resume=args.resume,
            checkpointer=checkpointer,
            reporter=reporter,
        )
        total_source += src
        if dst is not None:
            total_dest += dst
        if status == "FAILED":
            failed_tables.append(table)

    print()
    print("=" * 60)
    print(f"Total source rows: {total_source}")
    print(f"Total dest rows:   {total_dest}")
    print(f"Failed tables:     {len(failed_tables)}")
    if failed_tables:
        print(f"  Failed: {', '.join(failed_tables)}")
    print(f"Overall:           {'SUCCESS' if not failed_tables else 'PARTIAL FAILURE'}")

    if reporter:
        report = reporter.save()
        if report["overall_status"] != "SUCCESS" and args.confirm:
            sys.exit(1)

    if args.dry_run:
        print("\nDry run complete. Run with --confirm to execute.")

    return 0 if not failed_tables else 1


if __name__ == "__main__":
    sys.exit(main())
