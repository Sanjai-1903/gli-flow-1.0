# PostgreSQL Production Readiness Checklist v1

**Generated:** 2026-06-23
**Project:** GLI-FLOW ASIC — PostgreSQL (Supabase) Migration

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| [ ] | Not started |
| [~] | In progress |
| [✓] | Completed |
| [✗] | Blocked / Failed |

---

## Phase A: Connectivity & Infrastructure

- [ ] **Supabase connectivity verified** — `scripts/test_supabase_connection.py` passes with `DATABASE_URL`
- [ ] **SSL/TLS configured** — Supabase requires SSL; `sslmode=require` in connection string
- [ ] **Connection pooling configured** — Supabase uses PgBouncer on port 6543; `pool_mode=transaction` recommended
- [ ] **DATABASE_URL added to Railway** — Environment variable configured in Railway dashboard
- [ ] **GLI_FLOW_DB kept as fallback** — SQLite path remains configurable for local development
- [ ] **Database migration script created** — `scripts/migrate_to_postgres.py` ready
- [ ] **Rollback script created** — Backup and restore procedures documented

---

## Phase B: Schema

- [ ] **Schema validated** — All 24 tables created via `docs/database/postgresql_schema_v1.md`
- [ ] **All CHECK constraints present** — Column types match PostgreSQL conventions
- [ ] **All indexes created** — All unique indexes and performance indexes applied
- [ ] **JSONB columns validated** — All TEXT→JSONB conversions verified
- [ ] **TIMESTAMPTZ columns validated** — All TEXT→TIMESTAMPTZ conversions verified
- [ ] **BOOLEAN columns validated** — All INTEGER(0/1)→BOOLEAN conversions verified
- [ ] **SERIAL columns validated** — All AUTOINCREMENT→SERIAL conversions verified
- [ ] **UUID defaults configured** — `gen_random_uuid()` set as default for UUID PKs
- [ ] **`ingestion` schema created** — Cloud ingestion tables in separate schema

---

## Phase C: Data Migration

- [ ] **Pre-migration SQLite backup created** — `~/.gli_flow/gli_flow.db.pre_migration`
- [ ] **Pre-migration upload_queue backup created** — `~/.gli-flow/upload_queue.db.pre_migration`
- [ ] **Dry-run executed** — `python scripts/migrate_to_postgres.py --dry-run` passes
- [ ] **Row counts match** — Every table's `COUNT(*)` identical between SQLite and PostgreSQL
- [ ] **Sample data validated** — First/last 5 rows match for all tables
- [ ] **JSONB round-trip validated** — JSON columns survive serialize/deserialize
- [ ] **Timestamps preserved** — All timestamps correctly converted to TIMESTAMPTZ
- [ ] **UUIDs preserved** — All UUID primary keys identical between databases

---

## Phase D: Component Validation

### D.1 Telemetry

- [ ] **Telemetry writes pass** — `gli-flow run` telemetry events are stored in PostgreSQL
- [ ] **Upload queue works** — `UploadQueue` enqueue/dequeue functions with PostgreSQL
- [ ] **Telemetry warehouse writes pass** — `TelemetryWarehouse` stores execution records

### D.2 Failure Atlas

- [ ] **Failure Atlas writes pass** — `FailureAtlasRepository.insert_entry()` works with PostgreSQL
- [ ] **Failure Atlas queries pass** — `search_entries()`, `get_entries_for_run()`, analytics all work
- [ ] **Failure Atlas dedup works** — UNIQUE index on (run_id, failure_type, signature) enforced
- [ ] **Resolution tracking works** — `update_resolution()`, `get_analytics_summary()` work

### D.3 Dashboard & API

- [ ] **Dashboard queries pass** — All FastAPI `/runs`, `/failures`, `/analytics` endpoints work
- [ ] **Dashboard aggregation queries pass** — COUNT, AVG, GROUP BY queries work
- [ ] **Dashboard search works** — `LIKE`/`ILIKE` queries return correct results
- [ ] **Dashboard sorting works** — `ORDER BY timestamp DESC` returns correct order

