# Ground Truth Report: gcd & picorv32 Real ASIC Flow

**Date**: 2026-06-20
**PDK**: sky130A (sky130hd platform)
**Tools**: Yosys 0.40, OpenROAD v2.0-17598, Magic 8.3.659, KLayout 0.30.7, netgen 1.5.133

---

## 1. Run Summary

### GCD

| Metric | Value |
|---|---|
| Run ID | `run_1781952813_5f415aee_gcd` |
| Execution Status | SUCCESS |
| Signoff Status | FAILED |
| Tapeout Ready | NO |
| Runtime | 47s |
| Clock Period | 10.0 ns (100 MHz) |
| Cell Count | 34 |
| Utilization | 19% |
| Die Area | 2490 µm² (CSV) / 14139 µm² (JSON) — discrepancy |
| QoR Score | 0.800 |

### PicoRV32

| Metric | Value |
|---|---|
| Run ID | `run_1781952921_92ee0437_picorv32` |
| Execution Status | SUCCESS |
| Signoff Status | FAILED |
| Tapeout Ready | NO |
| Runtime | 1286s (~21.4 min) |
| Clock Period | 20.0 ns (50 MHz) |
| Cell Count | 1273 |
| Utilization | 36% |
| Die Area | 100559 µm² (CSV) / 284201 µm² (JSON) — discrepancy |
| QoR Score | 0.000 |

---

## 2. Signoff Status Matrix

### GCD

| Check | Result | Detail |
|---|---|---|
| DRC (Magic) | FAIL | 2 violations (licon.8a only) |
| DRC (KLayout) | PASS | 0 violations |
| LVS | PASS | 0 unmatched devices, 0 unmatched nets |
| Setup Timing | PASS | WNS = 0.0 ns, TNS = 0.0 ns |
| Hold Timing | PASS | Worst slack = 0.452 ns |
| Antenna | PASS | No violations |
| Density | WARN | `check_density` cmd not found (flow bug) |
| EM/IR | PASS | Total power = 0.97 mW |
| Formal | PASS | |
| Routing DRC | PASS | 0 violations |

### PicoRV32

| Check | Result | Detail |
|---|---|---|
| DRC (Magic) | FAIL | 2 violations (licon.8a only) |
| DRC (KLayout) | PASS | 0 violations |
| LVS | NOT RUN | Magic extraction timeout at 600s (131.9MB .ext) |
| Setup Timing | PASS | WNS = 0.0 ns, TNS = 0.0 ns |
| Hold Timing | PASS | Worst slack = 0.079 ns |
| Antenna | PASS | No violations |
| Density | WARN | `check_density` cmd not found (flow bug) |
| EM/IR | PASS | Total power = 6.18 mW |
| Formal | PASS | |
| Routing DRC | PASS | 0 violations |
| CDC | NOT DONE | 2 clock domains — requires external tool |

---

## 3. DRC Deep Dive

### Rule: licon.8a — "poly overlap of poly contact < 0.08um in one direction"

#### GCD

- **Magic**: 2 violations (3 coordinate sets reported)
- **KLayout**: 0 violations
- **Determination**: **FALSE POSITIVE** (Category G)
- **Evidence**: KLayout runs the same sky130 DRC deck and finds ZERO violations. The licon.8a rule is a known Magic false positive documented in the tech files (INF-MAGIC-002).
- **AI Hallucination**: The AI explanation claims "1 real li.3 spacing violation detected by both Magic and KLayout" — this is factually incorrect. Neither Magic nor KLayout reports any li.3 violations. Magic reports only licon.8a. KLayout reports 0 total violations.

#### PicoRV32

- **Magic**: 2 violations (42 coordinate sets reported)
- **KLayout**: 0 violations
- **Determination**: **FALSE POSITIVE** (Category G)
- **Evidence**: Same pattern as gcd. KLayout runs full DRC suite and finds 0 violations.
- **AI Hallucination**: Same li.3 hallucination as gcd — there are NO li.3 violations in any report.

### Cross-Tool DRC Analysis

| Design | Magic | KLayout | Agreement | Disagreement Type |
|---|---|---|---|---|
| gcd | 2 | 0 | TOOL_DISAGREEMENT | MAGIC_FAIL_KLAYOUT_PASS |
| picorv32 | 2 | 0 | TOOL_DISAGREEMENT | MAGIC_FAIL_KLAYOUT_PASS |

### Routing DRC

Both designs: **0 routing DRC violations** after detailed routing completion.

---

## 4. LVS Deep Dive

### GCD — PASS

- All 23+ cell types matched perfectly
- Every subcircuit: circuits match uniquely, netlists match uniquely
- Cell pin lists equivalent for all cells
- No merged device discrepancies
- Extraction completed in 0.66s (Magic) + LVS comparison in 44.7s

### PicoRV32 — NOT RUN (Timeout)

