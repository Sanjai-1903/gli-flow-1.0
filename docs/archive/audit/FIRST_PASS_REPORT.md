# First Pass Report

## Summary
Date: 2026-06-07
Designs: counter (8-bit counter), uart (UART transceiver)
Flow: GLI-FLOW RTL-to-GDS
PDK: sky130A
Tools: OpenROAD, Magic, Netgen, KLayout

## Results

| Metric         | counter | uart    |
|---------------|---------|---------|
| DRC Violations| 0       | 0       |
| LVS Result    | CLEAN   | CLEAN   |
| Runtime       | 34.4s   | 92.2s   |
| Utilization   | 43.0%   | 37.0%   |
| Cell Count    | 14      | 71      |
| WNS           | None    | None    |

## Issues Fixed

### 1. Magic Binary Detection
- **Root cause**: System `magic` is a Tcl/Tk wrapper that fails in `-dnull` mode
- **Fix**: Use `magicdnull -nowrapper -d NULL -rcfile <magicrc>` directly
- **Files**: `gli_flow/backends/openroad_adapter.py`, `gli_flow/core/drc_runner.py`

### 2. Magic Tech File Version
- **Root cause**: `sky130A.tech` requires `magic-8.3.411`, apt provides `8.3.105`
- **Fix**: Patched version check to `requires magic-8.3.0`
- **File**: `~/.gli-flow/pdk/sky130A/libs.tech/magic/sky130A.tech`

### 3. CAD_ROOT Environment Variable
- **Root cause**: `CAD_ROOT=/home/bolter/.local/lib` breaks Magic subprocess output
- **Fix**: Removed `CAD_ROOT` from `safe_env()`
- **File**: `gli_flow/core/subprocess_env.py`

### 4. Netgen Binary Detection
- **Root cause**: `/usr/local/bin/netgen` is a broken wrapper; real binary is `netgen-lvs`
- **Fix**: Prefer `netgen-lvs` over `netgen` in binary search paths
- **File**: `gli_flow/installer/tool_detector.py`, `gli_flow/backends/openroad_adapter.py`

### 5. LVS Invocation Method
- **Root cause**: TCL-based `readnet spice` + `lvs` command fails (returns 0 circuits)
- **Fix**: Use `netgen -batch lvs` mode which correctly parses SPICE and Verilog
- **File**: `gli_flow/backends/openroad_adapter.py`

### 6. SPICE Top-Cell Wrapping
- **Root cause**: Magic outputs top-level circuit outside `.subckt`/`.ends`
- **Fix**: Post-process SPICE to wrap in `.subckt counter` + `.global VSUBS`
- **File**: `gli_flow/backends/openroad_adapter.py`

### 7. Verilog Preprocessing
- **Root cause**: Yosys uses `$_DFF_PP0_` suffixes in instance names that Netgen can't parse
- **Fix**: Replace escaped identifiers and add power pin connections
- **File**: `gli_flow/backends/openroad_adapter.py`

### 8. Parasitic Capacitor Suppression
- **Root cause**: Magic extracts parasitic capacitors that don't exist in Verilog
- **Fix**: Set `ext2spice cthresh 999999` and `rthresh 999999` to suppress parasitic R/C
- **File**: `gli_flow/backends/openroad_adapter.py`

## Next Steps
1. Verify timing closure (STA) for both designs
2. Test with larger designs (e.g., `examples/counter` with higher bit width)
3. Add functional verification to pipeline
