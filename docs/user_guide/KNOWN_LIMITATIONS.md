# GLI-FLOW-ASIC v1.1.0-beta — Known Limitations

This document honestly describes what GLI-FLOW-ASIC v1.1.0-beta cannot do. Read this before starting a tapeout.

## Flow Limitations

**No CDC Analysis**
Clock domain crossing analysis is not performed. For multi-clock designs, use a dedicated CDC tool (SpyGlass CDC, Questa CDC) before tapeout.

**No Monte Carlo Timing**
Only deterministic corner analysis is performed. Statistical timing (SSTA) is not supported.

**Single Parasitic Extraction Model**
OpenROAD's internal RC model is used. This is an approximation. For foundry sign-off accuracy, use Calibre RCX or StarRC.

**No ESD Analysis**
Electrostatic discharge protection must be verified separately.

**No Seal Ring Automation**
Standalone die seal rings must be added manually.

**SRAM Integration**
OpenRAM integration is partial. Behavioral SRAM models do not have timing constraints. Verify SRAM interface timing manually.

**SystemVerilog**
SystemVerilog requires sv2v preprocessing. Not all SV constructs are supported by sv2v. Prefer Verilog-2001 for maximum compatibility.

**No Analog or Mixed-Signal Support**
GLI-FLOW-ASIC supports digital-only flows.

**No Hierarchical Flows**
Hierarchical partition-and-assemble flows are not supported in v1.1.0-beta.

## PDK Support

| PDK | Status | Notes |
|-----|--------|-------|
| sky130A | ✓ Tested | Full support |
| gf180mcuD | Defined | Partially tested |
| IHP SG13G2 | Planned | v1.1 |

## Maximum Tested Complexity

| Design | Cells | Runtime |
|--------|-------|---------|
| counter | ~500 | 4m |
| uart | ~2,000 | 8m |
| systolic array | ~15,000 | 23m |
| ibex RISC-V | ~50,000 | ~90m |

Designs above 100,000 cells are untested.

## Environment Resilience

| Limitation | Status |
| ---------- | ------ |
| Multi-candidate discovery | ✓ Implemented for magic, netgen, yosys, openroad, klayout |
| Self-healing repair | ✓ Magic PATH shadowing repair |
| Generic repair framework | ✓ Framework exists for future tool-specific repairs |
| Adversarial environment tests | ✓ 10 tests covering broken wrappers, symlinks, permissions, PATH shadowing |
| Release gates | ✓ 4 gates enforce resilience architecture at release time |
| Telemetry for shadowing events | ✓ Captured as environment events |
| Repair for all tools | Partial — magic only, other tools in future releases |

## Commercial EDA Tools

GLI-FLOW v1.1.0-beta uses open-source tools only. No Synopsys, Cadence, or Siemens tools.
