# RISC-V Constraints Guide for GLI-FLOW

## Overview

The SDC (Synopsys Design Constraints) file tells the synthesis and timing analysis tools what the design's timing requirements are. For PicoRV32, we constrain the clock and the external memory interface.

## Required: `create_clock`

Every design needs at least one clock constraint.

```sdc
create_clock -name clk -period 20.0 [get_ports clk]
```

| Field | Meaning | Required |
|-------|---------|----------|
| `-name` | Logical clock name | Recommended |
| `-period` | Clock period in nanoseconds | Yes |
| `[get_ports clk]` | Clock source port | Yes |
| `-waveform` | Rise/fall times (default: 0/period/2) | Optional |

## Recommended: I/O Delays

Input and output delays model the external timing environment.

```sdc
# Input delays (memory interface)
set_input_delay -clock clk -max 2.0 [get_ports {mem_ready mem_rdata}]
set_input_delay -clock clk -min 0.5 [get_ports {mem_ready mem_rdata}]

# Output delays (memory interface)
set_output_delay -clock clk -max 4.0 [get_ports {mem_valid mem_instr mem_addr mem_wdata mem_wstrb}]
set_output_delay -clock clk -min 1.0 [get_ports {mem_valid mem_instr mem_addr mem_wdata mem_wstrb}]
```

| Field | Meaning | Required |
|-------|---------|----------|
| `-max` | Maximum delay (setup check) | Recommended |
| `-min` | Minimum delay (hold check) | Recommended |
| `$clock` | Related clock | Yes |
| `$ports` | Target ports | Yes |

### I/O Delay Reasoning for PicoRV32

- Memory interface is the primary external path
- mem_ready/mem_rdata: inputs from memory (can arrive late)
- mem_addr/mem_wdata: outputs to memory (must arrive in time)
- 20 ns period: 2 ns input + 16 ns internal + 2 ns output margin

## Recommended: False Paths

```sdc
# PCPI interface (unused in this configuration)
set_false_path -from [get_ports {pcpi_wr pcpi_rd pcpi_wait pcpi_ready}]

# IRQ interface (unused in this configuration)
set_false_path -from [get_ports {irq}]

# Trace interface (debug only)
set_false_path -from [get_ports {trace_data trace_valid}]

# Formal verification interface (debug only)
set_false_path -from [get_ports {rvfi_*}]
```

### Why False Paths?

PCPI, IRQ, Trace, and Formal interfaces are not connected to any external timing path in this simple validation setup. Timing on these paths does not affect correct operation.

## Advanced: Multicycle Paths

Not required for PicoRV32 at 50 MHz. Would be needed if:
- External memory requires multiple cycles
- PCPI co-processor needs multi-cycle operations

```sdc
# Example: 2-cycle memory read
set_multicycle_path -setup 2 -from [get_ports mem_ready] -to [all_registers]
```

## Minimum Valid SDC

The absolute minimum for GLI-FLOW to run:

```sdc
create_clock -name clk -period 20.0 [get_ports clk]
```

## Recommended SDC

```sdc
create_clock -name clk -period 20.0 [get_ports clk]

set_input_delay -clock clk -max 2.0 [get_ports {mem_ready mem_rdata}]
set_input_delay -clock clk -min 0.5 [get_ports {mem_ready mem_rdata}]

set_output_delay -clock clk -max 4.0 [get_ports {mem_valid mem_instr mem_addr mem_wdata mem_wstrb}]
set_output_delay -clock clk -min 1.0 [get_ports {mem_valid mem_instr mem_addr mem_wdata mem_wstrb}]
```

## Checking Your SDC

GLI-FLOW validates the SDC during the SYNTHESIS stage. Common errors:
- Clock port name mismatch between RTL and SDC
- Invalid port names (use `get_ports` with correct names)
- Missing clock definition (tools will issue warnings)
