# First-Time User CLI Audit

**Generated:** 2026-06-12  
**Test scenario:** Brand-new user workflow from scratch

---

## Recommended Workflow

```
1. gli-flow setup
2. gli-flow doctor
3. gli-flow run examples/counter --mock
4. gli-flow dashboard
```

---

## Step 1: `gli-flow setup`

### Result: ✅ WORKS (non-interactive)

```
GLI-FLOW Setup
  • PDK location
  • EDA tool paths
  • Workspace directory
  • Telemetry preference

✓ Configuration saved to ~/.gli-flow/config.yaml
✓ PDK root: /home/bolter/.gli-flow/pdk
✓ Created workspace: /home/bolter/gli-flow-workspace
✓ Telemetry: enabled

Setup complete!
  gli-flow doctor     — validate EDA tools
  gli-flow quickstart — run your first design
  gli-flow run examples/counter — run the counter example
```

**Exit code:** 0 | **Runtime:** 0.25s

**Notes:**
- Interactive mode (`--non-interactive` flag for automation) works
- Creates `~/.gli-flow/config.yaml`
- Validates PDK root existence, creates workspace directory
- Suggests next steps (doctor, quickstart, run examples/counter)

**Confusion risk:** Low. Prompts are clear, defaults are reasonable.

---

## Step 2: `gli-flow doctor`

### Result: ✅ WORKS

```
GLI-FLOW Doctor — Environment Health Report
  SYSTEM:    PASS
  TOOLS:     PASS (git, cmake, yosys, openroad, klayout, netgen, sv2v, magic)
  DATABASE:  PASS
  PDK:       PASS
  DOCKER:    INFO
  ORFS:      PASS
  NETWORK:   PASS
  PERMISSIONS: PASS

READY FOR TAPEOUT FLOW
```

**Exit code:** 0 | **Runtime:** 3.5s

**Notes:**
- Runs actual tool version checks and smoke tests (not just `--version`)
- Doctor with `--fix` runs 7 repair actions (cache cleanup, schema repair)
- Magic discovery shows all installed magic binaries with validation
- `--repair-magic` flag for fixing path shadowing issues

**Confusion risk:** Low. Output is well-structured with status colors.

---

## Step 3: `gli-flow run examples/counter --mock`

### Result: ✅ WORKS

Runs a full 30-stage ASIC flow pipeline in mock mode:
```
INITIALIZING → SYNTHESIS → FLOORPLANNING → PLACEMENT → CTS →
ROUTING → DRC → LVS → TIMING_ANALYSIS → SIGN_OFF → ...

Duration: 42.0s (mock)
QoR Score: 0.6
WNS: 0.0
TNS: 0.0
Utilization: 65.0%
Cell Count: 100
```

**Exit code:** 0 | **Runtime:** 3.8s

**Notes:**
- Mock mode requires no EDA tools installed
- Runs all pipeline stages with simulated execution
- Produces run summary, telemetry, and database records
- Cross-tool DRC analysis with consistency checking
- LVS verification step included

**Confusion risk:** Medium — user sees "30 stages" which may be overwhelming. The `--mock` flag is essential for first runs but not obvious.

**First-run telemetry notice** is shown automatically (informative, not blocking).

---

## Step 4: `gli-flow dashboard`

### Result: ⚠️ NOT FULLY TESTED

The dashboard command starts:
1. Backend: `uvicorn backend.server:app` (port 8000)
2. Frontend: `npm run dev` (port 5173)

**Issues:**
- Requires backend source at `backend/server.py`
- Frontend requires `dashboard/dist/index.html` (built assets) or `npm` for dev server
- Opens browser automatically (may fail in headless/WSL environments)
- No `Ctrl+C` handler output visible in capture

**Confidence:** Untested in this session — should be tested in a GUI environment.

---

## Step 5: Additional First-User Commands

### `gli-flow quickstart`
**Result:** ✅ WORKS  
Interactive wizard that creates a design directory, RTL file, and manifest.  
Prompts for design name, auto-detects RTL if present in directory.

### `gli-flow history` / `gli-flow status`
**Result:** ✅ WORKS  
Shows clean table of past runs. If no runs exist, shows "No runs found."

### `gli-flow init <name>`
**Result:** ✅ WORKS  
Creates `gli_manifest.yaml` with sensible defaults. Supports `--rtl-dir` for auto-detection.

### `gli-flow config`
**Result:** ✅ WORKS  
Shows current telemetry setting. `--telemetry on|off` to change.

### `gli-flow upgrade-check`
**Result:** ✅ WORKS (graceful offline)  
Checks PyPI + GitHub for newer version. Handles offline gracefully.

---

## Summary

| Step | Command | Status | Runtime |
|------|---------|--------|---------|
| 1 | `setup` | ✅ Works | 0.25s |
| 2 | `doctor` | ✅ Works | 3.5s |
| 3 | `run --mock` | ✅ Works | 3.8s |
| 4 | `dashboard` | ⚠️ Untested | — |

**Overall first-time experience:** Positive. All core workflow commands work. The `--mock` flag is the key enabler for new users without EDA tools installed.
