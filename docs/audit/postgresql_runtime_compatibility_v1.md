# PostgreSQL Runtime Compatibility Audit v1

**Generated:** 2026-06-23
**Goal:** Verify that all GLI-FLOW components function correctly after PostgreSQL migration.

---

## 1. Component Compatibility Matrix

| Component | SQLite | PostgreSQL | SQLite-Specific Patterns Found | Migration Impact |
|-----------|--------|------------|-------------------------------|------------------|
| Signoff Engine | ✅ | ⚠️ | Uses `DatabaseManager.update_run_signoff()` — static UPDATE with positional params | LOW — parameter style change (`?` → `%s`) |
| Failure Atlas | ✅ | ⚠️ | `INSERT OR REPLACE`, `rowid` dedup, `json_extract()`, `LIKE` search | HIGH — 3 SQLite-specific patterns |
| Telemetry | ✅ | ⚠️ | `AUTOINCREMENT`, `lastrowid`, `PRAGMA journal_mode=WAL` | MEDIUM — serialization pattern change |
| QoR Analytics | ✅ | ⚠️ | `DatabaseManager.get_qor_trend()` — simple SELECT | LOW — trivial change |
| Dashboard | ✅ | ⚠️ | Backend API via `get_connection()` — uses `sqlite3.Row` | MEDIUM — row factory abstraction |
| API (FastAPI) | ✅ | ⚠️ | Mixed: `sqlite3.Row`, `LIKE`, `json_extract()`, direct cursor | HIGH — comprehensive rewrite needed |
| Artifacts | ✅ | ⚠️ | File-system based (not DB) | NONE — no DB changes |
| Run History | ✅ | ⚠️ | CLI `DatabaseManager.get_runs()` — simple SELECT | LOW |
| CLI `db` commands | ✅ | ⚠️ | `sqlite_master`, inline `sqlite3.connect()`, PRAGMA | MEDIUM |
| Support bundle | ✅ | ⚠️ | Inline `sqlite3.connect()` in CLI | MEDIUM |
| Resolution Intelligence | ✅ | ⚠️ | `ON CONFLICT(id) DO UPDATE` (already PostgreSQL-compatible!) | LOW |
| Design Intelligence | ✅ | ⚠️ | `INSERT OR REPLACE`, `LIKE` search | LOW |
| Community Intelligence | ✅ | ⚠️ | `AUTOINCREMENT`, inline `sqlite3.connect()` | MEDIUM |
| Intelligence Warehouse | ✅ | ⚠️ | Inline `sqlite3.connect()`, `sqlite3.Row` | MEDIUM |
| Cloud Ingestion | ✅ | ❌ | Separate SQLite DB with `AUTOINCREMENT`, full PRAGMA usage | HIGH — separate migration |

---

## 2. Component Detail Analysis

### 2.1 Signoff Engine

**Files affected:** `gli_flow/database/sqlite.py` (methods 23–53, 94–182, 305–341)

**SQL patterns used:**
- `UPDATE runs SET ... WHERE run_id = ?` — positional params
- `SELECT ... FROM runs WHERE run_id = ?` — positional params

**Changes required:**
- `?` → `%s` placeholder conversion
- `sqlite3.connect()` → `DatabaseProvider.connect()`
- No semantic changes needed

**Risk:** LOW — only parameter style change.

---

### 2.2 Failure Atlas

**Files affected:** `failure_atlas/repository.py` (entire file, 530 lines)

**SQL patterns used:**
- `INSERT OR REPLACE INTO failure_atlas_entries (...)` — line 116
- `INSERT INTO execution_intelligence (...)` — line 500
- `LIKE` queries for search — line 189
- `json_extract(after_metrics, '$.wns')` — line 346
- `DATE(detected_at)` — line 361
- `CAST(SUM(fix_applied) AS FLOAT) / COUNT(*)` — lines 332, 369, 381
- `ROUND(CAST(COUNT(*) AS FLOAT) / (SELECT COUNT(*) ...) * 100, 1)` — lines 426, 442, 472
- `ROW_NUMBER` subqueries — lines 394-401

**Changes required:**
- `INSERT OR REPLACE` → `INSERT ... ON CONFLICT (id) DO UPDATE SET`
- `?` → `%s` parameter conversion
- `json_extract(col, '$.path')` → `col #>> '{path}'`
- `DATE(col)` → `col::date`
- `CAST(... AS FLOAT)` → `CAST(... AS DOUBLE PRECISION)` or use `::float`

**Risk:** HIGH — 8 distinct SQL patterns requiring changes.

---

### 2.3 Telemetry (UploadQueue)

**Files affected:** `gli_flow/telemetry/upload_queue.py` (entire file, 160 lines)

**SQL patterns used:**
- `AUTOINCREMENT` — line 14
- `INSERT INTO upload_queue (...)` + `cur.lastrowid` — lines 54, 60
- `UPDATE ... SET status = 'in_progress' WHERE id IN (...)` — line 80

**Changes required:**
- `AUTOINCREMENT` → `SERIAL`
- `lastrowid` → `RETURNING id`
- `?` → `%s` parameter conversion

**Risk:** MEDIUM — this is a separate database that can be migrated independently.

---

### 2.4 QoR Analytics

**Files affected:** `gli_flow/database/sqlite.py` (method `get_qor_trend()`, lines 282–303)

**SQL patterns used:**
- `SELECT qor_score, wns, tns, utilization, timestamp FROM runs WHERE qor_score IS NOT NULL ...`

**Changes required:**
- `?` → `%s` placeholder conversion
- No semantic changes

**Risk:** LOW

---

### 2.5 Dashboard / Backend API

**Files affected:** `backend/server.py` (entire file, 3579 lines)

