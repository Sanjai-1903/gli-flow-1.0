# Telemetry Field Provenance Audit v1

**Date:** 2026-06-18
**Scope:** Every field uploaded to cloud ingestion via all three upload paths, plus every field produced by the telemetry parser (`telemetry.json`).

---

## Classification System

| Class | Definition | Color |
|-------|-----------|-------|
| **VERIFIED** | Directly measured from a known source (tool report, command output, DB record, filesystem stat) | Green |
| **DERIVED** | Computed or derived from VERIFIED fields (e.g., `drc_is_clean` from `total_violations == 0`) | Blue |
| **HEURISTIC** | Estimated, inferred, or algorithmically weighted (e.g., trust scores, QoR breakdown) | Yellow |
| **SYNTHETIC** | Fabricated — hardcoded constant, always-None, or placeholder awaiting real implementation | Red |

---

## Upload Paths

| Path | Entry Point | Destination | Used By |
|------|------------|-------------|---------|
| **A** — Run telemetry | `TelemetryUploader.upload_run_telemetry(run_id)` | `POST /api/v1/telemetry` | Background upload after each run |
| **B** — Failure Atlas (direct) | `FailureAtlasUploader.upload_entry(entry)` | `POST /api/v1/telemetry` | API callers |
| **C** — Failure Atlas (queued) | `FailureAtlasUploader.upload_entry_queued(entry)` | `POST /api/v1/telemetry` | API callers |
| Local-only | `TelemetryManager.export_metrics()` → `telemetry/metrics.json` | Local disk | Dashboard, telemetry JSON |

---

## Path A Payload: Top-level Envelope

Source: `gli_flow/telemetry/uploader.py:64-85`

| Field | Source | Evidence | Null? | Classification | GLI-SDI Safe? |
|-------|--------|----------|-------|---------------|---------------|
| `run_id` | Function arg (from orchestrator) | `uploader.py:84` | No | **VERIFIED** | ✅ |
| `source_version` | Hardcoded `"1.0"` | `uploader.py:85` | No | **SYNTHETIC** | ⚠️ Hardcoded, no semantic value |
| `telemetry_events` | `community_telemetry` DB table | `export.py:219` | Default `[]` | **VERIFIED** | ✅ |
| `failure_atlas_entries` | Exported as `unknown_failures` — **NEVER REACHES SERVER** | See Finding #1 | N/A | **SYNTHETIC** (always empty for Path A) | ❌ Never populated |
| `escalations` | `community_escalations` DB table | `export.py:221` | Default `[]` | **VERIFIED** | ✅ |
| `export_metadata` | Computed by exporter | `export.py:208` | No | **DERIVED** | ✅ |
| `resolution_patterns` | Exported but **DROPPED BY SERVER** | See Finding #2 | N/A | **SYNTHETIC** (never received) | ❌ Never received |

---

## Path A: `export_metadata` Fields

Source: `gli_flow/telemetry/export.py:208-218`

| Field | Source | Evidence | Null? | Classification | GLI-SDI Safe? |
|-------|--------|----------|-------|---------------|---------------|
| `version` | Hardcoded `"1.0"` | `export.py:209` | No | **SYNTHETIC** | ⚠️ No semantic value |
| `exported_at` | `datetime.utcnow().isoformat()` | `export.py:210` | No | **VERIFIED** | ✅ Timestamp |
| `record_count.telemetry_events` | `len(telemetry)` | `export.py:212` | No | **DERIVED** | ✅ |
| `record_count.unknown_failures` | `len(unknowns)` | `export.py:213` | No | **DERIVED** | ✅ |
| `record_count.escalations` | `len(escalations)` | `export.py:214` | No | **DERIVED** | ✅ |
| `record_count.resolution_patterns` | `len(patterns)` | `export.py:215` | No | **DERIVED** | ✅ |
| `privacy_validated` | `PrivacyValidator.generate_report()` | `export.py:225` | No | **VERIFIED** | ✅ |
| `privacy_report.valid` | Boolean from validator | `export.py:96-102` | No | **VERIFIED** | ✅ |
| `privacy_report.issues` | List of issue strings | `export.py:97` | Yes (empty) | **VERIFIED** | ✅ |
| `privacy_report.issue_count` | `len(issues)` | `export.py:98` | No | **DERIVED** | ✅ |
| `privacy_report.validated_at` | `datetime.utcnow().isoformat()` | `export.py:99` | No | **VERIFIED** | ✅ Timestamp |

---

## Path A: `telemetry_events[]` Fields

