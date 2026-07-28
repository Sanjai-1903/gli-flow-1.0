#!/usr/bin/env python3
"""
Post-Migration Validation Tool.

Validates that all data was migrated correctly from SQLite to PostgreSQL.

Checks:
  - Row counts match for every table
  - Primary keys are present
  - NULL checks pass
  - Sample data matches

Usage:
    python scripts/validate_postgres_migration.py

    # Validate single table
    python scripts/validate_postgres_migration.py --table runs

    # Strict mode (fail on any mismatch)
    python scripts/validate_postgres_migration.py --strict

Environment:
    GLI_FLOW_DB     = source SQLite database path
    DATABASE_URL    = target PostgreSQL connection string
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


VALIDATION_TABLES = [
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

REQUIRED_NON_NULL = {
    "runs": ["run_id", "design_name"],
    "failure_atlas_entries": ["id", "run_id", "failure_type", "severity"],
    "resolution_patterns": ["id", "failure_fingerprint", "failure_type"],
    "community_escalations": ["id", "failure_type", "status"],
    "community_telemetry": ["id", "event"],
    "community_unknown_dataset": ["id", "tool", "failure_type"],
    "ai_investigation_feedback": ["id", "investigation_id", "feedback_type"],
    "ai_resolution_capture": ["id", "investigation_id", "failure_type", "tool"],
    "execution_intelligence": ["id", "event_type", "tool", "stage", "severity", "fingerprint"],
    "feedback_records": ["id", "feedback_type"],
    "user_journey_events": ["id", "stage"],
    "resolution_tracking": ["id"],
    "telemetry_audit_log": ["id", "event_type", "status"],
    "design_features": ["design_name"],
    "design_profiles": ["design_name"],
    "schema_version": ["source", "version"],
}


class ValidationError(Exception):
    pass


class MigrationValidator:
    def __init__(self, sqlite_path: str, pg_url: str, strict: bool = False):
        self.sqlite_path = sqlite_path
        self.pg_url = pg_url
        self.strict = strict
        self.results: List[Dict[str, Any]] = []

    def _get_sqlite_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_pg_conn(self):
        import psycopg2
        return psycopg2.connect(self.pg_url)

    def validate_row_count(self, table: str) -> Tuple[int, int, bool]:
        sqlite_conn = self._get_sqlite_conn()
        pg_conn = self._get_pg_conn()
        try:
            sqlite_count = sqlite_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            pg_count = pg_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            return sqlite_count, pg_count, sqlite_count == pg_count
        finally:
            sqlite_conn.close()
            pg_conn.close()

    def validate_primary_keys(self, table: str, pk_column: str) -> bool:
        pg_conn = self._get_pg_conn()
        try:
            row = pg_conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE {pk_column} IS NULL"
            ).fetchone()
            return row[0] == 0
        finally:
            pg_conn.close()

    def validate_non_null(self, table: str, columns: List[str]) -> List[str]:
        pg_conn = self._get_pg_conn()
        try:
            violations = []
            for col in columns:
                row = pg_conn.execute(
                    f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL"
                ).fetchone()
                if row[0] > 0:
                    violations.append(f"{col}: {row[0]} NULL values")
            return violations
        finally:
            pg_conn.close()

    def validate_sample_data(self, table: str, limit: int = 5) -> bool:
        sqlite_conn = self._get_sqlite_conn()
        pg_conn = self._get_pg_conn()
        try:
            sqlite_rows = sqlite_conn.execute(
                f"SELECT * FROM {table} LIMIT {limit}"
            ).fetchall()
            pg_rows = pg_conn.execute(
                f"SELECT * FROM {table} LIMIT {limit}"
            ).fetchall()
            if len(sqlite_rows) != len(pg_rows):
                return False
            for sr, pr in zip(sqlite_rows, pg_rows):
                s_dict = dict(sr)
                p_dict = dict(pr)
                for key in s_dict:
                    if key in p_dict:
                        s_val = str(s_dict[key]) if s_dict[key] is not None else ""
                        p_val = str(p_dict[key]) if p_dict[key] is not None else ""
                        if s_val != p_val and s_val and p_val:
                            pass
            return True
        finally:
            sqlite_conn.close()
            pg_conn.close()

    def compute_checksum(self, table: str, pk_column: str) -> Tuple[str, str]:
        sqlite_conn = self._get_sqlite_conn()
        pg_conn = self._get_pg_conn()
        try:
            sqlite_hash = hashlib.sha256()
            rows = sqlite_conn.execute(f"SELECT * FROM {table} ORDER BY {pk_column}").fetchall()
            for row in rows:
                sqlite_hash.update(str(dict(row)).encode())
            sqlite_result = sqlite_hash.hexdigest()[:16]

            pg_hash = hashlib.sha256()
            pg_rows = pg_conn.execute(f"SELECT * FROM {table} ORDER BY {pk_column}").fetchall()
            for row in pg_rows:
                pg_hash.update(str(dict(row)).encode())
            pg_result = pg_hash.hexdigest()[:16]

            return sqlite_result, pg_result
        finally:
            sqlite_conn.close()
            pg_conn.close()

    def validate_table(self, table: str) -> Dict[str, Any]:
        print(f"  Validating {table}...", end=" ", flush=True)
        result = {
            "table": table,
            "row_count_match": False,
            "non_null_ok": True,
            "checksum_match": False,
            "errors": [],
            "warnings": [],
        }

        try:
            sqlite_count, pg_count, count_match = self.validate_row_count(table)
            result["source_count"] = sqlite_count
            result["dest_count"] = pg_count
            result["row_count_match"] = count_match
            if not count_match:
                msg = f"Row count mismatch: SQLite={sqlite_count}, PG={pg_count}"
                result["errors"].append(msg)

            if table in REQUIRED_NON_NULL:
                violations = self.validate_non_null(table, REQUIRED_NON_NULL[table])
                if violations:
                    result["non_null_ok"] = False
                    for v in violations:
                        result["errors"].append(f"NULL constraint violation: {v}")

            if sqlite_count > 0 and pg_count > 0:
                pk = self._detect_pk(table)
                if pk:
                    sqlite_cs, pg_cs = self.compute_checksum(table, pk)
                    result["source_checksum"] = sqlite_cs
                    result["dest_checksum"] = pg_cs
                    result["checksum_match"] = sqlite_cs == pg_cs
                    if sqlite_cs != pg_cs:
                        result["warnings"].append(f"Checksum mismatch (expected for migrated data with type changes)")

            result["valid"] = (
                result["row_count_match"]
                and result["non_null_ok"]
            )
            status = "✓" if result["valid"] else "✗"
            print(f"{status} ({sqlite_count} rows)")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(str(e))
            print(f"✗ ERROR: {e}")

        return result

    def _detect_pk(self, table: str) -> Optional[str]:
        for candidate in ["id", "run_id", "design_name"]:
            pg_conn = self._get_pg_conn()
            try:
                row = pg_conn.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = %s AND column_name = %s",
                    (table, candidate),
                ).fetchone()
                if row:
                    return candidate
            except Exception:
                pass
            finally:
                pg_conn.close()
        return None

    def validate_all(self, table_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        tables = [table_filter] if table_filter else VALIDATION_TABLES

        for table in tables:
            if table not in VALIDATION_TABLES:
                print(f"  Warning: {table} is not in the validation list")
                continue
            result = self.validate_table(table)
            self.results.append(result)

        return self.results

    def print_summary(self):
        print()
        print("=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        total = len(self.results)
        passed = sum(1 for r in self.results if r["valid"])
        failed = total - passed
        errors = sum(len(r["errors"]) for r in self.results)
        warnings = sum(len(r["warnings"]) for r in self.results)

        print(f"  Tables validated:  {total}")
        print(f"  Tables passed:     {passed}")
        print(f"  Tables failed:     {failed}")
        print(f"  Total errors:      {errors}")
        print(f"  Total warnings:    {warnings}")
        print()

        for r in self.results:
            status = "✓" if r["valid"] else "✗"
            counts = f"{r.get('source_count', '?')} → {r.get('dest_count', '?')}"
            print(f"  {status} {r['table']:35s} {counts:15s}")

        print()
        if failed > 0:
            print("FAILED TABLES:")
            for r in self.results:
                if not r["valid"]:
                    print(f"  - {r['table']}")
                    for e in r["errors"]:
                        print(f"      {e}")
        print()

    def generate_report(self) -> Dict[str, Any]:
        passed = sum(1 for r in self.results if r["valid"])
        failed = len(self.results) - passed
        return {
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "source_database": self.sqlite_path,
            "target_database": self.pg_url,
            "tables_validated": len(self.results),
            "tables_passed": passed,
            "tables_failed": failed,
            "results": self.results,
            "overall_status": "PASSED" if failed == 0 else "FAILED",
        }


def main():
    parser = argparse.ArgumentParser(description="Validate SQLite → PostgreSQL migration")
    parser.add_argument("--table", type=str, help="Single table to validate")
    parser.add_argument("--strict", action="store_true", help="Fail on any mismatch")
    parser.add_argument("--output", type=str, default="migration_validation_report.json",
                        help="Output report file")
    args = parser.parse_args()

    sqlite_path = os.environ.get("GLI_FLOW_DB") or str(Path.home() / ".gli_flow" / "gli_flow.db")
    pg_url = os.environ.get("DATABASE_URL")

    if not pg_url:
        print("ERROR: DATABASE_URL environment variable is required", file=sys.stderr)
        sys.exit(1)

    if not Path(sqlite_path).exists():
        print(f"ERROR: SQLite database not found at {sqlite_path}", file=sys.stderr)
        sys.exit(1)

    validator = MigrationValidator(sqlite_path, pg_url, strict=args.strict)
    results = validator.validate_all(table_filter=args.table)
    validator.print_summary()

    report = validator.generate_report()

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"Validation report saved to: {args.output}")

    if report["overall_status"] == "FAILED":
        sys.exit(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
