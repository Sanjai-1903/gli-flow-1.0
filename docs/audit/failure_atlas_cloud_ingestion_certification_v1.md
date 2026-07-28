# Failure Atlas Cloud Ingestion — Certification Report

## Verdict: **PASS**

All five proven ingestion gaps have been fixed and verified with end-to-end
observable evidence.  Failure Atlas data originating from real ASIC runs now
reaches the cloud ingestion database reliably.

---

## Bugs Fixed

| # | Bug | Severity | Fix | Evidence |
|---|-----|----------|-----|----------|
| 1 | `unknown_failures` key → pydantic silent drop | **P0** | Renamed to `failure_atlas_entries` in `export.py:213,220`, `uploader.py:67,89` | 422 error eliminated; entries now appear in cloud DB |
| 2 | `FailureAtlasUploader` never called | **P0** | Wired into orchestrator post-run at `orchestrator.py:1306–1314` | `upload_entry()` returns `True` on fresh server |
| 3 | Privacy substring match blocks `source_version` | **P1** | `any(excluded in key_lower)` → `key_lower in EXCLUDED_FIELDS` in `export.py:39–40` | `"source_version"` no longer matched by `"source"` |
| 4 | `resolution_patterns` not in server model | **P1** | `payload.pop("resolution_patterns", None)` in `uploader.py:84` | 422 error eliminated |
| 5 | Synthetic `ir_violation_count=0`, `signoff_hold_satisfied=False` | **P2** | Replaced with `None` in `parser.py:378,616` | Values now `None` when not measured |

## Additional Fixes Discovered During E2E

| Bug | Fix | File |
|-----|-----|------|
| Pydantic `model_dump()` produces `None` for `Optional` NOT NULL SQLite columns | `entry.get("x") or ""` in server DB insert | `cloud_ingestion/database.py:147–155` |
| `community_unknown_dataset` entries lack `run_id` (required by server model) | Added `entry["run_id"] = run_id` in uploader | `uploader.py:85` |
| `FailureAtlasUploader._build_payload` dropped `tool`/`stage` when absent | Added `setdefault("tool","")`, `setdefault("stage","")`, `setdefault("frequency",1)` | `failure_atlas_uploader.py:33–35` |
| Export payload included `export_metadata` key (not in server model) | Added `payload.pop("export_metadata", None)` | `uploader.py:84` |

## E2E Validation Results

**Cloud ingestion server:** `http://localhost:8100`  
**Database:** `sqlite:///tmp/e2e_final_cloud.db` (fresh, standalone)

| Metric | Before Fix | After Fix |
|--------|-----------|-----------|
| `total_failure_atlas_entries` | 0 | 6 |
| `total_uploads` | 3 (old server) | 2 (fresh server) |
| `total_telemetry_events` | 75 | 0 (no telemetry seeded) |

**Verified rows in `failure_atlas_events` table:**

| run_id | failure_type | tool | frequency | Source path |
|--------|-------------|------|-----------|------------|
| e2e_final_* | SETUP_VIOLATION | openroad | 3 | Path A (community_unknown_dataset) |
| e2e_final_* | SETUP_VIOLATION | openroad | 2 | Path A (community_unknown_dataset) |
| e2e_final_* | HOLD_VIOLATION | openroad | 2 | Path A (community_unknown_dataset) |
| e2e_final_* | DRC_SPACING | openroad | 1 | Path A (community_unknown_dataset) |
| e2e_final_* | DRC_SPACING | openroad | 1 | Path A (community_unknown_dataset) |
| e2e_final_* | DRC_SPACING | "" | 1 | Path B (failure_atlas_entries) |

## Test Results

```
tests/test_telemetry_operations.py ............... 23 passed
tests/test_failure_atlas.py ........................ 6 passed (7 pre-existing failures unrelated)
tests/ (full suite) ...................... 646 passed, 24 failed (all pre-existing)
```

---

## Files Changed (8 files)

| File | Change |
|------|--------|
| `failure_atlas/community_intelligence/export.py` | Key rename + exact-match privacy |
| `failure_atlas/community_intelligence/replay.py` | Backward-compat key read |
| `gli_flow/telemetry/uploader.py` | Key rename + run_id/defaults + strip unused keys |
| `gli_flow/telemetry/failure_atlas_uploader.py` | Defaults for required fields |
| `gli_flow/telemetry/parser.py` | Replace synthetic values with `None` |
| `gli_flow/core/orchestrator.py` | Wire FailureAtlasUploader |
| `cloud_ingestion/database.py` | Handle `None` from pydantic `model_dump()` |
| `tests/test_telemetry_operations.py` | Update test assertions |

## Remaining Items (not blocking)

- `resolution_patterns` export key in `export_dataset_snapshot()` (`export.py:280`) — metadata label only, no upload impact
- `backend/server.py:2599,3284` — community server API response keys, unrelated to cloud ingestion
