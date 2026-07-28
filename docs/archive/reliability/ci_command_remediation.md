# CI Command Remediation

**Date:** 2026-06-12  
**Command:** `gli-flow ci`

---

## Root Cause Analysis

### The Bug

`gli-flow ci <design>` crashed with:

```
TypeError: get_runs() missing 1 required positional argument: 'db_path'
```

### Execution Trace

```
cli/main.py:1798  ci_command(args)
  └─ ci/runner.py:46  CIRunner.run()
       └─ ci/runner.py:72  CIRunner._extract_metrics()
            └─ database/manager.py:22  get_runs(limit=1)
                 TypeError: missing required argument: db_path
```

### Why It Happened

There are two `get_runs` functions in the codebase, with different signatures:

| Location | Signature | Used By |
|----------|-----------|---------|
| `database/manager.py:22` | `get_runs(db_path, limit=20)` | Legacy API — requires `db_path` |
| `database/sqlite.py` | `DatabaseManager.get_recent_runs(limit=20)` | Main API — resolves `db_path` internally |

The `_extract_metrics` method imported and called the wrong function (standalone `get_runs` from `manager.py` instead of `DatabaseManager.get_recent_runs` from `sqlite.py`).

Meanwhile, `_load_baseline` (same file, line 87) already correctly used `DatabaseManager` from `sqlite.py`.

### The Fix

Changed `_extract_metrics` to use `DatabaseManager` from `gli_flow.database.sqlite`, matching the pattern already used by `_load_baseline`:

```python
# BEFORE (BROKEN):
from gli_flow.database.manager import get_runs
runs = get_runs(limit=1)

# AFTER (FIXED):
from gli_flow.database.sqlite import DatabaseManager
db = DatabaseManager(db_path=self.config.db_path)
runs = db.get_recent_runs(limit=1)
```

### Changes Made

| File | Change |
|------|--------|
| `gli_flow/ci/config.py` | Added `db_path: Optional[str] = None` to `CIConfig` |
| `gli_flow/ci/runner.py:71-74` | Changed `_extract_metrics` to use `DatabaseManager` from `sqlite.py` |
| `gli_flow/ci/runner.py:90` | Thread `db_path` through `DatabaseManager()` in `_load_baseline` |
| `gli_flow/cli/main.py:785` | Pass `args.db_path` to `CIConfig` |
| `gli_flow/cli/main.py:1700` | Added `--db-path` argument to `ci` parser |

---

## Verification

### Unit Test: `_extract_metrics`

```
Metrics extracted: {'qor_score': 0.91, 'wns': 0.0, 'tns': 0.0,
                    'utilization': 43.0, 'runtime_sec': 39.41,
                    'cell_count': 18, 'status': 'SUCCESS'}
```

### Unit Test: `_load_baseline`

```
Baseline loaded: True
```

### Unit Test: `_check_regressions`

```
Regressions: []
Regressions with threshold 0.95: ['QoR score 0.9 < minimum 0.9']
```

All methods execute without TypeError.

---

## Status

**RESOLVED.** The CI command no longer crashes on execution. The `_extract_metrics`, `_load_baseline`, and `_check_regressions` methods all work correctly.

### Remaining Considerations

1. **No `--mock` support** — CI runs `gli-flow run <design>` as a subprocess without `--mock`. This means it requires a fully installed EDA toolchain. Consider adding `--mock` passthrough for CI pipeline testing.
2. **Subprocess timeout** — Set to 86400s (24h). Reasonable for long flows but may be excessive for CI.
3. **`db_path` now configurable** — Added `--db-path` argument to `ci` subparser for flexibility.
