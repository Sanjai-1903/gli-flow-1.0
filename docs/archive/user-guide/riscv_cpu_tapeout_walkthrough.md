# RISC-V CPU Tapeout Walkthrough

## From Clone to Signoff

This guide walks through processing PicoRV32 — a real RISC-V CPU — through the GLI-FLOW ASIC toolchain. It assumes you have never used GLI-FLOW before.

## Prerequisites

```bash
# Check required tools
which yosys openroad magic netgen klayout
# All should return a path

# Check PDK installation
ls ~/.gli-flow/pdk/sky130A

# Check ORFS installation
ls ~/.gli-flow/orfs/flow/Makefile
```

## Step 1: Install GLI-FLOW (if not already done)

```bash
git clone https://github.com/Jegadiswar-SM/gli-flow-asic.git
cd gli-flow-asic
pip install -e .
gli-flow install
# This installs PDK, ORFS, and verifies toolchain
```

## Step 2: Verify Environment

```bash
gli-flow doctor
# All items should show PASS
# If any FAIL, run: gli-flow doctor --fix
```

## Step 3: Obtain RISC-V CPU RTL

```bash
# Clone PicoRV32
git clone https://github.com/YosysHQ/picorv32.git /tmp/picorv32
cp /tmp/picorv32/picorv32.v examples/picorv32/rtl/
```

## Step 4: Create Project Structure

```
examples/picorv32/
├── rtl/
│   └── picorv32.v           # RTL source
├── constraints/
│   └── picorv32.sdc         # Timing constraints
├── gli_manifest.yaml         # GLI-FLOW manifest
└── README.md
```

## Step 5: Create Manifest

File: `examples/picorv32/gli_manifest.yaml`

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
  - name: worst
    type: worst
    process: slow
    voltage: 1.62
    temperature: 125
  - name: typical
    type: typical
    process: typical
    voltage: 1.80
    temperature: 25
  - name: best
    type: best
    process: fast
    voltage: 1.95
    temperature: -40
```

## Step 6: Create Constraints

File: `examples/picorv32/constraints/picorv32.sdc`

```sdc
create_clock -name clk -period 20.0 [get_ports clk]
set_input_delay -clock clk -max 2.0 [get_ports {mem_ready mem_rdata}]
set_output_delay -clock clk -max 4.0 [get_ports {mem_valid mem_instr mem_addr mem_wdata mem_wstrb}]
```

## Step 7: Mock Run (Validate Configuration)

```bash
export PDK_ROOT=$HOME/.gli-flow/pdk
export ORFS_ROOT=$HOME/.gli-flow/orfs

gli-flow run examples/picorv32 --mock
```

**Expected result:** All 28 stages complete. DRC/LVS are mocked.
**Troubleshooting:**
- `Manifest not found`: Check manifest path
- `Manifest validation failed`: Check YAML syntax

## Step 8: Real Run (with EDA Tools)

```bash
# Set environment variables (required)
export PDK_ROOT=$HOME/.gli-flow/pdk
export ORFS_ROOT=$HOME/.gli-flow/orfs

# Run (will take 30-60 minutes for a CPU design)
gli-flow run examples/picorv32
```

**Expected runtime:**
- Counter example: < 1 minute
- PicoRV32 (10K cells): ~40 minutes
- Larger CPU (100K cells): several hours

**Progress monitoring:**
The PACKAGING stage runs the entire ORFS flow:
1. Synthesis (Yosys) — 1-2 minutes
2. Floorplanning — < 30 seconds
3. Placement — 2-5 minutes
4. CTS — 1-2 minutes
5. Global Routing — 1-2 minutes
6. **Detailed Routing — 5-30 minutes (longest)**
7. Fill Insertion — 1-2 minutes
8. GDS Merge — < 30 seconds

## Step 9: Check Results

```bash
# Find run directory
ls outputs/runs/

# View run summary
cat outputs/runs/run_*/run_summary.md

# Check artifacts
ls outputs/runs/run_*/artifacts/6_final.gds
ls outputs/runs/run_*/artifacts/6_final.def
ls outputs/runs/run_*/artifacts/6_final.v

# Check DRC/LVS results
cat outputs/runs/run_*/drc_lvs_summary.json

# View layout (if KLayout is installed)
klayout outputs/runs/run_*/artifacts/6_final.gds
```

## Step 10: Interpret DRC/LVS Results

**DRC Clean:** 0 violations — tapeout ready
**DRC with violations:** Check `reports/magic_drc.rpt` and `reports/klayout_drc.xml` for details
**LVS PASS:** Layout matches schematic
**LVS FAIL/TIMEOUT:** Review netgen logs; may need more time for large designs

## Step 11: Timing Signoff

Check final timing in ORFS results:

```bash
cat ~/.gli-flow/orfs/flow/logs/sky130hd/picorv32/base/6_report.json
```

Key metrics:
- `finish__timing__setup__ws`: Setup slack (positive = PASS)
- `finish__timing__hold__ws`: Hold slack (positive = PASS)

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `ORFS flow dir not found` | ORFS_ROOT misconfigured | Set `export ORFS_ROOT=$HOME/.gli-flow/orfs` |
| `PDK not found` | PDK not installed | Run `gli-flow install` |
| Package stage hangs | Routing taking long | Design has many cells; wait |
| DRC violations at die edge | Core margin too small | Adjust floorplan |
| LVS not running | Netgen timeout | Increase LVS timeout |
| CDC warning on single-clock design | Async reset detected | Safe to ignore |

## Known Limitations

1. CDC analysis not performed (requires external tool)
2. Formal verification not performed (requires external tool)
3. LVS may timeout for >10K cell designs
4. STA parser may not extract ORFS timing correctly
5. Minimal constraints may lead to optimistic timing
