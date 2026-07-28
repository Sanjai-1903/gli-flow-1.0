# RISC-V Design File Requirements for GLI-FLOW

## Required Files

### 1. RTL Source Files
**Required:** Yes
**Format:** `.v` (Verilog), `.sv` (SystemVerilog)
**Description:** All HDL source files for the design.
**Example:** `rtl/picorv32.v`
**Notes:**
- SystemVerilog files are automatically converted to Verilog via `sv2v`
- Include paths must be specified in manifest if using `include
- File paths are relative to project root

### 2. SDC Constraints File
**Required:** Yes
**Format:** `.sdc`
**Description:** Synopsys Design Constraints file.
**Example:** `constraints/picorv32.sdc`
**Notes:**
- Minimum: `create_clock`
- Recommended: `set_input_delay` / `set_output_delay`
- Optional: false paths, multicycle paths

### 3. GLI-FLOW Manifest
**Required:** Yes
**Format:** `.yaml`
**File Name:** `gli_manifest.yaml`
**Description:** Project configuration file.
**Notes:**
- Must be in the root of the design directory
- All paths relative to parent directory of manifest
- See manifest guide for full field documentation

## Optional Files

### LEF Files
**Required:** No
**Description:** Library Exchange Format for macros/blocks.

### LIB Files
**Required:** No (auto-detected from PDK)
**Description:** Liberty timing library files.

### DEF Files
**Required:** No
**Description:** Design Exchange Format for floorplan initialization.

### SPEF Files
**Required:** No
**Description:** Standard Parasitic Exchange Format for post-layout timing.

### SDF Files
**Required:** No
**Description:** Standard Delay Format for gate-level simulation.

### PDN Configuration
**Required:** No
**Description:** Power Delivery Network configuration.

### Floorplan Configuration
**Required:** No
**Description:** Initial floorplan constraints (die area, pin placement).

## Auto-Generated Files

During a GLI-FLOW run, the following files are auto-generated:

| File | Stage | Description |
|------|-------|-------------|
| `config.json` | Synthesis | OpenROAD configuration |
| `1_1_yosys.v` | Synthesis | Synthesized netlist |
| `2_floorplan.def` | Floorplanning | Floorplan DEF |
| `3_placement.def` | Placement | Placement DEF |
| `4_cts.def` | CTS | Clock tree synthesis DEF |
| `5_route.def` | Routing | Routing DEF |
| `6_final.gds` | Signoff | Final GDSII layout |
| `6_final.def` | Signoff | Final DEF |
| `6_final.v` | Signoff | Final netlist |
| `reports/*` | All | Various QoR reports |
| `drc_lvs_summary.json` | DRC/LVS | Combined DRC/LVS results |
