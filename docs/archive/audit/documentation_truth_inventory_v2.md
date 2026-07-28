# Documentation Truth Inventory v2

**Date:** 2026-06-17
**Authority:** Source code only

---

## 1. CLI COMMANDS (from `gli_flow/cli/main.py`)

### Production Commands

| Command | Args | Category |
|---------|------|----------|
| `gli-flow run <design>` | `--verbose/-v`, `--threads/-j`, `--memory/-m`, `--orfs-root`, `--mock`, `--db-path` | Execution |
| `gli-flow history` | `--limit`, `--db-path` | Execution |
| `gli-flow status` | `--db-path` | Execution |
| `gli-flow batch <designs...>` | `--parallel/-j`, `--threads`, `--memory` | Execution |
| `gli-flow init <design_name>` | `--rtl-dir`, `--rtl` | Setup |
| `gli-flow quickstart` | (none) | Setup |
| `gli-flow install` | `--pdk`, `--pdk-root`, `--orfs-root`, `--skip-orfs`, `--force/-f`, `--dry-run/-n`, `--skip-system`, `--skip-pdk`, `--verbose/-v` | Infrastructure |
| `gli-flow doctor` | `--fix`, `--repair-magic`, `--db-path`, `--verbose/-v` | Setup |
| `gli-flow diagnose <run_id>` | `--db-path`, `--verbose/-v` | Analysis |
| `gli-flow report [design] [platform]` | `--platform/-p`, `--orfs-root` | Analysis |
| `gli-flow ci <design>` | `--junit`, `--markdown`, `--baseline`, `--qor-min`, `--wns-max`, `--verbose/-v`, `--db-path` | Analysis |
| `gli-flow config` | `--telemetry on/off` | Setup |
| `gli-flow db <subcommand>` | `status`, `migrate`, `repair`, `path`; each `--db-path` | Infrastructure |
| `gli-flow reset-runs` | `--db-path`, `--verbose/-v` | Infrastructure |
| `gli-flow support-bundle` | `--output/-o`, `--run-id`, `--db-path` | Infrastructure |
| `gli-flow setup` | `--pdk-root`, `--workspace`, `--telemetry on/off`, `--non-interactive` | Setup |
| `gli-flow show-telemetry <run_id>` | `--db-path` | Analysis |

### Experimental Commands

| Command | Args | Category |
|---------|------|----------|
| `gli-flow remote [design]` | `--host` (req), `--port`, `--user`, `--key`, `--gli-flow-path`, `--work-dir`, `--check` | Experimental |
| `gli-flow cloud <action>` | `upload/download/list`; `--dir`, `--provider`, `--bucket`, `--prefix` | Experimental |
| `gli-flow dashboard` | `--backend-only` | Experimental |
| `gli-flow upgrade-check` | (none) | Experimental |
| `gli-flow investigate <run_id>` | `--db-path`, `--verbose/-v` | Experimental |
| `gli-flow investigate-migrate [run_id]` | `--db-path`, `--verbose/-v` | Experimental |
| `gli-flow ai-assist` | `--failure-type`, `--signature`, `--severity`, `--confidence`, `--tool`, `--stage`, `--error-text`, `--log-snippet`, `--run-id`, `--db-path`, `--feedback`, `--helpful`, `--not-helpful`, `--resolved`, `--did-not-resolve` | Experimental |
| `gli-flow escalate` | `--failure-type`, `--signature`, `--severity`, `--confidence`, `--tool`, `--stage`, `--error-text`, `--run-id`, `--db-path`, `--consent`, `--submit`, `--notes`, `--feedback` | Experimental |
| `gli-flow telemetry <subcommand>` | status, enable, disable, mode, preview, export, replay, health, snapshot, audit-log, upload-internal | Experimental |
| `gli-flow warehouse <subcommand>` | status, coverage, quality, correlations, snapshot | Experimental |
| `gli-flow predict <run_id>` | `--db-path` | Experimental (NOT wired in dispatch) |

