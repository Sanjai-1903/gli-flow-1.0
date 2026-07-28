# LVS Blast Radius Report

## Summary

| Metric | Value |
|--------|-------|
| Total historical runs | 57 |
| Runs with LVS CLEAN | 55 |
| Runs with device_count=0 | 55 |
| Runs with net_count=0 | 55 |
| Runs with missing lvs_report.txt | 57 |
| **Runs with compromised integrity** | **55 (96%)** |

## Affected Designs

| Design | Compromised Runs | Total Runs |
|--------|-----------------|------------|
| counter | 7 | 8 |
| tiny_or | 47 | 47 |
| uart_top | 1 | 1 |
| unknown | 0 | 1 |

## Pattern

Every single LVS CLEAN result across all runs has:
- `unmatched_devices = 0`
- `unmatched_nets = 0`
- `short_count = 0`
- `open_count = 0`
- `report_exists = false`

**No LVS comparison has ever produced a report file.** All 55 CLEAN results are false positives caused by the fallback logic interpreting crash defaults as a clean comparison.

## Findings

| Question | Answer |
|----------|--------|
| One run only? | **No** — all 55 runs with LVS data |
| One design only? | **No** — all 3 designs (counter, tiny_or, uart_top) |
| All designs? | **Yes** |
| All historical runs? | **Yes** — 55/57 runs (2 runs have no LVS data due to early crashes) |
| Is there any genuine LVS PASS? | **No** — zero device counts across all runs, zero report files across all runs |

## Conclusion

The LVS signoff integrity issue has **100% blast radius** across all designs and all runs. Every LVS PASS result in the system's history is a false positive.
