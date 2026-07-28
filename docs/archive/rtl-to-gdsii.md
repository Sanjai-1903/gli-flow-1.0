# RTL-to-GDSII Guide

> Everything you need to provide — beyond RTL — to take a design from Verilog/SystemVerilog to finished GDSII using gli-flow.

---

## Table of Contents

1. [Overview: What the Flow Needs](#overview-what-the-flow-needs)
2. [The Manifest (gli_manifest.yaml)](#the-manifest-gli_manifestyaml)
3. [Timing Constraints (SDC)](#timing-constraints-sdc)
4. [Floorplan Constraints](#floorplan-constraints)
5. [IO Pin Placement](#io-pin-placement)
6. [Macro Placement (SRAMs, PLLs, Hard Macros)](#macro-placement-srams-plls-hard-macros)
7. [Power Intent (UPF & PDN)](#power-intent-upf--pdn)
8. [Multi-Corner Liberty Libraries](#multi-corner-liberty-libraries)
9. [ORFS Tuning Variables](#orfs-tuning-variables)
10. [Signoff & Verification](#signoff--verification)
11. [Delivery Checklist](#delivery-checklist)
12. [Appendix: ORFS config.mk Reference](#appendix-orfs-configmk-reference)

---

## Overview: What the Flow Needs

gli-flow's RTL-to-GDSII pipeline requires **six categories of input** beyond the RTL source files:

```
 ┌──────────────────────────────────────────────────────────────────┐
 │                    RTL-to-GDSII Inputs                           │
 ├──────────────────────────────────────────────────────────────────┤
 │                                                                  │
 │  1. gli_manifest.yaml          Design metadata, PDK, config      │
 │  2. timing.sdc                 Timing constraints (mandatory)    │
 │  3. Floorplan constraints      Die area, core util, aspect ratio │
 │  4. IO pin placement           Padring, pin order                │
 │  5. Macro placement            SRAM, PLL, hard macro locations   │
 │  6. Power intent               UPF, PDN configuration            │
 │  7. Multi-corner libs          Liberty files per PVT corner      │
 │  8. ORFS tuning                Extra config.mk variables         │
 │                                                                  │
 └──────────────────────────────────────────────────────────────────┘
```

**Current gli-flow support level** for each input type:

| # | Input | Status | User Must Provide |
|---|-------|--------|-------------------|
| 1 | Manifest | ✅ Fully supported | Create `gli_manifest.yaml` |
| 2 | SDC Timing Constraints | ✅ Fully supported | Write `.sdc` file |
| 3 | Floorplan Constraints | ⚠️ Partial (hardcoded) | Manually extend `config.mk` |
| 4 | IO Pin Placement | ❌ Not supported | Create ORFS pin file manually |
| 5 | Macro Placement | ❌ Not supported | Place macros manually via Tcl |
| 6 | Power Intent | ❌ Not supported | Create PDN Tcl config manually |
| 7 | Multi-Corner Libs | ⚠️ PDK model exists, but STA only runs typical corner | Ensure PDK has all 3 corners |
| 8 | ORFS Tuning | ❌ Not exposed | Manually edit generated `config.mk` |

---

## 1. The Manifest (`gli_manifest.yaml`)

### What It Is

The manifest is the **single entry point** for gli-flow. It tells the flow what to build, with which PDK, and where to find everything.

### Where

Place it in your design directory:

```
my_design/
├── gli_manifest.yaml       ← HERE
└── rtl/
    └── top.v
```

### When

Create it **before running** `gli-flow run .`. Use `gli-flow init my_design` to bootstrap it.

### Fields Reference

| Field | Required | Type | Default | When Checked | Description |
|-------|----------|------|---------|--------------|-------------|
| `design_name` | ✅ | string | — | `run` | Name used for ORFS directories and GDS output |
| `rtl_files` | ✅ | list | — | `run` (must exist) | Paths to `.v`/`.sv` files, relative to project root |
| `top_module` | ✅ | string | — | `run` | Must match a module name in the RTL |
| `backend` | | string | `openroad` | `run` | `openroad` or `librelane` |
| `pdk` | | string | `sky130` | `run` | PDK name: `sky130`, `gf180mcu`, `ihp-sg13g2` |
| `pdk_variant` | | string | `sky130A` | `run` | PDK variant, e.g. `sky130A`, `sky130B` |
| `clock_port` | | string | `clk` | `run` (auto-SDC fallback) | Must match a port in the top module |
| `clock_period_ns` | | float | `10.0` | `run` (auto-SDC fallback) | Target clock period |
| `constraints` | | list | — | `run` (copied to ORFS dir) | Path to `.sdc` file(s); only the first is used |
| `threads` | | int | `4` | `run` | CPU threads for parallel operations |
| `corners` | | list | PDK defaults | `run` (resolved) | PVT corners for multi-corner analysis |
| `mode` | | string | `standard` | `run` | `standard` or `tinytapeout`; affects scaffolding |

### Currently Not Read by Pipeline (Metadata Only)

These fields appear in templates but are **not consumed** by any adapter code:

| Field | Where Defined | Intended Use |
|-------|--------------|--------------|
| `die_area` | tinytapeout template | Target die dimensions `"0 0 200 200"` |
| `core_utilization` | tinytapeout template | Target core density percentage |
| `io_constraints` | tinytapeout template | IO pin definitions (input/output/bidir) |

To use these today, you must **manually inject them** into the ORFS `config.mk` after `generate_config()` runs (see sections 4-6 below).

### Full Example

```yaml
design_name: my_accelerator
rtl_files:
  - rtl/top.v
  - rtl/pe.v
  - rtl/controller.v
top_module: my_accelerator
backend: openroad
pdk: sky130
pdk_variant: sky130A
clock_port: clk
clock_period_ns: 10.0
constraints:
  - constraints/my_accelerator.sdc
threads: 8
corners:
  - { name: worst, type: worst,  process: slow,    voltage: 1.62, temperature: 125 }
  - { name: typical, type: typical, process: typical, voltage: 1.80, temperature: 25  }
  - { name: best,   type: best,   process: fast,    voltage: 1.95, temperature: -40 }
```

---

## 2. Timing Constraints (SDC)

See [constraints.md](../developer/constraints.md) for the full SDC tutorial. Here's the minimal summary:

### What

An `.sdc` file containing timing constraints in Synopsys Design Constraints format.

### Where

```
my_design/
└── constraints/
    └── my_design.sdc        ← HERE
```

Referenced in manifest as:

```yaml
constraints:
  - my_design/constraints/my_design.sdc
```

### When

Written **before the run**. The pipeline reads it at `generate_config()` time (step 1 of the pipeline) and copies it into the ORFS design directory as `constraint.sdc`. It's applied at every subsequent stage.

### Minimum Viable SDC

```sdc
create_clock -name clk -period 10.0 [get_ports clk]
set_input_delay  -clock clk 2.0 [all_inputs]
set_output_delay -clock clk 2.0 [all_outputs]
```

### Production SDC Checklist

- [ ] `create_clock` for every clock port
- [ ] `create_generated_clock` for derived clocks (PLL outputs, dividers)
- [ ] `set_clock_uncertainty` (jitter + margin)
- [ ] `set_clock_transition` (clock slew)
- [ ] `set_clock_latency` (insertion delay)
- [ ] `set_input_delay` for all input ports (max/min)
- [ ] `set_output_delay` for all output ports (max/min)
- [ ] `set_load` on output ports
- [ ] `set_max_fanout` / `set_max_transition` / `set_max_capacitance`
- [ ] `set_false_path` for async resets and known CDC paths
- [ ] `set_operating_conditions` (or omit for multi-corner)

---

## 3. Floorplan Constraints

### What

Floorplan constraints define the chip's physical dimensions, core area, utilization target, and aspect ratio. These tell the P&R tool where to place the design.

### Where

ORFS reads floorplan constraints from `config.mk`. gli-flow's PDK `generate_config_mk()` generates this file at:

```
{orfs_root}/flow/designs/{platform}/{design_name}/config.mk
```

### When

Floorplan constraints take effect at the **FLOORPLANNING** stage (stage 8). They must be set before the run starts — they cannot be changed mid-flow.

### Current State

`CORE_UTILIZATION` is hardcoded to `30` in every PDK. `DIE_AREA`, `CORE_AREA`, and `ASPECT_RATIO` are **not set** — ORFS uses its own defaults (auto-computes die area from core utilization).

### How to Override (Workaround Until Supported)

After `generate_config()`, edit the generated `config.mk` or inject variables via a post-generation script:

```makefile
# Floorplan variables you can add to config.mk
export DIE_AREA          = 0 0 300 300
export CORE_AREA         = 10 10 290 290
export CORE_UTILIZATION  = 50
export ASPECT_RATIO      = 1
export MARGIN            = 10
```

Alternatively, create a `config_override.mk` and include it:

```makefile
# In config.mk, add:
-include $(CURDIR)/designs/$(PLATFORM)/$(DESIGN_NICKNAME)/config_override.mk
```

```makefile
# config_override.mk
export DIE_AREA          = 0 0 400 400
export CORE_UTILIZATION  = 60
export PL_TARGET_DENSITY = 0.55
```

### ORFS Floorplan Variables Reference

| Variable | Unit | Purpose | Example |
|----------|------|---------|---------|
| `DIE_AREA` | µm | Die dimensions `x0 y0 x1 y1` | `0 0 300 300` |
| `CORE_AREA` | µm | Core area boundaries | `10 10 290 290` |
| `CORE_UTILIZATION` | % | Target core density | `50` |
| `ASPECT_RATIO` | ratio | Core height / width | `1` |
| `MARGIN` | µm | Core-to-die margin | `10` |
| `PL_TARGET_DENSITY` | ratio | Placement density target | `0.55` |
| `FP_IO_HMETAL_LAYER` | metal | Horizontal IO pin metal | `met3` |
| `FP_IO_VMETAL_LAYER` | metal | Vertical IO pin metal | `met4` |

### How to Calculate Die Area

```
Die area ≈ (total cell area) / (core_utilization / 100)

Example:
  Total cell area from synthesis = 50,000 µm²
  Target CORE_UTILIZATION = 50%
  Die area = 50,000 / 0.5 = 100,000 µm²
  For a square die: 316 µm × 316 µm → round up to 0 0 320 320
```

---

## 4. IO Pin Placement

### What

IO pin placement defines where each top-level port is located along the die edge. This is critical for:
- Matching package pinout
- Meeting PCB routing requirements
- Ensuring bump/pad locations match the package substrate

### Where

ORFS supports IO pin constraints via:
1. **`IO_CONSTRAINTS`** in `config.mk` — points to a Tcl script or pin file
2. **Pin placement Tcl** — set pins at specific locations with specific metal layers

### When

IO pin placement takes effect during **FLOORPLANNING** stage 8. The constraints must be available before that stage runs.

### Current State

**Not supported by gli-flow.** The `io_constraints` field in the TinyTapeout template is metadata-only and never reaches ORFS. No IO pin placement file is generated.

### How to Do It Manually

**Step 1: Create a pin placement file.**

```tcl
# pin_placement.tcl — place IO pins for my design
# Load after floorplan initialization

# Top edge
set_pin_physical_constraints -pin_name clk -layer met3 -width 5 -height 5 -side 1 -order 1
set_pin_physical_constraints -pin_name rst_n -layer met3 -width 5 -height 5 -side 1 -order 2

# Right edge
set_pin_physical_constraints -pin_name data_out -layer met3 -width 5 -height 5 -side 3 -order 1

# Bottom edge
set_pin_physical_constraints -pin_name data_in -layer met4 -width 5 -height 5 -side 2 -order 1
set_pin_physical_constraints -pin_name valid -layer met4 -width 5 -height 5 -side 2 -order 2

# Left edge
set_pin_physical_constraints -pin_name addr -layer met4 -width 5 -height 5 -side 4 -order 1
```

**Step 2: Reference it in `config.mk`:**

```makefile
export IO_CONSTRAINTS = $(CURDIR)/designs/$(PLATFORM)/$(DESIGN_NICKNAME)/pin_placement.tcl
```

ORFS automatically sources `IO_CONSTRAINTS` during the floorplan stage if the variable is set.

### Side Numbers

| Side | Edge |
|------|------|
| 1 | Top (North) |
| 2 | Bottom (South) |
| 3 | Right (East) |
| 4 | Left (West) |

### ORFS IO Variable Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `IO_CONSTRAINTS` | Path to pin placement Tcl | `$(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/io.tcl` |
| `FP_IO_HLAYER` | Horizontal IO pin metal layer | `met3` |
| `FP_IO_VLAYER` | Vertical IO pin metal layer | `met4` |
| `FP_IO_MODE` | IO pin mode (`1`=auto, `2`=random) | `1` |
| `FP_IO_HMETAL_LAYER` | Horizontal metal for IO pins | `met3` |
| `FP_IO_VMETAL_LAYER` | Vertical metal for IO pins | `met4` |

---

## 5. Macro Placement (SRAMs, PLLs, Hard Macros)

### What

Hard macros (SRAMs, PLLs, analog blocks, custom datapaths) must be explicitly placed — the P&R tool cannot auto-place them. You must provide:
1. **LEF views** — physical boundary, pin locations, blockage layers
2. **Liberty (`.lib`) views** — timing data for STA
3. **GDS views** — final layout stream data
3. **Placement coordinates** — where each macro goes in the floorplan

### Where

```
my_design/
├── macros/
│   ├── sram_256x32.lef
│   ├── sram_256x32.lib
│   ├── sram_256x32.gds
│   └── pll.lef
├── macro_placement.tcl
└── gli_manifest.yaml
```

### When

Macro placement must be applied **after floorplan initialization** but **before standard cell placement** (stages 8–10). The typical order is:

1. Initialize floorplan (die area, core area)
2. Apply IO pin placement
3. **Place macros**
4. Run standard cell placement

### Current State

**Not supported.** The OpenRAM injector at `adapters/openram/injector.py` is a stub that returns `not_implemented`. There is no macro placement Tcl generation in any adapter.

### How to Do It Manually

**Step 1: Create a macro placement Tcl script.**

```tcl
# macro_placement.tcl — place hard macros
source "macro_placement.tcl"

# Place SRAM at bottom-left
set_placement -module sram_256x32 -location {50 50} -orientation R0 -fixed

# Place PLL at top-right
set_placement -module pll -location {200 200} -orientation R0 -fixed

# Add placement blockage over macro areas (prevents cell overlap)
create_placement_blockage -name sram_blockage -bbox {40 40 250 150} -type hard

# Report macro placements for verification
report_placement -blocks
```

**Step 2: Add the LEF/GDS/lib files to `config.mk`:**

```makefile
# Macro LEF files (technology + custom)
export ADDITIONAL_LEFS = $(wildcard $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/macros/*.lef)

# Macro GDS for stream out
export ADDITIONAL_GDS = $(wildcard $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/macros/*.gds)

# Macro liberty files for STA
export ADDITIONAL_LIBS = $(wildcard $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/macros/*.lib)
```

**Step 3: Add the macro placement to the main floorplan flow:**

Include it in the ORFS flow by either:
- Setting `PRE_PLACE_TCL` in `config.mk` (runs user Tcl before auto-placement)
- Or sourcing it manually after floorplan initialization

```makefile
export PRE_PLACE_TCL = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/macro_placement.tcl
```

### ORFS Macro Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `MACRO_PLACE_HALO` | Keep-out margin around macros (µm) | `10 10` |
| `MACRO_PLACE_CHANNEL` | Channel height between macros (µm) | `5 5` |
| `ADDITIONAL_LEFS` | Extra LEF files (macros, custom cells) | `$(wildcard .../*.lef)` |
| `ADDITIONAL_GDS` | Extra GDS files for stream out | `$(wildcard .../*.gds)` |
| `ADDITIONAL_LIBS` | Extra liberty files for macros | `$(wildcard .../*.lib)` |
| `PRE_PLACE_TCL` | Tcl script to run before placement | `$(DESIGN_HOME)/.../macro_place.tcl` |

### Generating SRAM Macros

Use **OpenRAM** (http://openram.org) to generate SRAM compilers:

```bash
# Install OpenRAM
git clone https://github.com/VLSIDA/OpenRAM.git
cd OpenRAM && pip install -e .

# Generate a 256×32 SRAM for sky130
openram -v -t "sram_256x32" -n 256 -b 32 -p sky130
```

This produces: `sram_256x32.lef`, `sram_256x32.lib`, `sram_256x32.gds`, `sram_256x32.v`.

Place these in your `macros/` directory and update `config.mk` and the macro placement Tcl.

---

## 6. Power Intent (UPF & PDN)

### What

Power intent describes how the chip is powered:
- **Power domains** — which blocks run at which voltage
- **Power grid** — strap widths, pitches, via stacks, metal layers
- **Level shifters** — between voltage domains
- **Isolation cells** — between powered-off and powered-on domains

### Where

Power intent is specified via:
1. **Unified Power Format (UPF)** — IEEE standard for power intent
2. **PDN Tcl** — OpenROAD-specific power grid configuration
3. **`config.mk` variables** — ORFS-level PDN settings

### When

- **UPF** : Required at synthesis (for power-aware synthesis) and throughout P&R
- **PDN config**: Applied during or after floorplanning, before detailed routing
- **Power analysis**: Post-route

### Current State

**Not supported.** No UPF support exists. The `configs/sky130-baseline/PDNConfig.tcl` is empty. The `analyze_power_grid` Tcl hardcodes VDD at 1.8V instead of reading the PDK's `default_voltage`.

### How to Do It Manually

**Step 1: Create a PDN Tcl configuration.**

```tcl
# pdn_config.tcl — Power distribution network configuration

# Global power net definitions
set_pdn -power_nets {VDD}
set_pdn -ground_nets {VSS}

# Standard cell power (from PDK)
add_pdn_stripe -layer met1 -width 0.5 -pitch 10 -offset 0 -nets {VDD VSS}

# Global power straps (top metal layers, wider)
add_pdn_stripe -layer met4 -width 5 -pitch 100 -offset 0 -nets {VDD VSS}
add_pdn_stripe -layer met5 -width 10 -pitch 200 -offset 0 -nets {VDD VSS}

# Power ring around the core
add_pdn_ring -layer met4 -width 5 -spacing 2 -core_offset 2 \
  -nets {VDD VSS} -extend_to periph

# Via connections between layers
add_pdn_via -layers {met1 met2} -spacing 2
add_pdn_via -layers {met2 met3} -spacing 2
add_pdn_via -layers {met3 met4} -spacing 10
add_pdn_via -layers {met4 met5} -spacing 20
```

**Step 2: Add PDN config to `config.mk`:**

```makefile
export PDN_TCL = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/pdn_config.tcl
```

**Step 3: Create an UPF file (for multi-voltage designs):**

```upf
# power_intent.upf — Unified Power Format
set_design_top my_accelerator

# Create power domains
create_power_domain PD_CORE -elements {my_accelerator}
create_power_domain PD_IO -elements {my_accelerator.io_bus}

# Define supply nets
create_supply_net VDD_CORE -domain PD_CORE
create_supply_net VDD_IO -domain PD_IO
create_supply_net VSS -domain PD_CORE

# Set voltage
set_domain_supply_net PD_CORE -primary_power_net VDD_CORE -primary_ground_net VSS
set_domain_supply_net PD_IO -primary_power_net VDD_IO -primary_ground_net VSS

# Level shifter strategy
set_level_shifter -domain PD_CORE -applies_to inputs
set_level_shifter -domain PD_IO -applies_to outputs

# Isolation strategy
set_isolation iso_core -domain PD_CORE -isolation_net VDD_CORE -clamp_value 0
```

### ORFS PDN Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `PDN_TCL` | Path to PDN configuration Tcl | `$(DESIGN_HOME)/.../pdn.tcl` |
| `FP_PDN_VPITCH` | Vertical power strap pitch (µm) | `100` |
| `FP_PDN_HPITCH` | Horizontal power strap pitch (µm) | `100` |
| `FP_PDN_VWIDTH` | Vertical power strap width (µm) | `5` |
| `FP_PDN_HWIDTH` | Horizontal power strap width (µm) | `5` |
| `FP_PDN_VOFFSET` | Vertical power strap offset | `0` |
| `FP_PDN_HOFFSET` | Horizontal power strap offset | `0` |
| `FP_PDN_VMACRO_VPITCH` | Macro vertical strap pitch | `100` |
| `FP_PDN_VMACRO_HPITCH` | Macro horizontal strap pitch | `100` |

---

## 7. Multi-Corner Liberty Libraries

### What

Liberty (`.lib`) files contain timing, power, and noise data for standard cells at specific process/voltage/temperature (PVT) conditions. A robust signoff requires at least three corners:

| Corner | Process | Voltage | Temperature | Use |
|--------|---------|---------|-------------|-----|
| Worst (slow-slow) | Slow | Minimum | Maximum | Setup timing analysis |
| Typical (tt) | Typical | Nominal | 25°C | Synthesis, optimization |
| Best (fast-fast) | Fast | Maximum | Minimum | Hold timing analysis |

### Where

Liberty files are part of the PDK installation at:

```
$PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/lib/
├── sky130_fd_sc_hd__ss_100C_1v60.lib   # worst
├── sky130_fd_sc_hd__tt_025C_1v80.lib   # typical
└── sky130_fd_sc_hd__ff_100C_1v95.lib   # best
```

### When

- **Synthesis** : Uses `LIB_SYNTH` (typically typical corner)
- **Placement/CTS/Routing** : Uses `LIB_SYNTH` for optimization
- **STA signoff**: Uses all three corners via `LIB_FASTEST` and `LIB_SLOWEST`

### Current State

The PDK models define all three corners with correct library name mappings (see `sky130.py:52-58`). However, **only the typical corner is actually used** in the pipeline — `TIMING_ANALYSIS` in the orchestrator hardcodes `"corner": {"name": "typical"}`. The `run_corner()` method exists but is not called.

### How to Enable Multi-Corner

**Step 1: Ensure all three liberty files exist in your PDK install.**

```bash
ls $PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/lib/
# Should show: ss_100C_1v60.lib, tt_025C_1v80.lib, ff_100C_1v95.lib
```

**Step 2: Define all three corners in the manifest.**

```yaml
corners:
  - { name: worst, type: worst,  process: slow,    voltage: 1.62, temperature: 125 }
  - { name: typical, type: typical, process: typical, voltage: 1.80, temperature: 25  }
  - { name: best,   type: best,   process: fast,    voltage: 1.95, temperature: -40 }
```

**Step 3: Verify the PDK's `lib_set()` maps correctly.**

The `config.mk` should set:
```makefile
export CORNER      = tt
export LIB_SYNTH   = -l $(OBJECTS_DIR)/sky130_fd_sc_hd__tt_025C_1v80.lib
export LIB_FASTEST = $(OBJECTS_DIR)/sky130_fd_sc_hd__ff_100C_1v95.lib
export LIB_SLOWEST = $(OBJECTS_DIR)/sky130_fd_sc_hd__ss_100C_1v60.lib
```

### PDK Library Name Table

| PDK | Worst | Typical | Best |
|-----|-------|---------|------|
| sky130hd | `sky130_fd_sc_hd__ss_100C_1v60.lib` | `sky130_fd_sc_hd__tt_025C_1v80.lib` | `sky130_fd_sc_hd__ff_100C_1v95.lib` |
| gf180mcuC | `gf180mcu_fd_sc_mcu9t5v0__ss_125C_1v62.lib` | `gf180mcu_fd_sc_mcu9t5v0__tt_25C_1v80.lib` | `gf180mcu_fd_sc_mcu9t5v0__ff_40C_1v95.lib` |
| sg13g2 | `sg13g2_ss_100C_1v08.lib` | `sg13g2_tt_025C_1v20.lib` | `sg13g2_ff_100C_1v32.lib` |

---

## 8. ORFS Tuning Variables

### What

gli-flow only sets a minimal subset of ORFS `config.mk` variables (DESIGN_NAME, PLATFORM, VERILOG_FILES, SDC_FILE, CORE_UTILIZATION, CORNER, LIB_*). ORFS supports **hundreds of variables** that control every aspect of the physical design flow.

### Where

Variables go in the `config.mk` generated at:

```
{orfs_root}/flow/designs/{platform}/{design_name}/config.mk
```

### When

Set at run-start, cannot be changed mid-flow.

### Key ORFS Variables Not Set by gli-flow

#### Synthesis

| Variable | Purpose | Default | Suggested |
|----------|---------|---------|-----------|
| `SYNTH_STRATEGY` | Synthesis optimization strategy | `AREA 0` | `DELAY 0` (for timing) or `DELAY 2` (aggressive) |
| `SYNTH_BUFFERING` | Enable synthesis buffer insertion | `1` | `1` |
| `SYNTH_SIZING` | Enable cell sizing during synthesis | `0` | `1` |
| `SYNTH_BIN_OPTS` | Yosys ABC command options | `"..."` | Tune for timing |
| `SYNTH_NO_FLAT` | Disable flattening | `0` | `0` (flatten for better QoR) |
| `SYNTH_SHARE_RESOURCES` | Resource sharing | `1` | `1` |
| `SYNTH_ADDER_TYPE` | Adder architecture | `YOSYS` | `YOSYS` |

#### Floorplan

| Variable | Purpose | Default | Suggested |
|----------|---------|---------|-----------|
| `DIE_AREA` | Die dimensions | auto | See floorplan section |
| `CORE_AREA` | Core area | auto | See floorplan section |
| `CORE_UTILIZATION` | Core utilization % | (30 in gli-flow) | 40–60 |
| `ASPECT_RATIO` | Core aspect ratio (H/W) | `1` | `1` |
| `MARGIN` | Core-to-die margin (µm) | `10` | `10` |
| `FP_CORE_UTIL` | Core utilization (%) | `50` | Overrides `CORE_UTILIZATION` |
| `FP_IO_HMETAL_LAYER` | Horizontal IO pin metal | `met3` | `met3` |
| `FP_IO_VMETAL_LAYER` | Vertical IO pin metal | `met4` | `met4` |

#### Placement

| Variable | Purpose | Default | Suggested |
|----------|---------|---------|-----------|
| `PL_TARGET_DENSITY` | Target placement density | `0.5` | `0.5`–`0.7` |
| `PL_TIME_DRIVEN` | Enable timing-driven placement | `1` | `1` |
| `GPL_TIMING_DRIVEN` | Enable GlobalPlacer timing opt | `0` | `1` |
| `GPL_ROUTABILITY_DRIVEN` | Enable routability-driven placer | `0` | `1` |
| `PL_BASIC_PLACEMENT` | Run basic placement (no GP) | `0` | `0` |
| `PL_SKIP_INITIAL_PLACE` | Skip initial placement | `0` | `0` |
| `PL_MACRO_HALO_X` | Macro keep-out X (µm) | `0` | `10` |
| `PL_MACRO_HALO_Y` | Macro keep-out Y (µm) | `0` | `10` |

#### CTS

| Variable | Purpose | Default | Suggested |
|----------|---------|---------|-----------|
| `CTS_CLUSTER_SIZE` | Max leaf registers per cluster | `30` | `30` |
| `CTS_CLUSTER_DISTANCE` | Max cluster distance (µm) | `50` | `50` |
| `CTS_SINK_CLUSTERING` | Enable sink clustering | `1` | `1` |
| `CTS_BUF_DISTANCE` | Max buffer-to-buffer distance | `50` | `50` |

#### Routing

| Variable | Purpose | Default | Suggested |
|----------|---------|---------|-----------|
| `ROUTING_STRATEGY` | Routing strategy (0–14) | `0` | `0` (fastest) or `14` (best QoR) |
| `GLOBAL_ROUTE_ARGS` | Global route extra args | `""` | `"-allow_congestion -dium_post_repack"` |
| `DETAILED_ROUTE_ARGS` | Detailed route extra args | `""` | `""` |
| `ROUTE_DETAILED_TCL` | Custom route Tcl overrides | `""` | `""` |

#### Power

| Variable | Purpose | Default | Suggested |
|----------|---------|---------|-----------|
| `FP_PDN_VPITCH` | Vertical power strap pitch | `100` | `100` |
| `FP_PDN_HPITCH` | Horizontal power strap pitch | `100` | `100` |
| `FP_PDN_VWIDTH` | Vertical strap width | `1.6` | `5` |
| `FP_PDN_HWIDTH` | Horizontal strap width | `1.6` | `5` |
| `FP_PDN_VOFFSET` | Vertical strap offset | `0` | `0` |
| `FP_PDN_HOFFSET` | Horizontal strap offset | `0` | `0` |
| `FP_PDN_VMACRO_VPITCH` | Macro vertical pitch override | `""` | `100` |
| `FP_PDN_VMACRO_HPITCH` | Macro horizontal pitch override | `""` | `100` |

#### DRC / Fill

| Variable | Purpose | Default | Suggested |
|----------|---------|---------|-----------|
| `FILL_INSERTION` | Enable fill cell insertion | `1` | `1` |
| `RUN_DRC` | Run DRC after routing | `1` | `1` |
| `DRC_EXCLUDE_SCREEN` | Skip DRC screen check | `0` | `0` |
| `USE_FILL_INSERTION` | Enable metal fill insertion | `1` | `1` |

### How to Add Tuning Variables

**Option A: Edit the generated `config.mk` after each `generate_config()` call.**

Not recommended — regenerated every run.

**Option B: Use a config override file (recommended).**

Create `config_override.mk` in your design directory:

```makefile
# config_override.mk — ORFS tuning overrides for my_accelerator

# Floorplan
export CORE_UTILIZATION  = 55
export DIE_AREA          = 0 0 350 350
export ASPECT_RATIO      = 1

# Synthesis
export SYNTH_STRATEGY    = DELAY 2

# Placement
export PL_TARGET_DENSITY = 0.55
export GPL_TIMING_DRIVEN = 1
export GPL_ROUTABILITY_DRIVEN = 1

# Routing
export ROUTING_STRATEGY  = 14
```

Then add this to the gli-flow pipeline by modifying the PDK's `generate_config_mk()` output (or by post-processing the generated `config.mk`):

```makefile
# Add to the end of every generated config.mk:
-include $(CURDIR)/designs/$(PLATFORM)/$(DESIGN_NICKNAME)/config_override.mk
```

---

## 9. Signoff & Verification

### What

Signoff confirms the design is ready for tapeout. The minimum checks are:

| Check | Tool | What It Validates | When |
|-------|------|-------------------|------|
| **DRC** | Magic / KLayout | Physical design rules (width, spacing, enclosure) | Post-route |
| **LVS** | Netgen | Layout vs. schematic equivalence | Post-route |
| **STA** | OpenROAD / OpenSTA | Timing meets constraints at all corners | Post-route |
| **Antenna** | OpenROAD | Antenna ratio violations | Post-route |
| **IR Drop** | OpenROAD | Power grid voltage drop analysis | Post-route |
| **EM** | OpenROAD | Electromigration reliability | Post-route |

### Current State

- **DRC** : Uses Magic (not KLayout by default). Requires Magic >= 8.3.411 for sky130A.
- **LVS** : Uses Netgen. Requires VLSI netgen, not the FEM meshing tool.
- **STA** : Multi-corner STA is defined but only typical corner runs.
- **Antenna, IR drop, EM**: All functional via post-ORFS Tcl scripts.

### What You Need to Provide

| Artifact | Required? | Provided By |
|----------|-----------|-------------|
| PDK DRC rule deck | ✅ | PDK install (magic techfile) |
| PDK LVS rule deck | ✅ | PDK install (netgen setup) |
| Liberty libs (3 corners) | ✅ | PDK install |
| Technology LEF | ✅ | PDK install |
| Extraction rules | ✅ | PDK install (for parasitic extraction) |

No user input required — these come from the PDK. But you must verify they're installed:

```bash
# sky130
ls $PDK_ROOT/sky130A/libs.tech/magic/sky130A.tech     # Magic techfile
ls $PDK_ROOT/sky130A/libs.tech/netgen/sky130A_setup.tcl  # Netgen LVS setup

# Verify DRC + LVS tools
which magic      # Must be >= 8.3.411
which netgen     # Must be VLSI netgen (not FEM)
```

---

## 10. Delivery Checklist

Use this checklist when preparing inputs for a gli-flow run:

### Before the Run

- [ ] **RTL** — All `.v`/`.sv` files compile without errors
- [ ] **Manifest** — `design_name`, `rtl_files`, `top_module`, `pdk`, `pdk_variant` set
- [ ] **SDC** — `constraints/my_design.sdc` written with clock, I/O, exceptions, design rules
- [ ] **SDC clock** — `clock_port` and `clock_period_ns` in manifest match SDC
- [ ] **Corners** — At least one corner defined (typical minimum)
- [ ] **PDK** — `gli-flow install --pdk <name>` completed successfully
- [ ] **Tools** — `yosys`, `openroad`, `magic`, `netgen` available on PATH

### Optional but Recommended

- [ ] **config_override.mk** — Floorplan, synthesis, placement, routing tuning variables
- [ ] **IO pin placement** — `pin_placement.tcl` + `IO_CONSTRAINTS` in config.mk
- [ ] **Macro LEF/lib/GDS** — For designs with SRAMs, PLLs, or hard macros
- [ ] **Macro placement Tcl** — `PRE_PLACE_TCL` script for macro locations
- [ ] **PDN config Tcl** — `PDN_TCL` for custom power grid
- [ ] **All three corners** — Slow, typical, fast liberty files verified in PDK install
- [ ] **UPF** — For multi-voltage designs

### After the Run

- [ ] **Timing met?** — Check WNS ≥ 0, TNS ≥ 0 in all corners
- [ ] **DRC clean?** — Zero DRC violations
- [ ] **LVS clean?** — Layout matches schematic
- [ ] **IR drop OK?** — Max IR drop < 10% of VDD
- [ ] **GDS produced?** — `outputs/runs/run_*/artifacts/6_final.gds` exists
- [ ] **Antenna clean?** — No antenna violations

---

## Appendix: ORFS `config.mk` Reference

### Structure of a Generated `config.mk`

```makefile
# Generated by gli-flow on 2025-01-15
export DESIGN_NAME       = my_accelerator
export DESIGN_NICKNAME   = my_accelerator
export PLATFORM          = sky130hd

export VERILOG_FILES     = $(CURDIR)/designs/src/$(DESIGN_NICKNAME)/top.v \
                           $(CURDIR)/designs/src/$(DESIGN_NICKNAME)/pe.v \
                           $(CURDIR)/designs/src/$(DESIGN_NICKNAME)/controller.v

export SDC_FILE          = $(CURDIR)/designs/$(PLATFORM)/$(DESIGN_NICKNAME)/constraint.sdc

export CORE_UTILIZATION  = 30
export TNS_END_PERCENT   = 100

# Corner: typical
export CORNER            = tt
export LIB_SYNTH         = -l $(OBJECTS_DIR)/sky130_fd_sc_hd__tt_025C_1v80.lib
export LIB_FASTEST       = $(OBJECTS_DIR)/sky130_fd_sc_hd__ff_100C_1v95.lib
export LIB_SLOWEST       = $(OBJECTS_DIR)/sky130_fd_sc_hd__ss_100C_1v60.lib

# Include user overrides (create this file for tuning)
-include $(CURDIR)/designs/$(PLATFORM)/$(DESIGN_NICKNAME)/config_override.mk
```

### Variable Categories

| Category | Key Variables |
|----------|--------------|
| **Design identity** | `DESIGN_NAME`, `DESIGN_NICKNAME`, `PLATFORM` |
| **Input files** | `VERILOG_FILES`, `SDC_FILE`, `ADDITIONAL_LEFS`, `ADDITIONAL_LIBS`, `ADDITIONAL_GDS` |
| **Floorplan** | `DIE_AREA`, `CORE_AREA`, `CORE_UTILIZATION`, `ASPECT_RATIO`, `MARGIN`, `FP_*` |
| **IO** | `IO_CONSTRAINTS`, `FP_IO_*` |
| **Synthesis** | `SYNTH_*` |
| **Placement** | `PL_TARGET_DENSITY`, `PL_*`, `GPL_*` |
| **CTS** | `CTS_*` |
| **Routing** | `ROUTING_STRATEGY`, `ROUTING_*`, `GLOBAL_ROUTE_*`, `DETAILED_ROUTE_*` |
| **Power** | `PDN_TCL`, `FP_PDN_*` |
| **Timing** | `CORNER`, `LIB_SYNTH`, `LIB_FASTEST`, `LIB_SLOWEST`, `TNS_END_PERCENT` |
| **Fill/DRC** | `FILL_INSERTION`, `USE_FILL_INSERTION`, `RUN_DRC` |
| **Custom hooks** | `PRE_PLACE_TCL`, `PRE_CTS_TCL`, `POST_CTS_TCL`, `PDN_TCL` |

### Default ORFS Source

The authoritative reference for all ORFS variables is:
```
{orfs_root}/flow/Makefile
{orfs_root}/flow/scripts/*.tcl
```
