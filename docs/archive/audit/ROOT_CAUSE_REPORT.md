# Root Cause Analysis: RTL→GDS Pipeline Failure

## 1. First Fatal Stage

**Stage:** `_run_failure_detection()` — called AFTER SIGN_OFF (100%) completes

**Stage in execution trace:** `telemetry_ingestion` / `failure_atlas_ingestion`

## 2. Exact Exceptions (in order)

### Exception 1 (always hits if any insert is attempted):
```
sqlite3.OperationalError: table failure_atlas_entries has no column named created_at
```

**Location:**
- `failure_atlas/repository.py:79` — INSERT statement includes `created_at`
- `failure_atlas/repository.py:99` — binds `entry.get("created_at")`
- Triggered from `gli_flow/core/orchestrator.py:368` — `repo.insert_entry(sig_entry)`

### Exception 2 (hits after Exception 1 is fixed, if a failure detection entry is found):
```
sqlite3.InterfaceError: Error binding parameter 7 - probably unsupported type.
```

**Location:**
- `failure_atlas/repository.py:92` — binds `entry.get("recommended_fix", "")` which returns a Python list
- The orchestrator's `_get_remediation_for()` and `_get_remediation_by_id()` both return `List[str]`
- SQLite cannot bind a list as a parameter for a TEXT column

## 3. Root Cause Chain

### Cause 1: Missing `created_at` column

### The Schema Mismatch

The `failure_atlas_entries` table was created by **legacy code** (before the migration system existed) with this column set:

```
id, run_id, failure_id, failure_type, severity, title, description,
recommended_fix, confidence, signature, detected_at, fix_applied,
fix_type, fix_description, fix_run_id, detection_stage, domain,
category, evidence, pre_failure_metrics, pdk_name, design_name,
flow_type, verified_by
```

Note: **no `created_at` column**.

Then migrations 1–5 were applied:

| Migration | SQL | Result |
|-----------|-----|--------|
| v1 (CREATE TABLE) | `CREATE TABLE IF NOT EXISTS failure_atlas_entries (... created_at ...)` | **NO-OP** — table already existed from legacy code |
| v2 (ALTER parent_run_id) | `ALTER TABLE ADD COLUMN parent_run_id TEXT` | Added `parent_run_id` |
| v3 (ALTER before_metrics) | `ALTER TABLE ADD COLUMN before_metrics TEXT` | Added `before_metrics` |
| v4 (ALTER after_metrics) | `ALTER TABLE ADD COLUMN after_metrics TEXT` | Added `after_metrics` |
| v5 (ALTER resolution_confidence) | `ALTER TABLE ADD COLUMN resolution_confidence TEXT` | Added `resolution_confidence` |

Since v1 was a no-op, `created_at` was **never added to the table**.

### The Insert That Crashes

The `FailureAtlasRepository.insert_entry()` method references `created_at` in its INSERT statement:

```python
def insert_entry(self, entry):
    entry.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    self._execute("""
        INSERT OR REPLACE INTO failure_atlas_entries (
            ..., created_at, ...
        ) VALUES (..., ?, ...)
    """, (..., entry.get("created_at"), ...))
```

### Why It Triggers for Some Designs but Not Others

The crash occurs during `_run_failure_detection()` which is called after SIGN_OFF for EVERY run. It only crashes if:

- `detect_failures()` returns entries, OR
- Log file scanning finds signature matches

**Counter** (runs to completion): had no ORFS log in its `logs/` directory, so log scanning found no matches, and `detect_failures()` returned empty list. No `insert_entry` call → no crash.

**UART** (stuck at RUNNING/SIGN_OFF): had a 90KB `openroad.log` that triggered signature matches in log scanning → `insert_entry` called → crash.

Difference: UART is more complex, generating more log output that matches failure signatures.

## 4. Why Previous Debugging Missed It

1. **Counter happened to work**: The counter and tiny_or designs completed as SUCCESS because they had no ORFS log files in their logs/ directory, so the insert was never triggered. This created a false signal that "some designs work."

2. **Running → SuCCESS** The crash occurs AFTER SIGN_OFF 100% is printed, so the user sees all stages complete and then an "ERROR: Unexpected error" — making it look like a post-processing issue.

3. **The error appears at the END**, not at the beginning. When debugging the pipeline hang (at DRC 86%), the team was looking at the wrong place. The real issue was only visible once the pipeline stopped hanging.

4. **`insert_entry` succeeds for `runs` table**: The `runs` table uses ALTER TABLE ADD COLUMN for its `created_at` column (migration 2), which always works. Developers assumed the same pattern works for `failure_atlas_entries`. But `failure_atlas_entries` embeds `created_at` in the initial CREATE TABLE (migration 1), which was a no-op.

## 5. Minimal Fix (applied)

### Fix 1: Add `created_at` column
Migration 6 in `gli_flow/database/migrations.py`:
```python
Migration(6, "add created_at to failure_atlas_entries", """
    ALTER TABLE failure_atlas_entries ADD COLUMN created_at TEXT DEFAULT (datetime('now'))
"""),
```

### Fix 2: JSON-serialize `recommended_fix` in INSERT binding
`failure_atlas/repository.py:92`:
```python
# BEFORE:
entry.get("recommended_fix", ""),

# AFTER:
json.dumps(rf) if not isinstance(rf := entry.get("recommended_fix", ""), str) else rf,
```

## 6. Permanent Fix

1. **Migration 6** handles existing databases (adds `created_at` column).
2. **JSON-serialize `recommended_fix`** ensures it binds as TEXT regardless of whether callers pass a list or string.
3. **Audit all migration v1 CREATE TABLE statements** to verify they match their INSERT column sets. Any column in INSERT that is in the initial CREATE TABLE but was added by legacy code will miss the ALTER TABLE migration.
4. **Audit all INSERT bindings** for type safety — `json.dumps()` dict/list fields before binding.
5. **Add a schema validation test** that: creates a fresh database, applies migrations, inserts a sample entry, and asserts no errors.

## 7. Regression Test

```python
def test_failure_atlas_insert_after_migration():
    """Verify insert_entry succeeds after full migration."""
    import tempfile
    from failure_atlas.repository import FailureAtlasRepository
    
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        repo = FailureAtlasRepository(db_path=f.name)
        entry = {
            "run_id": "test",
            "failure_id": "test_fail",
            "failure_type": "TEST",
            "severity": "LOW",
            "title": "Regression test",
            "description": "Verify insert works",
            "detected_at": "2026-01-01T00:00:00",
        }
        eid = repo.insert_entry(entry)
        assert eid is not None
        retrieved = repo.get_entries_for_run("test")
        assert len(retrieved) == 1
```

## Appendix: Ancillary Issues (Not First Fatal)

These issues exist but are downstream of the `created_at` crash:

| Issue | Impact | Stage |
|-------|--------|-------|
| Magic 8.3.105 vs required 8.3.411 | LVS extraction fails | LVS (caught, skipped) |
| KLayout DRC script lookup expects pdk="sky130A" but manifest sends pdk="sky130" | KLayout DRC silently skipped | DRC (caught, skipped) |
| DB run status stuck at "RUNNING" for failed runs | Status not updated | SIGN_OFF |
| `PDK_ROOT` env var not set; DRC helper defaults to `~/pdk` which doesn't exist | DRC tech files may not load | DRC (uses ORFS platform LEFs, not PDK direct) |
| Density check exits 1 for tiny designs | Warning only, non-blocking | DENSITY_CHECK |
| Docker daemon not running | INFO only in local mode | DOCKER (non-required) |