Source: `community_telemetry` DB table, inserted via `EscalationTelemetry.record()` at `gli_flow/telemetry/telemetry.py:57-84`

| Field | DB Column | Source | Null? | Classification | GLI-SDI Safe? |
|-------|-----------|--------|-------|---------------|---------------|
| `id` | Auto-increment | Database | No | **VERIFIED** | ✅ |
| `event` | Event name | Caller arg | No | **VERIFIED** | ✅ |
| `escalation_id` | Escalation ID | Caller arg | Yes (default `""`) | **VERIFIED** | ✅ |
| `failure_type` | Failure type string | Caller arg | Yes (default `""`) | **VERIFIED** | ✅ |
| `tool` | Tool name | Caller arg | Yes (default `""`) | **VERIFIED** | ✅ |
| `atlas_id` | Atlas ID | Caller arg | Yes (default `""`) | **VERIFIED** | ✅ |
| `details` | JSON dict | Caller arg, filtered to safe keys | Yes (default `{}`) | **VERIFIED** (caller-supplied, sanitized) | ✅ |
| `created_at` | ISO timestamp | `datetime.now(timezone.utc)` | No | **VERIFIED** | ✅ Timestamp |

### `details` Sub-fields (filtered to safe_keys in `backend/server.py:1710-1717`)

Always allowed (from `safe_keys` set): `signature`, `error_class`, `confidence`, `severity`, `stage`, `tool`, `failure_type`, `frequency`, `ai_helpfulness`, `resolution_outcome`.

Occasional extras from `_capture_unknown_failure`: `source`.

| Sub-field | Source | Evidence | Null? | Classification | GLI-SDI Safe? |
|-----------|--------|----------|-------|---------------|---------------|
| `signature` | Caller (from failure detection) | `server.py:2153` | Yes | **VERIFIED** | ✅ |
| `error_class` | Caller (failure type) | `server.py:2153` | Yes | **VERIFIED** | ✅ |
| `confidence` | Caller (AI confidence) | `server.py:2153` | Yes | **HEURISTIC** | ⚠️ AI-generated |
| `severity` | Caller | `server.py:2153` | Yes | **VERIFIED** | ✅ |
| `stage` | Caller | `server.py:2153` | Yes | **VERIFIED** | ✅ |
| `source` | Caller (not in safe_keys, but present) | `server.py:2153` | Yes | **VERIFIED** | ✅ |
| `frequency` | Caller | `server.py:1710` | Yes | **VERIFIED** | ✅ |
| `ai_helpfulness` | Caller (user feedback) | `server.py:1710` | Yes | **VERIFIED** | ✅ |
| `resolution_outcome` | Caller | `server.py:1710` | Yes | **VERIFIED** | ✅ |
| `consent_given` | Caller (from escalation) | `server.py:2475` | Yes | **VERIFIED** | ✅ |

---

## Path A: `escalations[]` Fields

Source: `community_escalations` DB table, inserted via `EscalationManager.create_escalation()` at `failure_atlas/community_intelligence/escalation.py:98-112`

| Field | Source | Evidence | Null? | Classification | GLI-SDI Safe? |
|-------|--------|----------|-------|---------------|---------------|
| `id` | Generated UUID (`ESC-YYYYMMDD-XXXXXX`) | `escalation.py:98` | No | **VERIFIED** | ✅ |
| `run_id` | Caller arg | `escalation.py:108` | Yes (default `""`) | **VERIFIED** | ✅ |
| `failure_type` | Caller arg | `escalation.py:108` | No | **VERIFIED** | ✅ |
| `tool` | Caller arg | `escalation.py:108` | Yes (default `""`) | **VERIFIED** | ✅ |
| `stage` | Caller arg | `escalation.py:108` | Yes (default `""`) | **VERIFIED** | ✅ |
| `status` | Hardcoded `'open'` on create | `escalation.py:106` | No | **SYNTHETIC** (always `"open"` first) | ⚠️ |
| `consent_given` | Bool converted from caller arg | `escalation.py:109` | No (0/1) | **VERIFIED** | ✅ |
| `consent_timestamp` | `datetime.now(...)` if consent given | `escalation.py:110` | Yes (default `""`) | **VERIFIED** | ✅ |
| `bharatcode_submission_id` | From email API response | `escalation.py:139-155` | Yes (default `""`) | **VERIFIED** | ✅ |
| `bharatcode_status` | From email API response | `escalation.py:140-164` | Yes (default `""`) | **VERIFIED** | ✅ |
| `ai_summary` | Caller arg | `escalation.py:111` | Yes (default `""`) | **HEURISTIC** (AI-generated) | ⚠️ |
| `user_notes` | Caller arg | `escalation.py:111` | Yes (default `""`) | **VERIFIED** (user-provided) | ✅ |
| `engineer_response` | JSON-dumped response from engineer | `escalation.py:191` | Yes (default `'{}'`) | **VERIFIED** | ✅ |
| `atlas_id_created` | From engineer response | `escalation.py:192` | Yes (default `""`) | **VERIFIED** | ✅ |
| `created_at` | `datetime.now(timezone.utc).isoformat()` | `escalation.py:112` | No | **VERIFIED** | ✅ |
| `sent_at` | Timestamp set on send | `escalation.py:146` | Yes (default `""`) | **VERIFIED** | ✅ |
| `resolved_at` | Timestamp set on resolve | `escalation.py:193` | Yes (default `""`) | **VERIFIED** | ✅ |

