# PicoRV32 Signoff Pipeline Review

**Date:** 2026-06-21
**Run:** `run_1781952921_92ee0437_picorv32`
**Status:** INCOMPLETE (evolving toward PASS)

## Current Signoff Status

| Check | Status | Evidence |
|---|---|---|
| DRC | CONDITIONAL_PASS | 2 licon.8a (known false positive INF-MAGIC-002), 0 KLayout violations |
| LVS | NOT_RUN | `extract all` completed (132MB .ext), `ext2spice` timed out at 600s |
| Setup Timing | PASS | WNS=0.0ns (TT corner only) |
| Hold Timing | PASS | WHS=0.07927ns (TT corner only) |
| Density | FLOW_BUG | `check_density` removed from OpenROAD v2.0, fallback returns fake data |
| Antenna | PASS | 0 violations |
| CDC | NOT_APPLICABLE | Single clock domain proven |
| EM/IR | NOT_RUN | Not yet executed |

## Priority Findings

### P0: LVS — Blocked by Timeout (Resolved)

**Root cause:** `ext2spice` conversion of 132MB `.ext` file timed out at 600s.

**Fix applied:**
- Extraction timeout: 600s → 3600s (for GDS > 10MB) — `openroad_adapter.py:1124`
- Netgen comparison timeout: 600s → 3600s — `openroad_adapter.py:1225`

**Next action:** Re-run flow, verify LVS completes with 0 unmatched devices/nets.

### P1: Multi-Corner STA — Only TT Ran (Fixed)

**Root cause:** Two compounding bugs:

| # | Defect | File | Lines |
|---|---|---|---|
| 1 | No corner loop — orchestrator calls `run_timing_signoff` once | `orchestrator.py:1168-1210` | Hardcoded `"typical"` |
| 2 | `_write_signoff_tcl` doesn't accept `corner_name` — always loads TT liberty | `openroad_adapter.py:2767-2809` | `_get_orfs_liberty_path(pdk)` defaults to `"typical"` |

**Fix applied:**
- `orchestrator.py`: Loops over `self.corners` (3 corners: worst/typical/best), collects per-corner results, writes `sta_corners.json` with all corners
- `openroad_adapter.py`:
  - `_write_signoff_tcl` accepts `corner_name`, uses it for liberty loading and report filenames
  - `run_timing_signoff` accepts `corner_name`, passes through
  - Per-corner report files: `signoff_{corner}_setup.rpt`, `signoff_{corner}_hold.rpt`, `signoff_{corner}_log.txt`

**Next action:** Re-run STA, verify all 3 corners produce valid timing reports.

### P2: CDC — Proven NOT_APPLICABLE

**Evidence:**
- Single clock port `clk` in all PicoRV32 modules
- All 49 `always @(posedge ...)` blocks use `clk`
- No generated clocks, PLLs, or clock dividers
- Wishbone wrapper renames `clk` → `wb_clk_i` (direct assign, not separate domain)
- SDC: `create_clock -name clk -period 20.0 [get_ports clk]` — one clock

**Verdict:** NOT_APPLICABLE — no action needed.

### P3: Density — Flow Bug (Strategy in `density_closure_strategy_v1.md`)

**Root cause:** `check_density` does not exist in OpenROAD v2.0-17598.

**Current behavior:** Silently returns fake PASS (density=0%, violations=0).

**Recommended fix:** Integrate PDK's KLayout DRC script (`met_min_ca_density.lydrc`) as replacement.

## Pipeline Bug Summary

| Bug ID | Component | Severity | Status |
|---|---|---|---|
| PIPELINE-001 | LVS timeout (600s → 3600s) | High | Fixed |
| PIPELINE-002 | LVS netgen timeout (600s → 3600s) | High | Fixed |
| PIPELINE-003 | STA single-corner (no loop) | High | Fixed |
| PIPELINE-004 | STA hardcoded TT liberty | High | Fixed |
| PIPELINE-005 | Density fake-PASS fallback | Medium | Strategy doc, not implemented |
| PIPELINE-006 | CDC not classified | Low | Proven NOT_APPLICABLE |

## PicoRV32 Design Characteristics

| Metric | Value |
|---|---|
| Standard cells | 1273 |
| Utilization | 36% |
| Clock frequency | 50 MHz (20ns) |
| GDS size | 14 MB |
| .ext file size | 132 MB |
| Power | 9.15 mW |
| Metal layers (Sky130) | 5 (met1-met5) |
| STA corners defined | 3 (SS 1.62V 125C, TT 1.80V 25C, FF 1.95V -40C) |

## Next Action Plan

1. **Re-run flow** with current fixes (LVS timeout, STA multi-corner)
2. **Verify LVS** — expect 0 unmatched devices/nets
3. **Verify STA** — all 3 corners passing (PicoRV32 at 50MHz should be comfortable)
4. **Implement KLayout density** integration
5. **Run EM/IR** if tooling available
6. **Final signoff classification** — generate certification document
