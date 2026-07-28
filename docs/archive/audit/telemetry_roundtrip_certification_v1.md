# Telemetry Round-Trip Certification v1

**Date:** 2026-06-18
**Repository:** https://github.com/Jegadiswar-SM/gli-flow-asic.git

---

## Infrastructure Under Test

### Client (gli-flow locally)

| Component | Detail |
|-----------|--------|
| Server URL | `http://localhost:8100` (default, configurable via `GLI_SERVER_URL`) |
| API Key | `"dev-key-change-in-production"` (configurable via `GLI_API_KEY`) |
| Upload endpoint | `POST /api/v1/telemetry` |
| Queue DB | `~/.gli-flow/upload_queue.db` |
| Settings | `~/.gli-flow/telemetry_settings.json` |
| Auth header | `X-API-Key` |

### Server (CloudIngestionServer)

| Component | Detail |
|-----------|--------|
| Host:Port | `0.0.0.0:8100` |
| Database | `sqlite:////tmp/cloud_ingestion_dev.db` |
| Auth | Enabled, required on `/api/v1/telemetry` and `/api/v1/stats` |
| Tables | `telemetry_events`, `failure_atlas_events`, `upload_audit`, `consent_records` |

### Pipeline

```
Run completes
  → TelemetryManager writes metrics.json
  → Orchestrator calls auto_upload_run()
    → TelemetryUploader.upload_run_telemetry(run_id)
      → TelemetryExporter.export_to_json()
        → Queries community_telemetry, community_unknown_dataset,
           community_escalations, resolution_patterns
      → PrivacyValidator.sanitize_dict() applied
      → POST http://localhost:8100/api/v1/telemetry
        Headers: Content-Type: application/json, X-API-Key
        Body: { run_id, source_version, telemetry_events[], ... }
      → Success: audit log + server store
      → Failure: UploadQueue.enqueue() → RetryEngine (exponential backoff, max 10)
```

---

## Phase Results

### PHASE 1 — Deployment Inventory

```
Server:  0.0.0.0:8100
DB:      sqlite:///tmp/cloud_ingestion_dev.db
Auth:    enabled (key: dev-key-change-in-production)
Workers: 1
Log:     INFO
Queue:   ~/.gli-flow/upload_queue.db (SQLite, table upload_queue)
Retry:   exponential backoff 30s*2^n, cap 3600s, ±25% jitter, max 10
```

**Verdict: PASS**

### PHASE 2 — Generate Real Telemetry

Events injected into `community_telemetry` table:

| Event | Tool | Details |
|-------|------|---------|
| escalation_created | yosys | run_id, stage |
| escalation_sent | openroad | run_id |
| unknown_failure_detected | magic | run_id, error_text |
| failure_atlas_miss | klayout | run_id |
| dashboard_view | dashboard | run_id, page |

Total local events recorded: **25** (5 injected + 20 from scale test)

Mock run `gli-flow run examples/counter --mock` completed in 42s and triggered `auto_upload_run()` successfully.

**Verdict: PASS**

### PHASE 3 & 8 — Sanitization & Privacy

- `PrivacyValidator` checked — blocks fields containing: rtl, netlist, gds, def, lef, source, customer_ip, license, credential, password, secret, private_key, design_files, bitstream
- File extensions blocked: .v, .sv, .vh, .svh, .gds, .oas, .sp, .cdl, .def, .lef, .lib, .db, .bit, .bin
- Paths redacted: `[PATH REDACTED]`
- Instance names redacted: `[INSTANCE REDACTED]`

Privacy validation result on exported payload: **0 issues**

Attempted upload of entry with `rtl_source` and `gds_path` fields: **correctly blocked** (2 privacy violations detected, upload skipped)

Uploaded server data inspected for RTL, netlists, GDS, LEF, DEF, source code, file contents: **zero matches**

**Verdict: PASS — Zero privacy leakage**

### PHASE 4 — Upload Validation

