# UART Failure Atlas Lineage Audit

**Run:** `run_1781246066_3c483cb5_uart_top`
**Design:** uart_top
**PDK:** sky130A
**Audit Date:** 2026-06-12

---

## Overview

This run produces 4 Failure Atlas entries from 3 independent creator paths, all tracing to the same root cause: Magic DRC falsely flags 2 licon.8a violations that KLayout does not detect (INF-MAGIC-002).

---

## Entry 1: Cross-tool DRC Disagreement

| Field | Value |
|---|---|
| **failure_type** | `CROSS_TOOL_DRC_DISAGREEMENT` |
| **signature** | `inf_magic_002_cross_tool_disagreement` |
| **severity** | `MEDIUM` |
| **entry_level** | `WARNING` |
| **creator function** | `CrossToolDRCAnalyzer._create_disagreement_incident()` |
| **source file** | `gli_flow/core/cross_tool_drc.py:135` |
| **trigger condition** | `magic_violations=2, klayout_violations=0` → `TOOL_DISAGREEMENT` → `MAGIC_FAIL_KLAYOUT_PASS` |
| **parent incident** | None (first detection of root cause pattern) |
| **evidence** | Full `magic_result` and `klayout_result` dicts, `analysis_type: "cross_tool_comparison"`, `citation: "inf_magic_002"` |
| **creation time** | During DRC stage (orchestrator.py:896), earliest of the 4 entries |
| **incident_id** | `872e87a3-9ed1-4a87-a5b8-2e6bf1806ff6` |

**Deduplication guard:** `insert_entry_if_not_exists` (repository.py:90-99) prevents duplicates with same `(run_id, failure_type, signature)` triples.

---

## Entry 2: DRC Failed

| Field | Value |
|---|---|
| **failure_type** | `DRC_SPACING` (mapped from `detect_failures` rules) |
| **signature** | `DRC failed: 2 violations, categories: [DRC_SPACING]` |
| **severity** | `TAPEOUT_BLOCKING` |
| **entry_level** | `FAILURE` |
| **creator function** | `detect_failures()` in `failure_atlas/detector.py:66-91` |
| **source file** | `failure_atlas/detector.py:85` |
| **trigger condition** | `metrics["drc_total_violations"] = 2` and `metrics["drc_is_clean"] = false` |
| **parent incident** | Entry 1 (same violations, metric-based view) |
| **evidence** | `{"drc_total": 2, "by_category": {}, "level2_categories": ["DRC_SPACING"]}` |

**Data source:** Reads `drc_lvs_summary.json` → `total_violations=2`, `is_clean=false`.

---

## Entry 3: Signoff Failure — Magic DRC

| Field | Value |
|---|---|
| **failure_type** | `SIGNOFF_FAILURE` |
| **signature** | `signoff_magic_drc_not_run_error_or_violations_found` |
| **severity** | `TAPEOUT_BLOCKING` |
| **entry_level** | `FAILURE` |
| **creator function** | `_record_signoff_failures()` |
| **source file** | `gli_flow/core/orchestrator.py:777` |
| **trigger condition** | `self.signoff_gate.magic_drc_pass == False` blocks `tapeout_ready` |
| **parent incident** | Entry 1 (consequence at signoff gate) |
| **evidence** | `{"failure": "Magic DRC: NOT_RUN, ERROR, or violations found", "stage": "SIGN_OFF"}` |

**Note:** `klayout_drc_pass = True` (KLayout found 0 violations), so only this single signoff failure is recorded. If both tools failed, a second signoff entry would also be created.

---

## Entry 4: Pipeline Failure — Signoff Gate

| Field | Value |
|---|---|
| **failure_type** | `PIPELINE_FAILURE` |
| **signature** | `pipeline_failure_SIGN_OFF` |
| **severity** | `TAPEOUT_BLOCKING` |
| **entry_level** | `FAILURE` |
| **creator function** | `_handle_failure()` |
| **source file** | `gli_flow/core/orchestrator.py:766` |
| **trigger condition** | Signoff gate fails → `_handle_failure(error_msg)` called |
| **parent incident** | Entry 1 (pipeline-level consequence) |
| **evidence** | `{"error_message": "Signoff gate failed: Magic DRC: ...", "stage": "SIGN_OFF"}` |

---

## Lineage Summary

```
INF-MAGIC-002 (Magic false-positive on licon.8a)
 │
 ├─ [ROOT_CAUSE]  Entry 4: Cross-tool DRC disagreement (CROSS_TOOL_DRC_DISAGREEMENT)
 │                  Detects tool mismatch at DRC stage
 │
 ├─ [SUMMARY]     Entry 3: DRC failed: 2 violations (DRC_SPACING)
 │                  Metric-based detection of same violations
 │
 ├─ [CONSEQUENCE] Entry 2: Magic DRC signoff failure (SIGNOFF_FAILURE)
 │                  Blocking failure at signoff gate
 │
 └─ [CONSEQUENCE] Entry 1: Signoff gate failed (PIPELINE_FAILURE)
                    Pipeline-level failure record
```

All 4 entries describe the same root cause at different abstraction layers:
- **Layer 1 (Root):** Tool comparison detects the disagreement
- **Layer 2 (Metric):** DRC metrics show violations exist
- **Layer 3 (Gate):** Individual signoff check fails
- **Layer 4 (Pipeline):** Pipeline records terminal failure

---

## Over-Counting Assessment

**Yes, over-counting occurs.** One root cause → 4 separate entries. This inflates:
- `occurrence_count` if counted per-entry rather than per-signature
- Resolution tracking (resolution requires 4 entries to be marked `fix_applied`)
- Dashboard UX (engineer sees 4 "problems" for 1 actual issue)
