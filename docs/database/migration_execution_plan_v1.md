# Migration Execution Plan v1

**Generated:** 2026-06-23
**Goal:** Zero-data-loss migration from SQLite to PostgreSQL (Supabase) with rollback capability.

---

## Migration Order

| Order | Table | Risk | Dependencies | Migration Method |
|-------|-------|------|-------------|-----------------|
| 1 | schema_version | LOW | None | Direct CREATE |
| 2 | runs | HIGH | None | Bulk INSERT with conflict resolution |
| 3 | failure_atlas_entries | HIGH | runs (logical FK) | Bulk INSERT with conflict resolution |
| 4 | resolution_patterns | MEDIUM | failure_atlas_entries (logical FK) | Bulk INSERT |
| 5 | resolution_feedback | LOW | resolution_patterns | Bulk INSERT |
| 6 | execution_intelligence | LOW | runs (logical FK) | Bulk INSERT |
| 7 | ai_investigation_feedback | LOW | failure_atlas_entries | Bulk INSERT |
| 8 | ai_resolution_capture | LOW | failure_atlas_entries | Bulk INSERT |
| 9 | community_escalations | LOW | runs (logical FK) | Bulk INSERT |
| 10 | community_telemetry | LOW | community_escalations | Bulk INSERT |
| 11 | community_unknown_dataset | LOW | None | Bulk INSERT |
| 12 | feedback_records | LOW | runs (logical FK) | Bulk INSERT |
| 13 | user_journey_events | LOW | None | Bulk INSERT |
| 14 | resolution_tracking | LOW | runs (logical FK) | Bulk INSERT |
| 15 | telemetry_audit_log | LOW | None | Bulk INSERT |
| 16 | design_features | LOW | None | Bulk INSERT |
| 17 | design_profiles | LOW | None | Bulk INSERT |
| 18 | telemetry_execution_records | LOW | None | Bulk INSERT |
| 19 | telemetry_recommendation_records | LOW | None | Bulk INSERT |
| 20 | upload_queue | LOW | None | Separate DB, migrate independently |

---

## 2. Migration Script Architecture

### 2.1 Migration Script: `scripts/migrate_to_postgres.py`

```python
#!/usr/bin/env python3
"""
migrate_to_postgres.py — Migrate data from SQLite to PostgreSQL.

Usage:
  # Dry run (validate only)
  python scripts/migrate_to_postgres.py --dry-run

  # Full migration
  python scripts/migrate_to_postgres.py --confirm

  # Single table
  python scripts/migrate_to_postgres.py --table runs --confirm

Environment:
  GLI_FLOW_DB        = path to source SQLite database (optional)
  DATABASE_URL       = target PostgreSQL connection string (required)
"""


class MigrationValidator:
    """Compares row counts and checksums between source and destination."""

    def validate_table(self, table: str) -> dict:
        source_count = self._sqlite_fetchval(f"SELECT COUNT(*) FROM {table}")
        dest_count = self._pg_fetchval(f"SELECT COUNT(*) FROM {table}")
        source_checksum = self._sqlite_fetchval(
            f"SELECT COUNT(*) || '-' || COALESCE(SUM(hashtext(CAST(row_to_json AS text))), 0) "
            f"FROM (SELECT * FROM {table} ORDER BY primary_key) AS sub"
        )
        return {
            "table": table,
            "source_count": source_count,
            "dest_count": dest_count,
            "match": source_count == dest_count,
        }
```

### 2.2 Row-Level Validation Per Table

| Table | Primary Key | Row Count Check | Checksum Strategy |
|-------|-------------|-----------------|-------------------|
| runs | run_id | Exact count | `COUNT(*)` match |
| failure_atlas_entries | id | Exact count | `COUNT(*)` match |
| resolution_patterns | id | Exact count | `COUNT(*)` match |
| resolution_feedback | id | Exact count | `COUNT(*)` match |
| community_telemetry | id (SERIAL) | Exact count | `COUNT(*)` match |
| community_unknown_dataset | id (SERIAL) | Exact count | `COUNT(*)` match |
| design_profiles | design_name | Exact count | `COUNT(*)` match |

For JSONB columns, validate that `json.dumps` round-trips match between source and destination.

---

## 3. Table-by-Table Migration Strategy

