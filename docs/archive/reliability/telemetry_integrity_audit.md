# Telemetry Integrity Audit

## Findings & Fixes

### 1. Hold Timing Key Typo — Silent Data Corruption

**Location:** `gli_flow/telemetry/parser.py:72`

**Problem:** CSV path wrote `metrics["hold_whs_ns"]` but read `parsed["hold_wns"]`. All regex and signoff parsers read from `"hold_whs_ns"`. CSV hold timing was written under a mismatched key and silently lost.

**Fix:** Changed to `parsed["hold_whs"]` — the correct CSV column name.

**Same typo at line 74:** `parsed["hold_tns"]` → `parsed["hold_ths"]`

**Downstream:** `orchestrator.py:294-295` had copy-paste bug with dead first-key lookups. Fixed to direct reads:
```python
self.record.hold_wns = parsed.get("hold_whs_ns")
self.record.hold_tns = parsed.get("hold_ths_ns")
```

### 2. Power Unit Conversion Bug — Values 1000x Too Large

**Location:** `parser.py:352-355, 370`

**Problem:** Three parsing strategies all multiplied raw values by 1000.0 (assuming Watts→mW conversion), but ORFS reports values in mW already. Result: `total_power_mw` showed 2377.0 instead of 2.377.

**Fix:** Removed `* 1000.0` from all three parsing paths. Input values are already in mW.

**Tests that now pass:**
- `test_power_valid_returns_done` — `6.0 mW == 6.0 mW` (was 6000.0)
- `test_parse_power_report_with_data` — `2.377 mW == 2.377 mW` (was 2377.0)

### 3. Fabricated Decap Coverage

**Location:** `parser.py:433`

**Problem:** `decap_coverage_pct` was never parsed from any report. It was a pure heuristic: `min(100.0, total * 0.5)`. A consumer trusting this metric would receive meaningless, potentially misleading data.

**Fix:** Replaced with `None` and added `"decap_coverage_note": "not_measured"`. Real parsing should be implemented when decap logs include coverage percentage.

### 4. Parser Test Coverage

| Parsers | Status |
|---------|--------|
| Tested (9): timing, utilization, runtime, DRC, LVS, power, EM, formal, SI | Dedicated tests exist |
| Untested (13): decap, scan, ATPG, antenna, density, signoff, clock gating, PRO, hierarchical partition, block synthesis, top floorplan, D2D, yield | **No dedicated tests** |

## Validation

- All parsers verified for NOT_RUN/ERROR/clean paths
- Power values end-to-end validated: input file → parser → dict → test assertion
- Full test suite: 466 passed, 0 failed, 1 skipped