- Magic GDS-to-SPICE extraction timed out at 600 seconds
- Generated `.ext` file is 131.9 MB
- Root cause: flat extraction of 1273 cells + fill cells → excessive extraction time
- **Determination**: **FLOW BUG** (Category E) — extraction timeout too short for design of this size
- **Recommendation**: Increase timeout to >600s or implement hierarchical extraction

---

## 5. Timing Closure Audit

### GCD

| Metric | Value |
|---|---|
| Setup WNS | 0.0 ns |
| Setup TNS | 0.0 ns |
| Hold WNS | 0.452 ns |
| Worst Critical Path | 2.80 ns (of 10 ns period) |
| Critical Path Slack | 7.35 ns |
| Max Slew Violations | 0 |
| Max Cap Violations | 0 |
| Max Fanout Violations | 0 |

### PicoRV32

| Metric | Value |
|---|---|
| Setup WNS | 0.0 ns |
| Setup TNS | 0.0 ns |
| Hold WNS | 0.079 ns |
| Worst Critical Path | 1.91 ns (of 20 ns period) |
| Critical Path Slack | 14.09 ns |
| Max Slew Violations | 0 |
| Max Cap Violations | 0 |
| Max Fanout Violations | 0 |

### STA Coverage Gap

Only the **typical** corner was analyzed. The manifest specifies 3 corners (worst/slow, typical, best/fast) but only typical appears in `sta_corners.json`. This is either a flow gap or the report parser only captures the first corner.

---

## 6. Physical Design Audit

### GCD

| Metric | Value |
|---|---|
| Cell Count | 34 |
| Utilization | 19% (target: 15%) |
| Die Area | 2490–14139 µm² |
| Core Utilization | Very low — design is trivially small |
| Clock Buffers | 2 (clkbuf_16 cells) |
| Congestion | None — 0 routing violations |
| Antenna | PASS |
| Tap Cells | Present (standard flow) |
| PDN | Standard sky130hd PDN |

### PicoRV32

| Metric | Value |
|---|---|
| Cell Count | 1273 |
| Utilization | 36% |
| Die Area | 100559–284201 µm² |
| Core Utilization | Moderate — well within sky130hd limits |
| Routing Iterations | 16 iterations, peaked at 8619 violations, converged to 0 |
| Clock Buffers | Multiple H-tree clock buffers |
| Congestion | Resolved after 16 routing iterations |
| Antenna | PASS |
| Tap Cells | Present |
| PDN | Standard sky130hd PDN |

---

## 7. Density Check Flow Bug

Both designs fail density check with:
```
Error: invalid command name "check_density"
```

The TCL script calls `check_density -layers -min 15 -max 85` which is not a valid OpenROAD command in v2.0-17598. This is purely a **flow bug** — not an actual density violation.

---

## 8. Metrics Discrepancies

| Design | Metrics CSV | Metrics JSON | Delta |
|---|---|---|---|
| gcd die_area_um2 | 2490 | 14140 | ~5.7× |
| picorv32 die_area_um2 | 100559 | 284201 | ~2.8× |

The CSV appears to report core area while JSON reports total die area including pad ring margins.

---

## 9. Root Cause Classification

### GCD

| Issue | Category | Evidence | Severity | Confidence |
|---|---|---|---|---|
| licon.8a DRC violations | G — False Positive | KLayout 0 violations, known Magic false-positive | LOW | HIGH |
| AI li.3 hallucination | F — Reporting Bug | No li.3 in any DRC report | LOW | HIGH |
| Density check command | E — Flow Bug | `check_density` not in OpenROAD v2.0 | LOW | HIGH |

### PicoRV32

| Issue | Category | Evidence | Severity | Confidence |
|---|---|---|---|---|
| licon.8a DRC violations | G — False Positive | KLayout 0 violations, known Magic false-positive | LOW | HIGH |
| LVS extraction timeout | E — Flow Bug | 600s timeout, 131.9MB .ext | MEDIUM | HIGH |
| AI li.3 hallucination | F — Reporting Bug | No li.3 in any DRC report | LOW | HIGH |
| Density check command | E — Flow Bug | `check_density` not in OpenROAD v2.0 | LOW | HIGH |

---

## 10. Key Findings

1. **No real DRC violations exist** in either design. All Magic-reported licon.8a violations are known false positives cross-validated by KLayout.
2. **No timing violations** in either design. Both meet their clock period targets with significant margin.
3. **LVS is clean for gcd** but could not complete for picorv32 due to extraction timeout.
4. **The AI explanation is actively misleading** — it hallucinates "li.3 spacing violations" that do not exist.
5. **The density check is broken** due to an outdated OpenROAD TCL command.
6. **Only one STA corner was analyzed** despite 3 being configured.
7. **Die area reporting has a significant discrepancy** between CSV and JSON metrics.