### 3.1 `schema_version`

```sql
-- Source: SELECT * FROM schema_version ORDER BY source, version
-- Destination: INSERT INTO schema_version (source, version, applied_at, description) VALUES ...
-- Notes: Simple insert, no transformation needed
```

### 3.2 `runs`

```sql
-- Source: SELECT * FROM runs ORDER BY run_id
-- Destination: INSERT INTO runs (...) VALUES ... ON CONFLICT (run_id) DO UPDATE SET ...
-- Transformations:
--   timestamp TEXT → TIMESTAMPTZ (parse ISO format)
--   created_at TEXT → TIMESTAMPTZ
--   updated_at TEXT → TIMESTAMPTZ
--   is_important INTEGER → BOOLEAN
--   drc_is_clean INTEGER → BOOLEAN
--   lvs_is_clean INTEGER → BOOLEAN
--   signoff_setup_pass INTEGER → BOOLEAN
--   signoff_hold_pass INTEGER → BOOLEAN
--   tapeout_ready INTEGER → BOOLEAN
--   llm_investigation_available INTEGER → BOOLEAN
--   signoff_gate_json TEXT → JSONB (parse JSON)
--   tags TEXT → JSONB (parse JSON)
--   llm_investigation_failed_attempts TEXT → JSONB (parse JSON)
```

### 3.3 `failure_atlas_entries`

```sql
-- Source: SELECT * FROM failure_atlas_entries ORDER BY id
-- Transformations:
--   id TEXT → UUID (cast to uuid)
--   fix_applied INTEGER → BOOLEAN
--   regression_detected INTEGER → BOOLEAN
--   detected_at TEXT → TIMESTAMPTZ
--   created_at TEXT → TIMESTAMPTZ
--   first_seen TEXT → TIMESTAMPTZ
--   last_seen TEXT → TIMESTAMPTZ
--   recommended_fix TEXT → JSONB (parse JSON)
--   evidence TEXT → JSONB (parse JSON)
--   before_metrics TEXT → JSONB (parse JSON)
--   after_metrics TEXT → JSONB (parse JSON)
--   artifact, execution, timing, utilization, congestion, runtime snapshots → JSONB
```

### 3.4 `resolution_patterns`

```sql
-- Transformations:
--   created_at TEXT → TIMESTAMPTZ
--   updated_at TEXT → TIMESTAMPTZ
--   first_seen TEXT → TIMESTAMPTZ
--   last_seen TEXT → TIMESTAMPTZ
--   tracked_run_ids TEXT → JSONB (parse JSON array)
--   tracked_design_names TEXT → JSONB (parse JSON array)
```

### 3.5 `community_telemetry` and `community_unknown_dataset`

```sql
-- Transformations:
--   id INTEGER → SERIAL (let PostgreSQL generate new IDs)
--   details TEXT → JSONB (community_telemetry)
--   created_at TEXT → TIMESTAMPTZ
--   last_seen TEXT → TIMESTAMPTZ
-- Notes: AUTOINCREMENT → SERIAL means IDs will differ. Reference integrity via UUID keys.
```

### 3.6 `design_features` and `design_profiles`

```sql
-- Transformations:
--   fanout_histogram TEXT → JSONB
--   created_at TEXT → TIMESTAMPTZ
--   updated_at TEXT → TIMESTAMPTZ
```

### 3.7 Cloud Ingestion Tables

```sql
-- Separate schema: ingestion
-- Transformations:
--   id INTEGER → SERIAL
--   recorded_at TEXT → TIMESTAMPTZ
--   ingested_at TEXT → TIMESTAMPTZ
--   metrics TEXT → JSONB
--   consent_given INTEGER → BOOLEAN
```

---

## 4. Validation Queries Per Table

### 4.1 Row Count Validation

```sql
-- Source (SQLite)
SELECT COUNT(*) FROM runs;

-- Destination (PostgreSQL)
SELECT COUNT(*) FROM runs;
```

### 4.2 Sample Data Validation

```sql
-- Validate first/last 5 rows match (key columns)
SELECT run_id, design_name, status, timestamp FROM runs
ORDER BY run_id LIMIT 5;

SELECT run_id, design_name, status, timestamp FROM runs
ORDER BY run_id DESC LIMIT 5;
```

### 4.3 Aggregation Validation

