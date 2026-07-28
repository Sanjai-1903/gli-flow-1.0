# Telemetry Pipeline Audit

> Trace of the complete telemetry path: Execution through Database.
> Generated: 2026-06-15

---

## 1. EXECUTION STAGE

### Inputs
- Run directory (contains: `reports/`, `logs/`, flow scripts, config files)
- Environment: tool paths, PDK, design metadata
- Run manifest: design_name, top_module, clock_period, utilization_target

### Processing
The orchestrator (`gli_flow/core/orchestrator.py`) drives a flow stage (synth, floorplan, place, cts, route, etc.). At each stage it:
1. Invokes EDA tools
2. Captures tool output (stdout/stderr)
3. Parses tool reports into structured metrics
4. Detects failures (DRC violations, LVS mismatches, timing violations, tool crashes)

### Outputs
| Output | Format | Location |
|--------|--------|----------|
| Tool reports | `.rpt`, `.csv`, `.xml`, `.json` | `reports/` |
| Stage metrics | `.json` | `telemetry/{stage}.json` |
| Run metrics | `.json` | `telemetry/metrics.json` |
| Error logs | `.log` | `logs/` |
| DRC agreement | `.json` | `telemetry/drc_agreement.json` |
| AI explanation | `.json` | `ai_explanation.json` |
| Environment events | `.json` | `telemetry/environment_events.json` |

### Privacy Implications
- **Reports directory** may contain tool-specific output that includes design netlists, DEF/LEF snippets, or full timing paths
- **Logs** may include command lines with design file paths, PDK cell names
- **Metrics JSON** is SAFE — contains only numeric aggregations (WNS, TNS, utilization, cell_count, runtime_sec, power)
- **DRC agreement JSON** is SAFE — contains violation type counts and per-tool comparisons
- **AI explanation** is SAFE — deterministic structured analysis, no raw IP

---

## 2. TELEMETRY COLLECTOR

### Implementation
Three parallel implementations (should be consolidated):

| File | Role | Extra Methods |
|------|------|---------------|
| `gli_flow/runtime/telemetry_manager.py` | Orchestrator runtime | `record_environment_event()`, `export_environment_events()` |
| `gli_flow/telemetry/manager.py` | Duplicate | None |
| `telemetry/telemetry_manager.py` | Server usage | None |

### Inputs
- Stage results (timing, utilization, runtime)
- Flow environment state
- Error/success outcomes

### Processing
- `export_metrics()` writes `telemetry/metrics.json` with: WNS, TNS, utilization, cell_count, runtime_sec, QoR score/breakdown/weights, power metrics (die_area, total_power_mw, internal_power_mw, switching_power_mw, leakage_power_mw, DRC runtime, LVS runtime)
- `export_stage_data()` writes per-stage JSON to `telemetry/{stage}.json`
- `record_environment_event()` appends to `telemetry/environment_events.json`

### Outputs
| File | Contents |
|------|----------|
| `telemetry/metrics.json` | All numeric metrics from run |
| `telemetry/{stage}.json` | Per-stage breakdown |
| `telemetry/environment_events.json` | Tool shadowing, broken wrappers, repair outcomes |

### Privacy Implications
- **All numeric** — no design IP exposure
- Environment events may include tool names and version strings — SAFE
- No source code, no RTL, no netlists

---

## 3. TELEMETRY PARSER

### Implementation
Two parallel implementations:

| File | Path |
|------|------|
| `gli_flow/telemetry/parser.py` | gli_flow internal |
| `telemetry/parser.py` | Top-level, used by server |
| `telemetry/collect_metrics.py` | Standalone `parse_reports()` |

### Inputs
- `reports/metrics.csv` — WNS, TNS
- `reports/timing.rpt` — Timing metrics
- `reports/utilization.rpt` — Utilization, cell count
- `reports/runtime.rpt` — Runtime in seconds
- `reports/metrics.rpt` — Additional metrics

### Processing
Parses text reports using regex/string extraction. For each file, extracts numeric values.

### Outputs
```python
{
  "wns": float,           # Worst negative slack (ns)
  "tns": float,           # Total negative slack (ns)
  "utilization": float,   # Cell utilization (%)
  "cell_count": int,      # Number of cells
  "runtime_sec": float,   # Wall-clock runtime
}
```

### Privacy Implications
- **SAFE** — only aggregate numeric values extracted
- Raw report files contain synthesis results and potentially timing paths with register names — but these are never uploaded, only parsed locally

---

## 4. TELEMETRY QUEUE

