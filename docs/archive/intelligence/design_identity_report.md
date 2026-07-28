# Design Identity Recovery Report

**Generated**: 2026-06-16T09:06:36.187786+00:00

## Summary

| Metric | Before | After |
|---|---|---|
| Entries without design_name | 0 | 0 |
| Total entries | 908 | 908 |
| Coverage | 100.0% | 100.0% |

## Designs Discovered

**14 distinct designs**

| Design Name | Atlas Entries | Runs |
|---|---|---|
| aes_cipher | 61 | 0 |
| counter | 65 | 10 |
| fir | 82 | 0 |
| fir_top | 0 | 1 |
| gcd | 59 | 3 |
| gpio | 64 | 0 |
| ibex | 164 | 0 |
| picorv32 | 109 | 2 |
| serv | 82 | 0 |
| sram_controller | 68 | 0 |
| tiny_or | 0 | 8 |
| tinyml_accel | 81 | 0 |
| uart | 65 | 0 |
| uart_top | 8 | 4 |

## Data Sources Used
- `runs.design_name`: Direct mapping from pipeline execution records
- Run ID pattern inference: Extracted design name from run naming conventions
- Fallback: Used `run_id` as design_name when no mapping found