ATLAS-mode filtered (uploader only sends `tool`, `stage`, `failure_type` from details).

---

## Path A: `unknown_failures[]` Fields (DROPPED BY SERVER — Finding #1)

Source: `community_unknown_dataset` DB table at `failure_atlas/community_intelligence/dataset.py:54-97`

**Critical:** Exported under key `unknown_failures` (line 220 of `export.py`) but server expects `failure_atlas_entries`. All records silently dropped by pydantic.

| Field | Source | Evidence | Null? | Classification | GLI-SDI Safe? |
|-------|--------|----------|-------|---------------|---------------|
| `id` | Auto-increment | Database | No | **VERIFIED** | ✅ |
| `tool` | Caller arg | `dataset.py:91` | No | **VERIFIED** | ✅ |
| `failure_type` | Caller arg | `dataset.py:91` | No | **VERIFIED** | ✅ |
| `signature` | Caller arg | `dataset.py:91` | Yes (default `""`) | **VERIFIED** | ✅ |
| `frequency` | Counted (incremented) | `dataset.py:91` | No | **VERIFIED** | ✅ |
| `ai_helpfulness` | Caller arg, default `"unknown"` | `dataset.py:91` | No | **VERIFIED** | ✅ |
| `resolution_outcome` | Hardcoded `''` on insert | `dataset.py:87` | Yes (empty string) | **SYNTHETIC** (always empty on insert) | ⚠️ |
| `consent_given` | `int(consent_given)` from caller | `dataset.py:92` | No (0/1) | **VERIFIED** | ✅ |
| `escalation_id` | Caller arg | `dataset.py:92` | Yes (default `""`) | **VERIFIED** | ✅ |
| `last_seen` | `datetime.now(timezone.utc).isoformat()` | `dataset.py:93` | No | **VERIFIED** | ✅ Timestamp |

---

## Path A: `resolution_patterns[]` Fields (DROPPED BY SERVER — Finding #2)

Source: `resolution_patterns` DB table at `failure_atlas/resolution_intelligence/repository.py:28-60`

**Exported** in the payload but **not in server's `UploadPayload` model** — silently dropped.

