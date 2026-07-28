# INF-LVS-002 Blast Radius Report

## Summary

| Metric | Value |
|--------|-------|
| Root cause | Malformed netgen command construction when pdk_sc_spice is found |
| Total historical runs | 57 |
| Runs where pdk_sc_spice was found | 55 (96%) |
| Runs with malformed command | 55 (100% of runs with pdk found) |
| Runs with zero device counts | 55 |
| Runs with missing lvs_report.txt | 57 |
| **Runs with compromised integrity** | **55 (96%)** |

## Affected Designs

| Design | Compromised Runs | Total Runs | Impact |
|--------|-----------------|------------|--------|
| counter | 7 | 8 | All 7 LVS results invalid (no comparison performed) |
| tiny_or | 47 | 47 | All 47 LVS results invalid (no comparison performed) |
| uart_top | 1 | 1 | Signoff failure — LVS never completed comparison |

## Pattern

All 55 compromised runs share the same pattern:
- Netgen exited with return code **0**
- `report_exists = false`
- `comparison_completed = false`
- `unmatched_devices = 0`, `unmatched_nets = 0` (defaults, not genuine results)
- `parser_status = "no comparison evidence — stdout had no device counts, report missing"`
- No `lvs_report.txt` file was ever created

## Root Cause Mechanism

When `_find_pdk_sc_spice()` returned a valid PDK SPICE path (which occurred for all sky130hd designs), the netgen command was constructed as:

```
netgen -batch lvs "layout.spice top" "pdk.spice top" "netlist.v top" setup.tcl reports/lvs_report.txt
```

Netgen interpreted:
- **circuit1**: `layout.spice top` ✓
- **circuit2**: `pdk.spice top` (netlist NOT included — wrong!)
- **setup file**: `netlist.v top` (netlist path consumed as setup file!)
- **report file**: `setup.tcl` (setup file consumed as report path!)
- **actual report path**: silently discarded

Netgen compared the layout against only the PDK cell definitions (no design netlist). Since the PDK cells share no device counts with the design, and the setup file was missing, netgen exited with no output and no report.

## When pdk_sc_spice was NOT found

When the PDK SPICE file was not found (2 runs), the command was:

```
netgen -batch lvs "layout.spice top" "netlist.v top" setup.tcl reports/lvs_report.txt
```

This is **correct** — all 4 positional args are in the right place. However, even in these 2 runs, other issues (netgen crash, missing netlist) prevented successful LVS.

## Detection Timeline

| Date | Event |
|------|-------|
| All historical runs | INF-LVS-002 active — no LVS comparison performed |
| Run run_1781066003_a438343e_uart_top | Signoff gate (INF-LVS-001) detected missing comparison evidence and blocked signoff |
| [Current] | INF-LVS-002 root cause identified and fixed |

## Conclusion

INF-LVS-002 has a **96% blast radius** (55/57 runs). All LVS results in the system's history are invalid because netgen never performed a genuine comparison. The only reason this was not caught earlier is that the signoff gate (INF-LVS-001) was added before INF-LVS-002 was triggered, allowing the uart_top run to correctly detect the failure.

With the fix applied, all future LVS runs will construct correct netgen commands and produce genuine comparison results.
