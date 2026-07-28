# Timing & QoR Ground Truth v1

## Methodology
Ground truth values extracted directly from EDA reports, NOT from dashboard or database.

## Designs Under Test

### Counter (latest: `run_1782118253_8869499f_counter`)

| Metric | Report Value | Source File |
|--------|-------------|-------------|
| Setup WNS | 0.05 ns | `reports/signoff_worst_setup.rpt:1` |
| Setup TNS | 0.00 ns | `reports/signoff_worst_setup.rpt:2` |
| Hold Slack | 0.02 ns | `sta_corners.json:13` |
| Critical Path Delay | N/A (not in signoff report) | |
| Critical Path Slack | N/A (not in signoff report) | |
| Cell Count | 100 | `reports/metrics.csv:4` |
| Utilization | 65.0% | `reports/metrics.csv:3` |
| Die Area | 100.0 um² | `telemetry/metrics.json:46` |
| QoR Inputs | timing=1.0, area=0.58, density=1.0 | `telemetry/metrics.json:36-45` |

### GCD (latest: `run_1782118325_62c195de_gcd`)

| Metric | Report Value | Source File |
|--------|-------------|-------------|
| Setup WNS | 0.0 ns | `reports/metrics.csv:1` |
| Setup TNS | 0.0 ns | `reports/metrics.csv:2` |
| Hold Slack | 0.90208 ns | `sta_corners.json:15` |
| Critical Path Delay | N/A | |
| Critical Path Slack | N/A | |
| Cell Count | 40 | `reports/metrics.csv:7` |
| Utilization | 19.0% | `reports/metrics.csv:6` |
| Die Area | 14139.6 um² | `telemetry/metrics.json:46` |
| QoR Inputs | timing=1.0, area=0.96, density=1.0 | `telemetry/metrics.json:36-45` |

### UART Top (latest: `run_1782118439_fa6710f6_uart_top`)

| Metric | Report Value | Source File |
|--------|-------------|-------------|
| Setup WNS | 0.0 ns | `reports/metrics.csv:1` |
| Setup TNS | 0.0 ns | `reports/metrics.csv:2` |
| Hold Slack | 0.16296 ns | `sta_corners.json:15` |
| Critical Path Delay | N/A | |
| Critical Path Slack | N/A | |
| Cell Count | 52 | `reports/metrics.csv:7` |
| Utilization | 43.0% | `reports/metrics.csv:6` |
| Die Area | 11272.07 um² | `telemetry/metrics.json:46` |
| QoR Inputs | timing=1.0, area=0.82, density=1.0 | `telemetry/metrics.json:36-45` |

### PicoRV32 (latest: `run_1782127003_aca911db_picorv32`)

| Metric | Report Value | Source File |
|--------|-------------|-------------|
| Setup WNS | 0.0 ns | `reports/metrics.csv:1` |
| Setup TNS | 0.0 ns | `reports/metrics.csv:2` |
| Hold Slack | 0.05958 ns | `sta_corners.json:15` |
| Critical Path Delay | 3.1345 ns | `reports/6_finish.rpt:445` |
| Critical Path Slack | 12.8655 ns | `reports/6_finish.rpt:450` |
| Cell Count | 1092 | `reports/metrics.csv:7` |
| Utilization | 36.0% | `reports/metrics.csv:6` |
| Die Area | 284200.94 um² | `telemetry/metrics.json:46` |
| QoR Inputs | timing=1.0, area=0.87, density=1.0 | `telemetry/metrics.json:36-45` |

## Signoff Classification (all designs)

| Design | Signoff Status | Tapeout Ready | Signoff Score |
|--------|---------------|---------------|---------------|
| Counter | PASS | YES | 1.0 |
| GCD | PASS | YES | 1.0 |
| UART | PASS | YES | 1.0 |
| PicoRV32 | PASS | YES | 1.0 |

## Summary

All four designs have:
- Timing met (WNS >= 0, TNS >= 0)
- Signoff PASS
- Tapeout Ready = YES
- No blocking issues

The ground-truth QoR inputs (timing, area, density scores) are all positive and non-zero for every design.
