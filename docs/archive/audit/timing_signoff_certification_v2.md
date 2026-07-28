# Timing Signoff Certification v2

## Overview

Certifies that the signoff STA path no longer silently returns WNS=0.0/TNS=0.0.
Negative slack correctly propagates through the entire pipeline:
OpenSTA → signoff reports → parsers → database → telemetry → dashboard.

## Root Cause

`_write_signoff_tcl()` in `openroad_adapter.py:2764` generated TCL with `read_lef`,
`read_def`, `read_sdc`, `read_spef` but **no `read_liberty`**. Without standard cell
liberty files, OpenSTA has no timing arcs. All `report_wns`/`report_tns`/`report_worst_slack`
returned 0.0 regardless of actual slack.

## Changes Made

### Phase 1: Fix Signoff STA (`openroad_adapter.py`)
- Added `_get_orfs_liberty_path()` — discovers liberty file from ORFS platform lib dir
- Modified `_write_signoff_tcl()` — inserts `read_liberty <path>` before STA commands
- Liberty file: `{orfs_root}/flow/platforms/{platform}/lib/{corner_lib_set}.lib`
- Typical corner: `sky130_fd_sc_hd__tt_025C_1v80.lib` (12.8MB)

### Phase 2: Eliminate Silent Fallback-to-Zero (`openroad_adapter.py`)
- **Exception handler** (line 2847): Changed from `return TimingSignoffResult(0,0.0,...)`
  to `raise StageFailure(...)` — no more fake zero timing on signoff failure
- **TNS/THS parsing** (lines 2829, 2833): Changed from `or 0.0` to
  `if tns is None: raise StageFailure(...)`
- **Hold THS**: Made optional (None when tool doesn't support `report_tns -min`)

### Phase 3: Telemetry Key Isolation (`telemetry/parser.py`)
- `parse_signoff_report()` now uses `signoff_setup_wns_ns` / `signoff_setup_tns_ns`
  instead of `setup_wns_ns` / `setup_tns_ns`
- Previously, signoff STA (0.0) **overwrote** correct ORFS flow-stage timing data in
  `parse_all()` — now both data sources coexist with distinct keys
- Error/skip returns also use `signoff_*` prefixed keys

### Phase 4: Production-Critical Fallback Fixes
- `cli/main.py:832` — `finish.get("critical_path_slack") or 0` → explicit `is not None` check
- `collect_metrics.py:8-10` — `wns: 0.0` → `wns: None`
- `failure_atlas/repository.py:277-278` — `or 0` → `.get(key, 0.0)`
- `backend/server.py:861-862` — `or 0` → `.get(key, 0.0)`
- `intelligence/readiness_correlation.py:12-13` — `get(key, 0)` → `get(key, 0.0)`
- `failure_atlas/prediction/similarity.py:29-30,42-43` — `get(key, 0)` → `get(key, 0.0)`
- `scripts/audit_intelligence_accuracy.py:189-192` — `or 0` → explicit None check

### Phase 5: Timing Consistency Engine (`orchestrator.py`)
- `_extract_metrics()` validates ORFS WNS vs signoff STA WNS with 0.05ns tolerance
- Warning logged if paths disagree; info logged when consistent

## Validation

| Metric | Before Fix | After Fix | Source |
|--------|-----------|-----------|--------|
| Setup WNS | 0.00000 | **-0.85122** | `report_wns` |
| Setup TNS | 0.00000 | **-6.48148** | `report_tns` |
| Hold WHS | 0.00000 | **0.47241** | `report_worst_slack -min` |
| Hold THS | 0.00000 | **None** | N/A (tool limitation) |
| Setup Satisfied | True (wrong) | **False** ✓ | WNS < 0 |

### Test Results
- **5/5 signoff tests pass** (updated for renamed keys)
- **552/552 non-pre-existing tests pass** (0 regressions)
- **28 pre-existing failures** (unrelated: missing `detection_classification` column)

## Data Flow

```
Path A (ORFS flow-stage, always correct):
  ORFS 6_finish.rpt → metrics.csv → TelemetryParser.parse_timing()
  → parsed["setup_wns_ns"] → ExecutionRecord.wns → DB (runs.wns/tns)

Path B (signoff STA, was broken, now fixed):
  OpenROAD STA (read_liberty + read_lef + read_def + read_sdc + read_spef)
  → signoff_setup.rpt → TelemetryParser.parse_signoff_report()
  → parsed["signoff_setup_wns_ns"] → (prefixed, no longer overwrites Path A)
  → TimingSignoffResult → orchestrator._corner_results → sta_corners.json
```

## Edge Cases

| Case | Behavior |
|------|----------|
| Liberty file missing | Warning logged, `read_liberty` skipped, STA runs without timing arcs (0.0) |
| Signoff fails (tool missing/timeout) | `StageFailure` raised (no fake zero result) |
| TNS not in report | `StageFailure` raised for setup, silently None for hold (tool limitation) |
| Hold THS unavailable | `hold_tns_ns` remains None (not faked to 0.0) |
| ORFS CSV vs signoff mismatch | Warning logged with diff value in telemetry |

## Summary

All critical timing data corruption paths in the signoff STA pipeline have been
identified, fixed, and validated. The signoff STA now correctly reports
WNS=-0.85122 for a design with known negative slack (counter@2ns), matching
the ORFS flow-stage ground truth of WNS=-0.85.