The current system does **NOT** implement a persistent telemetry queue.

### Current Behavior
- Metrics are written directly to the local filesystem
- Server reads from local filesystem on request
- No buffering, no batching, no retry queue

### Missing (Should Exist for Production)
- In-memory or persistent queue for batching uploads
- Retry mechanism on failure
- Back-pressure handling
- Queue persistence across restarts

### Privacy Implications
- Without a queue, telemetry data is written to disk as fast as it's produced — no privacy concern here since data stays local
- A queue would need the same sanitization as the upload path

---

## 5. UPLOAD API

### Community Intelligence Upload Path

#### Endpoint
`POST /community/escalate` (server.py line 2147)

#### Input (from dashboard)
```json
{
  "failure_type": "DRC_VIOLATION",
  "tool": "openroad",
  "stage": "ROUTING",
  "run_id": "run_abc123",
  "error_text": "...",
  "notes": "...",
  "consent": true
}
```

#### Processing
1. `FailurePackageBuilder.build()` constructs a sanitized FailurePackage
2. `EscalationManager.create_escalation()` writes to `community_escalations` table
3. `EscalationManager.submit_escalation()` calls `EmailWorkflow.submit()`:
   - Endpoint: `https://api.bharatcode.com/v1/green-lantern/submit`
   - Auth: `Authorization: Bearer {BHARATCODE_API_KEY}`
4. On success: records `bharatcode_submission_id`, status → `sent`

#### Output (over the wire)
```json
{
  "package_version": "1.0",
  "consent_record": {
    "consent_given": true,
    "consent_timestamp": "2026-06-15T...",
    "user_acknowledged_no_sensitive_data": true
  },
  "failure": {
    "tool": "openroad",
    "stage": "ROUTING",
    "failure_type": "DRC_VIOLATION",
    "error_text": "Error: ...",
    "log_excerpt": "(last 100 lines)",
    "metrics": {"wns": -0.05, "tns": -12.3},
    "design_metadata": {
      "design_name": "top",
      "top_module": "top",
      "pdk": "sky130A",
      "pdk_variant": "",
      "clock_period_ns": 10.0,
      "utilization_target": 70,
      "threads": 4
    },
    "run_metadata": {
      "run_id": "run_abc123",
      "timestamp": "...",
      "backend": "openroad",
      "gli_version": "1.0.0",
      "status": "FAILED",
      "current_stage": "ROUTING"
    },
    "ai_context": { ... }
  },
  "ai_suggestions": { ... },
  "user_notes": "..."
}
```

#### Primary Telemetry Upload Endpoint (non-escalation)
`POST /telemetry/event` (server.py line 1511)

#### Input
```json
{
  "event": "failure_atlas_miss",
  "details": {
    "signature": "drc:li.3",
    "error_class": "DRC",
    "confidence": 0.0,
    "severity": "HIGH",
    "stage": "ROUTING",
    "tool": "openroad",
    "failure_type": "DRC_VIOLATION",
    "frequency": 3,
    "ai_helpfulness": "unknown",
    "resolution_outcome": ""
  }
}
```

#### Processing
1. Validates event type against allowed set
2. Sanitizes `details` to an allowlist of keys
3. `EscalationTelemetry.record()` writes to `community_telemetry` table

### Privacy Implications
- **Escalation path**: Fully consent-gated, sanitized package, exclude-list enforced at transport layer
- **Telemetry event path**: Only metadata (signature, failure type, tool, stage) — SAFE
- Log excerpts in escalation contain the last 100 lines of log files which may include tool command lines with file paths — this is the **highest privacy risk** in the upload path

---

## 6. DATABASE (Local SQLite)

### Telemetry-Related Tables

#### `community_telemetry`
| Column | Type | Privacy |
|--------|------|---------|
| id | INTEGER PK | Safe |
| event | TEXT | Safe — event type string |
| escalation_id | TEXT | Safe — internal ID |
| failure_type | TEXT | Safe |
| tool | TEXT | Safe |
| atlas_id | TEXT | Safe |
| details | TEXT (JSON) | Sanitized to allowlist keys |
| created_at | TEXT | Safe — timestamp |

#### `community_unknown_dataset`
| Column | Type | Privacy |
|--------|------|---------|
| id | INTEGER PK | Safe |
| tool | TEXT | Safe |
| failure_type | TEXT | Safe |
| signature | TEXT | Safe — hashed/derived |
| frequency | INTEGER | Safe |
| ai_helpfulness | TEXT | Safe |
| resolution_outcome | TEXT | Safe |
| consent_given | INTEGER | Safe |
| escalation_id | TEXT | Safe |
| last_seen | TEXT | Safe |

