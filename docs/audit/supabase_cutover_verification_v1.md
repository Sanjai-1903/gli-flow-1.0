# Supabase Cutover Verification Report v1

**Date:** 2026-06-24  
**Verification Sprint:** 8 tests executed  
**Status:** NOT COMPLETE — Hybrid mode (SQLite is source of truth)

---

## Executive Summary

GLI-FLOW remains in **hybrid mode**. SQLite is the true source of truth for all production data. Supabase contains a stale copy that is kept in sync only through manual migration scripts. The backend reads from Supabase for dashboard display, but `gli-flow run` never writes to Supabase directly.

---

## Test Results

### Test 1 — New Run Visibility: **FAIL**

| Metric | Value |
|---|---|
| `gli-flow run` test | `run_1782306849_39914cf4_counter` (SUCCESS, QoR 0.91) |
| SQLite after run | 95 runs (new run present) |
| Supabase after run | 94 runs (unchanged) |
| Auto-sync? | **No** — migration required |

**Evidence:**
- SQLite latest: `run_1782306849_39914cf4_counter` at `2026-06-24 13:14:09`
- Supabase latest: `run_1782305522_b07a98fc_counter` at `2026-06-24 12:52:02+00`

**Root cause:** `gli_flow/core/orchestrator.py:244`:
```python
self.database = DatabaseManager(db_path=self.db_path)
```
`DatabaseManager` (`gli_flow/database/sqlite.py:16`) uses raw `sqlite3.connect()` — not `create_provider()`, not `SupabaseApiProvider`.

---

### Test 2 — SQLite Dependency: **FAIL**

| Action | Result |
|---|---|
| Renamed `~/.gli_flow/gli_flow.db` to `.bak` | Run completed successfully |
| New SQLite DB auto-created | Yes (same path) |
| Supabase updated? | No (still 94 runs) |
| Can operate without SQLite? | **No** — auto-creates replacement SQLite DB |

**Evidence:**
- Original DB: `1916928 bytes` (hidden)
- New DB: auto-created, contains new run only
- `DatabaseManager.__init__` always opens `sqlite3.connect()`. If the file doesn't exist, SQLite creates it.

---

### Test 3 — Failure Atlas Direct Storage: **FAIL**

| Question | Answer |
|---|---|
| FA entries written to Supabase during flow? | **No** |
| Where do they go? | SQLite via `FailureAtlasRepository.insert_entry()` |
| Then what? | Optional HTTP POST to ingestion server (port 8100) |
| Supabase `public.failure_atlas_entries`? | Only from manual migration |

**Root cause:** All 40+ `FailureAtlasRepository` call sites use raw `sqlite3.connect()` (e.g., `failure_atlas/repository.py:37`). The orchestrator (`orchestrator.py:488,519,924,956,1006`) calls `repo.insert_entry()` which writes to SQLite only.

---

### Test 4 — Telemetry Direct Storage: **FAIL**

| Storage Layer | Telemetry Events |
|---|---|
| Upload Queue (local SQLite) | 520 items (20 completed, 500 failed) |
| Ingestion Server (local SQLite) | 7 events |
| **Supabase `ingestion.telemetry_events`** | **3 events** (manual test only, not from flow runs) |

**Pipeline:** `Run → UploadQueue (SQLite) → HTTP POST → Ingestion Server (SQLite)`  
**Supabase reach:** **No** — ingestion server stores in its own SQLite, not Supabase.

---

### Test 5 — Dashboard Freshness: **FAIL**

| Source | Run Count | Latest Run |
|---|---|---|
| Dashboard (proxy → backend → Supabase) | 94 | `run_1782305522_b07a98fc_counter` |
| SQLite (actual source of truth) | 95 | `run_1782306849_39914cf4_counter` |
| Freshness lag | **Manual migration required** | |

**Dashboard shows stale data.** New runs created by `gli-flow run` are invisible until a migration script copies them from SQLite to Supabase.

---

### Test 6 — Database Provider Trace: **FAIL**

| Component | File:Line | Provider | Supabase? |
|---|---|---|---|
| **Orchestrator** (runs, FA) | `orchestrator.py:244` | `DatabaseManager` → raw SQLite | No |
| **Orchestrator** (FA upload) | `orchestrator.py:1449` | `FailureAtlasRepository` → raw SQLite | No |
| **Backend** (FastAPI) | `server.py:47` | `create_provider()` → `SupabaseApiProvider` | **Yes** |
| **UploadQueue** | `upload_queue.py:38` | `create_provider(db_path=X)` → `SQLiteProvider` | No |
| **CLI: history/status** | `cli/main.py:609+` | `DatabaseManager` → raw SQLite | No |
| **FailureAtlasRepository** (40+ sites) | `repository.py:37` | Raw `sqlite3.connect()` | No |
| **Ingestion Server** | `database.py:91` | Raw `sqlite3.connect()` | No |
| **All Intelligence Engines** (50+ sites) | Various | Raw `sqlite3.connect()` | No |
| **All Community Intel modules** | Various | Raw `sqlite3.connect()` | No |
| **All Data Program modules** | Various | Raw `sqlite3.connect()` | No |
| **All Design Intel modules** | Various | Raw `sqlite3.connect()` | No |

**Conclusion:** Only 1 component (Backend) writes to Supabase. All other 90+ components write to SQLite.

---

### Test 7 — QoR Integrity: **FAIL** (pre-existing, not cutover-related)

