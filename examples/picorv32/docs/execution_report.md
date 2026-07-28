# PicoRV32 GLI-FLOW Execution Report — Golden Run

## Run Details

| Field | Value |
|-------|-------|
| Run ID | `run_1781586782_b4b86c77_picorv32` |
| Design | picorv32 |
| PDK | sky130A |
| Clock Target | 50 MHz (20 ns) |
| Date | 2026-06-16 |
| Duration | 1295.83s (~21.6 min) |
| Status | Implementation: SUCCESS / Signoff: FAILED |

## QoR Summary

| Metric | Value |
|--------|-------|
| Die Area | 284,201 µm² |
| Standard Cells | 1,282 |
| Utilization | 36.0% |
| Setup WNS | 0.0 ns |
| Setup TNS | 0.0 ns |
| Hold WNS | 0.0 ns |
| Total Power | 9.15 µW |
| Internal Power | 6.86 µW |
| Switching Power | 2.29 µW |
| Leakage Power | 38.5 nW |
| Magic DRC | 2 violations (1 real li.3 + 1 false-positive licon.8a) |
| KLayout DRC | 0 violations |
| LVS | NOT_RUN (extraction timeout at 600s) |

## ORFS Flow Steps

All OpenROAD flow steps completed successfully:
1. Yosys synthesis ✓ (1_synth.v)
2. Floorplan ✓ (534.8 x 534.8 µm)
3. Power distribution network ✓
4. Placement ✓ (36% utilization)
5. Clock Tree Synthesis ✓
6. Detailed Routing ✓ (35 iterations, 0 DRC errors)
7. Fill Insertion ✓
8. GDS Merge ✓ (12.7 MB)
9. Timing/Power/Area report ✓

## DRC Details

### Magic DRC: 2 violations
- **li.3** (local interconnect spacing): 1 real violation — at die-edge boundary
- **licon.8a** (poly overlap of contact): 1 false-positive — known Magic issue (INF-MAGIC-002)

### KLayout DRC: 0 violations

**Cross-Tool Analysis:** TOOL_DISAGREEMENT — KLayout validates clean GDS; licon.8a is a false-positive.

## Deliverables

| File | Size | Description |
|------|------|-------------|
| `artifacts/6_final.gds` | 12.7 MB | Final GDSII layout |
| `artifacts/6_final.def` | 11.2 MB | Final DEF |
| `artifacts/6_final.v` | 873 KB | Final netlist |
| `telemetry/metrics.json` | — | 149-field metrics |
| `drc_lvs_summary.json` | — | DRC/LVS results |
| `reproducibility.json` | — | Provenance manifest |

## Signoff Gate

| Check | Result |
|-------|--------|
| Setup Timing | PASS |
| Hold Timing | PASS |
| Antenna | PASS |
| Density | PASS (warnings) |
| EM/IR | PASS |
| Formal | PASS |
| DRC (Magic) | FAIL (2 violations) |
| DRC (KLayout) | PASS (0 violations) |
| LVS | NOT_RUN |

## Tapeout Blockers

1. **li.3 spacing** — 1 real DRC violation; needs routing margin increase
2. **LVS** — Extraction timed out at 600s (129.9MB .ext); needs timeout increase or hierarchical extraction
