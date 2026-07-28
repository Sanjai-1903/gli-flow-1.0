# LVS Signoff Integrity Audit

## Status: CRITICAL — Signoff integrity broken

## Evidence Chain

### 1. LVS Launch

**File:** `gli_flow/backends/openroad_adapter.py:1165-1173`

```python
result = _run_with_env(
    [netgen_bin, "-batch", "lvs",
     f"{spice_path} {design_name}",
     circuit2_spec,       # ← BUG: multi-token single string
     setup_file,
     str(report_path)],
    cwd=run_dir,
    timeout=600,
)
```

**Actual command executed** (from instrumented trace):

```
/usr/bin/netgen-lvs -batch lvs \
  "/home/.../counter_lvs.spice counter" \
  "/home/.../sky130_fd_sc_hd.spice /home/.../6_final_lvs.v counter" \
  /home/.../sky130A_setup.tcl \
  /home/.../reports/lvs_report.txt
```

**Bug in `circuit2_spec` construction** (`openroad_adapter.py:1160-1162`):

```python
circuit2_spec = f"{clean_netlist} {design_name}"       # 2 tokens
if pdk_sc_spice:
    circuit2_spec = f"{pdk_sc_spice} {circuit2_spec}"   # 3 tokens → 1 string
```

Netgen receives `circuit2_spec` as a single list element: `"/path/to/spice /path/to/netlist.v counter"`. It tries to open a file with that entire space-containing string as the filename.

---

### 2. Netgen Result

**Trace data** (from `/tmp/netgen_trace.log`):

| Field | Value |
|-------|-------|
| PID | 11778 |
| Duration | 31ms (from trace timestamps) |
| Return code | **-6 (SIGABRT)** |
| stdout (truncated) | `Netgen 1.5.133...\nWarning: ...\nReading netlist file /home/.../counter_lvs.spice` |
| stderr (truncated) | `Error in SPICE file read: No file /home/.../sky130_fd_sc_hd.spice /home/.../6_final_lvs.v counter` |
| Report file exists? | **No** (`ls reports/lvs_report.txt` — file not found) |
| Report file size | N/A |

Netgen prints the startup banner, successfully reads the first circuit (`counter_lvs.spice`), then attempts to read the second circuit. Because `circuit2_spec` is a single argument with embedded spaces, netgen interprets the entire string as a filename. The file does not exist → netgen crashes with SIGABRT (rc=-6).

**Contrast with manual test** (same netgen version, malformed second arg):

```python
# Passing similar malformed args via subprocess
result = subprocess.run(
    ['/usr/bin/netgen-lvs', '-batch', 'lvs',
     '/tmp/test.spice counter',
     '/nonexistent/file.v counter',   # single file, works gracefully
     '/dev/null', '/tmp/out.txt'],
    capture_output=True, text=True)
# rc=0, graceful error message
```

With the actual `circuit2_spec` (two files + name in one string, e.g., `"spice_a spice_b name"`), netgen crashes with SIGABRT.

---

### 3. Parser Output

**File:** `gli_flow/backends/openroad_adapter.py:1265-1327`

```python
def _parse_lvs_report(self, report_path, result, runtime):
    report = Path(report_path)
    unmatched_devices = 0    # default
    unmatched_nets = 0       # default
    lvs_pass = False
```

**Stdout parsing** (lines 1276-1290):

| Regex pattern | Target text in stdout | Match? |
|--------------|----------------------|--------|
| `Circuit 1 contains (\d+) devices.*Circuit 2 contains (\d+)` | Not present (netgen crashed before comparison) | **No** |
| `Circuit 1 contains (\d+) nets.*Circuit 2 contains (\d+)` | Not present | **No** |
| `Netlists match` | Not present | **No** |

All counters remain at default (0).

**Report file parsing** (lines 1292-1311):

```python
if report.exists():      # ← False — netgen crashed before writing
```

Block skipped entirely.

**Fallback logic** (line 1315):