**SQL patterns used:**
- `sqlite3.Row` row factory — line 49
- Mixed `?` positional params (psycopg2 uses `%s`)
- `LIKE` queries — scattered
- `COALESCE` usage — multiple places
- `datetime('now')` defaults — server-side

**Changes required:**
- Row factory → use `RealDictCursor` or provider abstraction
- `?` → `%s` throughout
- `datetime('now')` → `NOW()` in SQL strings
- Comprehensive parameter audit

**Risk:** HIGH — largest single file with most SQL.

---

### 2.6 Resolution Intelligence

**Files affected:** `gli_flow/resolution_intelligence/repository.py` (299 lines)

**SQL patterns used:**
- `INSERT INTO ... ON CONFLICT(id) DO UPDATE SET` — line 62
- This is already PostgreSQL-compatible UPSERT syntax
- `?` positional params (but could use `%s`)

**Changes required:**
- `?` → `%s` parameter conversion
- `COALESCE(?, datetime('now'))` → `COALESCE(%s, NOW())`

**Risk:** LOW — already uses PostgreSQL-compatible UPSERT.

---

### 2.7 Design Intelligence

**Files affected:**
- `gli_flow/design_intel/feature_extractor.py` (233 lines)
- `gli_flow/design_intel/profile_engine.py` (248 lines)
- `gli_flow/design_intel/quality_audit.py` (148 lines)
- `gli_flow/design_intel/similarity_engine.py`
- `gli_flow/design_intel/design_classifier.py`

**SQL patterns used:**
- `INSERT OR REPLACE INTO design_features` — line 187
- `INSERT OR REPLACE INTO design_profiles` — line 175
- `LIKE` queries in similarity_engine

**Changes required:**
- `INSERT OR REPLACE` → `INSERT ... ON CONFLICT (design_name) DO UPDATE SET`
- `?` → `%s` parameter conversion

**Risk:** LOW — simple patterns.

---

### 2.8 Community Intelligence

**Files affected:**
- `failure_atlas/community_intelligence/audit.py` (111 lines)
- `failure_atlas/community_intelligence/telemetry.py` (119 lines)
- `failure_atlas/community_intelligence/dataset.py` (215 lines)
- `failure_atlas/community_intelligence/escalation.py` (316 lines)
- `failure_atlas/community_intelligence/export.py` (293 lines)
- `failure_atlas/community_intelligence/health.py`
- `failure_atlas/community_intelligence/snapshot.py` (26 lines)
- `failure_atlas/community_intelligence/replay.py` (151 lines)
- `failure_atlas/ai_assistant/feedback.py` (145 lines)
- `failure_atlas/ai_assistant/resolution_capture.py` (116 lines)

**SQL patterns used:**
- `AUTOINCREMENT` in 3 tables (telemetry, dataset, audit_log)
- `INSERT OR IGNORE` in some modules
- Inline `sqlite3.connect()` in every module

**Changes required:**
- `AUTOINCREMENT` → `SERIAL`
- `INSERT OR IGNORE` → `ON CONFLICT DO NOTHING`
- `?` → `%s` parameter conversion
- Connection management via provider

**Risk:** MEDIUM — many files but each has simple SQL.

---

### 2.9 Intelligence Warehouse

**Files affected:** `intelligence/warehouse.py` (185 lines)

**SQL patterns used:**
- Inline `sqlite3.connect()` with `sqlite3.Row`
- Simple INSERTs and SELECTs

**Changes required:**
- Provider abstraction
- `?` → `%s` parameter conversion

**Risk:** LOW

---

### 2.10 CLI (main.py) — `db reset`, support bundle

**Files affected:** `gli_flow/cli/main.py` (lines 310–326, 1860–1919)

**SQL patterns used:**
- `sqlite_master` — line 314
- Inline `sqlite3.connect()` — lines 312, 1872, 1893
- `DELETE FROM runs` — line 320

**Changes required:**
- `sqlite_master` → `information_schema.tables`
- Provider injection
- `?` → `%s` parameter conversion

**Risk:** MEDIUM

---

### 2.11 Legacy APIs (deprecated)

**Files affected:**
- `outputs/execution_history/history_api.py`
- `outputs/execution_history/live_status.py`
- `outputs/metrics/qor_api.py`

**SQL patterns used:**
- Hardcoded `"gli_flow.db"` path
- `SELECT * FROM runs` with positional column indexing

**Risk:** LOW — these are deprecated but should be updated or marked as broken.

---

## 3. Incompatibility Summary

| Component | Total SQL Patterns | SQLite-Specific | Migration Effort |
|-----------|-------------------|-----------------|------------------|
| Signoff Engine | 6 | 0 | 1 day |
| Failure Atlas | 25 | 6 | 3 days |
| Telemetry UploadQueue | 12 | 2 | 0.5 day |
| Backend API | 80+ | 5 | 5 days |
| CLI | 8 | 2 | 1 day |
| Resolution Intelligence | 15 | 1 | 0.5 day |
| Design Intelligence | 8 | 1 | 0.5 day |
| Community Intelligence | 30 | 4 | 2 days |
| Intelligence Warehouse | 6 | 0 | 0.5 day |
| Cloud Ingestion | 15 | 3 | 1 day |
| **TOTAL** | **~205** | **~24** | **~15 engineer-days** |

---

## 4. Parallel Validation Strategy

```python
# Run the same test suite against both backends
def test_runtime_compatibility():
    # SQLite
    os.environ.pop("DATABASE_URL", None)
    result_sqlite = subprocess.run(["gli-flow", "smoke-test"], capture_output=True)

    # PostgreSQL
    os.environ["DATABASE_URL"] = "postgresql://..."
    result_pg = subprocess.run(["gli-flow", "smoke-test"], capture_output=True)

    assert result_sqlite.returncode == 0
    assert result_pg.returncode == 0
```