| Anomaly | Count | Design | Pattern |
|---|---|---|---|
| QoR=0 on SUCCESS | 15 | picorv32 (13), uart_top (2) | WNS=0.0, runtime>0, metrics present |
| QoR=NULL | 3 | test_design | Synthetic test fixtures |

**Example:**
- `run_1782025371_93234a72_picorv32`: qor=0.0, wns=0.0, tns=0.0, util=36%, cells=1300, runtime=1317s
- This is a QoR **computation bug**, not a cutover issue. The design meets timing (WNS=0) but QoR collapses to 0.

---

### Test 8 — Production Telemetry Pipeline: **FAIL**

| Stage | Status | Detail |
|---|---|---|
| Run generates telemetry | ✅ | Events created during flow execution |
| Upload Queue (SQLite) | ✅ | 520 items queued |
| HTTP POST to ingestion server | ⚠️ | 20 succeeded, 500 failed |
| Ingestion Server (local SQLite) | ✅ | 7 events, 19 FA, 22 audits |
| **Reach Supabase** | **❌** | **Pipeline ends at ingestion server SQLite** |

**Upload Queue breakdown:** 0 pending, 20 completed, 500 failed.  
**Ingestion Server:** Running on port 8100, storing in `/home/gli/GLI/tapeitout.com/gli-flow-asic/tmp/cloud_ingestion_dev.db` (SQLite).  
**Supabase `ingestion.*` tables:** Only 3 old manual test rows (not from any flow run).

---

## Answers to Key Questions

### 1. What is the true source of truth today?

**SQLite.** All runs, FA entries, and telemetry data are written to SQLite during `gli-flow run`. Supabase is a read-only mirror updated only via manual migration scripts.

### 2. Is SQLite still required?

**Yes, unconditionally.** Every core component uses raw `sqlite3.connect()` or `DatabaseManager`:
- Orchestrator line 244: `DatabaseManager(db_path=self.db_path)` — hardcoded SQLite
- FailureAtlasRepository line 37: `sqlite3.connect(self.db_path)` — hardcoded SQLite
- All CLI commands, intelligence engines, community modules, design intel modules — all hardcoded SQLite

Removing SQLite would break `gli-flow run` entirely.

### 3. Is Supabase receiving runs directly?

**No.** Runs are written to SQLite via `DatabaseManager.insert_run()`. Supabase is only updated when a migration script (`migrate_sqlite_to_postgres.py`) is manually executed.

### 4. Is Supabase receiving telemetry directly?

**No.** Telemetry flows: `Run → UploadQueue (SQLite) → HTTP POST → Ingestion Server (local SQLite)`. The ingestion server stores in its own SQLite, not Supabase. The Supabase `ingestion.*` tables receive zero data from production flow runs.

### 5. Is Failure Atlas stored in Supabase directly?

**No.** FA entries are inserted into SQLite via `FailureAtlasRepository.insert_entry()` during the run. An optional HTTP upload sends them to the ingestion server (which stores in its own SQLite). The only FA data in Supabase comes from manual migration.

### 6. Is the dashboard reading live Supabase data?

**The dashboard reads Supabase data, but it is NOT live.** The backend serves data from Supabase, but Supabase only contains the last manually migrated snapshot. New runs created after the last migration are invisible to the dashboard.

- Last migration: ~18:44 UTC
- Dashboard shows: 94 runs
- Actual data in SQLite: 95 runs
- Freshness lag: one manual migration cycle

### 7. Is QoR integrity fixed?

**No.** 15 SUCCESS runs (picorv32, uart_top) show QoR=0 despite valid metrics (WNS=0, runtime>0, utilization and cell_count present). This is a QoR computation bug unrelated to the cutover. The QoR formula collapses to 0 when certain metrics (possibly `hold_wns`/`hold_tns`) are NULL.

### 8. Is telemetry production-ready?

**No.** 500 out of 520 upload queue items have failed. The ingestion server is running but the retry engine has exhausted its retries (10 max). The ingestion server stores data in SQLite (not Supabase). There is no mechanism to forward ingestion server data to Supabase.

### 9. Is the SQLite → Supabase cutover actually complete?

**No.** The cutover is **not complete**. The current architecture is:

```
gli-flow run
  ├── runs → DatabaseManager → SQLite (always, hardcoded)
  ├── FA entries → FailureAtlasRepository → SQLite (always, hardcoded)  
  ├── telemetry → UploadQueue → SQLite → HTTP → Ingestion Server SQLite
  └── post-run → HTTP POST → Ingestion Server (failure_atlas_entries)

migration script (manual, Async)
  ↓
Backend (server.py:47) → SupabaseApiProvider → Supabase → Dashboard
```

**SQLite remains the source of truth. Supabase is a stale read-only mirror.**

---

## Required Changes to Complete Cutover

1. **DatabaseManager** (`gli_flow/database/sqlite.py`): Replace `sqlite3.connect()` with `create_provider(db_path)` so the orchestrator can write to Supabase when configured. This is the single most impactful change.

2. **FailureAtlasRepository** (`failure_atlas/repository.py`): Replace `sqlite3.connect(self.db_path)` with a provider-based connection. Currently all 40+ call sites use raw SQLite.

3. **Cloud Ingestion Server** (`cloud_ingestion/database.py`): Replace `sqlite3.connect()` with SupabaseApiProvider to write `ingestion.*` tables directly to Supabase.

4. **QoR computation**: Fix the formula that collapses QoR to 0 when certain metrics are NULL. The 15 picorv32/uart_top SUCCESS runs with QoR=0 are incorrect.

5. **Upload Queue retry exhaustion**: 500 items have permanently failed (10 retries each). These need diagnosis and cleanup.
