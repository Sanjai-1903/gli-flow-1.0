# RISC-V Failure Atlas Validation

## Overview

This document validates GLI-FLOW's Failure Atlas against real failures encountered during the PicoRV32 ASIC flow.

## Failures Encountered

### F1: Magic DRC Violations (li.3 — Local Interconnect Spacing)
- **Domain:** DRC
- **Rule:** li.3 (min. li spacing : 0.17um)
- **Count:** 4 violations (Magic), 4 violations (KLayout)
- **Severity:** MEDIUM
- **Atlas Entry:** CROSS_TOOL_DRC_DISAGREEMENT
- **Classification:** VALIDATED_TOOL_DISAGREEMENT (consistent — both tools agree)
- **Root Cause:** Routing at die edge boundary near tap cells. Spacing margin insufficient.

### F2: Magic DRC Violations (licon.8a — Poly Overlap of Contact)
- **Domain:** DRC
- **Rule:** licon.8a (poly overlap of poly contact < 0.08um in one direction)
- **Count:** 2 violations (Magic only)
- **Severity:** LOW
- **Atlas Entry:** Not captured — expected as cross-tool discrepancy
- **Root Cause:** Minor via-to-poly overlap at cell boundary

### F3: LVS Not Run (Netgen Timeout)
- **Domain:** LVS
- **Status:** NOT_RUN
- **Severity:** HIGH
- **Atlas Entry:** No entry created (tool timeout not captured)
- **Root Cause:** Netgen LVS extraction exceeded 600-second timeout

### F4: QoR Score Regression (Mock vs Real)
- **Domain:** METRICS
- **Metric:** QoR score dropped from 0.60 (mock) to 0.00 (real)
- **Severity:** INFO
- **Cause:** Mock run uses placeholder values; regression check is meaningless after first real run

### F5: STA Parser Failed to Extract ORFS Timing
- **Domain:** TIMING
- **Issue:** GLI-FLOW parser extracted WNS=0.0, hold_wns=Infinity instead of real values (12.83 ns, 0.13 ns)
- **Severity:** MEDIUM
- **Root Cause:** Parser expects OpenROAD native format; ORFS 6_report.json has different key names

## Atlas Coverage Analysis

| Failure Domain | Atlas Has Entry? | Entry Accurate? | Remediation Available? |
|---------------|-----------------|----------------|----------------------|
| DRC Spacing (li.3) | Yes (CROSS_TOOL_DRC) | Yes | DRC_SPACING remediation exists |
| DRC Enclosure (licon.8a) | Partial | Partial | DRC_ENCLOSURE remediation exists |
| LVS Timeout | No | N/A | No entry for tool timeout |
| Parser Failure | No | N/A | No entry for STA parser |
| QoR Regression | No | N/A | No entry needed (informational) |

## Gaps Found in Failure Atlas

1. **Missing: LVS_TOOL_TIMEOUT** — No entry exists for netgen/magic extraction timeout
2. **Missing: STA_PARSER_FAILURE** — No entry exists for timing parser extraction failure
3. **Missing: MIXED_LAYER_DRC** — No entry for combination violations spanning li + poly
4. **Classification gap:** "CONSISTENT_FAIL" correctly identified but no automated remediation for li.3 violations

## Recommendations

1. Add new failure type `LVS_TOOL_TIMEOUT` to the Atlas taxonomy
2. Add new failure type `TIMING_PARSER_EXTRACTION_FAILURE`
3. Enhance cross-tool DRC analyzer to suggest specific fixes (e.g., "increase core margin by 5%")
4. Add documentation for `droute_end_iter` tuning when DRC violations persist
