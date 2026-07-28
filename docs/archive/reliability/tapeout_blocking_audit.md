# TAPEOUT_BLOCKING Severity Assignment Audit

All locations where `TAPEOUT_BLOCKING` is assigned to a Failure Atlas entry.

## Summary

10 assignment sites across 4 files. Only #2 (DRC) and #10 (signoff) are triggered by the INF-MAGIC-002 pattern.

---

## 1. `failure_atlas/detector.py:43`

- **Condition**: `setup_wns_ns < -0.5`
- **Domain**: TIMING / SETUP_VIOLATION
- **Trigger**: Setup timing margin below threshold
- **Relevant to INF-MAGIC-002?** No

## 2. `failure_atlas/detector.py:52`

- **Condition**: `hold_whs_ns < 0`
- **Domain**: TIMING / HOLD_VIOLATION
- **Trigger**: Hold timing violated
- **Relevant to INF-MAGIC-002?** No

## 3. `failure_atlas/detector.py:62`

- **Condition**: `max(overflow_h, overflow_v) > 0.1`
- **Domain**: CONGESTION / GLOBAL_OVERFLOW
- **Trigger**: Routing congestion above warning threshold
- **Relevant to INF-MAGIC-002?** No

## 4. `failure_atlas/detector.py:88`

- **Condition**: `drc_total > 0` or `not drc_is_clean`
- **Domain**: DRC / DRC_SPACING (or DRC_WIDTH, DRC_ENCLOSURE, etc.)
- **Trigger**: Any DRC violations found by Magic
- **Relevant to INF-MAGIC-002?** YES — this fires for all DRC violations including licon.8a
- **IFE**: Found in `detect_failures()` → called by `FlowOrchestrator._run_failure_detection()` at orchestrator.py:382
- **Effect**: Creates `DRC_SPACING` entry with `severity=TAPEOUT_BLOCKING`

## 5. `failure_atlas/detector.py:110`

- **Condition**: `lvs_status == "FAIL"` and `short_count > 0`
- **Domain**: LVS / LVS_SHORT
- **Trigger**: LVS failure with shorts detected
- **Relevant to INF-MAGIC-002?** No

## 6. `failure_atlas/detector.py:119`

- **Condition**: `lvs_status == "ERROR"`
- **Domain**: LVS / LVS_DEVICE_MISMATCH
- **Trigger**: LVS execution error
- **Relevant to INF-MAGIC-002?** No

## 7. `failure_atlas/detector.py:131`

- **Condition**: `lvs_status == "NOT_RUN"`
- **Domain**: LVS / LVS_DEVICE_MISMATCH
- **Trigger**: LVS skipped
- **Relevant to INF-MAGIC-002?** No

## 8. `failure_atlas/detector.py:143`

- **Condition**: `has_sram and drc_total > 0 and SPACING violations > 0`
- **Domain**: MACRO_INTEGRATION / SRAM_PIN_BLOCKED
- **Trigger**: SRAM macro with spacing violations
- **Relevant to INF-MAGIC-002?** No

## 9. `gli_flow/core/orchestrator.py:781` (`_record_signoff_failures`)

- **Condition**: `not self.signoff_gate.tapeout_ready`
- **Domain**: SIGNOFF / SIGNOFF_FAILURE
- **Trigger**: Any signoff gate check failed
- **Relevant to INF-MAGIC-002?** YES — fires when Magic DRC fails (including known licon.8a)
- **IFE**: Called at orchestrator.py:1193 after the backend result is processed
- **Effect**: Creates `SIGNOFF_FAILURE` entry with `severity=TAPEOUT_BLOCKING`

## 10. `failure_atlas/detector.py` (implicit in `make_entry`)

- **Condition**: All callers that pass `FailureSeverity.TAPEOUT_BLOCKING`
- **Covered by**: Items 1–8 above

---

## INF-MAGIC-002 Trigger Path

```
Magic FAIL (licon.8a violations)
  ↓
CrossToolDRCAnalyzer detects TOOL_DISAGREEMENT (line 896)
  → creates CROSS_TOOL_DRC_DISAGREEMENT entry (severity=MEDIUM)
  → telemetry written to drc_agreement.json
  ↓
_run_failure_detection() (line 1102)
  → detect_failures() reads drc_lvs_summary.json
  → DRC_SPACING entry created (severity=TAPEOUT_BLOCKING)  ← ITEM 4
  ↓
signoff_gate.tapeout_ready → False (magic_drc_pass is False)
  → _record_signoff_failures(blocking_failures())
  → SIGNOFF_FAILURE entry created (severity=TAPEOUT_BLOCKING)  ← ITEM 9
```

## Actions Taken

- **Item 4**: DRC_SPACING entry reclassified to `UNDER_REVIEW` with `classification=VALIDATED_TOOL_DISAGREEMENT` when cross-tool disagreement with `inf_magic_002` citation exists.
- **Item 9**: SIGNOFF_FAILURE entry retains `TAPEOUT_BLOCKING` severity (signoff really blocked) but gains `classification` and `citation` in evidence for dashboard context.
- **Items 1,2,3,5,6,7,8**: Unchanged — not related to INF-MAGIC-002.
