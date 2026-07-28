# Status Model Redesign

## Problem

Current model collapses everything into a single `FAILED` status:

```
run_1781335891_66db0bd7_picorv32:
  status: FAILED
  qor_score: 0.0
```

The picorv32 design:
- ✅ Synthesis completed successfully
- ✅ Placement completed successfully
- ✅ CTS completed successfully
- ✅ Routing completed successfully
- ✅ GDS generated (6_final.gds exists, 1.2MB)
- ❌ DRC: 6 violations
- ❌ LVS: extraction timed out

A first-time user sees `FAILED` and `QoR: 0.0` and cannot tell whether their
RTL is broken or whether the signoff checks need tuning.

## New Model: Three-Axis Status

### Axis 1: Implementation Status (RTL → GDS)

| Status | Meaning |
|--------|---------|
| `NOT_STARTED` | Flow hasn't begun |
| `IN_PROGRESS` | Implementation running |
| `SUCCESS` | GDS generated, all implementation stages passed |
| `FAILED` | Implementation stage failed (synthesis/placement/routing crash) |

**Determination:**
- Check if `6_final.gds` exists AND has content > 0 bytes
- Check if all implementation stages (SYNTHESIS through PACKAGING) completed without exception
- If GDS present: SUCCESS
- If GDS not present after implementation stages: FAILED

### Axis 2: Signoff Status (GDS → Signoff)

| Status | Meaning |
|--------|---------|
| `NOT_RUN` | No signoff checks executed |
| `IN_PROGRESS` | Signoff checks running |
| `PASS` | All signoff checks pass |
| `FAILED` | One or more signoff checks fail |

**Determination:**
- Signoff gate: ALL 17 checks must pass
- If DRC/LVS/timing not run: NOT_RUN
- If any check fails: FAILED

### Axis 3: Tapeout Ready (binary gate)

| Value | Meaning |
|-------|---------|
| `YES` | Both Implementation SUCCESS and Signoff PASS |
| `NO` | Either axis not clean |

### Score Separation

| Score | Meaning |
|-------|---------|
| `Implementation Score` | QoR based on timing, area, density (same formula, computed when GDS exists) |
| `Signoff Score` | Binary: 1.0 if all signoff pass, 0.0 otherwise |
| `Combined Score` | Implementation × Signoff (for trend comparisons only) |

**Key Rule:** `Implementation Score` is NEVER 0.0 when GDS exists. Even with
DRC violations, if timing met and routing completed, the implementation score
reflects actual design quality.

### Database Schema Changes

New columns in `runs` table:
- `implementation_status` TEXT DEFAULT 'NOT_STARTED'
- `signoff_status` TEXT DEFAULT 'NOT_RUN'
- `tapeout_ready` INTEGER DEFAULT 0
- `implementation_score` REAL DEFAULT NULL
- `signoff_score` REAL DEFAULT NULL

### Backward Compatibility

- Old `status` field kept as derived convenience: 
  - If implementation FAILED → FAILED
  - If implementation SUCCESS + signoff FAILED → "SIGNOFF_FAILED" (new)
  - If both SUCCESS → SUCCESS
- QoR remains in database but dashboard displays implementation_score as primary