---

## 2. API ENDPOINTS (from `backend/server.py`)

### Runs (19 endpoints)
`GET /runs`, `GET /runs/count`, `GET /live_runs`, `GET /trends`, `GET /runs/{run_id}`, `GET /runs/{run_id}/drc`, `GET /runs/{run_id}/image/{image_name:path}`, `GET /runs/{run_id}/report/{report_type:path}`, `GET /runs/{run_id}/artifacts`, `GET /runs/{run_id}/artifact`, `GET /runs/{run_id}/artifact/preview`, `GET /releases`, `GET /health`, `PATCH /runs/{run_id}/important`, `GET /runs/{run_id}/diff/{previous_run_id}`, `GET /runs/{run_id}/compare/{other_run_id}`, `GET /runs/{run_id}/trust-score`, `GET /runs/{run_id}/investigation`, `POST /runs/{run_id}/investigation`

### Failures (7 endpoints)
`GET /failures`, `GET /runs/{run_id}/failures`, `GET /failures/{failure_id}`, `POST /failures/{failure_id}/resolution`, `GET /failures/{failure_id}/run`, `GET /failure-atlas`, `GET /failures/correlation/{failure_type}`

### Analytics (10 endpoints)
`GET /analytics/summary`, `GET /analytics/common-failures`, `GET /analytics/fix-effectiveness`, `GET /analytics/qor-improvements`, `GET /analytics/failure-trends`, `GET /analytics/resolution-confidence`, `GET /analytics/mttr`, `GET /analytics/coverage`, `POST /analytics/event`, `GET /analytics/product`

### Regressions (1 endpoint)
`GET /regressions`

### Similar Failures (1 endpoint)
`GET /similar-failures/{failure_type}`

### Knowledge Base (4 endpoints)
`GET /knowledge/failures`, `GET /knowledge/failures/{identifier}`, `GET /knowledge/search`, `GET /knowledge/qor`

### Reliability (3 endpoints)
`GET /reliability/summary`, `GET /reliability/health`, `GET /reliability/trends`

### Provenance (3 endpoints)
`GET /provenance/summary`, `GET /provenance/manifests`, `GET /provenance/graph`

### Telemetry (8 endpoints)
`GET /telemetry/events`, `POST /telemetry/event`, `GET /telemetry/export`, `GET /telemetry/health`, `GET /telemetry/audit-log`, `POST /telemetry/replay`, `POST /telemetry/snapshot`, `GET /telemetry/privacy-validate`

### AI Investigation (9 endpoints)
`GET /ai/health`, `GET /ai/trigger`, `POST /ai/investigate`, `GET /ai/investigate/failure`, `POST /ai/feedback`, `GET /ai/feedback/{investigation_id}`, `GET /ai/feedback-summary`, `POST /ai/resolution`, `GET /ai/resolutions`

### Resolution Intelligence (11 endpoints)
`GET /resolutions/patterns`, `GET /resolutions/patterns/{fingerprint}/timeline`, `POST /resolutions/capture`, `POST /resolutions/feedback`, `GET /resolutions/summary`, `GET /resolutions/trust-summary`, `GET /resolutions/candidates`, `POST /resolutions/promote`, `GET /resolutions/top-resolved`, `GET /resolutions/top-unresolved`, `GET /resolutions/metrics`

### Community Intelligence (8 endpoints)
`POST /community/escalate`, `GET /community/escalations`, `GET /community/escalation/{escalation_id}`, `POST /community/escalation/{escalation_id}/response`, `GET /community/stats`, `GET /community/unknown-dataset`, `GET /community/dataset`, `GET /community/knowledge-gaps`

### Feedback Center (5 endpoints)
`GET /feedback`, `POST /feedback`, `PATCH /feedback/{feedback_id}`, `GET /feedback/stats`, `POST /feedback/{feedback_id}/prioritize`

