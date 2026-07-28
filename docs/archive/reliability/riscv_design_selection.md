# RISC-V Design Selection for GLI-FLOW Certification

## Selection Summary

**Selected Core:** PicoRV32
**Repository:** https://github.com/YosysHQ/picorv32
**License:** ISC (MIT/BSD-equivalent)
**Author:** Claire Xenia Wolf (YosysHQ)
**Language:** Verilog (IEEE 1364-2001)

## Candidate Evaluation

### PicoRV32 (SELECTED)

| Criterion | Assessment |
|-----------|-----------|
| Open Source | Yes, ISC license |
| Synthesizable | Yes, proven in ASIC tapeouts |
| Clean Licensing | ISC (permissive, no copyleft) |
| ASIC-friendly | Yes; no FPGA primitives, sync reset, clean single-edge clock |
| Size for SKY130 | ~750-2000 LUT equivalent, ~2500-5000 standard cells |
| Repository Health | Active, 2.5k+ stars, YosysHQ maintained |
| RTL Size | 3049 lines, single file |
| Module Count | 8 modules (picorv32 core + variants + PCPI cores) |
| Documentation | Excellent README, well-commented code |
| Toolchain | Pure Verilog, no preprocessing needed |

### SERV (Not Selected)

| Criterion | Assessment |
|-----------|-----------|
| Open Source | Yes |
| Synthesizable | Yes |
| Clean Licensing | Yes |
| ASIC-friendly | Yes |
| Size | Extremely small (bit-serial) |
| Reason not selected | Less widely used; bit-serial design less representative of typical CPU flow |

### FemtoRV (Not Selected)

| Criterion | Assessment |
|-----------|-----------|
| Open Source | Yes |
| Synthesizable | Yes |
| Clean Licensing | Yes |
| ASIC-friendly | Moderate |
| Reason not selected | Educational focus; less proven in ASIC |

### VexRiscv (Not Selected)

| Criterion | Assessment |
|-----------|-----------|
| Open Source | Yes |
| Synthesizable | Yes (via SpinalHDL) |
| Clean Licensing | Yes |
| Toolchain | Requires SpinalHDL/Scala toolchain |
| Reason not selected | Preprocessing step adds complexity; SpinalHDL not in standard flows |

## PicoRV32 Configuration for This Flow

Parameters selected for ASIC implementation:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| ENABLE_COUNTERS | 1 | Standard RISC-V requirement |
| ENABLE_COUNTERS64 | 1 | Standard RISC-V requirement |
| ENABLE_REGS_16_31 | 1 | Full RV32I register set |
| ENABLE_REGS_DUALPORT | 1 | Performance |
| COMPRESSED_ISA | 0 | Simpler flow without C extension |
| ENABLE_MUL | 0 | Minimal area (M extension optional) |
| ENABLE_DIV | 0 | Minimal area |
| ENABLE_IRQ | 0 | Not needed for flow validation |
| PROGADDR_RESET | 0 | Standard boot address |

## Top-Level I/O

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| clk | Input | 1 | Main clock |
| resetn | Input | 1 | Active-low reset |
| trap | Output | 1 | Trap/halt indicator |
| mem_valid | Output | 1 | Memory request valid |
| mem_instr | Output | 1 | Instruction fetch indicator |
| mem_ready | Input | 1 | Memory ready |
| mem_addr | Output | 32 | Memory address |
| mem_wdata | Output | 32 | Memory write data |
| mem_wstrb | Output | 4 | Memory write strobe |
| mem_rdata | Input | 32 | Memory read data |

## Expected Complexity (SKY130)

| Metric | Estimate |
|--------|----------|
| Cell Count | ~3000-5000 |
| Die Area | ~10000-25000 um^2 |
| Frequency Target | 50 MHz (20 ns) |
| Power | < 1 mW |
