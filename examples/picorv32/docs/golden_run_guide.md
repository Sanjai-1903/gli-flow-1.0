# PicoRV32 Golden Run Guide — GLI-FLOW

> **A step-by-step walkthrough of running PicoRV32 through the GLI-FLOW RTL-to-GDS ASIC pipeline with real EDA tools.**
>
> Golden Run ID: `run_1781586782_b4b86c77_picorv32`
> Date: 2026-06-16
> Duration: 1295.83s (~21.6 min)

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Environment Setup](#2-environment-setup)
3. [Design Overview](#3-design-overview)
4. [Running the Flow](#4-running-the-flow)
5. [Pipeline Walkthrough](#5-pipeline-walkthrough)
6. [Outputs and Artifacts](#6-outputs-and-artifacts)
7. [Signoff Gate Results](#7-signoff-gate-results)
8. [Troubleshooting](#8-troubleshooting)
9. [Next Steps](#9-next-steps)

---

## 1. Prerequisites

Before running, ensure these are installed and working:

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| Yosys | 0.33+ | RTL synthesis |
| OpenROAD | 2.0+ | Place & route |
| Magic | 8.3+ | DRC, extraction |
| KLayout | any | DRC validation |
| Netgen | 1.5+ | LVS |
| sv2v | any | SystemVerilog → Verilog |
| Python | 3.9+ | GLI-FLOW runtime |

### Verify Installation

```bash
gli-flow doctor
```

Expected output: `READY FOR TAPEOUT FLOW` with all tools showing `PASS`.

### PDK Setup

The SkyWater 130nm PDK (sky130A) must be installed:

```bash
gli-flow install --pdk sky130
# or verify:
ls ~/.gli-flow/pdk/sky130A/
# Should see: SOURCES  libs.ref  libs.tech
```

### Environment Variables

```bash
export PDK_ROOT=~/.gli-flow/pdk
export ORFS_ROOT=~/.gli-flow/orfs
```

These can also be set in `~/.gli-flow/config.json`:

```json
{
  "pdk_root": "/home/user/.gli-flow/pdk",
  "orfs_root": "/home/user/.gli-flow/orfs"
}
```

---

## 2. Environment Setup

### 2.1 Clone the Repository

```bash
git clone https://github.com/Jegadiswar-SM/gli-flow-asic.git
cd gli-flow-asic
pip install -e .
gli-flow install
```

### 2.2 Verify Tools

```bash
which yosys openroad magic klayout netgen sv2v
gli-flow doctor
```

### 2.3 Configure Telemetry (Optional)

```bash
# Disable telemetry for local-only runs:
gli-flow config --telemetry off
```

---

## 3. Design Overview

### Design: PicoRV32

A size-optimized RISC-V RV32I CPU core by Claire Xenia Wolf (YosysHQ).

- **RTL:** `rtl/picorv32.v` (3,049 lines, single file)
- **Top module:** `picorv32`
- **PDK:** SkyWater 130nm (sky130A)
- **Clock:** 50 MHz (20 ns period)
- **Configuration:** RV32I subset (counters ON, MUL/DIV/COMPRESSED/IRQ OFF)

### Manifest (`gli_manifest.yaml`)

```yaml
design_name: picorv32
rtl_files:
  - examples/picorv32/rtl/picorv32.v
top_module: picorv32
backend: openroad
pdk: sky130
pdk_variant: sky130A
clock_port: clk
clock_period_ns: 20.0
constraints:
  - examples/picorv32/constraints/picorv32.sdc
threads: 4
corners:
  - { name: worst,  type: worst,  process: slow,    voltage: 1.62, temperature: 125 }
  - { name: typical,type: typical,process: typical, voltage: 1.80, temperature: 25  }
  - { name: best,   type: best,   process: fast,    voltage: 1.95, temperature: -40 }
parameters:
  ENABLE_COUNTERS: 1
  ENABLE_COUNTERS64: 1
  ENABLE_REGS_16_31: 1
  ENABLE_REGS_DUALPORT: 1
```

### Constraints (`constraints/picorv32.sdc`)

- Clock: 50 MHz (20.0 ns period)
- Input delays: 0.5–3.0 ns on memory interface
- Output delays: 1.0–4.0 ns on memory interface
- False paths on: trap, PCPI interface, IRQ, trace, RVFI

---

## 4. Running the Flow

### 4.1 Basic Command

```bash
cd /path/to/gli-flow
export PDK_ROOT=~/.gli-flow/pdk
export ORFS_ROOT=~/.gli-flow/orfs
gli-flow run examples/picorv32
```

### 4.2 With Custom Options

```bash
gli-flow run examples/picorv32 \
  --threads 8 \
  --memory 16000 \
  --verbose
```

### 4.3 Mock Mode (No Tools)

```bash
gli-flow run examples/picorv32 --mock
```

---

## 5. Pipeline Walkthrough

### Stage 1: INITIALIZING

Reads the manifest, validates the environment, creates the run directory.

```
Run ID: run_1781586782_f8973cb6_picorv32
Design: picorv32
PDK: sky130
PDK Root: /home/user/.gli-flow/pdk
Corners: ['worst', 'typical', 'best']
Threads: 4
Run Dir: outputs/runs/run_1781586782_f8973cb6_picorv32
```

### Stage 2–3: HIERARCHICAL_PARTITIONING / BLOCK_SYNTHESIS

Placeholder stages — skipped for flat designs.

### Stage 4: SYNTHESIS

Yosys converts the Verilog RTL to a gate-level netlist using the sky130 standard cell library.

**What happens:**
1. If RTL contains SystemVerilog, `sv2v` preprocesses it to Verilog
2. Yosys synthesizes to generic gates
3. Yosys maps gates to the sky130 standard cell library
4. A config file is generated for OpenROAD

**Output:** `1_synth.v` — synthesized gate-level netlist

**Note:** PicoRV32 uses SystemVerilog constructs (always_ff, always_comb, logic types). GLI-FLOW's sv2v preprocessor handles this automatically.

### Stage 5: PACKAGING

This is the main ORFS (OpenROAD Flow Scripts) run — the longest stage (~20 minutes).

**Sub-steps executed by ORFS:**

| Step | Description | Time (approx) |
|------|-------------|---------------|
| `1_synth` | Yosys synthesis (second pass) | ~30s |
| Floorplan | Die area, I/O pins | ~10s |
| Floorplan (PDN) | Power distribution network | ~10s |
| Global Placement | Initial cell placement | ~60s |
| Detail Placement | Legalized placement | ~30s |
| Clock Tree Synth | Clock tree insertion | ~30s |
| **Detailed Routing** | **Metal interconnect routing** | **~15 min** |
| Fill Cell | Density fill insertion | ~30s |
| Final Report | Timing/power/area extraction | ~10s |

**Routing convergence:** The router ran ~35 iterations, reducing violations from 8,619 → 0.

### Stage 6–26: Additional Checks

These are GLI-FLOW-managed stages that run after ORFS completes:

| Stage | What It Does | Golden Result |
|-------|-------------|---------------|
| CLOCK_GATING | Clock gate insertion | SKIP (not enabled) |
| SCAN_INSERTION | DFT scan chains | SKIP |
| FORMAL_VERIFICATION | RTL vs gate equivalence | PASS |
| FLOORPLANNING | Post-hoc review | PASS |
| DENSITY_CHECK | Density verification | WARN (post-fill) |
| YIELD | Yield enhancement | PASS |
| ATPG | Test pattern generation | SKIP |
| D2D_INTERFACE_CHECK | Die-to-die interface | SKIP |

### Stage 21: DRC (Design Rule Check)

Two DRC engines run:

**Magic DRC:**
```
2 violations found:
- li.3 (local interconnect spacing): 1 real violation
- licon.8a (contact enclosure): 1 false-positive (known issue)
```

**KLayout DRC:**
```
0 violations found
```

**Cross-Tool Analysis:** `TOOL_DISAGREEMENT`
- The `licon.8a` violation is a known Magic false-positive (INF-MAGIC-002)
- KLayout validates the GDS as clean
- One real `li.3` spacing violation needs attention

### Stage 22: LVS (Layout vs. Schematic)

**Result:** NOT RUN — extraction timed out

**Root cause:** Magic's GDS-to-spice extraction produced a 129.9MB `.ext` file (due to fill cell inclusion) and exceeded the 600-second timeout.

### Stage 24–26: TIMING_ANALYSIS / SI_ANALYSIS / SIGN_OFF

| Check | Result |
|-------|--------|
| Setup Timing (WNS) | 0.0 ns — PASS |
| Hold Timing (WHS) | 0.0 ns — PASS |
| Signal Integrity | PASS |
| Power Analysis | PASS (9.15 µW) |

### Stage 28: QOR_EXTRACTION

Metrics collected (149 fields):

```json
{
  "wns": 0.0, "tns": 0.0,
  "utilization": 36.0,
  "cell_count": 1282,
  "die_area_um2": 284200.94,
  "total_power_mw": 0.00915,
  "runtime_sec": 1295.83
}
```

---

## 6. Outputs and Artifacts

### Directory Structure

```
outputs/runs/run_1781586782_b4b86c77_picorv32/
├── artifacts/
│   ├── 6_final.gds          # Final GDSII (12.7 MB)
│   ├── 6_final.def          # Final DEF (11.2 MB)
│   ├── 6_final.v            # Final netlist (873 KB)
│   ├── 1_synth.v            # Synthesized netlist
│   ├── 2_floorplan.sdc      # Floorplan constraints
│   ├── 6_final.sdc          # Final constraints
│   └── *.ext                # Cell extractions
├── reports/
│   ├── timing.rpt           # Timing report
│   ├── power.rpt            # Power report
│   ├── metrics.csv          # ORFS metrics
│   └── util.rpt             # Utilization report
├── logs/
│   ├── openroad.log         # Main ORFS log
│   ├── yosys.log            # Synthesis log
│   ├── magic_drc.log        # Magic DRC log
│   └── klayout_drc.log      # KLayout DRC log
├── telemetry/
│   ├── metrics.json         # Structured metrics
│   └── drc_agreement.json   # Cross-tool DRC analysis
├── config.json              # Full design config
├── reproducibility.json     # Provenance manifest
├── drc_lvs_summary.json     # DRC/LVS results
├── sta_corners.json         # Multi-corner STA
├── run_summary.md           # Human-readable summary
└── ai_explanation.json      # AI-generated analysis
```

### Key File Details

| File | Size | Description |
|------|------|-------------|
| `artifacts/6_final.gds` | 12,748 KB | Final GDSII — ready for tapeout |
| `artifacts/6_final.def` | 11,221 KB | Design Exchange Format |
| `artifacts/6_final.v` | 873 KB | Gate-level Verilog netlist |
| `telemetry/metrics.json` | 2 KB | 149 metric fields |
| `drc_lvs_summary.json` | 1 KB | DRC: 2 violations, LVS: timeout |

---

## 7. Signoff Gate Results

### Implementation Score Breakdown

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Timing (WNS) | 1.0 | 50% | 0.50 |
| Area (utilization) | 0.87 | 30% | 0.26 |
| Density | 1.0 | 20% | 0.20 |
| **QoR Score** | | | **0.96** |

**Note:** The QoR score was reported as 0.000 in the output due to signoff failures overriding the implementation score.

### Signoff Gate Checklist

```
✓ Setup Timing (WNS = 0.0 ns)
✓ Hold Timing (WHS = 0.0 ns)
✓ Antenna Check
✓ Density Check
✓ EM/IR Check
✓ Formal Verification
✗ DRC (Magic) — 1 real + 1 false-positive violation
✗ LVS — Extraction timeout
```

### Tapeout Blockers

| Blocker | Severity | Fix |
|---------|----------|-----|
| li.3 spacing violation | HIGH | Increase die area / routing margin |
| LVS extraction timeout | HIGH | Increase timeout >600s or use hierarchical extraction |

### Known False Positives

- **licon.8a** — Known Magic false-positive (INF-MAGIC-002). KLayout reports 0 violations. Safe to waive.

---

## 8. Troubleshooting

### Common Issues Encountered

| Issue | Symptom | Fix |
|-------|---------|-----|
| ORFS not found | `ORFS flow dir not found` | Set `ORFS_ROOT` correctly (to parent of `flow/`) |
| PDK not found | `PDK_ROOT directory not found` | Run `gli-flow install --pdk sky130` |
| LVS timeout | `Magic extraction timed out` | Increase timeout in adapter or disable parasitic extraction |
| QoR = 0.000 | Signoff failed | Check DRC/LVS results — QoR is 0 if tapeout blockers exist |
| licon.8a DRC | Violation only in Magic | Known false-positive — cross-validate with KLayout |
| sv2v warning | `.v` file contains SV constructs | Non-fatal — GLI-FLOW automatically preprocesses |

### LVS Extraction Tuning

The default 600s timeout may be insufficient for large designs with fill cells.

**Quick fix options:**
1. Increase timeout: Edit `openroad_adapter.py` → `_run_magic_extraction` timeout parameter
2. Disable parasitic extraction: Add `cthresh=0 rthresh=0` to extraction flags
3. Use hierarchical extraction: Extract blocks separately

---

## 9. Next Steps

### To Achieve Full Tapeout Readiness

1. **Fix DRC violation:** Increase die area by 10–15% in manifest to fix the li.3 spacing violation
2. **Fix LVS extraction:** Increase LVS timeout or configure hierarchical extraction
3. **Rerun:** After fixes:
   ```bash
   gli-flow run examples/picorv32
   ```

### Compare with Baseline

```bash
# Compare with golden run:
gli-flow ci examples/picorv32 \
  --baseline run_1781586782_b4b86c77_picorv32 \
  --qor-min 80 \
  --wns-max 0.0
```

### View Dashboard

```bash
# Start the web dashboard:
gli-flow dashboard
```

### View Run History

```bash
gli-flow history
gli-flow status
```

---

## Appendix: Full Console Output

The complete console output from the golden run is preserved in:
```
outputs/runs/run_1781586782_b4b86c77_picorv32/logs/openroad.log
```

---

*Generated by GLI-FLOW v1.0.0 — Green Lantern Industries*