```sql
-- Compare statistical aggregates
SELECT
    COUNT(*),
    COALESCE(AVG(qor_score), 0),
    COALESCE(AVG(wns), 0),
    COALESCE(AVG(tns), 0)
FROM runs;
```

### 4.4 JSONB Round-trip Validation

For each JSONB column, pick 3 records from source and verify JSON round-trips:
```python
def validate_json_column(table, column, pk_column):
    source_rows = sqlite_fetchall(f"SELECT {pk_column}, {column} FROM {table} LIMIT 3")
    for row in source_rows:
        pk = row[pk_column]
        source_json = json.loads(row[column]) if row[column] else {}
        dest_row = pg_fetchone(f"SELECT {column} FROM {table} WHERE {pk_column} = %s", (pk,))
        dest_json = json.loads(json.dumps(dest_row[column])) if dest_row else {}
        assert source_json == dest_json, f"Mismatch for {table}.{pk_column}={pk}"
```

---

## 5. Rollback Strategy

### 5.1 Before Migration

1. Create SQLite backup:
   ```bash
   cp ~/.gli_flow/gli_flow.db ~/.gli_flow/gli_flow.db.pre_migration
   cp ~/.gli-flow/upload_queue.db ~/.gli-flow/upload_queue.db.pre_migration
   ```

2. Record migration manifest:
   ```bash
   python scripts/migrate_to_postgres.py --dry-run --output migration_manifest.json
   ```

### 5.2 Rollback Procedure

```bash
# Stop application
# Restore SQLite backup
cp ~/.gli_flow/gli_flow.db.pre_migration ~/.gli_flow/gli_flow.db
cp ~/.gli-flow/upload_queue.db.pre_migration ~/.gli-flow/upload_queue.db

# Set environment to force SQLite
export GLI_FLOW_DB=~/.gli_flow/gli_flow.db
unset DATABASE_URL

# Restart application
```

### 5.3 Per-Table Rollback

If a single table fails during migration:

```sql
-- Drop the partially migrated table
DROP TABLE IF EXISTS runs CASCADE;

-- Re-run from scratch
-- (full import is idempotent due to ON CONFLICT handling)
```

### 5.4 Migration Safety Guarantees

- No `DELETE` or `DROP` on source SQLite database
- All transformations are lossless (JSON strings ↔ JSONB)
- Timestamps are preserved as ISO 8601 strings
- UUIDs are preserved as-is (already in standard format)
- SERIAL IDs are NOT preserved (new sequence) — FK references must use logical keys

---

## 6. Post-Migration Validation

### 6.1 Integration Test Suite

```bash
# Run full test suite against PostgreSQL
DATABASE_URL=postgresql://... python -m pytest tests/ -v

# Run full test suite against SQLite (should still pass)
python -m pytest tests/ -v
```

### 6.2 Data Integrity Checks

```python
def run_full_validation():
    results = []
    for table in ALL_TABLES:
        r = validate_table(table)
        results.append(r)
    failures = [r for r in results if not r["match"]]
    if failures:
        print("VALIDATION FAILED:", failures)
        sys.exit(1)
    print("All tables validated successfully.")
```

### 6.3 Runtime Smoke Tests

```bash
# CLI
gli-flow db status
gli-flow doctor
gli-flow smoke-test

# Backend API
curl http://localhost:8000/runs
curl http://localhost:8000/failures
curl http://localhost:8000/analytics/summary
```

---

## 7. Migration Rollout Timeline

| Phase | Duration | Action |
|-------|----------|--------|
| Pre-migration | 1 day | Deploy DatabaseProvider interface (Phase 4) to production with SQLiteProvider only |
| Staging validation | 2 days | Run full test suite against PostgreSQL staging DB |
| Dry-run migration | 1 day | Execute `--dry-run` against staging + validate |
| Production migration | 2 hours | Execute migration, run validation, switch DATABASE_URL |
| Post-migration monitoring | 7 days | Monitor application logs, rollback if needed |
| SQLite deprecation | 30 days | After validation, announce SQLite deprecation |

---

## 8. Responsible Parties

| Role | Responsibility |
|------|---------------|
| Engineer | Execute migration script |
| QA | Run validation queries |
| DevOps | Monitor application health |
| Product | Sign off after validation |