### D.4 QoR Analytics

- [ ] **QoR analytics pass** — `get_qor_trend()`, score aggregations work
- [ ] **QoR improvement queries pass** — `json_extract` → `#>>` path expressions work

### D.5 Signoff Engine

- [ ] **Signoff engine pass** — `update_run_signoff()` updates all signoff columns correctly
- [ ] **Signoff gate checks pass** — `tapeout_ready`, `signoff_setup_pass` BOOLEAN values correct

### D.6 Resolution Intelligence

- [ ] **Resolution upsert works** — `INSERT ... ON CONFLICT DO UPDATE` behaves correctly
- [ ] **Trust scoring queries pass** — Complex aggregate queries work with PostgreSQL
- [ ] **Candidate generation works** — Subquery with NOT EXISTS works correctly

### D.7 Community Intelligence

- [ ] **Escalation CRUD works** — Create, read, update, delete community escalations
- [ ] **Telemetry audit log works** — Record and query audit log entries
- [ ] **Unknown dataset works** — Insert and query unknown failure records
- [ ] **Export works** — TelemetryExporter queries return correct results
- [ ] **Snapshot works** — DatasetSnapshot creates valid JSON snapshots

### D.8 Design Intelligence

- [ ] **Feature extractor works** — `INSERT ... ON CONFLICT` for design_features works
- [ ] **Profile engine works** — `INSERT ... ON CONFLICT` for design_profiles works
- [ ] **Quality audit works** — Complex audit queries with `IN` clauses work

### D.9 CLI

- [ ] **`gli-flow db status` works** — Schema version query works
- [ ] **`gli-flow db migrate` works** — PostgreSQL schema migration works
- [ ] **`gli-flow doctor` works** — Environment validation passes
- [ ] **`gli-flow smoke-test` works** — Full smoke test against PostgreSQL passes
- [ ] **`gli-flow support-bundle` works** — Data export queries work

---

## Phase E: Performance & Reliability

- [ ] **Query performance acceptable** — All queries return within expected latency
- [ ] **Connection pooling handles load** — No connection starvation under concurrent access
- [ ] **Migration time acceptable** — Full migration completes within 2 hours
- [ ] **No deadlocks** — Concurrent writes don't cause deadlock errors
- [ ] **WAL mode not needed** — PostgreSQL handles concurrency natively

---

## Phase F: Rollback Confidence

- [ ] **Rollback tested** — Full rollback procedure validated in staging
- [ ] **SQLite fallback preserved** — Application works with `unset DATABASE_URL`
- [ ] **No data loss during rollback** — SQLite database untouched during migration
- [ ] **Rollback within RTO** — Rollback completes within 1 hour

---

## Phase G: Security & Compliance

- [ ] **Credentials not in code** — `DATABASE_URL` set via environment, not hardcoded
- [ ] **SSL enforced** — Connection uses `sslmode=require`
- [ ] **Least privilege** — Database user has minimum required permissions
- [ ] **No secrets in logs** — Connection strings redacted in log output

---

## Sign-off

```
Component            Status    Tester    Date
─────────────────────────────────────────────────
Supabase connectivity [ ]       ______    ______
Schema validated      [ ]       ______    ______
Row counts match      [ ]       ______    ______
Telemetry writes      [ ]       ______    ______
Failure Atlas writes  [ ]       ______    ______
Dashboard queries     [ ]       ______    ______
QoR analytics pass    [ ]       ______    ______
Signoff engine pass   [ ]       ______    ______
API pass              [ ]       ______    ______
Rollback tested       [ ]       ______    ______
SQLite fallback       [ ]       ______    ______
```

**Authorization for Production Go-Live:**

```
Name: __________________________
Role: __________________________
Date: __________________________
Signature: _____________________
```
