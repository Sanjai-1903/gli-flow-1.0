# GPIO Example Design

## Description

A general-purpose input/output block. Provides multiple bidirectional I/O pins with configurable direction, output drive, and pull-up/pull-down control via a memory-mapped register interface.

- **RTL:** `rtl/gpio.v` (placeholder — RTL to be added)
- **Top module:** `gpio_top`
- **PDK:** SkyWater 130nm (sky130A)
- **Clock:** 100 MHz (10 ns period)
- **Configuration:** 8-bit GPIO, APB slave interface

## Expected QoR (approximate, sky130A)

| Metric          | Estimate           |
|-----------------|--------------------|
| Cell area       | ~3,000–6,000 µm²  |
| Standard cells  | ~200–500           |
| Frequency       | > 200 MHz          |
| Power           | ~50–200 µW         |

## Expected Runtime

| Step     | Time   |
|----------|--------|
| Synthesis | < 1 min |
| Floorplan  | < 10 s |
| Placement  | < 1 min |
| CTS        | < 10 s |
| Routing    | < 1 min |
| **Total**  | **~3 min** |

## How to Run

```bash
gli-flow run examples/gpio
```

## Outputs

After a successful run, the following key outputs are generated in the run directory:

- `reports/` — timing, area, and power reports
- `results/` — final GDSII, LEF, and DEF files
- `logs/` — synthesis and P&R logs
- `checkpoints/` — intermediate database snapshots