#### `community_escalations`
| Column | Type | Privacy |
|--------|------|---------|
| id | TEXT PK | Safe |
| run_id | TEXT | Internal reference |
| failure_type | TEXT | Safe |
| tool | TEXT | Safe |
| stage | TEXT | Safe |
| status | TEXT | Safe |
| consent_given | INTEGER | Safe |
| consent_timestamp | TEXT | Safe |
| bharatcode_submission_id | TEXT | Safe |
| bharatcode_status | TEXT | Safe |
| ai_summary | TEXT | Safe |
| user_notes | TEXT | User-provided, could contain references |
| engineer_response | TEXT (JSON) | Safe |
| atlas_id_created | TEXT | Safe |
| created_at | TEXT | Safe |
| sent_at | TEXT | Safe |
| resolved_at | TEXT | Safe |

#### `failure_atlas_entries`
| Column | Type | Privacy |
|--------|------|---------|
| id | TEXT PK | Safe |
| run_id | TEXT | Internal reference |
| failure_id | TEXT | Safe |
| failure_type | TEXT | Safe |
| severity | TEXT | Safe |
| title | TEXT | Safe — failure description |
| description | TEXT | Safe |
| recommended_fix | TEXT | Safe |
| confidence | REAL | Safe |
| signature | TEXT | Safe |
| domain | TEXT | Safe |
| category | TEXT | Safe |
| evidence | TEXT (JSON) | **Risk** — may contain log snippets, error output |
| created_at | TEXT | Safe |

#### `resolution_patterns`
| Column | Type | Privacy |
|--------|------|---------|
| id | TEXT PK | Safe |
| failure_fingerprint | TEXT | Safe |
| failure_type | TEXT | Safe |
| root_cause | TEXT | Safe |
| resolution | TEXT | Safe |
| resolution_type | TEXT | Safe |
| success_count | INTEGER | Safe |
| failure_count | INTEGER | Safe |
| confidence | REAL | Safe |
| trust_score | REAL | Safe |
| trust_level | TEXT | Safe |
| trust_reason | TEXT | Safe |
| unique_runs | INTEGER | Safe |
| unique_designs | INTEGER | Safe |

### Privacy Implication Summary
| Table | Risk Level | Concern |
|-------|-----------|---------|
| community_telemetry | LOW | Metadata only, keys allowlisted |
| community_unknown_dataset | LOW | Metadata only |
| community_escalations | LOW | Consent-gated, sanitized |
| failure_atlas_entries | **MEDIUM** | `evidence` field may contain log output with design-specific info |
| resolution_patterns | LOW | Aggregate patterns, no raw data |

---

## 7. ANALYTICS PIPELINE

### Flow
```
Database Tables
  ↓
Server API (server.py)
  ↓
Dashboard (React)
```

### Analytics Endpoints
| Endpoint | Source Data | Privacy |
|----------|------------|---------|
| `/analytics/summary` | failure_atlas_entries | Safe — count aggregations |
| `/analytics/common-failures` | failure_atlas_entries | Safe |
| `/analytics/fix-effectiveness` | failure_atlas_entries | Safe |
| `/analytics/qor-improvements` | runs | Safe — numeric only |
| `/analytics/failure-trends` | failure_atlas_entries | Safe |
| `/analytics/resolution-confidence` | failure_atlas_entries | Safe |
| `/analytics/coverage` | failure_atlas_entries | Safe |
| `/resolutions/summary` | resolution_patterns | Safe |
| `/resolutions/trust-summary` | resolution_patterns | Safe |

### Privacy Implications
- **All analytics endpoints aggregate data** — no raw records exposed
- Dashboard renders only aggregated summaries
- No customer IP reaches the analytics pipeline

---

## 8. FAILURE ATLAS PIPELINE

### Entry Creation Flow
```
Failure Detected
  ↓
Signature Engine generates failure_hash + signature
  ↓
should_use_ai() (always True for unknown failures)
  ↓
Trigger-based entry: signature matches → existing entry updated
  ↓
No match → UnknownFailureDataset.record_unknown_failure()
  ↓
Candidate Generation:
  Resolution patterns with confidence >= threshold
  ↓
Engineer Review (manual promotion via /resolutions/promote)
  ↓
FailureAtlasRepository.insert_entry()
```

