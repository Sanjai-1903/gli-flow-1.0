# Failure Atlas Cloud Ingestion — Upload Path Inventory

## Overview

Three distinct upload paths carry Failure Atlas data from local execution to the
cloud ingestion server at `/api/v1/telemetry`.  Before today's fixes, only Path C
(CLI export) existed; Path A had a key-name mismatch (P0) and Path B was not
wired to any caller (P0).

---

## Path A — Bulk Upload via `TelemetryUploader`

**File:** `gli_flow/telemetry/uploader.py`  
**Trigger:** `auto_upload_run()` called from `orchestrator.py:1304` after stage loop completes.

Flow:

1. `FlowOrchestrator.run()` finishes all `STAGES`
2. Calls `auto_upload_run(self.run_id, self.db_path)` → spawns subprocess
3. Subprocess calls `TelemetryUploader.upload_run_telemetry(run_id)`
4. Calls `TelemetryExporter.export_to_json(run_id=run_id)` (`export.py:229`)
5. `export_telemetry()` queries `community_unknown_dataset` table, builds payload
6. Payload contains: `telemetry_events`, `failure_atlas_entries` (was `unknown_failures`), `escalations`
7. `resolution_patterns` is stripped before POST (`uploader.py:84`)
8. POST to `{server_url}/api/v1/telemetry`

**Status:** FIXED — key renamed `unknown_failures` → `failure_atlas_entries` in `export.py:213,220` and
`uploader.py:67,89`.  `resolution_patterns` removed from upload payload (`uploader.py:84`).

**Resilience:** Queue + retry via `UploadQueue` / `RetryEngine`.

---

## Path B — Dedicated Upload via `FailureAtlasUploader`

**File:** `gli_flow/telemetry/failure_atlas_uploader.py`  
**Trigger:** NOW wired in `orchestrator.py:1306–1314` after `auto_upload_run()`.

Flow:

1. After bulk upload completes, orchestrator creates `FailureAtlasUploader`
2. Fetches all `FailureAtlasRepository.get_entries_for_run(self.run_id)`
3. For each entry: `fa_uploader.upload_entry_queued(entry, run_id=self.run_id)`
4. Calls `fa_uploader.process_queue()` which retries any failed uploads
5. Each entry is privacy-sanitized (via `PrivacyValidator`) before upload
6. Payload uses correct `failure_atlas_entries` key (already correct before fix)

**Status:** FIXED — wired into orchestrator post-run section at `orchestrator.py:1306`.

**Resilience:** Individual entry retry via `UploadQueue` / `RetryEngine`.

---

## Path C — CLI Export (No Upload)

**File:** `failure_atlas/community_intelligence/export.py` (`.export_to_json()`, `.export_to_csv()`)  
**Trigger:** User runs `gli-flow export` or similar.

Flow:

1. CLI calls `TelemetryExporter.export_to_json()` or `export_to_csv()`
2. Queries `community_unknown_dataset` table
3. Outputs to local file (JSON or CSV)
4. **No network request** — purely local data export

**Status:** Key name updated for consistency (`unknown_failures` → `failure_atlas_entries`).
`ReplayEngine` reads exports with backward-compatible fallback (`replay.py:44`).

---

## Payload Key Mapping (Before vs After Fixes)

| Export key (before) | Export key (after) | Server model field | Server table |
|---|---|---|---|
| `unknown_failures` | `failure_atlas_entries` | `UploadPayload.failure_atlas_entries` | `failure_atlas_events` |
| `resolution_patterns` | *(removed from upload)* | *(not in UploadPayload)* | *(silently dropped)* |

---

## Bugs Fixed in This Sprint

| Bug | Severity | File | Fix |
|---|---|---|---|
| `unknown_failures` key → pydantic silent drop | **P0** | `export.py:213,220`, `uploader.py:67,89` | Rename to `failure_atlas_entries` |
| `FailureAtlasUploader` never called | **P0** | `orchestrator.py:1306–1314` | Wire into post-run section |
| Privacy substring match blocks `source_version` | **P1** | `export.py:39–40` | `any(excluded in key_lower)` → `key_lower in EXCLUDED_FIELDS` |
| `resolution_patterns` not in server model | **P1** | `uploader.py:84` | Strip before POST |
| `ir_violation_count=0`, `signoff_hold_satisfied=False` | **P2** | `parser.py:378,616` | Replace with `None` |

---

## Schema Alignment

| Source | `community_unknown_dataset` columns | `UploadPayload.failure_atlas_entries` fields | `failure_atlas_events` table columns |
|---|---|---|---|
| Match? | Partial | Full | Full |
| Gap | DB has `signature`, `ai_helpfulness`, `resolution_outcome`, `consent_given`, `escalation_id` | Model has `detected_at`, `title`, `description`, `severity`, `tool_name`, `tool_stage` | Table has `ingested_at`, `upload_batch_id` |

The upload path filters to intersection fields via `FailureAtlasUploader._build_payload()` (`failure_atlas_uploader.py:29–35`).
