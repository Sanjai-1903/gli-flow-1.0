# Local Mode Telemetry Certification v1

**Date:** 2026-06-20
**Components:** `FailureAtlasUploader`, `uploader.py`, `orchestrator.py`
**Modules:** `gli_flow/telemetry/failure_atlas_uploader.py`, `gli_flow/telemetry/uploader.py`, `gli_flow/core/orchestrator.py`

---

## Requirements

- [x] No HTTP/connection-refused warnings when telemetry mode is LOCAL or DISABLED
- [x] No stale queued uploads retried on every run
- [x] Queued uploads are silently dropped (no logging noise) when upload is not allowed

## Changes Made

### 1. `FailureAtlasUploader.should_upload()` (new method)
Checks `TelemetrySettings.mode` and `consent_given` before any upload attempt.

```python
def should_upload(self) -> bool:
    if self.settings.mode == TelemetryMode.LOCAL or self.settings.mode == TelemetryMode.DISABLED:
        return False
    if not self.settings.consent_given:
        return False
    return True
```

### 2. `upload_entry()` — early return guard
```python
if not self.should_upload():
    return False
```

### 3. `upload_entry_queued()` — early return guard
```python
if not self.should_upload():
    return
```

### 4. Stale queue cleared
11 stale upload items (10 failed, 1 pending) were removed from the upload queue database to prevent retry-engine noise on future runs.

## Guard Coverage

| Upload path | Affected code | Guarded |
|-------------|---------------|---------|
| `auto_upload_run` → `trigger_background_upload` | `uploader.py:159` | Already guarded (`should_upload()`) |
| `FailureAtlasUploader.upload_entry()` | `failure_atlas_uploader.py` | Now guarded |
| `FailureAtlasUploader.upload_entry_queued()` | `failure_atlas_uploader.py` | Now guarded |
| `FailureAtlasUploader.process_queue()` (via retry) | `failure_atlas_uploader.py` → `retry_engine.py` | Guarded — `upload_entry_queued` returns early |
| Orchestrator call at `orchestrator.py:1306-1314` | `orchestrator.py` | Covered by `upload_entry_queued` guard |

## Verification

- [x] `gli-flow run examples/counter --mock` produces no connection-refused warnings
- [x] Queue stats show only expected items (from atlas-mode runs)
- [x] `gli-flow telemetry status` works correctly (mode: atlas)
- [x] Mode `local` tested via `should_upload()` returning False
- [x] Mode `disabled` tested via `should_upload()` returning False

## Certification
**Status:** PASS
**Reviewer:** Automated audit
**Evidence:** Mock run executed without connection-refused noise on 2026-06-20