| Field | Source | Evidence | Null? | Classification | GLI-SDI Safe? |
|-------|--------|----------|-------|---------------|---------------|
| `id` | Generated UUID | `repository.py:28` | No | **VERIFIED** | ✅ |
| `failure_fingerprint` | Caller-supplied | `repository.py:54` | No | **VERIFIED** | ✅ |
| `failure_type` | Caller-supplied | `repository.py:54` | No | **VERIFIED** | ✅ |
| `root_cause` | Caller-supplied | `repository.py:55` | Yes (nullable) | **VERIFIED** | ✅ |
| `resolution` | Caller-supplied | `repository.py:55` | No | **VERIFIED** | ✅ |
| `resolution_type` | Caller-supplied | `repository.py:55` | Yes (nullable) | **VERIFIED** | ✅ |
| `success_count` | Tracked/counted | `repository.py:56` | No (default 0) | **VERIFIED** | ✅ |
| `failure_count` | Tracked/counted | `repository.py:56` | No (default 0) | **VERIFIED** | ✅ |
| `confidence` | **COMPUTED** by `ResolutionScorer` | `repository.py:35` | No | **HEURISTIC** | ⚠️ Algorithmic |
| `first_seen` | Timestamp | `repository.py:29-30` | Yes (nullable) | **VERIFIED** | ✅ |
| `last_seen` | `datetime.utcnow()` | `repository.py:31` | No | **VERIFIED** | ✅ |
| `created_at` | Passed or COALESCE'd | `repository.py:60` | Yes | **VERIFIED** | ✅ |
| `updated_at` | `datetime.utcnow()` | `repository.py:32` | No | **VERIFIED** | ✅ |
| `unique_runs` | Computed from tracked run IDs | `repository.py:57` | No (default 0) | **DERIVED** | ✅ |
| `unique_designs` | Computed from tracked design names | `repository.py:57` | No (default 0) | **DERIVED** | ✅ |
| `engineer_confirmations` | Incremented on feedback | `repository.py:57` | No (default 0) | **VERIFIED** | ✅ |
| `contradictory_reports` | Incremented on feedback | `repository.py:58` | No (default 0) | **VERIFIED** | ✅ |
| `trust_score` | **COMPUTED** by `TrustScorer.calculate_trust()` | `repository.py:47` | No (default 0.0) | **HEURISTIC** | ⚠️ Algorithmic |
| `trust_level` | **COMPUTED** from trust_score | `repository.py:48` | No (default `UNVERIFIED`) | **HEURISTIC** | ⚠️ Algorithmic |
| `trust_reason` | **COMPUTED** from trust factors | `repository.py:49` | Yes (nullable) | **HEURISTIC** | ⚠️ Algorithmic |
| `tracked_run_ids` | JSON list | `repository.py:89` | No (default `[]`) | **VERIFIED** | ✅ |
| `tracked_design_names` | JSON list | `repository.py:89` | No (default `[]`) | **VERIFIED** | ✅ |

---

## Paths B/C Payload: FailureAtlasUploader

Source: `failure_atlas/community_intelligence/failure_atlas_uploader.py:29-52`

| Field | Source | Evidence | Null? | Classification | GLI-SDI Safe? |
|-------|--------|----------|-------|---------------|---------------|
| `run_id` | Function arg | `failure_atlas_uploader.py:47` | No | **VERIFIED** | ✅ |
| `source_version` | Hardcoded `"1.0"` | `failure_atlas_uploader.py:48` | No | **SYNTHETIC** | ⚠️ |
| `failure_atlas_entries` | List with one sanitized entry | `failure_atlas_uploader.py:49` | No (list) | **VERIFIED** (entry passed in) | ✅ |
| `telemetry_events` | Hardcoded `[]` | `failure_atlas_uploader.py:50` | No | **SYNTHETIC** | ⚠️ Always empty |
| `escalations` | Hardcoded `[]` | `failure_atlas_uploader.py:51` | No | **SYNTHETIC** | ⚠️ Always empty |

### failure_atlas_entries[0] sub-fields

| Field | Source | Evidence | Null? | Classification | GLI-SDI Safe? |
|-------|--------|----------|-------|---------------|---------------|
| `run_id` | From entry dict | `failure_atlas_uploader.py:33` | Yes (stripped) | **VERIFIED** | ✅ |
| `tool` | From entry dict | `failure_atlas_uploader.py:33` | Yes (stripped) | **VERIFIED** | ✅ |
| `stage` | From entry dict | `failure_atlas_uploader.py:33` | Yes (stripped) | **VERIFIED** | ✅ |
| `failure_type` | From entry dict | `failure_atlas_uploader.py:34` | Yes (stripped) | **VERIFIED** | ✅ |
| `error_text` | From entry dict | `failure_atlas_uploader.py:34` | Yes (stripped) | **VERIFIED** | ✅ |
| `design_name` | From entry dict | `failure_atlas_uploader.py:34` | Yes (stripped) | **VERIFIED** | ✅ |
| `design_category` | From entry dict | `failure_atlas_uploader.py:34` | Yes (stripped) | **VERIFIED** | ✅ |
| `log_excerpt` | From entry dict | `failure_atlas_uploader.py:34` | Yes (stripped) | **VERIFIED** | ✅ |
| `frequency` | From entry dict | `failure_atlas_uploader.py:35` | Yes (stripped) | **VERIFIED** | ✅ |
| `first_seen` | From entry dict | `failure_atlas_uploader.py:35` | Yes (stripped) | **VERIFIED** | ✅ |
| `last_seen` | From entry dict | `failure_atlas_uploader.py:35` | Yes (stripped) | **VERIFIED** | ✅ |

---

## Local Telemetry File: `telemetry/metrics.json` Fields

Source: `gli_flow/core/orchestrator.py:525-555` via `TelemetryManager.export_metrics()`

These are the primary measured values from an ASIC run. Most are written by the orchestrator after parsing tool reports.