### Support Bundle (1 endpoint)
`POST /support-bundle/generate`

### User Journey (3 endpoints)
`POST /journey/event`, `GET /journey`, `GET /journey/report`

### Atlas Metrics (2 endpoints)
`GET /atlas/trust-summary`, `GET /atlas/metrics`

### Beta (2 endpoints)
`GET /beta/dashboard`, `GET /beta/report`

### Generic (1 endpoint)
`POST /record-event`

**Total: 79 endpoints** (plus 1 static SPA mount at `/`)

---

## 3. DASHBOARD PAGES (from `dashboard/src/App.jsx`)

| Nav Name | Component | Route Trigger |
|----------|-----------|---------------|
| Dashboard | (inline in App.jsx) | `activeNav === "Dashboard"` |
| Run Design | `RunDesignPage` | `activeNav === "Run Design"` |
| Run Matrix | `RunMatrixPage` | `activeNav === "Run Matrix"` |
| Run Monitor | `RunMonitorPage` | `activeNav === "Run Monitor"` |
| Important Runs | `RunsPage(importantOnly=true)` | `activeNav === "Important Runs"` |
| Artifacts | `ArtifactsPage` | `activeNav === "Artifacts"` |
| QoR Analytics | `QoRAnalyticsPage` | `activeNav === "QoR Analytics"` |
| Regression Detector | `RegressionDetectorPage` | `activeNav === "Regression Detector"` |
| Trends & Reports | `TrendsReportsPage` | `activeNav === "Trends & Reports"` |
| Failure Atlas | `FailureAtlasPage` | `activeNav === "Failure Atlas"` |
| Engineering Dashboard | `EngineeringDashboardPage` | `activeNav === "Engineering Dashboard"` |
| Provenance | `ProvenancePage` | `activeNav === "Provenance"` |
| Release Validation | `ReleaseValidationPage` | `activeNav === "Release Validation"` |
| Policy Suite | `PolicySuitePage` | `activeNav === "Policy Suite"` |
| Beta Dashboard | `BetaDashboardPage` | `activeNav === "Beta Dashboard"` |
| Feedback Center | `FeedbackCenterPage` | `activeNav === "Feedback Center"` |
| Product Analytics | `ProductAnalyticsPage` | `activeNav === "Product Analytics"` |
| User Journey | `UserJourneyPage` | `activeNav === "User Journey"` |
| Infrastructure | `InfrastructurePage` | `activeNav === "Infrastructure"` |
| Telemetry | `TelemetryPage` | `activeNav === "Telemetry"` |
| Telemetry Health | `TelemetryHealthPage` | `activeNav === "Telemetry Health"` |
| Telemetry Replay | `TelemetryReplayPage` | `activeNav === "Telemetry Replay"` |
| Settings | `SettingsPage` | `activeNav === "Settings"` |
| Help | `HelpPage` | `activeNav === "Help"` |

Run detail view: `RunDetail.jsx` (10 tabs: Summary, Timing, Area/Power, DRC/LVS, Layout Images, Artifacts, Failure Atlas, Reproducibility, AI Investigation, Compare)

---

## 4. DATABASE TABLES

