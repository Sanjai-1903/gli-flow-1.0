# Magic Root Cause Analysis

## Issue: Magic Fails to Execute in Batch Mode

### Symptoms
- `magic -dnull -noconsole -T <techfile> <script>` produces no output or crashes
- `crashbackups disable` error during DRCI runs
- LVS extraction produces no SPICE file
- `gli-flow doctor` reports `magic version 0`

### Root Cause 1: Wrong Magic Binary (Wrapper Script)
The system package `magic` (apt) installs `/usr/bin/magic` as a **wrapper script**, not the actual binary. This wrapper:
- Invokes Tcl/Tk Wish for GUI mode
- Does not properly handle `-dnull` (no display) in batch mode
- Tries to open the display even with `-dnull` flag

**Fix**: Use `magicdnull` directly, located at:
```
/usr/lib/x86_64-linux-gnu/magic/tcl/magicdnull
```
Invoke with:
```
magicdnull -nowrapper -d NULL -rcfile <magicrc> script.tcl
```

### Root Cause 2: Wrong Tech File Version Check
`sky130A.tech` (line 19) requires `magic-8.3.411`, but the installed version is `magic-8.3.105` (Ubuntu apt). Magic refuses to load the tech file on version mismatch.

**Fix**: Patch the version requirement in `sky130A.tech`:
```
requires magic-8.3.0
```

### Root Cause 3: CAD_ROOT Environment Variable Breaks Magic
The `safe_env()` function in `subprocess_env.py` sets `CAD_ROOT=/home/bolter/.local/lib`, which interferes with Magic's internal resource lookup. When set, Magic subprocess runs but produces no output — no `.ext` file, no `.spice` file. No error is raised.

**Fix**: Remove `CAD_ROOT` from `safe_env()` entirely.

### Root Cause 4: PATH Shadowing (Broken Local Binary) ⚠️
A broken Tcl wrapper installed at `~/.local/bin/magic` referenced `/usr/local/lib/magic/tcl/wrapper.tcl` which did not exist. Because `~/.local/bin` appears before `/usr/bin` in PATH, the broken binary was selected over the valid system `/usr/bin/magic`.

**Original symptom:** `magic version 0` — no explanation, no alternative candidates shown, no repair offered.

**Fix — Multi-Candidate Discovery:** GLI-FLOW now discovers ALL candidates and selects based on functional validation, not PATH order.

**Current behavior:**
```
Magic Discovery — 2 candidate(s) found

Candidate #1
  Path:      ~/.local/bin/magic
  Version:   unknown
  Status:    BROKEN
  Reason:    couldn't read file "/usr/local/lib/magic/tcl/wrapper.tcl"
  Selected:  NO

Candidate #2
  Path:      /usr/bin/magic
  Version:   8.3.105
  Status:    VALID
  Evidence:  TCL interpreter OK
  Selected:  YES
```

**Self-healing repair:**
```bash
gli-flow doctor --repair-magic
# Renames ~/.local/bin/magic → ~/.local/bin/magic.broken
```

## Detection
- In the run logs, look for `crashbackups disable` errors (Magic not starting)
- In the run logs, look for "Magic extraction did not produce SPICE file"
- The DRC summary shows 0 checks run (Magic DRC didn't execute)
- `gli-flow doctor` shows `BROKEN` candidate with failure reason and valid alternative

## Prevention (Implemented)

| Measure | Component | Location |
| ------- | --------- | -------- |
| Multi-candidate discovery | `discover_magic_binaries()` | `gli_flow/core/tool_discovery.py` |
| Evidence-based ranking | `rank_tool_candidates()` | `gli_flow/core/tool_discovery.py` |
| Functional validation | `validate_magic_candidate()` | `gli_flow/core/tool_discovery.py` |
| Doctor discovery report | `DiscoveryReport` | `gli_flow/doctor.py` |
| Self-healing repair | `PathShadowingRepair` | `gli_flow/infrastructure/repair_actions.py` |
| CLI repair command | `--repair-magic` | `gli_flow/cli/main.py` |
| Adversarial tests | 10 tests | `tests/adversarial/environment/` |
| Regression tests | 7 tests | `tests/regressions/test_path_shadowing_prefers_functional_binary.py` |
| Failure Atlas entry | INF-ENV-001 | `failure_atlas/taxonomy.py` |
| Telemetry tracking | `tool_shadowing`, `broken_wrapper` events | `gli_flow/runtime/telemetry_manager.py` |

## Affected Versions
- Magic 8.3.105 (Ubuntu apt package)
- GLI-FLOW versions prior to the environment resilience program (v1.0.0+)