| Field | Source | Evidence | Null? | Classification | GLI-SDI Safe? |
|-------|--------|----------|-------|---------------|---------------|
| `run_id` | `self.run_id` | `orchestrator.py:528` | No | **VERIFIED** | ✅ |
| `design_name` | `self.design_name` | `orchestrator.py:529` | No | **VERIFIED** | ✅ |
| `pdk` | Manifest `pdk` field | `orchestrator.py:530` | Yes (`""`) | **VERIFIED** | ✅ |
| `pdk_variant` | Manifest `pdk_variant` field | `orchestrator.py:531` | Yes (`""`) | **VERIFIED** | ✅ |
| `corners` | Corner configs serialized | `orchestrator.py:532` | No (empty list) | **VERIFIED** | ✅ |
| `metrics.wns` | From `self.record.wns` | `orchestrator.py:534` | Yes (None) | **VERIFIED** (measured, possibly null) | ✅ |
| `metrics.tns` | From `self.record.tns` | `orchestrator.py:535` | Yes (None) | **VERIFIED** | ✅ |
| `metrics.utilization` | From `self.record.utilization` | `orchestrator.py:536` | Yes (None) | **VERIFIED** | ✅ |
| `metrics.cell_count` | From `self.record.cell_count` | `orchestrator.py:537` | Yes (None) | **VERIFIED** | ✅ |
| `metrics.runtime_sec` | From `self.record.runtime_sec` | `orchestrator.py:538` | Yes (None) | **VERIFIED** | ✅ |
| `metrics.qor_score` | From QoR computation | `orchestrator.py:539` | Yes (None) | **DERIVED** (weighted formula) | ✅ |
| `metrics.qor_breakdown` | From QoR breakdown dict | `orchestrator.py:540` | No | **HEURISTIC** (weighted sub-scores) | ⚠️ |
| `metrics.qor_weights` | From QoR weight config | `orchestrator.py:541` | No | **HEURISTIC** (config-defined weights) | ⚠️ |
| `metrics.die_area_um2` | Parsed from report | `orchestrator.py:542` | Yes (None) | **VERIFIED** | ✅ |
| `metrics.total_power_mw` | Parsed from report | `orchestrator.py:543` | Yes (None) | **VERIFIED** | ✅ |
| `metrics.internal_power_mw` | Parsed from report | `orchestrator.py:544` | Yes (None) | **VERIFIED** | ✅ |
| `metrics.switching_power_mw` | Parsed from report | `orchestrator.py:545` | Yes (None) | **VERIFIED** | ✅ |
| `metrics.leakage_power_mw` | Parsed from report | `orchestrator.py:546` | Yes (None) | **VERIFIED** | ✅ |
| `metrics.drc_runtime_seconds` | Parsed from report | `orchestrator.py:547` | Yes (None) | **VERIFIED** | ✅ |
| `metrics.lvs_runtime_seconds` | Parsed from report | `orchestrator.py:548` | Yes (None) | **VERIFIED** | ✅ |
| `corner_results` | From corner analysis | `orchestrator.py:553` | Yes (optional) | **VERIFIED** | ✅ |

---

## Parser Fields: Full Classification

Source: `gli_flow/telemetry/parser.py` — `TelemetryParser.parse_all()` and all sub-parsers.

### Timing Parser (`parse_timing`, lines 60-149)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `timing_unit` | Hardcoded `"ns"` | **SYNTHETIC** | ⚠️ Always same value |
| `setup_wns_ns` | Metrics CSV or timing/metrics.rpt | **VERIFIED** | ✅ |
| `setup_tns_ns` | Metrics CSV or timing/metrics.rpt | **VERIFIED** | ✅ |
| `hold_whs_ns` | Metrics CSV or regex from timing.rpt | **VERIFIED** | ✅ |
| `hold_ths_ns` | Metrics CSV or regex from timing.rpt | **VERIFIED** | ✅ |
| `hold_failing_endpoints` | Regex from timing.rpt | **VERIFIED** | ✅ |
| `sta_setup_status` | **COMPUTED** from setup_wns_ns >= 0 → PASS/FAIL/NOT_RUN | **DERIVED** | ✅ |
| `sta_hold_status` | **COMPUTED** from hold_whs_ns >= 0 → PASS/FAIL/NOT_RUN | **DERIVED** | ✅ |
| `timing_status` | **COMPUTED** from sta_setup_status + sta_hold_status | **DERIVED** | ✅ |