| Table | DB File | Columns | Source |
|-------|---------|---------|--------|
| `schema_version` | gli_flow.db | 4 | Migrations |
| `runs` | gli_flow.db | 41 | Migrations v1-8 |
| `failure_atlas_entries` | gli_flow.db | 40 | Migrations v1-35 |
| `ai_investigation_feedback` | gli_flow.db | 8 | Migration v26 |
| `ai_resolution_capture` | gli_flow.db | 12 | Migration v27 |
| `community_escalations` | gli_flow.db | 17 | Migration v28 |
| `community_telemetry` | gli_flow.db | 8 | Migration v29 |
| `community_unknown_dataset` | gli_flow.db | 10 | Migration v30 |
| `resolution_patterns` | gli_flow.db | 13+9 | Migrations v31-34 |
| `resolution_feedback` | gli_flow.db | 5 | Migration v32 |
| `execution_intelligence` | gli_flow.db | 12 | Migration v34 |
| `feedback_records` | gli_flow.db | 15 | Beta Migration v1 |
| `user_journey_events` | gli_flow.db | 7 | Beta Migration v2 |
| `resolution_tracking` | gli_flow.db | 10 | Beta Migration v3 |
| `design_profiles` | gli_flow.db | 14 | Ad-hoc |
| `design_features` | gli_flow.db | 9 | Ad-hoc |
| `telemetry_execution_records` | gli_flow.db | 8 | Ad-hoc |
| `telemetry_recommendation_records` | gli_flow.db | 10 | Ad-hoc |
| `telemetry_audit_log` | gli_flow.db | 7 | Ad-hoc |
| `telemetry_events` | cloud_ingestion.db | 12 | Ad-hoc |
| `failure_atlas_events` | cloud_ingestion.db | 14 | Ad-hoc |
| `upload_audit` | cloud_ingestion.db | 11 | Ad-hoc |
| `consent_records` | cloud_ingestion.db | 5 | Ad-hoc |
| `upload_queue` | upload_queue.db | 9 | Ad-hoc |

---

## 5. TELEMETRY CONSENT WORKFLOW (from `gli_flow/telemetry/`)

- **Wizard**: `run_telemetry_wizard()` in `wizard.py` — interactive yes/no prompt
- **Non-interactive**: defaults to `LOCAL` mode
- **Modes**: `FULL` (upload), `ATLAS` (failure atlas only), `LOCAL` (no upload), `DISABLED` (no collection)
- **Config**: `~/.gli-flow/config.yaml` → `telemetry: on/off` or mode string
- **CLI**: `gli-flow telemetry enable/disable/mode/status`
- **API**: `GET /telemetry/health`, `GET /telemetry/events`, `GET /telemetry/export`
- **Sanitization**: Removes RTL, netlists, GDS, DEF, LEF, source code from details
- **Queue**: SQLite-backed at `~/.gli-flow/upload_queue.db`, exponential backoff 30s×2^n, max 10 retries

---

## 6. SUPPORT BUNDLE (from `gli_flow/cli/main.py:1781`)

Collects: config, version info, tool versions, telemetry health, recent runs (20), failure fingerprints (20), audit summaries, doctor output, logs, run artifacts → ZIP

---

## 7. CLOUD INGESTION (from `cloud_ingestion/`)

- Standalone FastAPI server on port 8100
- Tables: `telemetry_events`, `failure_atlas_events`, `upload_audit`, `consent_records`
- Config: `configs/cloud_ingestion.yaml`

---

## 8. INSTALLATION (from `gli-flow install` and `scripts/install.sh`)

- CLI: `gli-flow install` with flags for PDK, ORFS, dry-run, skip options
- Script: `scripts/install.sh` (bash fallback)
- Default PDK: `sky130`
- Default PDK root: `~/.gli-flow/pdk`
- Default ORFS root: `~/.gli-flow/orfs`

---

## 9. DOCTOR WORKFLOW (from `gli_flow/cli/main.py:969`)

Sections: SYSTEM, TOOLS, DATABASE, PDK, DOCKER, ORFS, NETWORK, PERMISSIONS
Flags: `--fix`, `--repair-magic`, `--db-path`, `--verbose/-v`

---

## 10. DESIGN EXAMPLES

- `examples/counter/` — RTL-to-GDS with `gli_manifest.yaml`
- `examples/gcd/` — Primary onboarding design
- `examples/uart/` — UART with `run_uart.py`
- `examples/picorv32/` — RISC-V CPU
- `examples/systolic_array/` — Systolic array (from merged `systolic-parsed/`)
- `examples/fir/`, `examples/gpio/`, `examples/mini_mac/`, `examples/mini_mac_soc/`, `examples/tiny_or/`
