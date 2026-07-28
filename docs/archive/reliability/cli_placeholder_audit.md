# CLI Placeholder & Stub Audit

**Generated:** 2026-06-12  
**Methodology:** Source code inspection, grep for TODO/NotImplementedError/pass/stub patterns

---

## Summary

**Zero placeholders or stubs found in the CLI layer.**

No command handler contains:
- `TODO` or `FIXME` or `HACK` or `XXX`
- `NotImplementedError` or `raise NotImplementedError`
- `pass` as a function body (all `pass` instances are in exception handlers or abstract methods)
- Print-only "stub" messages
- Empty function bodies

---

## Detailed Findings

### `pass` Statements Found (all legitimate)

| File | Line | Context |
|------|------|---------|
| `core/orchestrator.py` | 306 | `except` block (error suppression) |
| `core/orchestrator.py` | 322 | `except` block (error suppression) |
| `core/orchestrator.py` | 748 | `except` block (error suppression) |
| `core/orchestrator.py` | 1035 | `except` block (error suppression) |
| `core/orchestrator.py` | 1039 | `except` block (error suppression) |
| `infrastructure/repair_actions.py` | 24, 28, 32 | Abstract base class method declarations |
| `infrastructure/repair_actions.py` | 310 | `except` block (error suppression) |
| `environment_validator.py` | 91 | `except` block (platform detection fallback) |
| `installer/installer.py` | 273 | `except ImportError` block |
| `parser/rtl_parser.py` | 197 | Intentional no-op for width=0 |
| `database/migrations.py` | 248, 269, 350 | Error recovery backward-compat |
| `scheduler/worker.py` | 123 | `except` block (resource error fallback) |

All 14 `pass` statements are **legitimate** — none indicate a stub or placeholder.

---

### `TODO` / `FIXME` / `HACK` / `XXX`

**Zero instances** across the entire `gli_flow/` source tree.

---

### `NotImplementedError`

**Zero instances.** The only match is `scheduler/resource.py:44` which uses `NotImplementedError` in a legitimate `try/except` fallback, not as a placeholder.

---

## Broken Code Found

### 1. `ci` command — TypeError Bug

**File:** `gli_flow/ci/runner.py:72-73`  
**Code:**
```python
def _extract_metrics(self) -> dict:
    from gli_flow.database.manager import get_runs
    runs = get_runs(limit=1)  # BUG: missing required db_path argument
```

**Function signature:** `def get_runs(db_path, limit=20):`

The `get_runs` function requires `db_path` as first positional argument. The `CIRunner._extract_metrics` method calls it without `db_path`, causing a `TypeError` at runtime.

**Impact:** `gli-flow ci <design>` crashes with `TypeError: get_runs() missing 1 required positional argument: 'db_path'`

---

## Conclusion

The CLI and core modules are **genuinely implemented** with no intentional stubs or placeholders. The only blocking defect is the CI command argument mismatch.
