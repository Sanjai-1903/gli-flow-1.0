# INF-MAGIC-002: Cross-Tool DRC Validation Framework — Architecture Audit

**Citation:** `inf_magic_002`
**Date:** 2026-06-11
**Scope:** Full DRC pipeline from invocation through signoff, Failure Atlas, telemetry, and dashboard.

---

## 1. Pipeline Overview

```
drc_runner.py ──> orchestrator.py ──> signoff gate ──> Failure Atlas ──> telemetry ──> dashboard
     │                    │                 │                │                │              │
     │                    │           (release_gate_errors)  │                │              │
     ├─ run_magic_drc()   │                                 │                │              │
     ├─ run_klayout_drc() │                                 │                │              │
     └─ run_dual_drc()    │                                 │                │              │
                          └─ drc_combined.json              │                │              │
                                                             │                │              │
                                              (failure_atlas_entries)         │              │
                                                                 (drc.json telemetry)        │
                                                                                     (API endpoints)
```

## 2. Data Flow Touchpoints

### Touchpoint 1 — drc_runner.py: DRC Dual Execution
- **File:** `gli_flow/core/drc_runner.py`
- **Entry:** `run_dual_drc(gds_path, design_name, pdk, run_dir)` at line 133
- **Calls:** `run_magic_drc()` (line 41) and `run_klayout_drc()` (line 100)
- **Output:** Merged dict with keys `drc_clean`, `drc_status`, `total_violations`, `magic`, `klayout`, `note`
- **Persistence:** Written to `reports/drc_combined.json` at line 191

### Touchpoint 2 — orchestrator.py: DRC Stage Invocation
- **File:** `gli_flow/core/orchestrator.py`
- **Lines:** 868–905 (DRC stage block)
- **Calls:** `run_dual_drc()` from line 872
- **Extracts:** `magic_data` and `klayout_data` sub-dicts at lines 879–880
- **Sets signoff gates:** `signoff_gate.magic_drc_pass` (line 882) and `signoff_gate.klayout_drc_pass` (line 886)
- **Summary:** Written to `drc_lvs_summary.json` at lines 889–901

### Touchpoint 3 — orchestrator.py: Signoff Gate
- **File:** `gli_flow/core/orchestrator.py`
- **Entry:** `release_gate_errors()` at line 1156
- **Logic:** Checks `signoff_gate.tapeout_ready` at line 1162
- **Failure handling:** Records failures via `_add_failure_atlas_entry()` at line 1160
- **Current policy:** Both Magic AND KLayout must pass for signoff

### Touchpoint 4 — Failure Atlas Insertion
- **File:** `gli_flow/core/orchestrator.py`
- **Method:** `_add_failure_atlas_entry()` (line ~1160)
- **Called for:** Release gate failures with severity "CRITICAL"
- **Repository:** `failure_atlas/repository.py` — `insert_entry()` at line 90
- **Schema:** `failure_atlas/schema.py` — `FailureAtlasEntry` dataclass

### Touchpoint 5 — Failure Atlas DB Queries (Dashboard)
- **File:** `backend/server.py`
- **Endpoints:**
  - `/runs/{run_id}/failures` (line 395) — per-run failure list
  - `/failures` (line 409) — paginated failure search
  - `/failures/{failure_id}` (line 474) — single failure detail

### Touchpoint 6 — DRC Telemetry
- **File:** `backend/server.py`
- **Logic:** `run_dir / "telemetry" / "metrics.json"` loaded at line 301
- **Also:** `drc_combined.json` contents available at `/runs/{run_id}/report/reports/drc_combined.json`
- **No dedicated DRC telemetry endpoint currently**

### Touchpoint 7 — Dashboard DRC Display
- **Mount:** Static files from `dashboard/dist/` at line 1211
- **Fallback:** No DRC-specific frontend template exists in backend

## 3. Current Behavior — No Cross-Tool Validation

| Aspect | Current State |
|--------|--------------|
| Magic DRC | Runs, parses `magic_drc.rpt`, counts violations |
| KLayout DRC | Runs, parses `klayout_drc.xml`, counts violations |
| Combined result | `max(magic_count, klayout_count)` |
| Signoff | Both must pass (`violations == 0`) |
| Tool disagreement | **NOT detected** — no comparison logic exists |
| Failure Atlas entry | Created for signoff failure, but NOT per-tool disagreement |
| Dashboard | Raw counts displayed; no tool agreement status |

## 4. Gap Analysis

| Gap | Impact | Severity |
|-----|--------|----------|
| No cross-tool comparison | Tool false-positives go undetected | HIGH |
| No disagreement telemetry | No data to tune tool weights | MEDIUM |
| No Failure Atlas incident for tool disagreement | Knowledge base incomplete | MEDIUM |
| Dashboard shows no agreement status | Engineer must manually compare | LOW |
| No automated review workflow | False-positives block signoff | HIGH |

## 5. Remediation Strategy

### Phase 1 (This Document)
Architecture audit complete — identifies all 7 touchpoints.

### Phase 2 — Failure Atlas Incident
Create incident `inf_magic_002` with classification `tool_false_positive`, citation linking to GCD DRC audit.

### Phase 3 — CrossToolDRCAnalyzer
New class that compares Magic and KLayout results, returns `CONSISTENT_PASS`, `CONSISTENT_FAIL`, or `TOOL_DISAGREEMENT`.

### Phase 4 — Failure Atlas Enrichment
When disagreement detected, auto-create a Failure Atlas incident with `confidence=medium`.

### Phase 5 — Dashboard Enhancement
Add `tool_agreement` field to `/api/run/<id>/drc` endpoint and summary endpoint.

### Phase 6 — Policy Review Document
Document three policy options: Conservative (current), Review-Gated (recommended), Auto-Pass.

### Phase 7 — Telemetry
Record `cross_tool_drc_disagreement` event to `telemetry/drc_agreement.json`.

### Phase 8 — Validation
Unit tests for all analyzer paths; verify existing signoff flow unchanged.
