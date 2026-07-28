# Pipeline Stages

The full RTL-to-GDS pipeline executes approximately 29 stages. Major groups:

1. **Synthesis** (Yosys) — Verilog to gate-level netlist
2. **Floorplanning** — die area, I/O pin placement
3. **Placement** — standard cell placement
4. **CTS** (Clock Tree Synthesis) — build the clock distribution network
5. **Routing** — connect all cells with metal wires
6. **DRC** (Design Rule Check) — verify the layout against foundry rules (Magic + KLayout)
7. **LVS** (Layout vs. Schematic) — verify the layout matches the original design
8. **STA** (Static Timing Analysis) — verify all paths meet timing constraints (OpenSTA)
9. **GDS Export** — final layout file for tapeout

Some stages (fill, decap, antenna check, ATPG) run in parallel. Each stage runs
through OpenROAD Flow Scripts (ORFS) and reports results to the database.
