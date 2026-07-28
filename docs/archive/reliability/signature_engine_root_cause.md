# Signature Engine Root Cause Analysis

## Summary

**Problem:** Only 6 signatures loaded from `failure_atlas/signatures/` directory. Test expected >=20. `test_signature_engine_scan` found 0 matches (expected >=1). The Failure Atlas could not detect any known failure modes.

## Root Cause

`failure_atlas/signature_engine.py:load_signatures()` used a **mutual-exclusion pattern** — load from new directory structure OR fall back to old `signatures.json`, but never both.

```python
# Old code — mutual exclusion
signatures_dir = ROOT_DIR / "failure_atlas" / "signatures"
if signatures_dir.exists():
    for json_file in signatures_dir.rglob("*.json"):
        ...
        signatures.append(json.load(f))  # 6 files loaded
if not signatures:                       # ← 6 is truthy, so THIS IS NEVER REACHED
    with open(SIGNATURE_FILE) as f:
        signatures = json.load(f)        # 21 entries — always skipped
```

## Evidence

| Source | Location | Count | Reachable? |
|--------|----------|-------|-----------|
| `failure_atlas/signatures/` directory | 6 individual JSON files | 6 | Always (exists first) |
| `failure_atlas/signatures.json` | 21 entries in JSON array | 21 | Never (blocked by `if not signatures`) |

## Impact

- `test_signature_engine_load` failed: 6 != >=20
- `test_signature_engine_scan` failed: 0 findings (loaded signatures lack `observed_signature` field)
- Failure Atlas log scanning produced zero matches for known failure patterns
- All 21 signatures in `signatures.json` (FA-0001 through FA-0020, INF-PWR-001) were invisible to the system

## Fix Applied

Merged both sources in `load_signatures()`:
1. Load all files from `signatures/` directory (deduplicated by `rule_id`/`atlas_id`)
2. Always also load from `signatures.json` (deduplicated, directory takes priority)
3. Sorted directory traversal for deterministic loading

**Result:** 27 signatures load (6 directory + 21 legacy), satisfying the >=20 assertion.

## Validation

- `test_signature_engine_load` — PASS (27 >= 20)
- `test_signature_engine_scan` — PASS (legacy signatures have `observed_signature`, so keyword scanning works)
- Manual: `load_signatures()` returns 27 entries covering all original FA-0001 through INF-PWR-001 plus directory-based deep signatures
- Full test suite: 466 passed, 0 failed, 1 skipped