### Utilization Parser (`parse_utilization`, lines 151-194)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `utilization` | Metrics CSV or utilization.rpt | **VERIFIED** | ✅ |
| `cell_count` | Metrics CSV or utilization.rpt | **VERIFIED** | ✅ |

### Runtime Parser (`parse_runtime`, lines 196-216)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `runtime_sec` | Metrics CSV or runtime.rpt | **VERIFIED** | ✅ |

### DRC Parser (`parse_drc_report`, lines 218-272)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `drc_{tool}_status` | **COMPUTED** from total violations | **DERIVED** | ✅ |
| `drc_status` | Same as above (aggregated) | **DERIVED** | ✅ |
| `drc_total_violations` | drc_raw.txt or drc_klayout.xml | **VERIFIED** | ✅ |
| `drc_by_category` | Parsed from VIOLATION: lines | **VERIFIED** | ✅ |
| `drc_locations` | Parsed coordinate data | **VERIFIED** | ✅ |
| `drc_is_clean` | **COMPUTED** `total == 0` | **DERIVED** | ✅ |
| `drc_report_error` | Hardcoded error string | **SYNTHETIC** | ⚠️ Only on error |

### LVS Parser (`parse_lvs_report`, lines 274-330)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `lvs_result` | lvs_comp.out (`CLEAN`/`FAIL`/`ERROR`) | **VERIFIED** | ✅ |
| `lvs_status` | **COMPUTED** PASS/FAIL from is_clean | **DERIVED** | ✅ |
| `lvs_unmatched_devices` | Regex from lvs_comp.out | **VERIFIED** | ✅ |
| `lvs_unmatched_nets` | Regex from lvs_comp.out | **VERIFIED** | ✅ |
| `lvs_short_count` | Regex from lvs_comp.out | **VERIFIED** | ✅ |
| `lvs_open_count` | Regex from lvs_comp.out | **VERIFIED** | ✅ |
| `lvs_parameter_mismatches` | Regex from lvs_comp.out | **VERIFIED** | ✅ |
| `lvs_is_clean` | **COMPUTED** from all counts == 0 | **DERIVED** | ✅ |

### Power Parser (`parse_power_report`, lines 332-379)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `power_status` | **COMPUTED** DONE/ERROR/NOT_RUN | **DERIVED** | ✅ |
| `total_power_mw` | power_report.txt regex | **VERIFIED** | ✅ |
| `leakage_mw` | power_report.txt regex | **VERIFIED** | ✅ |
| `internal_mw` | power_report.txt regex | **VERIFIED** | ✅ |
| `switching_mw` | power_report.txt regex | **VERIFIED** | ✅ |
| `max_ir_drop_mv` | **HARDCODED None** | **SYNTHETIC** — never parsed | ❌ Unsuitable for GLI-SDI |
| `mean_ir_drop_mv` | **HARDCODED None** | **SYNTHETIC** — never parsed | ❌ Unsuitable for GLI-SDI |
| `ir_violation_count` | **HARDCODED 0** | **SYNTHETIC** — fabricated | ❌ Unsuitable for GLI-SDI |

### EM Parser (`parse_em_report`, lines 381-408)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `em_status` | **COMPUTED** PASS/FAIL/NOT_RUN/ERROR | **DERIVED** | ✅ |
| `em_total_violations` | em_report.txt regex | **VERIFIED** | ✅ |
| `em_max_current_density_ma_um` | em_report.txt regex | **VERIFIED** | ✅ |
| `em_is_clean` | **COMPUTED** `violations == 0` | **DERIVED** | ✅ |

### Decap Parser (`parse_decap_report`, lines 410-435)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `decap_status` | **COMPUTED** DONE/NOT_RUN/ERROR | **DERIVED** | ✅ |
| `decap_total_cells` | decap_log.txt regex | **VERIFIED** | ✅ |
| `decap_capacitance_pf` | decap_log.txt regex | **VERIFIED** | ✅ |
| `decap_coverage_pct` | **HARDCODED None** | **SYNTHETIC** — never parsed | ❌ Unsuitable for GLI-SDI |
| `decap_coverage_note` | Hardcoded `"not_measured"` | **SYNTHETIC** | ⚠️ |

### Scan Parser (`parse_scan_report`, lines 437-462)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `scan_status` | **COMPUTED** DONE/NOT_RUN/ERROR | **DERIVED** | ✅ |
| `scan_total_flops` | scan_log.txt regex | **VERIFIED** | ✅ |
| `scan_scanned_flops` | scan_log.txt regex | **VERIFIED** | ✅ |
| `scan_coverage_pct` | **COMPUTED** `scanned / total * 100` | **DERIVED** | ✅ |

