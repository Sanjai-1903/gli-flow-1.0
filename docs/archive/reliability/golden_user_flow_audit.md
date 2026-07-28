# Golden User Flow Audit

**Date:** 2026-06-12  
**Test:** End-to-end first-time user experience from clean state

---

## Flow Tested

```
1. gli-flow setup
2. gli-flow doctor
3. gli-flow quickstart
4. gli-flow run examples/counter --mock
5. gli-flow dashboard
```

---

## Step 1: `gli-flow setup --non-interactive`

### Result: ✅ PASS

| Aspect | Verdict |
|--------|---------|
| Creates config | ✅ `~/.gli-flow/config.yaml` created |
| Creates workspace | ✅ Workspace directory created |
| Validates PDK | ✅ Checks PDK root exists, warns if missing |
| Telemetry prompt | ✅ Respects `--telemetry` flag |
| Clear next steps | ✅ Shows doctor/quickstart/run suggestions |

### Issues
- `--non-interactive` flag is not mentioned in the help description's first line
- No `--workspace` default shown in help (defaults to `~/gli-flow-workspace`)

---

## Step 2: `gli-flow doctor`

### Result: ✅ PASS

| Aspect | Verdict |
|--------|---------|
| Tool detection | ✅ All 10+ tools checked with version detection |
| PDK validation | ✅ sky130A and sky130B verified |
| ORFS validation | ✅ ORFS root and tools found |
| Database health | ✅ Schema up to date |
| Magic discovery | ✅ Binary validated |
| Repair capability | ✅ `--fix` runs 7 repair actions |
| Output clarity | ✅ Color-coded PASS/FAIL/WARN/INFO |

### Issues
- Output is very long (50+ lines). User may not read all sections.
- "HISTORICAL-RISK" tag on magic version 8.3.105 may alarm new users without context

---

## Step 3: `gli-flow quickstart`

### Result: ✅ PASS

| Aspect | Verdict |
|--------|---------|
| Interactive prompt | ✅ Asks for design name |
| No-RTL fallback | ✅ Creates boilerplate SystemVerilog file |
| RTL directory created | ✅ `rtl/` dir with `.sv` file |
| Manifest created | ✅ `gli_manifest.yaml` with correct values |
| Next steps | ✅ Shows `gli-flow run <name> --mock` |

### Issues
- No `--help` content beyond usage line (no description, no examples)
- `--non-interactive` flag would be useful for scripting

---

## Step 4: `gli-flow run examples/counter --mock`

### Result: ✅ PASS

| Aspect | Verdict |
|--------|---------|
| Manifest validation | ✅ `gli_manifest.yaml` validated |
| Environment checks | ✅ Mock mode skips real tool checks |
| Pipeline execution | ✅ All 30 stages run to completion |
| Stage progress | ✅ Progress bar with percentage |
| QoR metrics | ✅ QoR=0.6, WNS=0.0, TNS=0.0, Util=65% |
| Cross-tool DRC | ✅ Magic + KLayout DRC consistency check |
| LVS verification | ✅ Pass/fail reported |
| Run summary | ✅ Markdown summary generated |
| DB recording | ✅ Run recorded in database |

### Issues
- `--mock` flag is essential but might not be discovered by new users (not mentioned in `run --help` first line)
- Output is very verbose with 30 stage lines — may overwhelm new users
- `gli_manifest.yaml` path is assumed but auto-discovery could be more helpful

---

## Step 5: `gli-flow dashboard`

### Result: ⚠️ NOT TESTED IN HEADLESS ENV

| Aspect | Verdict |
|--------|---------|
| Backend starts | ❓ Requires uvicorn — not tested |
| Frontend serves | ❓ Requires npm or dist build — not tested |
| Browser opens | ❓ Requires display (X11/WSL) — not tested |
| Ctrl+C handling | ⚠️ Process termination logic present but untested |

### Issues
- No dependency check for uvicorn before starting
- No health check / ready signal before opening browser
- No fallback message if prerequisites are missing
- `--backend-only` flag useful but not clearly documented

---

## Summary

| Step | Command | Status | Issues |
|------|---------|--------|--------|
| 1 | `setup` | ✅ PASS | Minor help text polish |
| 2 | `doctor` | ✅ PASS | Output verbosity |
| 3 | `quickstart` | ✅ PASS | No `--help` detail |
| 4 | `run --mock` | ✅ PASS | `--mock` discoverability |
| 5 | `dashboard` | ⚠️ UNTESTED | Dependency checks needed |

### Confusion Points Identified

1. **`--mock` flag** — critical for first-time users but not highlighted in help. Users who run `gli-flow run examples/counter` without `--mock` will fail if tools aren't installed.
2. **`gli_manifest.yaml`** — users need to understand this file exists. `init`/`quickstart` create it, but the concept needs explanation.
3. **Output verbosity** — `run` shows 30 stage lines which may overwhelm. A summary-only mode would help.
4. **Dashboard prerequisites** — no clear error message if uvicorn or npm is missing.

### Recommendations

1. Add `--mock` usage example to `run --help`
2. Add summary-only mode to `run` (suppress stage progress)
3. Add dependency pre-check to `dashboard` before starting processes
