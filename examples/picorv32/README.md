# PicoRV32 — GLI-FLOW Golden Reference Design

## Description

PicoRV32 is a size-optimized RISC-V RV32I CPU core by Claire Xenia Wolf (YosysHQ).
This project processes PicoRV32 through the full GLI-FLOW ASIC toolchain:
Yosys → OpenROAD → Magic → Netgen → KLayout.

- **RTL:** `rtl/picorv32.v` — 3049 lines, 8 modules
- **Top module:** `picorv32`
- **PDK:** SkyWater 130nm (sky130A)
- **Clock:** 50 MHz (20 ns period)
- **Configuration:** RV32I (no multiply, no divide, no compressed, no IRQ)

## How to Run

```bash
# Production run (with real EDA tools — requires ORFS + PDK installed)
gli-flow run examples/picorv32

# Mock run (for CI/testing — no tools required)
gli-flow run examples/picorv32 --mock
```

## Golden Run Results (2026-06-16)

### Summary

| Metric | Value |
|--------|-------|
| **Implementation (RTL→GDS)** | **SUCCESS** |
| **Signoff** | **FAILED** (DRC + LVS issues) |
| **Runtime** | 1296s (~21.6 min) |
| **WNS / TNS** | 0.0 ns / 0.0 ns (timing met) |
| **Utilization** | 36% |
| **Cell Count** | 1,282 |
| **Die Area** | 284,201 µm² |
| **Total Power** | 9.15 µW |

### Pipeline Stages

| Stage | Status | Details |
|-------|--------|---------|
| SYNTHESIS | PASS | Yosys 0.40, 1282 cells |
| FLOORPLANNING | PASS | Die area defined |
| PLACEMENT | PASS | 36% util |
| CTS | PASS | 50 MHz clock tree |
| ROUTING | PASS | 0 violations after 30+ iterations |
| DRC | FAIL | 1 real (li.3 spacing), 1 false-positive (licon.8a) |
| LVS | NOT RUN | Magic extraction timed out at 600s (129.9MB .ext) |
| TIMING | PASS | Setup and hold met |
| POWER | PASS | 9.15 µW total |

### Key Output Files

| File | Size | Description |
|------|------|-------------|
| `artifacts/6_final.gds` | 12.7 MB | Final GDSII layout |
| `artifacts/6_final.def` | 11.2 MB | Final DEF |
| `artifacts/6_final.v` | 873 KB | Final netlist |
| `drc_lvs_summary.json` | — | DRC: 2 viol, LVS: timeout |
| `telemetry/metrics.json` | — | Full 149-field telemetry |
| `reproducibility.json` | — | SHA256 hashes + versions |

### Signoff Gate

| Check | Status |
|-------|--------|
| Setup Timing | PASS |
| Hold Timing | PASS |
| DRC (Magic) | FAIL (2 violations) |
| DRC (KLayout) | PASS (0 violations) |
| LVS | FAIL (timeout) |
| Antenna | PASS |
| Density | PASS |
| EM/IR | PASS |
| Formal | PASS |

### Known Issues

1. **li.3 spacing violations** — 1 real DRC violation at die edge. Fix by increasing core margin or adjusting routing constraints.
2. **licon.8a false positive** — Known Magic false-positive (INF-MAGIC-002). Cross-validated clean by KLayout.
3. **LVS extraction timeout** — Magic `.ext` file is 129.9 MB due to fill cell inclusion. Increase timeout >600s or use hierarchical extraction.

## Design Files

```
examples/picorv32/
├── rtl/
│   └── picorv32.v          # RTL source (single file)
├── constraints/
│   └── picorv32.sdc        # Timing constraints (50 MHz)
├── docs/
│   ├── execution_report.md  # Detailed execution report
│   └── golden_run_guide.md  # Step-by-step walkthrough
├── gli_manifest.yaml        # GLI-FLOW configuration
└── README.md               # This file
```

## Parameters

PicoRV32 configured as RV32I:
- Counters enabled
- No compressed ISA
- No multiply/divide
- No interrupt controller
- Native memory interface