### ATPG Parser (`parse_atpg_report`, lines 464-494)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `atpg_status` | **COMPUTED** DONE/NOT_RUN/ERROR | **DERIVED** | ✅ |
| `atpg_total_patterns` | atpg_report.txt regex | **VERIFIED** | ✅ |
| `atpg_detected_faults` | atpg_report.txt regex | **VERIFIED** | ✅ |
| `atpg_total_faults` | atpg_report.txt regex | **VERIFIED** | ✅ |
| `atpg_fault_coverage_pct` | **COMPUTED** `detected / total * 100` | **DERIVED** | ✅ |

### Formal Parser (`parse_formal_report`, lines 496-516)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `formal_status` | **COMPUTED** PASS/FAIL/NOT_RUN/ERROR | **DERIVED** | ✅ |
| `formal_compare_points` | formal_log.txt regex | **VERIFIED** | ✅ |
| `formal_is_equivalent` | **COMPUTED** from "not equivalent" check | **DERIVED** | ✅ |
| `formal_failures` | **COMPUTED** `0 if equiv else points` | **DERIVED** | ✅ |

### Antenna Parser (`parse_antenna_report`, lines 518-540)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `antenna_status` | **COMPUTED** PASS/FAIL/NOT_RUN/ERROR | **DERIVED** | ✅ |
| `antenna_total_violations` | antenna_report.txt regex | **VERIFIED** | ✅ |
| `antenna_max_ratio` | antenna_report.txt regex | **VERIFIED** | ✅ |
| `antenna_is_clean` | **COMPUTED** `violations == 0` | **DERIVED** | ✅ |

### Density Parser (`parse_density_report`, lines 542-571)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `density_pct` | density_report.txt regex | **VERIFIED** | ✅ |
| `density_min_pct` | density_report.txt regex | **VERIFIED** | ✅ |
| `density_max_pct` | density_report.txt regex | **VERIFIED** | ✅ |
| `density_violations` | density_report.txt regex | **VERIFIED** | ✅ |
| `density_status` | **COMPUTED** PASS/FAIL/NOT_RUN/ERROR | **DERIVED** | ✅ |

### Signoff Parser (`parse_signoff_report`, lines 573-616)

| Field | Source | Classification | GLI-SDI Safe? |
|-------|--------|---------------|---------------|
| `signoff_timing_status` | **COMPUTED** PASS/ERROR from WNS >= 0 | **DERIVED** | ✅ |
| `signoff_setup_wns_ns` | signoff_setup.rpt regex | **VERIFIED** | ✅ |
| `signoff_setup_tns_ns` | signoff_setup.rpt regex | **VERIFIED** | ✅ |
| `signoff_hold_whs_ns` | **HARDCODED None** — not parsed | **SYNTHETIC** | ❌ Unsuitable for GLI-SDI |
| `signoff_hold_ths_ns` | **HARDCODED None** — not parsed | **SYNTHETIC** | ❌ Unsuitable for GLI-SDI |
| `signoff_setup_satisfied` | **COMPUTED** `wns is not None and wns >= 0` | **DERIVED** | ✅ |
| `signoff_hold_satisfied` | **HARDCODED False** | **SYNTHETIC** — fabricated | ❌ Unsuitable for GLI-SDI |
| `signoff_report_error` | Hardcoded error string | **SYNTHETIC** | ⚠️ Only on error |

### Other Parsers (lines 618-861)

Clock gating, PRO, SI, hierarchical partition, block synthesis, top floorplan, D2D interface, yield — each produces 2-4 fields. All VERIFIED (parsed from specific report files) or DERIVED (status from parsed values). GDS fields (`gds_mtime`, `gds_size_bytes`) are VERIFIED (from `os.stat`).

---

## Summary Statistics

| Classification | Count | Percentage |
|---------------|-------|-----------|
| **VERIFIED** | ~130 | ~60% |
| **DERIVED** | ~55 | ~25% |
| **HEURISTIC** | ~15 | ~7% |
| **SYNTHETIC** | ~18 | ~8% |
| **Total Fields** | ~218 | 100% |

---

## Fields Unsuitable for GLI-SDI Training

These fields contain fabricated or hardcoded data that would introduce noise into any training dataset:

