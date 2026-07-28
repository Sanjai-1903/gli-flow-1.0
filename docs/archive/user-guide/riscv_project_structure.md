# RISC-V CPU Project Structure for GLI-FLOW

## Recommended Directory Layout

```
picorv32/                        # Project root (name matches design)
├── rtl/                         # RTL source files
│   └── picorv32.v               # PicoRV32 CPU core (3049 lines)
├── constraints/                  # Timing constraints
│   └── picorv32.sdc             # SDC constraints file
├── configs/                     # Optional configuration overrides
│   └── (optional)               # PDN config, floorplan config
├── verification/                 # Testbenches and simulation
│   └── (optional)               # Functional verification collateral
├── docs/                        # Design-specific documentation
│   └── (optional)               # Architecture notes
├── gli_manifest.yaml            # GLI-FLOW manifest (REQUIRED)
└── README.md                    # Design overview
```

## File Purposes

### `rtl/picorv32.v`
- Single-file RTL implementation of PicoRV32
- Contains all 8 modules: picorv32, picorv32_regs, picorv32_pcpi_mul, picorv32_pcpi_fast_mul, picorv32_pcpi_div, picorv32_axi, picorv32_axi_adapter, picorv32_wb
- Top module for flow: `picorv32`

### `constraints/picorv32.sdc`
- Defines clock period, input/output delays, false paths
- Clock defined on `clk` port at 50 MHz (20 ns)
- Memory interface outputs constrained as virtual external registers
- All PCPI/IRQ/AXI ports set as false paths (not connected in this validation)

### `gli_manifest.yaml`
- GLI-FLOW project configuration
- Specifies RTL files, top module, PDK, target frequency
- Defines PVT corners for signoff
- Configures OpenROAD backend

## Design Directory Usage

The design directory is passed to `gli-flow run`:
```bash
gli-flow run examples/picorv32
```

Outputs are generated under `outputs/runs/run_<timestamp>_<id>_picorv32/`:
```
outputs/runs/run_<ts>_<id>_picorv32/
├── artifacts/         # Final GDS, DEF, netlist
├── reports/           # Timing, area, power reports
├── logs/              # Synthesis, P&R logs
├── checkpoints/       # Intermediate results
├── outputs/telemetry/  # Metrics and telemetry
└── config.json        # Generated OpenROAD config
```