### Privacy Implications
- **Signatures** are derived hashes of failure characteristics, not raw data
- **Evidence field** is JSON — content depends on what the caller provides
- Deterministic analysis (ExplanationEngine, RootCauseEngine) produces structured data, no raw IP

---

## 9. RESOLUTION INTELLIGENCE PIPELINE

### Pattern Creation Flow
```
Run Recovery (FAILED → PASS)
  ↓
ResolutionCapture.capture_from_run_recovery()
  ↓
ResolutionRepository upsert
  ↓
TrustScorer evaluates 7 factors →
  trust_score, trust_level, trust_reason
  ↓
Engineer Feedback (confirmed/rejected)
  ↓
ResolutionRepository increments + recalculates trust
```

### Privacy Implications
- **Only aggregate pattern data** — fingerprint (string), success/failure counts, scores
- No raw logs, no tool output, no design data
- Design names tracked as `unique_designs` count only — actual names stored as JSON array in `tracked_design_names` for internal dedup only
- **SAFE** for upload

---

## 10. COMPLETE DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│ EXECUTION                                                        │
│ (orchestrator.py)                                                │
│  ├─ EDA tool output → reports/*.rpt, *.csv, *.xml               │
│  ├─ Failure detection → failure_atlas_entries                   │
│  ├─ Metrics export → telemetry/metrics.json                     │
│  └─ AI explanation → ai_explanation.json                        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ TELEMETRY PARSER                                                 │
│ (gli_flow/telemetry/parser.py, telemetry/parser.py)             │
│  ├─ Reports/ → WNS, TNS, utilization, cell_count, runtime       │
│  └─ → Database (runs table)                                     │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ TELEMETRY MANAGER                                                │
│ (gli_flow/runtime/telemetry_manager.py)                         │
│  ├─ export_metrics() → telemetry/metrics.json                   │
│  ├─ export_stage_data() → telemetry/{stage}.json               │
│  └─ record_environment_event() → telemetry/environment_events   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ LOCAL DATABASE (SQLite)                                          │
│  ├─ runs            ── run-level metrics + QoR                  │
│  ├─ failure_atlas_entries ── failure signatures + evidence      │
│  ├─ resolution_patterns ── fix patterns + trust scores          │
│  ├─ community_telemetry ── telemetry events (metadata only)     │
│  ├─ community_unknown_dataset ── unknown failure patterns       │
│  └─ community_escalations ── consent-gated escalations          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ UPLOAD PATH (CONSENT-GATED ONLY)                                 │
│                                                                  │
│  ┌─ Escalation:                                                  │
│  │  FailurePackageBuilder → validate_sanitized() → EmailWorkflow │
│  │  → api.bharatcode.com/v1/green-lantern/submit                │
│  │  Gate: consent checkbox in UI + API + transport              │
│  │                                                               │
│  └─ Telemetry Event:                                             │
│     EscalationTelemetry.record() → community_telemetry table    │
│     Keys allowlisted; no raw data                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. KEY FINDINGS

### Privacy Strengths
1. **Multiple consent layers** (7 identified) for escalations — no single point of failure
2. **Excluded fields/extensions list** enforced at package build time
3. **Allowlist-based design metadata filtering** — only 7 whitelisted keys
4. **Allowlist-based run metadata filtering** — only 6 whitelisted keys
5. **All telemetry event details keys are allowlisted** — no generic pass-through
6. **AI context builder explicitly blocks** `.v`, `.sv`, `.gds`, `.def`, `.lef`, `.lib`, `.db` extensions
7. **TrustScorer uses only aggregate counts** — no raw design data in trust scoring

### Privacy Risks
1. **Log excerpts in escalation packages** (last 100 lines) — may contain file paths, register names, cell names from tool output
2. **`failure_atlas_entries.evidence` field** — unvalidated JSON blob that may contain tool output with design-specific references
3. **`tracked_design_names` in resolution_patterns** — stores design names as JSON array; design names could be proprietary project names
4. **No telemetry queue** — all data written directly to disk with no retry/back-pressure mechanism

### Structural Issues
1. **Triplicate TelemetryManager** — `gli_flow/runtime/`, `gli_flow/telemetry/`, `telemetry/` all have copies
2. **Duplicate TelemetryParser** — `gli_flow/telemetry/` and `telemetry/`
3. **No standalone sanitizer module** — sanitization is embedded in `FailurePackageBuilder` only
4. **No telemetry preview capability** — users cannot see what would be uploaded (transparency mode)
5. **No rate limiting or deduplication** on telemetry ingestion
6. **No telemetry signing or integrity checking** on upload
