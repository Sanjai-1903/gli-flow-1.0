# Magic 8.3.105 Validation Audit

## Historical Context

### When Added
- **Commit**: `9af9e43` ("rtl - gdsii works, should add failure atlas and other ip tests")
- **Date**: During initial GLI-FLOW MVP development
- **Blacklist entry**: `KNOWN_BROKEN_VERSIONS["magic"] = [(8, 3, 105)]`
- **Commit message**: *"rtl - gdsii works, should add failure atlas and other ip tests"*

The blacklist was introduced in the same commit that created `tool_discovery.py` from scratch. There was no prior version without the blacklist — it was part of the initial implementation.

### Why Added (Original Evidence)

Three documented root causes from `docs/audit/MAGIC_ROOT_CAUSE.md`:

1. **Wrong Magic Binary (Wrapper Script)** — `/usr/bin/magic` installed by apt is a Tcl/Tk Wish wrapper that fails in `-dnull` batch mode. It tries to open the display even with `-dnull`.
   - **Fix applied**: Use `magicdnull -nowrapper -d NULL -rcfile <magicrc>` directly.
   - **File**: `gli_flow/backends/openroad_adapter.py`, `gli_flow/core/drc_runner.py`

2. **Tech File Version Mismatch** — `sky130A.tech` (line 19) required `magic-8.3.411`, but apt provides 8.3.105.
   - **Fix applied**: Patched to `requires magic-8.3.0`.
   - **File**: `~/.gli-flow/pdk/sky130A/libs.tech/magic/sky130A.tech`

3. **CAD_ROOT Environment Variable** — `safe_env()` set `CAD_ROOT=/home/bolter/.local/lib`, interfering with Magic's internal resource lookup.
   - **Fix applied**: Removed `CAD_ROOT` from `safe_env()` entirely.
   - **File**: `gli_flow/core/subprocess_env.py`

### Associated Bug Reports
- Root cause documented in `docs/audit/MAGIC_ROOT_CAUSE.md`
- First-pass integration report: `docs/audit/FIRST_PASS_REPORT.md`
- Pipeline root cause report: `docs/audit/ROOT_CAUSE_REPORT.md`

### Associated Failure Atlas Entry
- `INF-MAGIC-001` (created during this audit)

### Associated Regression Test
- `tests/regressions/test_magic_version_selection.py` — Tests that 8.3.105 is rejected and 8.3.659 preferred.

## Original Defect Classification

All three root causes were **GLI-FLOW integration/environment issues**, not Magic version defects:

| Cause | Type | Status |
|-------|------|--------|
| Wrong binary wrapper | Environment packaging | Fixed |
| Tech file version mismatch | Environment configuration | Fixed |
| CAD_ROOT env var | Code bug in GLI-FLOW | Fixed |

**None of the original bugs were inherent defects in Magic 8.3.105 itself.**

## Functional Validation Results (2026-06-08)

| Test | Result | Evidence |
|------|--------|----------|
| `magic --version` | PASS | Exit 0, output "8.3.105" |
| `magic -dnull -noconsole` TCL startup | PASS | Exit 0, TCL interpreter works |
| `magicdnull -nowrapper -d NULL` batch | PASS | Exit 0, all TCL commands execute |
| DRC check | PASS | Exit 0, reports 0 violations |
| DRC report file generation | PASS | Creates non-empty file, exit 0 |
| Exit codes | PASS | All return 0 |
| `crashbackups disable` | PASS | No error (tested explicitly) |

## Root Cause Re-evaluation

**A. Magic version defect**: NO — 8.3.105 performs all required functions.
**B. Broken local wrapper**: Was an issue — but only `/usr/bin/magic` is a wrapper; `magicdnull` works correctly.
**C. Tool discovery bug**: Was an issue — tool discovery now correctly finds `magicdnull`.
**D. Environment-specific packaging issue**: YES — original bugs were all environment/integration issues, now fixed.

## Policy Decision

**REMOVE blacklist.**

Replace `KNOWN_BROKEN_VERSIONS` with `HistoricalRiskVersions` (version warning only).

Use functional validation (`validate_magic_functionality()`) instead of version-based rejection.
