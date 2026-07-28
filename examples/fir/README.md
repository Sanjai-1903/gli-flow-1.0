# FIR Filter Example Design

## Description

A finite impulse response (FIR) filter design. Implements a tap-delay line with coefficient multipliers and an adder tree for the dot product.

- **RTL:** `rtl/fir.v` (placeholder — RTL to be added)
- **Top module:** `fir_top`
- **PDK:** SkyWater 130nm (sky130A)
- **Clock:** 100 MHz (10 ns period)
- **Configuration:** 8-tap symmetric, 16-bit data and coefficients

## Expected QoR (approximate, sky130A)

| Metric          | Estimate            |
|-----------------|---------------------|
| Cell area       | ~10,000–25,000 µm² |
| Standard cells  | ~1,000–2,500       |
| Frequency       | > 100 MHz           |
| Power           | ~0.5–2 mW           |

## Expected Runtime

| Step     | Time    |
|----------|---------|
| Synthesis | < 2 min |
| Floorplan  | < 30 s  |
| Placement  | < 2 min |
| CTS        | < 30 s  |
| Routing    | < 3 min |
| **Total**  | **~8 min** |

## How to Run

```bash
gli-flow run examples/fir
```

## Outputs

After a successful run, the following key outputs are generated in the run directory:

- `reports/` — timing, area, and power reports
- `results/` — final GDSII, LEF, and DEF files
- `logs/` — synthesis and P&R logs
- `checkpoints/` — intermediate database snapshots