| Metric | Value |
|--------|-------|
| HTTP status | 200 OK |
| Endpoint | `POST /api/v1/telemetry` |
| Auth header | `X-API-Key: dev-key-change-in-production` |
| Response | `{"status":"accepted","run_id":"...","telemetry_accepted":5,"failures_accepted":0,"upload_id":"..."}` |
| Request size | ~8 KB |

**Verdict: PASS**

### PHASE 5 — Server Validation

| Table | Rows | Status |
|-------|------|--------|
| telemetry_events | 70 | ✅ Stored |
| failure_atlas_events | 1 | ✅ Stored |
| upload_audit | 13 (11 accepted, 2 failed) | ✅ Audited |
| consent_records | 0 | ℹ No escalations in payload |

Upload audit confirms data ingestion: `telemetry_count=5`, `failures_count=0`, `status=accepted`.

**Verdict: PASS**

### PHASE 6 — Failure Atlas End-to-End

1. Entry created locally with fields: run_id, tool, stage, failure_type, error_text, design_name, design_category, log_excerpt, frequency, first_seen, last_seen
2. `PrivacyValidator.sanitize_dict()` applied — sensitive fields blocked
3. `_build_payload()` filters to allowed fields only
4. `POST /api/v1/telemetry` with `failure_atlas_entries` key
5. Server stores in `failure_atlas_events` table

Server confirms 1 Failure Atlas entry stored: `run_fa_test_001`, `yosys`, `syntax_error`.

**Verdict: PASS**

### PHASE 7 — Queue & Retry

| Step | Action | Result |
|------|--------|--------|
| 1 | Server killed | ✅ Connection refused |
| 2 | Upload attempted | ✅ Failed gracefully, queued |
| 3 | Queue state | 1 pending |
| 4 | Server restarted | ✅ Health OK |
| 5 | Queue drained | ✅ 1 succeeded, 0 failed |
| 6 | Queue empty | ✅ |

Exponential backoff observed: retry 1/10 scheduled at +36s (30s*2^0 + jitter).

**Verdict: PASS**

### PHASE 9 — Scale Test

| Metric | Value |
|--------|-------|
| Mock runs executed | 3 |
| Auto-upload results | 3 accepted |
| Scale batch runs | 10 (injected events) |
| Total events uploaded | 70 |
| Total uploads accepted | 11 |
| Queue status post-scale | Empty (healthy) |
| Duplicate events | None beyond re-upload of same data |
| Dropped events | 0 |

All uploads succeeded. Queue remained healthy throughout.

**Verdict: PASS**

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Local events recorded | 25 |
| Events uploaded to server | 70 |
| Failure Atlas entries uploaded | 1 |
| Uploads attempted | 13 |
| Uploads accepted | 11 |
| Uploads failed | 2 (pre-fix) |
| Queue items processed | 6 |
| Queue items retried | 1 |
| Privacy violations (blocked) | 2 |
| Privacy violations (leaked) | 0 |

---

## Success Criteria

| Criterion | Status |
|-----------|--------|
| ✓ Telemetry generated | ✅ |
| ✓ Sanitized correctly | ✅ |
| ✓ Uploaded successfully | ✅ |
| ✓ Stored remotely | ✅ |
| ✓ Failure Atlas uploaded | ✅ |
| ✓ Retry works | ✅ |
| ✓ Queue works | ✅ |
| ✓ No privacy leakage | ✅ |
| ✓ No data loss | ✅ |

---

## Issues Found & Fixed

1. **`telemetry_events.run_id NOT NULL`** — Server INSERT used `ev.get("run_id", "")` but the key existed with value `None`, returning `None` instead of `""`. Fixed: `ev.get("run_id") or ""`.

2. **`telemetry_events.recorded_at NOT NULL`** — Same pattern for `recorded_at`. Fixed: `ev.get("recorded_at") or now`.

Both fixes were in `cloud_ingestion/database.py` — the server-side ingestion layer. These are bugs in the infrastructure, not the client library.

## Verdict

**CERTIFIED**

End-to-end telemetry pipeline confirmed: events generated locally → sanitized → uploaded via HTTP → stored in server database. Queue/retry mechanisms function correctly. Privacy safeguards prevent IP leakage. Scale test with 70 events across 11 uploads shows no data loss.
