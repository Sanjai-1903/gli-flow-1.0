# Database Cutover Certification

**Date:** 2026-06-24
**Status:** CERTIFIED (core runtime paths)

## Summary

The `gli-flow-asic` runtime has been refactored to write all core data (runs, failure atlas entries) through `DatabaseProvider` instead of raw `sqlite3.connect()`. When `SUPABASE_API_TOKEN` and `SUPABASE_PROJECT_REF` are set, writes go directly to Supabase via the Management API. SQLite remains available as an alternate provider (`SQLiteProvider`) for environments without Supabase credentials.

## Files Modified

| File | Change |
|------|--------|
| `gli_flow/database/factory.py` | `create_provider()` returns `SupabaseApiProvider` only when `db_path is None` |
| `gli_flow/database/database_provider.py` | Added `rowcount` property (default `-1`) |
| `gli_flow/database/sqlite_provider.py` | Added `_last_cursor` tracking and `rowcount` property |
| `gli_flow/database/sqlite.py` | `DatabaseManager` refactored from `sqlite3.Connection` → `DatabaseProvider` |
| `failure_atlas/repository.py` | `FailureAtlasRepository` refactored from `sqlite3.Connection` → `DatabaseProvider` |
| `backend/server.py` | Uses `SupabaseApiProvider` via `create_provider()` |
| `dashboard/vite.config.js` | Proxy points to backend port 8008 |
| `tests/test_failure_atlas.py` | Updated test for non-KeyError behavior |

## Validation Results

### Phase 1: Direct SQLite Usage Audit ✅
73 `sqlite3.connect()` call sites identified; written to `docs/audit/direct_sqlite_usage_final.md`.

### Phase 2: DatabaseManager Refactored ✅
- `sqlite3` import removed from `gli_flow/database/sqlite.py`
- Uses `create_provider()` → `SupabaseApiProvider` (env vars) or `SQLiteProvider` (fallback)
- All methods (`insert_run`, `update_run`, `update_run_signoff`, `get_run`, etc.) use provider

### Phase 3: FailureAtlasRepository Refactored ✅
- `sqlite3` import removed from `failure_atlas/repository.py`
- Uses `create_provider()` same logic as DatabaseManager
- All methods (`insert_entry`, `get_entries`, `search_entries`, `update_resolution`, etc.) use provider
- `INSERT OR REPLACE` changed to `INSERT ... ON CONFLICT (id) DO UPDATE SET ...` for PostgreSQL compatibility
- Boolean fields (`fix_applied`) now pass Python `bool` instead of `int` (1/0)

### Phase 4: Provider Coverage Audit ✅
- Orchestrator runtime path: `DatabaseManager` + `FailureAtlasRepository` → both use provider
- UploadQueue: intentionally always `SQLiteProvider` (local buffer)
- CLI tooling (`cli/main.py`, `scripts/`): not in runtime path, left as-is
- Legacy `manager.py`: dead code, not imported in runtime paths

### Phase 5: Supabase Runtime Validation ✅
- `gli-flow run examples/counter --mock` completed **exit 0** with QoR 0.91
- Run appeared in Supabase with: `status: SUCCESS`, `qor_score: 0.91`, `tapeout_ready: true` (proper boolean)
- Boolean-to-integer conversion bug fixed for PostgreSQL compatibility

### Phase 6: SQLite Removal Test ✅
- `~/.gli_flow/gli_flow.db` renamed to `.bak`
- `gli-flow run examples/counter --mock` completed successfully
- Run appeared in Supabase without any local SQLite database
- Proof: no dependency on SQLite db file when Supabase is active

### Phase 7: Failure Atlas Validation ✅
- `FailureAtlasRepository.insert_entry()` via Supabase provider succeeded
- Entry retrieved via `get_entries_for_run()` from Supabase
- `INSERT ... ON CONFLICT` approach works for both providers

### Phase 8: Telemetry Validation ❌ (cancelled)
- Telemetry pipeline has separate schema (`telemetry_events`, `failure_atlas_events`, `upload_audit`)
- Ingestion server (`cloud_ingestion/database.py`) uses raw SQLite, not `DatabaseProvider`
- Would require separate cutover effort with new Supabase tables

## Boolean Handling

A critical fix for PostgreSQL compatibility: the codebase used `1 if X else 0` to convert Python booleans to integers for SQLite's integer-boolean convention. PostgreSQL has a native `boolean` type, so `True`/`False` must be passed as Python `bool`. The `SupabaseApiProvider._escape()` method handles this correctly (`bool` → `TRUE`/`FALSE`).

Files with boolean fixes:
- `gli_flow/database/sqlite.py` — `update_run()`, `update_run_investigation()`
- `failure_atlas/repository.py` — `insert_entry()`, `update_resolution()`

## Remaining SQLite Dependencies (not in runtime path)

- `cloud_ingestion/database.py` — ingestion server (separate service, separate schema)
- `outputs/execution_history/*.py` — output dashboards (local files)
- `outputs/metrics/qor_api.py` — QoR metrics API (local file)
- `analytics/*.py` — offline analytics scripts
- `intelligence/*.py` — design intelligence (offline batch)
- `scripts/*.py` — migration/testing scripts
- `tests/*.py` — test fixtures

## Test Results

```
tests/test_failure_atlas.py  ........... (44/45 pass, 1 pre-existing SVG format failure)
tests/test_production_readiness.py  ... (3/3 pass)
tests/  .............................. (394 pass, 1 pre-existing heartbeat OSError, 22 skip)
```

## How to Use

**With Supabase (production):**
```bash
export SUPABASE_API_TOKEN=sbp_xxx
export SUPABASE_PROJECT_REF=xxx
gli-flow run examples/counter --mock
# Run data goes directly to Supabase, no local SQLite needed
```

**Without Supabase (local development):**
```bash
unset SUPABASE_API_TOKEN SUPABASE_PROJECT_REF
gli-flow run examples/counter --mock
# Falls back to SQLite at ~/.gli_flow/gli_flow.db
```

**Check Supabase:**
```bash
curl -s -X POST "https://api.supabase.com/v1/projects/$SUPABASE_PROJECT_REF/database/query" \
  -H "Authorization: Bearer $SUPABASE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"SELECT run_id, status, qor_score, tapeout_ready FROM runs ORDER BY timestamp DESC LIMIT 5"}'
```
