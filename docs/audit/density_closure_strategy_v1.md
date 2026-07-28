# Density Closure Strategy v1

**Date:** 2026-06-21
**Scope:** PicoRV32 signoff density check repair
**Status:** Strategy document (no implementation yet)

## 1. Root Cause

**Command `check_density` does not exist in OpenROAD v2.0-17598.**

```tcl
% echo "check_density" | openroad -no_init -exit 2>&1
invalid command name "check_density"
```

The command was either:
- Removed during OpenROAD v2.x API refactoring
- Never merged from OpenLane's patched OpenROAD fork into upstream

## 2. What OpenROAD v2.0 Provides

Available density-related commands in `openroad v2.0-17598`:

| Command | Purpose | Can replace `check_density`? |
|---|---|---|
| `density_fill` | Inserts metal fill shapes from a JSON rules file | **No** — filling only, no compliance reporting |
| `report_design_area` | Reports standard cell placement utilization | **No** — cell area, not per-layer metal density |
| `report_design_area_metrics` | Machine-readable `report_design_area` | **No** — same cell-area data |

**Conclusion: Native OpenROAD has no replacement for `check_density`.**

## 3. Current Fallback Behavior (Broken)

In `openroad_adapter.py:2727-2731`:

```python
if result.returncode != 0:
    output = (result.stdout or '') + (result.stderr or '')
    if "no commands match" in output.lower() or "unknown command" in output.lower():
        logger.warning("check_density not supported by this OpenROAD version")
        return DensityResult(0.0, 15.0, 85.0, 0, runtime_seconds=runtime)
```

This returns:
- `density_pct = 0.0` (always)
- `violations = 0` (always)
- `min_density_pct = 15.0` (hardcoded, not from PDK)

Because `density_pct == 0.0`, the tapeout-blocking check at line 2708 is **always skipped**:

```python
if combined.density_pct > 0 and combined.density_pct < min_density:
    violations += 1
```

The result is a **silent, unconditional PASS** — no density checking occurs.

The orchestrator knows about this at `orchestrator.py:1248`:
```python
self._flow_bugs.append("Density check: check_density command not found in OpenROAD v2.0-17598")
```

## 4. What the PDK Ships for Density Checking

### 4.1 KLayout DRC (`met_min_ca_density.lydrc`)

Location: `~/.gli-flow/pdk/sky130A/libs.tech/klayout/drc/met_min_ca_density.lydrc`

- Tile-based measurement (70um tiles aggregated into 700um windows)
- Per-layer minimum density thresholds (e.g., MET5: 24%, others: 40%)
- Operates on GDS
- Ships with the official Sky130 PDK

### 4.2 Magic `check_density.py`

Location: `~/.gli-flow/pdk/sky130A/libs.tech/magic/check_density.py`

- Uses Magic VLSI for density computation
- Same tile-based approach
- SkyWater-specific rules
- Requires Magic runtime (not ideal for headless signoff)

## 5. Recommendation

### Option A: Native OpenROAD — **NOT VIABLE**
No implementation path exists. The command doesn't exist and cannot be added without patching OpenROAD.

### Option B: Parse Existing Reports — **PARTIALLY VIABLE**
ORFS generates `report_design_area` but it reports standard cell utilization, not per-layer metal density. A custom DEF/GDS parser would be needed — reimplementing what KLayout already does.

### Option C: KLayout DRC — **VIABLE (Recommended)**
Invoke the PDK's existing `met_min_ca_density.lydrc` DRC script on the final GDS:

```
klayout -b -r met_min_ca_density.lydrc -rd input=6_final.gds -rd top_cell=picorv32
```

**Rationale:**
- PDK-maintained rules (foundry-correct thresholds per layer)
- No new code — only integration and output parsing
- KLayout is already in the toolchain (GDS stream-out)
- Compatible with all Sky130 variants

### Option D: Custom Python Density Calculator — **VIABLE (Fallback)**
Write a standalone Python script using `gdspy` to parse GDS and compute per-layer metal area vs total chip area. More flexible but duplicates effort.

## 6. Migration Plan

1. **Immediate**: Change the fallback from fake-PASS to `NOT_RUN` so the signoff status reflects reality
2. **Short-term**: Implement integration with PDK's KLayout DRC script (`met_min_ca_density.lydrc`)
3. **Parse KLayout output**: Extract per-layer violation counts from the DRC report
4. **Update `_run_density_check_internal`**: Replace the broken OpenROAD call with the KLayout DRC invocation
5. **Config**: Read per-layer min/max density from PDK metadata instead of hardcoded defaults (15/85)

## 7. Code Locations

| File | Lines | Purpose |
|---|---|---|
| `openroad_adapter.py:2635-2653` | `_write_density_tcl` | Generates TCL with `check_density` (broken) |
| `openroad_adapter.py:2714-2739` | `_run_density_check_internal` | Runs density TCL, handles fallback |
| `openroad_adapter.py:2741-2765` | `_parse_density_output` | Parses density report |
| `openroad_adapter.py:3144-3165` | `DensityResult` | Dataclass with `density_pct`, `violations` |
| `orchestrator.py:1242-1248` | DENSITY_CHECK stage | Flow bug tracking for density |
