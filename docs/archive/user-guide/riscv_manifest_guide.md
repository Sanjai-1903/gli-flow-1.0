# RISC-V Manifest Guide for GLI-FLOW

## Overview

`gli_manifest.yaml` is the project configuration file. It tells GLI-FLOW what to build, how to build it, and what corners to analyze.

## Field Reference

### `design_name`
- **Meaning:** Human-readable name for this design
- **Required:** No (defaults to top_module)
- **Example:** `picorv32`

### `rtl_files`
- **Meaning:** List of RTL source files (Verilog/SystemVerilog)
- **Required:** Yes
- **Format:** List of paths relative to manifest parent directory
- **Example:**
```yaml
rtl_files:
  - examples/picorv32/rtl/picorv32.v
```

### `top_module`
- **Meaning:** Name of the top-level module
- **Required:** Yes (auto-detected if not provided and unique)
- **Example:** `picorv32`

### `backend`
- **Meaning:** EDA backend to use
- **Required:** No (default: openroad)
- **Values:** `openroad`, `librelane`
- **Example:** `openroad`

### `pdk`
- **Meaning:** Process Design Kit name
- **Required:** Yes
- **Values:** `sky130`, `gf180mcu`, `ihp130`
- **Example:** `sky130`

### `pdk_variant`
- **Meaning:** PDK variant/stackup
- **Required:** No
- **Values:** `sky130A`, `sky130B`
- **Example:** `sky130A`

### `clock_port`
- **Meaning:** Name of the clock port in the design
- **Required:** Yes
- **Example:** `clk`

### `clock_period_ns`
- **Meaning:** Target clock period in nanoseconds
- **Required:** Yes
- **Example:** `20.0` (50 MHz)

### `constraints`
- **Meaning:** List of SDC constraint file paths
- **Required:** Recommended
- **Example:**
```yaml
constraints:
  - examples/picorv32/constraints/picorv32.sdc
```

### `threads`
- **Meaning:** CPU threads for parallel operations
- **Required:** No
- **Default:** auto-detected
- **Example:** `4`

### `memory_mb`
- **Meaning:** Memory limit in megabytes
- **Required:** No
- **Example:** `8000`

### `corners`
- **Meaning:** PVT corners for analysis
- **Required:** No (uses PDK defaults)
- **Format:** List of corner definitions

Each corner:
| Field | Meaning | Required |
|-------|---------|----------|
| `name` | Corner name | Yes |
| `type` | Corner type (worst/typical/best) | No |
| `process` | Process corner (slow/typical/fast) | No |
| `voltage` | Supply voltage | No |
| `temperature` | Junction temperature (Celsius) | No |

### `include_paths`
- **Meaning:** Verilog include directories
- **Required:** No (auto-detected)
- **Example:**
```yaml
include_paths:
  - examples/picorv32/rtl
```

### `parameters`
- **Meaning:** Verilog parameters to override
- **Required:** No
- **Example:**
```yaml
parameters:
  ENABLE_COUNTERS: 1
  ENABLE_MUL: 0
```

## Complete Example

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
parameters:
  ENABLE_COUNTERS: 1
  ENABLE_COUNTERS64: 1
  ENABLE_REGS_16_31: 1
  ENABLE_REGS_DUALPORT: 1
  ENABLE_MUL: 0
  ENABLE_DIV: 0
  ENABLE_IRQ: 0
  COMPRESSED_ISA: 0
```

## Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Manifest validation failed` | Missing required field | Check YAML syntax and required fields |
| `RTL files not found` | Wrong path in rtl_files | Paths relative to manifest parent |
| `PDK not found` | Missing PDK installation | Run `gli-flow install` |
| `Top module not found` | Module name mismatch | Check top_module matches RTL |
