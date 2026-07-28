# SDC Constraints Reference

> Complete guide to writing Synopsys Design Constraints (`.sdc`) files for gli-flow RTL-to-GDS runs.

---

## Table of Contents

1. [Overview](#overview)
2. [SDC Command Reference](#sdc-command-reference)
3. [Clock Constraints](#clock-constraints)
4. [I/O Timing Constraints](#io-timing-constraints)
5. [Design Rule Constraints](#design-rule-constraints)
6. [Timing Exceptions](#timing-exceptions)
7. [Operating Conditions & Multi-Corner](#operating-conditions--multi-corner)
8. [PVT Corner Interaction](#pvt-corner-interaction)
9. [SDC in the Pipeline](#sdc-in-the-pipeline)
10. [Multi-Clock & Clock Groups](#multi-clock--clock-groups)
11. [Per-PDK Library Names](#per-pdk-library-names)
12. [Troubleshooting](#troubleshooting)
13. [Example Gallery](#example-gallery)

---

## Overview

Synopsys Design Constraints (SDC) is the industry-standard Tcl-based format for specifying timing, power, and design rule constraints for digital ASIC flows. gli-flow passes your SDC file through:

```
gli_manifest.yaml → openroad_adapter.py → constraint.sdc → ORFS config.mk → OpenROAD read_sdc
```

The SDC is applied at every pipeline stage: synthesis, floorplanning, placement, CTS, routing, post-route optimization, and timing signoff.

### File Format

- **Extension:** `.sdc`
- **Syntax:** Tcl (commands, variables, comments)
- **Comments:** `#` to end of line
- **Line continuation:** `\` at line end
- **Lists:** `{item1 item2 item3}`
- **Variables:** `set VAR value` → `$VAR`

---

## SDC Command Reference

### Clock Commands

| Command | SDC Version | Purpose |
|---------|-------------|---------|
| `create_clock` | 1.0+ | Define a primary clock |
| `create_generated_clock` | 1.0+ | Define a derived/generated clock |
| `set_clock_groups` | 1.8+ | Group clocks (async/exclusive/physically exclusive) |
| `set_clock_latency` | 1.0+ | Model clock source or network latency |
| `set_clock_transition` | 1.0+ | Model clock slew |
| `set_clock_uncertainty` | 1.0+ | Model clock jitter, PLL noise, margin |
| `set_clock_sense` | 1.8+ | Specify clock sense (positive/negative/stop) |
| `remove_clock_groups` | 1.9+ | Remove a clock grouping |
| `set_clock_gating_check` | 1.5+ | Setup/hold check for clock-gating logic |

### I/O Constraint Commands

| Command | SDC Version | Purpose |
|---------|-------------|---------|
| `set_input_delay` | 1.0+ | Input path delay relative to clock |
| `set_output_delay` | 1.0+ | Output path delay relative to clock |
| `set_load` | 1.0+ | Capacitive load on output ports |
| `set_driving_cell` | 1.0+ | Drive characteristic of input ports |
| `set_input_transition` | 1.5+ | Directly set input slew |
| `set_fanout_load` | 1.0+ | Fanout load on output ports |

### Design Rule Commands

| Command | SDC Version | Purpose |
|---------|-------------|---------|
| `set_max_transition` | 1.0+ | Maximum allowable transition/slew time |
| `set_max_capacitance` | 1.0+ | Maximum allowable capacitance |
| `set_max_fanout` | 1.0+ | Maximum allowable fanout |
| `set_min_capacitance` | 1.0+ | Minimum allowable capacitance |

### Timing Exception Commands

| Command | SDC Version | Purpose |
|---------|-------------|---------|
| `set_false_path` | 1.0+ | Exclude paths from STA (async resets, test logic) |
| `set_multicycle_path` | 1.0+ | Paths requiring >1 clock cycle |
| `set_max_delay` | 1.0+ | Override max path delay |
| `set_min_delay` | 1.0+ | Override min path delay |
| `set_case_analysis` | 1.0+ | Pin/port value for mode analysis |
| `set_disable_timing` | 1.0+ | Disable timing arcs on cells/pins |
| `group_path` | 1.0+ | Group paths for reporting |
| `reset_path` | 1.5+ | Remove delay constraints on paths |

### Operating Condition Commands

| Command | SDC Version | Purpose |
|---------|-------------|---------|
| `set_operating_conditions` | 1.0+ | Select PVT library for analysis |
| `set_analysis_mode` | 1.8+ | Set single/best-case/worst-case/on-chip-variation mode |
| `set_timing_derate` | 1.8+ | Apply OCV derating factors |
| `set_sense` | 1.8+ | Set wire load/operating mode sense |

---

## Clock Constraints

### Primary Clock — `create_clock`

```sdc
create_clock -name <name> -period <ns> [-waveform {rise fall}] [source_objects]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `-name` | No | Clock name for STA (defaults to port name) |
| `-period` | Yes | Clock period in the units specified by `set_units` (default: ns) |
| `-waveform` | No | Rise and fall edges: `{rise_time fall_time}` (default: `{0 period/2}`) |
| `-add` | No | Add a second clock to the same source object |

**Examples:**

```sdc
# 100 MHz clock with 50% duty cycle
create_clock -name clk -period 10.0 [get_ports clk]

# 50 MHz with 40% duty cycle (6ns high, 4ns low at 20ns period)
create_clock -name slow_clk -period 20.0 -waveform {6 16} [get_ports slow_clk]

# Two clocks on same port (for testing)
create_clock -name func_clk -period 10.0 [get_ports clk]
create_clock -name test_clk -period 100.0 [get_ports clk] -add
```

### Generated Clock — `create_generated_clock`

```sdc
create_generated_clock -name <name> -source <clk_pin> [divide_by|-multiply_by|-edges] [source_objects]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `-name` | No | Clock name |
| `-source` | Yes | Clock source pin/port |
| `-divide_by` | No | Clock division factor |
| `-multiply_by` | No | Clock multiplication factor |
| `-edges` | No | Explicit edge list: `{e1 e2 e3}` |
| `-edge_shift` | No | Shift for each edge: `{s1 s2 s3}` |
| `-duty_cycle` | No | Duty cycle in percent (default: 50) |
| `-invert` | No | Invert the generated clock |
| `-combinational` | No | Generated by combinational logic (no register) |

**Examples:**

```sdc
# Divide by 2
create_generated_clock -name clk_div2 -source [get_ports clk] -divide_by 2 [get_pins div_reg/Q]

# Multiply by 4 (PLL)
create_generated_clock -name core_clk -source [get_ports ref_clk] -multiply_by 4 [get_pins pll/out]

# Edge-specific (non-50% duty cycle)
create_generated_clock -name ddr_clk -source [get_ports clk] \
  -edges {1 3 5} -edge_shift {0 0.5 1.0} [get_pins ddr_ff/Q]
```

### Clock Latency, Transition, and Uncertainty

```sdc
# Source latency (from PLL/package to clock port pin)
set_clock_latency -source 0.5 [get_clocks clk]

# Network latency (from clock port to register clock pins)
set_clock_latency 1.0 [get_clocks clk]

# Source latency, min/max for hold/setup
set_clock_latency -source -max 0.8 [get_clocks clk]
set_clock_latency -source -min 0.3 [get_clocks clk]

# Clock transition (slew) at the waveform origin
set_clock_transition 0.3 [get_clocks clk]
set_clock_transition -rise 0.25 [get_clocks clk]
set_clock_transition -fall 0.2 [get_clocks clk]

# Clock uncertainty (jitter + margin)
set_clock_uncertainty -setup 0.3 [get_clocks clk]
set_clock_uncertainty -hold  0.1 [get_clocks clk]

# Inter-clock uncertainty (clock domain crossing)
set_clock_uncertainty -from clk_a -to clk_b -setup 0.8 [get_clocks clk_a]
```

**Recommended values for typical PDKs at 10ns period:**

| PDK | Uncertainty (setup) | Uncertainty (hold) | Transition | Network Latency |
|-----|-------------------|-------------------|------------|-----------------|
| sky130 (sky130hd) | 0.3–0.5 ns | 0.1 ns | 0.2–0.3 ns | 0.5–1.0 ns |
| gf180mcu | 0.4–0.6 ns | 0.15 ns | 0.3–0.5 ns | 0.5–1.5 ns |
| ihp-sg13g2 | 0.2–0.4 ns | 0.1 ns | 0.15–0.25 ns | 0.3–0.8 ns |

---

## I/O Timing Constraints

### set_input_delay

```sdc
set_input_delay -clock <clock_name> [-max|-min] [-rise|-fall] <delay> [port_list]
```

Models the external delay from the clock source to the input port pin.

```sdc
# Broad I/O delays (50% of period for initial estimation)
set_input_delay -clock clk 5.0 [all_inputs]

# Max/min for setup/hold analysis
set_input_delay -clock clk -max 5.0 [all_inputs]
set_input_delay -clock clk -min 0.5 [all_inputs]

# Per-port with rise/fall specificity
set_input_delay -clock clk -max -rise 4.5 [get_ports data_in]
set_input_delay -clock clk -max -fall 5.0 [get_ports data_in]
set_input_delay -clock clk -min -rise 0.3 [get_ports data_in]
```

### set_output_delay

```sdc
set_output_delay -clock <clock_name> [-max|-min] [-rise|-fall] <delay> [port_list]
```

Models the external delay from the output port pin to the receiving register.

```sdc
# Broad output delays
set_output_delay -clock clk 5.0 [all_outputs]

# Max/min
set_output_delay -clock clk -max 5.0 [all_outputs]
set_output_delay -clock clk -min 0.5 [all_outputs]

# Per-port with reference to clock edge
set_output_delay -clock clk -max 3.5 [get_ports result_valid]
set_output_delay -clock clk -clock_fall -max 3.0 [get_ports ddr_data]
```

### set_load

```sdc
set_load [-min|-max] [-pin_load|-wire_load] <value> [objects]
```

```sdc
# Capacitive load on outputs
set_load 0.05 [all_outputs]

# Per-port
set_load 0.1 [get_ports data_bus]
set_load -min 0.02 [get_ports data_bus]
```

### set_driving_cell

```sdc
set_driving_cell [-lib_cell <cell>] [-library <lib>] [-pin <pin>] [-from_pin <pin>] \
                 [-input_transition_rise <t>] [-input_transition_fall <t>] [port_list]
```

Models the drive strength of the off-chip driver connected to an input port.

```sdc
# Drive input ports with a specific library cell
set_driving_cell -lib_cell BUF_X2 [all_inputs]

# With explicit input transition (bypasses cell lookup)
set_input_transition -rise 0.5 [get_ports rst_n]
set_input_transition -fall 0.3 [get_ports rst_n]
```

---

## Design Rule Constraints

```sdc
# Maximum transition time at any pin
set_max_transition 0.5 [current_design]

# Maximum capacitance at any pin
set_max_capacitance 0.30 [current_design]

# Maximum fanout at any output pin
set_max_fanout 16 [current_design]

# Minimum capacitance (for hold fixing)
set_min_capacitance 0.01 [current_design]
```

**Design rule priority in OpenROAD:**

1. Library cell constraints (from `.lib`) — highest priority
2. SDC `set_max_transition` / `set_max_capacitance` — overrides library defaults
3. ORFS config `MAX_TRANSITION` / `MAX_CAPACITANCE` — overridden by SDC

---

## Timing Exceptions

### set_false_path

```sdc
set_false_path [-setup|-hold] [-rise|-fall] [-from <list>] [-to <list>] [-through <list>]
```

Excludes paths from STA entirely.

```sdc
# Async reset path
set_false_path -reset_path [get_ports rst_n]

# Cross-clock domain paths (when synchronizers are used)
set_false_path -from [get_clocks clk_a] -to [get_clocks clk_b]
set_false_path -from [get_clocks clk_b] -to [get_clocks clk_a]

# Test mode paths
set_false_path -from [get_pins scan_enable_reg/Q] -to [get_pins functional_data_reg/D]

# Through specific cells
set_false_path -through [get_pins sync_cell/*/Q]

# Specific port-to-port
set_false_path -from [get_ports test_mode] -to [all_outputs]
```

### set_multicycle_path

```sdc
set_multicycle_path <n> [-setup|-hold] [-rise|-fall] [-from <list>] [-to <list>] [-through <list>]
```

Specifies that a path requires more than one clock cycle.

```sdc
# 2-cycle setup path, hold remains at 1 cycle
set_multicycle_path 2 -setup -from [get_pins slow_reg/Q] -to [get_pins fast_reg/D]
set_multicycle_path 1 -hold  -from [get_pins slow_reg/Q] -to [get_pins fast_reg/D]

# 3-cycle path
set_multicycle_path 3 -from [get_pins counter_reg/Q] -to [get_pins display_reg/D]
```

**Important:** When using `set_multicycle_path`, always specify both `-setup` and `-hold` values. The hold check defaults to `N-1` cycles after the setup value. Without an explicit `-hold`, hold analysis may be too relaxed.

### set_max_delay / set_min_delay

```sdc
# Override maximum path delay for specific paths
set_max_delay 5.0 -from [get_ports start] -to [get_ports done]

# Override minimum path delay
set_min_delay 1.0 -from [get_ports] -to [get_ports]

# Combinational (pin-to-pin) delay
set_max_delay 3.0 -from [get_ports a] -to [get_ports b] -rise
```

### group_path

```sdc
# Group paths for reporting
group_path -name reg_to_reg -weight 1.0
group_path -name inputs -from [all_inputs]
group_path -name outputs -to [all_outputs]
group_path -name critical -critical_range 2.0 -weight 5.0
```

---

## Operating Conditions & Multi-Corner

### Single Corner

```sdc
set_operating_conditions -library sky130_fd_sc_hd__tt_025C_1v80 \
                         tt_025C_1v80
```

### Multi-Corner (Setup/Hold Min-Max)

```sdc
set_operating_conditions -max_library sky130_fd_sc_hd__ss_100C_1v60 \
                         -min_library sky130_fd_sc_hd__ff_100C_1v95 \
                         -max ss_100C_1v60 \
                         -min ff_100C_1v95
```

The `-max` library is used for **setup** (slow-slow) and `-min` for **hold** (fast-fast).

---

## PVT Corner Interaction

When the manifest defines multiple corners, gli-flow runs STA once per corner:

```yaml
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

Each corner run uses the **same SDC** but different liberty libraries (mapped by the PDK's `config.mk`). This means:

- The clock period constraint is identical across all corners
- The timing engine uses the appropriate PVT library for each corner
- The SDC's `set_operating_conditions` should either be omitted (let the tool pick the correct library per corner) or match the library names per PDK

**Recommended approach:** Omit `set_operating_conditions` from the SDC when running multi-corner, and let OpenROAD/ORFS set it per-corner via `config.mk`.

---

## SDC in the Pipeline

### Stage-by-Stage SDC Usage

| Pipeline Stage | SDC Usage | ORFS Script Action |
|---------------|-----------|-------------------|
| SYNTHESIS | `read_sdc` | Yosys reads SDC for timing-driven synthesis |
| FLOORPLANNING | `read_sdc` | OpenROAD reads SDC for IO planning |
| PLACEMENT | `read_sdc` | Timing-driven placement uses SDC |
| CTS | `read_sdc` | Clock tree synthesis respects clock constraints |
| ROUTING | `read_sdc` | Global/detail routing uses SDC for timing-driven routing |
| PRO | `read_sdc results/6_final.sdc` | Post-route optimization re-reads final SDC |
| SI_ANALYSIS | `read_sdc results/6_final.sdc` | Signal integrity analysis |
| TIMING_ANALYSIS | `read_sdc results/6_final.sdc` | Multi-corner STA signoff |
| D2D_INTERFACE_CHECK | `read_sdc results/6_final.sdc` | Die-to-die timing check |

### Auto-Generated Fallback

If the manifest has no `constraints` list, the adapter generates:

```sdc
create_clock -name clk -period {clock_period_ns} [get_ports {clock_port}]
set_input_delay -clock clk 2.0 [all_inputs]
set_output_delay -clock clk 2.0 [all_outputs]
```

This is intentionally minimal — enough for testing with `--mock` but insufficient for real silicon.

### Artifact Output

After a successful run, the SDC used during the final stages is available at:

```
outputs/runs/run_<timestamp>_<design>/
├── results/6_final.sdc          # SDC used for post-route STA
├── artifacts/6_final.sdc        # Same, in artifacts
└── config.json                  # Full run config including constraints path
```

---

## Multi-Clock & Clock Groups

### Asynchronous Clock Domains

```sdc
# Define both clocks
create_clock -name clk_a -period 10.0 [get_ports clk_a]
create_clock -name clk_b -period 40.0 [get_ports clk_b]

# Group as asynchronous (disables all inter-domain timing)
set_clock_groups -asynchronous \
  -group [get_clocks clk_a] \
  -group [get_clocks clk_b]

# Alternatively, use false paths for specific CDC paths
set_false_path -from [get_clocks clk_a] -to [get_clocks clk_b]
set_false_path -from [get_clocks clk_b] -to [get_clocks clk_a]
```

### Logically Exclusive Clocks

```sdc
# Functional vs. test clock (never active simultaneously)
create_clock -name func_clk -period 10.0 [get_ports clk]
create_clock -name test_clk -period 100.0 [get_ports clk] -add

set_clock_groups -logically_exclusive \
  -group [get_clocks func_clk] \
  -group [get_clocks test_clk]
```

### Physically Exclusive Clocks

```sdc
# Clocks that cannot physically exist at the same location
create_clock -name pll_out -period 5.0 [get_pins pll/clk_out]
create_clock -name bypass -period 10.0 [get_pins mux/clk_bypass]

set_clock_groups -physically_exclusive \
  -group [get_clocks pll_out] \
  -group [get_clocks bypass]
```

---

## Per-PDK Library Names

The `-library` argument in `set_operating_conditions` must match the liberty library names in the PDK's `.lib` files.

### sky130 (sky130hd)

| Corner | Liberty Library Name | Voltage | Temperature |
|--------|---------------------|---------|-------------|
| Worst | `sky130_fd_sc_hd__ss_100C_1v60` | 1.62V | 125°C |
| Typical | `sky130_fd_sc_hd__tt_025C_1v80` | 1.80V | 25°C |
| Best | `sky130_fd_sc_hd__ff_100C_1v95` | 1.95V | -40°C |

### gf180mcu

| Corner | Liberty Library Name | Voltage | Temperature |
|--------|---------------------|---------|-------------|
| Worst | `gf180mcu_fd_sc_mcu9t5v0__ss_125C_1v62` | 1.62V | 125°C |
| Typical | `gf180mcu_fd_sc_mcu9t5v0__tt_025C_1v80` | 1.80V | 25°C |
| Best | `gf180mcu_fd_sc_mcu9t5v0__ff_125C_1v95` | 1.95V | -40°C |

### ihp-sg13g2

| Corner | Liberty Library Name | Voltage | Temperature |
|--------|---------------------|---------|-------------|
| Worst | `sg13g2_ss_100C_1v08` | 1.08V | 125°C |
| Typical | `sg13g2_tt_025C_1v20` | 1.20V | 25°C |
| Best | `sg13g2_ff_100C_1v32` | 1.32V | -40°C |

---

## Troubleshooting

### SDC Not Applied

```
[WARNING] Could not find port 'clk'
```

**Cause:** `create_clock -name clk -period 10.0 [get_ports clk]` references a port that doesn't exist in the synthesized netlist. The port name in the SDC must match the top-level module port name in the RTL exactly (case-sensitive).

**Fix:** Verify the clock port name:
```bash
grep -i "module.*(.*clk" rtl/*.v rtl/*.sv
```

### Library Not Found

```
[ERROR] Library 'sky130_fd_sc_hd__tt_025C_1v80' not found
```

**Cause:** The library name in `set_operating_conditions -library` doesn't match any `.lib` file linked by the PDK.

**Fix:** List the available libraries:
```bash
ls $PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/lib/
```
Then update the SDC with the correct name.

### Timing Not Closing — Overly Optimistic

**Cause:** Missing `set_clock_uncertainty` and/or too-aggressive I/O delays.

**Fix:** Add realistic margins:
```sdc
set_clock_uncertainty -setup 0.5 [get_clocks clk]
set_input_delay -clock clk -max 5.5 [all_inputs]  # 55% of 10ns period
```

### Zero Slack on All Paths

**Cause:** No clock constraint applied — all paths are unconstrained.

**Fix:** Verify the SDC was copied into the run:
```bash
grep "create_clock" outputs/runs/run_*/results/6_final.sdc
```

### Timing Not Improving After SDC Change

**Cause:** The old SDC was cached. ORFS may not regenerate results if the SDC changes mid-flow.

**Fix:** Clean and re-run:
```bash
rm -rf outputs/runs/run_${DESIGN}_*
gli-flow run .
```

### Multi-Corner SDC Conflicts

If `set_operating_conditions` references a single library but the manifest defines multiple corners, only the first corner may get the correct library. **Either omit `set_operating_conditions` for multi-corner flows, or ensure the library exists in all corner configs.**

---

## Example Gallery

### 1. Minimal — 8-bit Counter

File: `examples/counter/counter.sdc` (4 lines)

```sdc
create_clock -name clk -period 10.000 [get_ports clk]
set_input_delay -clock clk 2.0 [get_ports reset]
set_output_delay -clock clk 2.0 [get_ports count]
set_load 0.05 [all_outputs]
```

### 2. Standard — GCD Calculator

File: `examples/gcd/gcd.sdc` (6 lines)

```sdc
create_clock -name clk -period 10.000 [get_ports clk]
set_input_delay -clock clk 2.0 [get_ports "a b"]
set_output_delay -clock clk 2.0 [get_ports "gcd_out"]
set_load 0.05 [all_outputs]
set_fanout_load 4 [all_outputs]
```

### 3. Full — UART

File: `examples/uart/constraints/top.sdc` (14 lines)

```sdc
set PERIOD 10.0
create_clock -name clk -period $PERIOD [get_ports clk]
set_clock_uncertainty 0.5 [get_clocks clk]
set_clock_transition  0.3 [get_clocks clk]
set_clock_latency     1.0 [get_clocks clk]
set_input_delay  -clock clk 5.0 [all_inputs]
set_output_delay -clock clk 5.0 [all_outputs]
set_false_path -reset_path [get_ports rst_n]
set_max_fanout 8 [current_design]
set_max_transition 0.5 [current_design]
```

### 4. Production — 4x4 Systolic Array

File: `examples/systolic_array/constraints/top.sdc` (27 lines)

```sdc
set PERIOD 10.0
create_clock -name clk -period $PERIOD [get_ports clk]
set_clock_uncertainty 0.5 [get_clocks clk]
set_clock_transition  0.3 [get_clocks clk]
set_clock_latency     1.0 [get_clocks clk]
set_input_delay  -clock clk 5.0 [all_inputs]
set_output_delay -clock clk 5.0 [all_outputs]
set_false_path -reset_path [get_ports rst_n]
set_max_fanout 8 [current_design]
set_max_transition 0.5 [current_design]
set_operating_conditions -max_library sky130_fd_sc_hd__ss_100C_1v60 \
                         -min_library sky130_fd_sc_hd__ff_100C_1v95 \
                         -max ss_100C_1v60 \
                         -min ff_100C_1v95
```

### 5. TinyTapeout — Shuttle Template

File: auto-generated by `scaffold_tinytapeout_design()`

```sdc
create_clock -name clk -period 10.0 [get_ports clk]
set_clock_uncertainty 1.0 [get_clocks clk]
set_input_delay -clock clk -max 2.0 [get_ports ena]
set_input_delay -clock clk -max 2.0 [get_ports rst_n]
set_input_delay -clock clk -max 2.0 [get_ports ui_in*]
set_input_delay -clock clk -max 2.0 [get_ports uio_in*]
set_output_delay -clock clk -max 2.0 [get_ports uo_out*]
set_output_delay -clock clk -max 2.0 [get_ports uio_out*]
set_output_delay -clock clk -max 2.0 [get_ports uio_oe*]
```
