# Counter Example Design

## Description

A simple 8-bit up-counter with synchronous reset. Counts from 0 to 255 on each rising clock edge, then wraps around.

- **RTL:** `counter.v` — single module, 14 lines
- **Top module:** `counter`
- **PDK:** SkyWater 130nm (sky130A)
- **Clock:** 100 MHz (10 ns period)

## Expected QoR (approximate, sky130A)

| Metric          | Estimate       |
|-----------------|----------------|
| Cell area       | ~200–400 µm²   |
| Standard cells  | ~15–25         |
| Frequency       | > 500 MHz      |
| Power           | < 10 µW        |

## Expected Runtime

| Step     | Time  |
|----------|-------|
| Synthesis | < 10 s |
| Floorplan  | < 5 s  |
| Placement  | < 10 s |
| CTS        | < 5 s  |
| Routing    | < 10 s |
| **Total**  | **< 1 min** |

## How to Run

```bash
gli-flow run examples/counter
```

## Outputs

After a successful run, the following key outputs are generated in the run directory:

- `reports/` — timing, area, and power reports
- `results/` — final GDSII, LEF, and DEF files
- `logs/` — synthesis and P&R logs
- `checkpoints/` — intermediate database snapshots