| Field | File | Reason |
|-------|------|--------|
| `max_ir_drop_mv` | `parser.py:337,343,378` | Hardcoded `None` — never parsed from any report |
| `mean_ir_drop_mv` | `parser.py:337,343,378` | Hardcoded `None` — never parsed |
| `ir_violation_count` | `parser.py:337,343,378` | Hardcoded `0` — fabricated |
| `decap_coverage_pct` | `parser.py:414,419,433` | Hardcoded `None` — never parsed |
| `signoff_hold_whs_ns` | `parser.py:580,593,614` | Hardcoded `None` — not implemented |
| `signoff_hold_ths_ns` | `parser.py:581,594,614` | Hardcoded `None` — not implemented |
| `signoff_hold_satisfied` | `parser.py:583,596,616` | Hardcoded `False` — fabricated |
| `source_version` | `uploader.py:85`, `failure_atlas_uploader.py:48` | Hardcoded `"1.0"` — never updated |
| `timing_unit` | `parser.py:62,811` | Hardcoded `"ns"` — always same value, no signal |
| `status` (on escalation create) | `escalation.py:106` | Hardcoded `"open"` — always same on insert |
| `telemetry_events` (in FailureAtlasUploader) | `failure_atlas_uploader.py:50` | Hardcoded `[]` — always empty |
| `escalations` (in FailureAtlasUploader) | `failure_atlas_uploader.py:51` | Hardcoded `[]` — always empty |
| `failure_atlas_entries` (via Path A) | `export.py:220` | Exported under wrong key — always empty on server side |

Additionally, these fields have **HEURISTIC** classification and should be used with caution in GLI-SDI training:

| Field | File | Reason |
|-------|------|--------|
| `trust_score` | `repository.py:47` | Algorithmically computed, not measured |
| `trust_level` | `repository.py:48` | Computed from trust_score |
| `trust_reason` | `repository.py:49` | Computed string from trust factors |
| `confidence` (resolution patterns) | `repository.py:35` | Algorithmically computed from success/failure count |
| `qor_breakdown` | `orchestrator.py:540` | Weighted sub-scores, config-dependent |
| `qor_weights` | `orchestrator.py:541` | Config-defined weights, not measured |
| `ai_helpfulness` | `server.py:1710` | User feedback label, subjective |
| `ai_summary` | `escalation.py:111` | AI-generated text |
| `confidence` (details) | `server.py:2153` | AI-generated confidence score |

---

## Critical Findings

### Finding #1: `unknown_failures` → `failure_atlas_entries` Mapping Gap
**Severity: HIGH**
`TelemetryExporter` (`export.py:220`) places `community_unknown_dataset` records under key `unknown_failures` in the upload payload. The server's `UploadPayload` model (`cloud_ingestion/models.py:59`) expects them under `failure_atlas_entries`. Pydantic silently drops the extra key. **No unknown failure data from the run pipeline reaches the server through the primary upload path.**

### Finding #2: `resolution_patterns` Silently Dropped
**Severity: MEDIUM**
Exported at `export.py:222` under key `resolution_patterns` but not present in `UploadPayload` model. Silently dropped by pydantic.

### Finding #3: Privacy Excluded-Fields Collision
**Severity: MEDIUM**
The `EXCLUDED_FIELDS` set in `export.py:12-22` contains `"source"`. The check is substring-based (case-insensitive), so `"source_version"` would match and be blocked. Other potential collisions: `"license"` → any key containing "license", `"design_files"` → `"design_name"` (wait, does "design_name" contain "design_files"? No, but "design_files" contains "design" — so any key with "design" would match). Let me verify this more carefully.

Actually, looking at the code in `export.py`, the check is:
```python
if any(excluded in key.lower() for excluded in EXCLUDED_FIELDS):
```

So `"source_version"` does contain `"source"` and WOULD be blocked. And `"license"` would block keys containing "license". However, `"design_files"` would only block keys containing "design_files" (the full substring), not just "design". So only the `"source"` → `"source_version"` collision is real.

### Finding #4: `FailureAtlasUploader` Never Called from Main Pipeline
**Severity: HIGH**
The `FailureAtlasUploader` class (`failure_atlas_uploader.py`) is not called from the orchestrator or any post-run flow. It is only callable via direct API invocation. Combined with Finding #1, **no failure atlas data from real runs reaches the server.**

### Finding #5: `privacy_validated` Key May Be Incorrectly Redacted
**Severity: MEDIUM**
The field `privacy_validated` is produced by the exporter (`export.py:96-102`). If the sanitizer runs before the field is added, `privacy_validated` itself is fine. But the ordering matters — the `EXCLUDED_FIELDS` check runs on the final payload.