```python
is_clean = lvs_pass or (unmatched_devices == 0 and unmatched_nets <= 5)
#        = False or (0 == 0 and 0 <= 5)
#        = True   ← FALSE POSITIVE
```

**Result returned:**

```python
LVSResult(
    result="CLEAN",
    unmatched_devices=0,
    unmatched_nets=0,
    short_count=0,
    open_count=0,
    is_clean=True,
    runtime_seconds=83.9,  # includes Magic extraction time
)
```

---

### 4. Signoff Gate State

**File:** `gli_flow/core/orchestrator.py:857-859`

```python
lvs_result = self.adapter.run_lvs(...)   # returns is_clean=True (false positive)
if lvs_result.is_clean:
    self.signoff_gate.lvs_pass = True     # ← FALSE PASS APPROVED
```

**SignoffGate defaults:**
```python
class SignoffGate:
    lvs_pass: bool = False        # default: not passed
```

After LVS stage: **`lvs_pass = True`**.

**tapeout_ready** requires `lvs_pass` (line 138):
```python
def tapeout_ready(self) -> bool:
    return all([
        ...
        self.lvs_pass,            # ← True (false positive)
        ...
    ])
```

**blocking_failures** (line 154):
```python
if not self.lvs_pass:
    failures.append("LVS failed or report missing")
```
No failure appended.

---

### 5. Failure Atlas State

**File:** `failure_atlas/detector.py:93-108`

```python
lvs_result = metrics.get("lvs_result")     # "CLEAN"
if lvs_result and lvs_result.upper() == "FAIL":   # False → skipped
```

**No Failure Atlas entry created.** The crash, the missing report, and the false clean classification are invisible to the monitoring system.

---

### 6. Telemetry / Database State

**File:** `outputs/runs/run_*/drc_lvs_summary.json`

```json
{
  "drc": { "total_violations": 0, "is_clean": true },
  "lvs": {
    "result": "CLEAN",
    "unmatched_devices": 0,
    "unmatched_nets": 0,
    "short_count": 0,
    "open_count": 0,
    "is_clean": true,
    "runtime_seconds": 83.9
  }
}
```

**Missing telemetry fields:**
- `netgen_return_code` — not stored
- `report_exists` — not stored
- `report_size` — not stored
- `comparison_completed` — not stored
- `parser_status` — not stored

---

### 7. Final Run State

**Run summary** (`outputs/runs/run_*/run_summary.md`):
```
## Signoff Status
- **LVS**: PASS
- **Status**: SUCCESS
```

**User-facing output:**
```
  LVS                █████████████████░░  89%
  ...
✓ Run complete: ...
SUCCESS — /home/.../outputs/runs/run_...
```

---

### 8. Root Cause Summary

| Component | Issue | File:Line |
|-----------|-------|-----------|
| **Netgen invocation** | `circuit2_spec` packs 3 tokens into 1 list element — netgen receives a single filename with spaces | `openroad_adapter.py:1160-1162` |
| **Parser fallback** | Default zero counters (from crash) satisfy the "clean" condition | `openroad_adapter.py:1315` |
| **Signoff gate** | Blindly trusts `is_clean` without verifying comparison evidence | `orchestrator.py:858-859` |
| **Failure Atlas** | Only checks for `"FAIL"` string — `"CLEAN"` bypasses detection | `detector.py:93-94` |
| **Telemetry** | No crash/completion/report-existence fields stored | `orchestrator.py:860-867` |
| **LVSResult** | `to_tool_result()` hardcodes `execution_success=True`, `return_code=0` regardless of actual result | `openroad_adapter.py:119-128` |

---

### 9. Impact

| Claim | Actual |
|-------|--------|
| LVS PASS | **False** — netgen crashed, no comparison performed |
| Signoff approved | **False** — missing required verification |
| Failure Atlas healthy | **False** — crash is invisible |
| Tapeout ready | **False** — critical verification step skipped |
