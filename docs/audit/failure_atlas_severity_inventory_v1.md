# Failure Atlas Severity Inventory v1

**Date:** 2026-06-20
**Goal:** Document every place Failure Atlas entries are created, their trigger conditions, and current severity

---

## Entry Creation Points

### 1. `failure_atlas/detector.py` — `detect_failures()` (12 rules)

The primary rule-based detection engine. Creates `FailureAtlasEntry` dataclass instances; the orchestrator serializes and inserts them.

| # | Lines | Trigger | Current Severity | Classification |
|---|-------|---------|-----------------|---------------|
| 1a | 39-46 | `setup_wns_ns < 0` | `TAPEOUT_BLOCKING` if wns < -0.5, else `PERFORMANCE_DEGRADATION` | Signoff Blocker / Warning |
| 1b | 48-55 | `hold_whs_ns < 0` | `TAPEOUT_BLOCKING` | Tapeout Blocker |
| 1c | 57-65 | `overflow_h > 0.05 or overflow_v > 0.05` | `TAPEOUT_BLOCKING` if max > 0.1, else `FUNCTIONAL_RISK` | Signoff Blocker / Warning |
| 1d | 67-92 | `drc_total_violations > 0` | `TAPEOUT_BLOCKING` | Tapeout Blocker |
| 1e | 94-113 | `lvs_status == "FAIL"` | `TAPEOUT_BLOCKING` | Tapeout Blocker |
| 1f | 115-126 | `lvs_status == "ERROR"` | `TAPEOUT_BLOCKING` | Tapeout Blocker |
| 1g | 128-137 | `lvs_status == "NOT_RUN"` | `TAPEOUT_BLOCKING` | Tapeout Blocker |
| 1h | 139-145 | SRAM macro DRC spacing violations | `TAPEOUT_BLOCKING` | Tapeout Blocker |
| 1i | 147-154 | `power_ir_drop_pct > 10.0` | `TAPEOUT_BLOCKING` if > 15, else `FUNCTIONAL_RISK` | Signoff Blocker / Warning |
| 1j | 156-163 | `clock_skew_ns > 0.5` | `FUNCTIONAL_RISK` if > 0.8, else `PERFORMANCE_DEGRADATION` | Warning |
| 1k | 165-172 | `max_transition_ns > 0.8` | `TAPEOUT_BLOCKING` if > 1.5, else `PERFORMANCE_DEGRADATION` | Signoff Blocker / Warning |
| 1l | 174-181 | `max_capacitance_pf > 0.3` | `TAPEOUT_BLOCKING` if > 0.5, else `PERFORMANCE_DEGRADATION` | Signoff Blocker / Warning |
| 1m | 183-195 | Power analysis false pass | `FUNCTIONAL_RISK` | Warning |

### 2. `gli_flow/core/orchestrator.py` — Path A (lines 406-447)

Metric-based failure detection. Calls `detect_failures()` then serializes results and inserts via `repo.insert_entry()`.
- **Classification:** `"VERIFIED"` (inherited from detection rules)

### 3. `gli_flow/core/orchestrator.py` — Path B (lines 449-478)

Log signature-based detection. Scans log files against signature patterns.
- **Severity:** From signature JSON (`sig.get("severity", "MEDIUM")`)
- **Classification:** `"VERIFIED"`, `"HEURISTIC"`, or `"UNVERIFIED"` depending on detection method

### 4. `gli_flow/core/orchestrator.py` — Path C (lines 851-868)

Pipeline failure recording when a stage crashes or exits non-zero.
- **Severity:** `"HIGH"` (hardcoded)
- **Classification:** `"VERIFIED"`
- **Type:** Signoff Blocker

### 5. `gli_flow/core/orchestrator.py` — Path D (lines 875-900)

Root cause recording from AI-based root cause analysis.
- **Severity:** Dynamic from `rc.severity`
- **Classification:** `"VERIFIED"`

### 6. `gli_flow/core/orchestrator.py` — Path E (lines 920-950)

Signoff failure recording when signoff checks fail.
- **Severity:** `"TAPEOUT_BLOCKING"` (hardcoded)
- **Classification:** `"VERIFIED"`

### 7. `gli_flow/core/cross_tool_drc.py` — `_create_disagreement_incident()` (lines 135-194)

Records tool disagreements (Magic vs KLayout DRC mismatch).
- **Severity:** `"MEDIUM"` (hardcoded)
- **Classification:** `"VERIFIED"`
- **Type:** Engineering observation

### 8. `gli_flow/resolution_intelligence/candidate.py` — `promote_to_atlas()` (lines 33-74)

Resolution candidate promotion from engineer workflow.
- **Severity:** `"MEDIUM"` (hardcoded)
- **Classification:** `"HEURISTIC"`

---

## Current Severity Distribution

| Severity Value | Used By | Visual Weight |
|---------------|---------|---------------|
| `TAPEOUT_BLOCKING` | Detector rules (1a/b/c/d/e/f/g/h/i/k/l), orchestrator Path E | Red — alarming |
| `HIGH` | Orchestrator Path C | Red — alarming |
| `FUNCTIONAL_RISK` | Detector rules (1c/i/j/m) | Orange — concerning |
| `PERFORMANCE_DEGRADATION` | Detector rules (1a/j/k/l) | Yellow — moderate |
| `MEDIUM` | Cross-tool DRC, resolution candidate, signature fallback | Yellow — moderate |
| `LOW` | Not actively used in creation | Blue — neutral |
| `WARNING` | Not actively used in creation | Gray — low visibility |
| `UNDER_REVIEW` | Not actively used in creation | Purple — ambiguous |
| `INFO` | Not actively used in creation | No color defined |

## Problem Summary

1. **9 severity levels** but only ~5 distinct visual weights → duplicate colors
2. `MEDIUM` and `PERFORMANCE_DEGRADATION` share yellow but mean different things
3. `HIGH` and `TAPEOUT_BLOCKING` share red but mean different things
4. `WARNING` and `INFO` have no active creation path
5. No severity level cleanly maps to "engineering observation in a passed run"
6. Entry count in tab header shows only total count — no severity breakdown
