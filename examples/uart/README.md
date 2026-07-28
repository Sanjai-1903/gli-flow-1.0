# UART Example Design

## Description

A full-duplex UART with configurable baud rate. Contains separate transmitter (`uart_tx`), receiver (`uart_rx`), and a top-level wrapper (`uart_top`) that implements a loopback: received data is forwarded directly back to the transmitter.

- **RTL:** `uart_top.sv`, `uart_tx.sv`, `uart_rx.sv`
- **Top module:** `uart_top`
- **PDK:** SkyWater 130nm (sky130A)
- **Clock:** 100 MHz (10 ns period)

## Expected QoR (approximate, sky130A)

| Metric          | Estimate            |
|-----------------|---------------------|
| Cell area       | ~1,000–2,000 µm²   |
| Standard cells  | ~100–200            |
| Frequency       | > 200 MHz           |
| Power           | ~50–100 µW          |

## Expected Runtime

| Step     | Time   |
|----------|--------|
| Synthesis | < 30 s |
| Floorplan  | < 10 s |
| Placement  | < 30 s |
| CTS        | < 10 s |
| Routing    | < 30 s |
| **Total**  | **~2 min** |

## How to Run

```bash
gli-flow run examples/uart
```

## Outputs

After a successful run, the following key outputs are generated in the run directory:

- `reports/` — timing, area, and power reports
- `results/` — final GDSII, LEF, and DEF files
- `logs/` — synthesis and P&R logs
- `checkpoints/` — intermediate database snapshots
