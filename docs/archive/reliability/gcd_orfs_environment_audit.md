# GCD ORFS Environment Audit

## Objective
Capture the exact toolchain and PDK environment used by the native OpenROAD Flow Scripts (ORFS) GCD run, establishing an independent reference baseline for comparison with GLI-FLOW.

## Methodology
All tool versions were captured from the ORFS log files in `/home/gli/.gli-flow/orfs/flow/logs/sky130hd/gcd/base/` on 2026-06-11. PDK paths were resolved from the platform configuration at `/home/gli/.gli-flow/orfs/flow/platforms/sky130hd/`.

## Tools

| Tool | Version | Source |
|------|---------|--------|
| OpenROAD | v2.0-17598-ga008522d8 | `6_report.log:1` |
| Yosys | 0.40 (git sha1 a1bb0255d) | `1_1_yosys_canonicalize.log:19` |
| Magic | 8.3.659 | `magic --version` (same binary as GLI-FLOW) |
| KLayout | 0.30.7 | `klayout -b -v` (same binary as GLI-FLOW) |
| Netgen | 1.5.257 | `netgen -batch -version` (same binary as GLI-FLOW) |
| GCC | 11.4.0-1ubuntu1~22.04.3 | Yosys build info |
| Python | (system default) | (not explicitly versioned in run) |

## PDK

| Parameter | Value |
|-----------|-------|
| PDK root | `/home/gli/.gli-flow/pdk` |
| PDK variant | `sky130A` |
| Platform | `sky130hd` |
| Library | `sky130_fd_sc_hd__tt_025C_1v80` |
| PDK version | `bdc9412b3e468c102d01b7cf6337be06ec6e9c9a` |
| Magic tech file | `sky130A.tech` (from volare) |
| KLayout DRC runset | `sky130A.lydrc` (from volare) |
| LVS rule deck | `sky130A.magicrc` with `sky130A.lvs` |
| LEF files | bundled in ORFS platform `platforms/sky130hd/lef/` |
| GDS reference lib | bundled in ORFS platform `platforms/sky130hd/gds/` |

## ORFS Configuration

| Parameter | Value |
|-----------|-------|
| Flow root | `/home/gli/.gli-flow/orfs/flow/` |
| Platform | `sky130hd` |
| Design | `gcd` |
| Clock period | 10.000 ns |
| Core utilization | (ORFS default) |
| Threads | 28 |

## Run Results (Native ORFS)

| Metric | Value |
|--------|-------|
| Cell count | 271 |
| Sequential cells | 26 |
| Die area | 2490 um^2 |
| Utilization | 19% |
| Worst slack | 7.35 ns |
| Worst TNS | 0.00 ns |
| Hold slack | 0.45 ns |
| Critical path delay | 2.80 ns |
| Max frequency | 377 MHz |
| Total power | 9.70e-04 W |
| IR drop VDD (worst) | 8.97e-05 V |
| IR drop VSS (worst) | 1.14e-04 V |
| OpenROAD DRC violations | 0 |
| Magic DRC violations | 2 (licon.8a) |
| KLayout DRC violations | 0 (licon.8a not in report categories) |

## GDS Identicality

| Hash | Path |
|------|------|
| `a08cd6def3ea157998c1c293943c25bb` | ORFS: `.../flow/results/sky130hd/gcd/base/6_final.gds` |
| `a08cd6def3ea157998c1c293943c25bb` | GLI-FLOW: (same hash confirmed) |

The GDS files from both flows are byte-identical.

## Notes
- Magic 8.3.659 requires `DISPLAY=:0` to initialize Tk and execute DRC; without it, Magic silently produces a 0-violation report. Both GLI-FLOW and this ORFS run were executed with `DISPLAY=:0`.
- KLayout's `sky130A.lydrc` defines licon.8a (`licon.8a : min. poly enclosure of licon by one of 2 opposite edges : 0.08um`) but the XML report (`klayout_drc.xml`) contains no licon.8a category or violations, suggesting the rule either was not executed or did not produce output. This is documented separately in INF-MAGIC-002.
