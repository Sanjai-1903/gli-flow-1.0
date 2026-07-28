# OpenSTA Timing Reality Audit v1

**Date**: 2026-06-18
**Status**: **FAILED** — Signoff STA pipeline is fundamentally broken

---

## Executive Summary

The timing extraction pipeline has a **critical structural defect** that causes OpenSTA to always report WNS=0.0, TNS=0.0 during signoff, regardless of actual timing closure. The system relies on a separate, parallel timing extraction path (the ORFS flow-stage reports) that operates correctly. However, the official signoff STA path (which populates `sta_corners.json`, `signoff_setup.rpt`, and the telemetry `corner_results` field) is broken.

The three certified designs (counter@10ns, gcd@10ns, uart@10ns) all have genuine positive slack (7.08, 7.35, 3.41 ns respectively), so the WNS=0.0 from the broken signoff pipeline happened to be accidentally correct. But the mechanism itself cannot detect timing failures.

A dedicated negative-slack test (counter@2ns clock) confirmed: real slack = -0.85ns, but signoff STA reported WNS=0.0.

---

## Phase 1 — Timing Source Locations

| Design | Run ID | Run Dir |
|--------|--------|---------|
| counter (10ns) | `run_1781762766_864b637c_counter` | `/home/bolter/gli-flow/outputs/runs/run_1781762766_864b637c_counter` |
| gcd (10ns) | `run_1781762825_cce688a0_gcd` | `/home/bolter/gli-flow/outputs/runs/run_1781762825_cce688a0_gcd` |
| uart (10ns) | `run_1781762983_cd0d6189_uart_top` | `/home/bolter/gli-flow/outputs/runs/run_1781762983_cd0d6189_uart_top` |
| counter (2ns, tight) | `run_1781779144_11679db8_counter` | `/home/bolter/gli-flow/outputs/runs/run_1781779144_11679db8_counter` |

### Key Files Per Run

| File | Path (relative to run dir) | Contains |
|------|---------------------------|----------|
| OpenSTA signoff report | `signoff_setup.rpt` | WNS/TNS from `report_wns`/`report_tns` |
| OpenSTA hold report | `signoff_hold.rpt` | Worst hold slack from `report_worst_slack` |
| OpenSTA signoff log | `signoff_log.txt` | Full OpenROAD log for signoff STA |
| Signoff TCL script | `signoff.tcl` | TCL commands executed by signoff STA |
| STA corners JSON | `sta_corners.json` | Structured timing results per corner |
| ORFS flow-stage report | `reports/6_finish.rpt` | ORFS-internal timing (includes `report_wns`/`report_tns`) |
| Metrics CSV | `reports/metrics.csv` | Key-value metrics from ORFS backend |
| Telemetry metrics | `telemetry/metrics.json` | Uploaded telemetry payload |
| OpenROAD flow log | `logs/openroad.log` | Full ORFS flow log covering all stages |
| SDC constraints | `artifacts/6_final.sdc` | Final timing constraints used by ORFS |

---

## Phase 2 — OpenSTA Report Inventory

### counter (10ns) — `run_1781762766_864b637c_counter`

| File | Size | Timestamp |
|------|------|-----------|
| `signoff_setup.rpt` | 26 B | 06:06:52 |
| `signoff_hold.rpt` | 17 B | 06:06:52 |
| `signoff_log.txt` | 1097 B | 06:06:52 |
| `signoff.tcl` | 916 B | 06:06:52 |
| `sta_corners.json` | 226 B | 06:06:52 |
| `reports/6_finish.rpt` | 24810 B | 06:06:37 |
| `reports/metrics.csv` | 120 B | 06:06:52 |

### gcd (10ns) — `run_1781762825_cce688a0_gcd`

| File | Size | Timestamp |
|------|------|-----------|
| `signoff_setup.rpt` | 26 B | 06:09:35 |
| `signoff_hold.rpt` | 17 B | 06:09:35 |
| `signoff_log.txt` | 354 B | 06:09:35 |
| `signoff.tcl` | 436 B | 06:09:35 |
| `sta_corners.json` | 226 B | 06:09:35 |
| `reports/6_finish.rpt` | 21808 B | 06:08:10 |
| `reports/metrics.csv` | 120 B | 06:08:10 |

### uart (10ns) — `run_1781762983_cd0d6189_uart_top`

| File | Size | Timestamp |
|------|------|-----------|
| `signoff_setup.rpt` | 26 B | 06:12:47 |
| `signoff_hold.rpt` | 17 B | 06:12:47 |
| `signoff_log.txt` | 1105 B | 06:12:47 |
| `signoff.tcl` | 921 B | 06:12:47 |
| `sta_corners.json` | 226 B | 06:12:47 |
| `reports/6_finish.rpt` | 27732 B | 06:11:14 |
| `reports/metrics.csv` | 120 B | 06:11:14 |

### counter (2ns, tight) — `run_1781779144_11679db8_counter`

| File | Size | Timestamp |
|------|------|-----------|
| `signoff_setup.rpt` | 26 B | 10:39:57 |
| `signoff_hold.rpt` | 17 B | 10:39:57 |
| `signoff_log.txt` | 1105 B | 10:39:57 |
| `signoff.tcl` | 916 B | 10:39:57 |
| `sta_corners.json` | 226 B | 10:39:57 |
| `reports/6_finish.rpt` | 27732 B | 10:39:43 |
| `reports/metrics.csv` | 120 B | 10:39:43 |

All report timestamps fall within the execution window of each run. No pre-existing files.

---

## Phase 3 — Ground Truth Extraction

### counter (10ns) — from `reports/6_finish.rpt`

```
finish report_wns:        wns 0.00
finish report_tns:        tns 0.00
finish worst_slack:       7.08
critical path delay:      0.919
critical path slack:      7.081
```

### gcd (10ns) — from `reports/6_finish.rpt`

```
finish report_wns:        wns 0.00
finish report_tns:        tns 0.00
finish worst_slack:       7.35
critical path delay:      2.805
critical path slack:      7.348
```

### uart (10ns) — from `reports/6_finish.rpt`

```
finish report_wns:        wns 0.00
finish report_tns:        tns 0.00
finish worst_slack:       3.41
critical path delay:      1.092
critical path slack:      3.408
```

### counter (2ns, tight) — from `reports/6_finish.rpt`

```
finish report_wns:        wns -0.85         ← NEGATIVE SLACK
finish report_tns:        tns -6.48
finish worst_slack:       -0.85
```

All ground truth values extracted manually from ORFS flow-stage report files.

---

## Phase 4 — Parser Trace

### Two Independent Timing Extraction Paths

```
          ORFS Path (CORRECT)                        Signoff Path (BROKEN)
          ==================                         =====================

ORFS internal STA                                    OpenROAD batch STA
(has .lib loaded by main flow)                       (NO .lib loaded — missing read_liberty)
          |                                                    |
          v                                                    v
  reports/N_finish.rpt                                  signoff.tcl
  (report_wns, report_tns)                              (signoff.tcl lines 1-15)
          |                                                    |
          v                                                    v
  _write_backend_metrics()                              read_lef X 2
  (openroad_adapter.py:760)                             read_def
          |                                             read_sdc
          v                                             read_spef
  reports/metrics.csv                                   report_wns → signoff_setup.rpt
  (wns,-0.85)                                           report_tns → signoff_setup.rpt
          |                                             report_worst_slack → signoff_hold.rpt
          v                                                    |
  TelemetryParser.parse_timing()                              v
  (telemetry/parser.py:60)                             _parse_wns_from_report()
  reads metrics.csv via _parse_csv()                   (openroad_adapter.py:639)
          |                                             _parse_tns_from_report()
          v                                             (openroad_adapter.py:648)
  parsed["wns"] = -0.85                                       |
  parsed["tns"] = -6.48                                       v
          |                                             run_timing_signoff()
          v                                             (openroad_adapter.py:2776)
  _extract_metrics()                                    TimingSignoffResult
  (orchestrator.py:292)                                 setup_wns_ns = 0.0  ← BROKEN
  record.wns = -0.85                                    setup_tns_ns = 0.0
  record.tns = -6.48                                            |
          v                                                    v
  Database: runs.wns = -0.85                           Database: runs.setup_wns_ns = 0.0
  Database: runs.tns = -6.48                           Database: runs.setup_tns_ns = 0.0
          |                                                    |
          v                                                    v
  telemetry/metrics.json                                telemetry/metrics.json
  "metrics": {"wns": -0.85, "tns": -6.48}              "corner_results": [{"setup_wns": 0.0, "setup_tns": 0.0}]
```

### Root Cause — `_write_signoff_tcl` missing `read_liberty`

**File**: `gli_flow/backends/openroad_adapter.py:2739-2772`

```python
def _write_signoff_tcl(self, run_dir, pdk) -> str:
    # Generates signoff.tcl with commands:
    content = f"""{lef_script}
read_def {def_path}
read_sdc {sdc_path}
read_spef {spef_path}
tee -variable _wns_out {{report_wns -digits 5}}
...
"""
```

The script reads LEF (physical), DEF (netlist), SDC (constraints), and SPEF (parasitics), but **never calls `read_liberty`**. Without the `.lib` liberty timing library file, OpenSTA has no standard cell timing models. It cannot compute cell delays, setup/hold checks, or arrival times. As a result, `report_wns` and `report_tns` always return 0.0 because there are no known timing arcs to violate.

For contrast, the ORFS flow loads the liberty file during the main flow via `read_liberty` (in ORFS scripts, not in gli-flow's `_write_signoff_tcl`), which is why the flow-stage reports (`6_finish.rpt`) have correct timing values.

### Parser Regex Validation

Each parser was verified against the actual file content:

| Parser | File | File Content | Regex | Match | Result |
|--------|------|-------------|-------|-------|--------|
| `_parse_wns_from_report` | `signoff_setup.rpt` | `wns 0.00000` | `r"wns\s+(-?[\d.]+)"` | `0.00000` | `0.0` |
| `_parse_tns_from_report` | `signoff_setup.rpt` | `tns 0.00000` | `r"tns\s+(-?[\d.]+)"` | `0.00000` | `0.0` |
| `_parse_csv` | `metrics.csv` | `wns,-0.85` | csv reader | `-0.85` | `-0.85` |
| `_parse_csv` | `metrics.csv` | `tns,-6.48` | csv reader | `-6.48` | `-6.48` |

The parsers work correctly. The data they consume is the problem.

---

## Phase 5 — Zero Value Investigation

### counter (10ns): WNS = 0.0 → Classification: **A** (report correctly contains 0.0)
- `signoff_setup.rpt`: `wns 0.00000` — root cause: missing `read_liberty`
- `reports/6_finish.rpt`: `wns 0.00` — actual slack is +7.08ns, so WNS=0 is correct
- The 10ns constraint is easily met by this 8-bit counter

### gcd (10ns): WNS = 0.0 → Classification: **A** (report correctly contains 0.0)
- `signoff_setup.rpt`: `wns 0.00000` — root cause: missing `read_liberty`
- `reports/6_finish.rpt`: `wns 0.00` — actual slack is +7.35ns, so WNS=0 is correct
- The 10ns constraint is easily met by this GCD design

### uart (10ns): WNS = 0.0 → Classification: **A** (report correctly contains 0.0)
- `signoff_setup.rpt`: `wns 0.00000` — root cause: missing `read_liberty`
- `reports/6_finish.rpt`: `wns 0.00` — actual slack is +3.41ns, so WNS=0 is correct
- The 10ns constraint is met by this UART design despite 13 hold violations in the finish stage (all resolved by signoff)

### counter (2ns, tight): WNS = 0.0 → Classification: **B** (report shows 0.0 despite actual negative slack)
- `signoff_setup.rpt`: `wns 0.00000` — root cause: missing `read_liberty` — THIS IS WRONG
- `reports/6_finish.rpt`: `wns -0.85` — CORRECT ground truth
- The 2ns constraint causes real timing violations (WNS=-0.85, TNS=-6.48)
- The signoff STA pipeline fails to detect them

---

## Phase 6 — Consistency Audit

### Timing Values Across All Sources

| Design | Source | WNS | TNS | Worst Slack | Consistent? |
|--------|--------|-----|-----|-------------|-------------|
| **counter (10ns)** | `signoff_setup.rpt` | 0.0 | 0.0 | — | ✅ With self |
| | `reports/6_finish.rpt` | 0.0 | 0.0 | 7.08 | ✅ With self |
| | `metrics.csv` | 0.0 | 0.0 | — | ✅ |
| | Database `runs.wns/tns` | 0.0 | 0.0 | — | ✅ |
| | `sta_corners.json` | 0.0 | 0.0 | — | ✅ |
| | Telemetry `metrics.wns` | 0.0 | 0.0 | — | ✅ |
| | Telemetry `corner_results.setup_wns` | 0.0 | 0.0 | — | ✅ |
| **gcd (10ns)** | `signoff_setup.rpt` | 0.0 | 0.0 | — | ✅ |
| | `reports/6_finish.rpt` | 0.0 | 0.0 | 7.35 | ✅ |
| | `metrics.csv` | 0.0 | 0.0 | — | ✅ |
| | Database | 0.0 | 0.0 | — | ✅ |
| | Telemetry | 0.0 | 0.0 | — | ✅ |
| **uart (10ns)** | `signoff_setup.rpt` | 0.0 | 0.0 | — | ✅ |
| | `reports/6_finish.rpt` | 0.0 | 0.0 | 3.41 | ✅ |
| | `metrics.csv` | 0.0 | 0.0 | — | ✅ |
| | Database | 0.0 | 0.0 | — | ✅ |
| | Telemetry | 0.0 | 0.0 | — | ✅ |
| **counter (2ns)** | `signoff_setup.rpt` | **0.0** | **0.0** | — | ❌ **MISMATCH** |
| | `reports/6_finish.rpt` | **-0.85** | **-6.48** | -0.85 | ✅ Ground truth |
| | `metrics.csv` | **-0.85** | **-6.48** | — | ✅ Correct |
| | Database `runs.wns/tns` | **-0.85** | **-6.48** | — | ✅ Correct |
| | Database `runs.setup_wns_ns` | **0.0** | **0.0** | — | ❌ **WRONG** |
| | `sta_corners.json` | **0.0** | **0.0** | — | ❌ **WRONG** |
| | `setup_satisfied` | **true** | — | — | ❌ **WRONG** |
| | `hold_satisfied` | **true** | — | — | ✅ (hold is fine) |
| | Telemetry `metrics.wns` | -0.85 | -6.48 | — | ✅ Correct |
| | Telemetry `corner_results.setup_wns` | **0.0** | **0.0** | — | ❌ **WRONG** |

### Mismatch Summary

The counter@2ns run reveals a clear inconsistency:

- **`metrics.csv` and `runs.wns/runs.tns`**: Correct (WNS=-0.85, TNS=-6.48) — from ORFS flow-stage path
- **`signoff_setup.rpt`, `sta_corners.json`, `runs.setup_wns_ns`**: Wrong (WNS=0.0, TNS=0.0) — from broken signoff STA path
- **Telemetry payload contains both correct and incorrect values** in different fields

---

## Phase 7 — Fallback Detection

### Critical Fallback Patterns (can silently mask timing failures)

| # | File | Line | Pattern | Risk |
|---|------|------|---------|------|
| 1 | `openroad_adapter.py` | 2815 | `return TimingSignoffResult(0, 0.0, 0.0, 0.0, 0.0, 0.0, False, ...)` | STA exception returns all-zero result |
| 2 | `openroad_adapter.py` | 2819-2822 | `setup_wns = 0.0; setup_tns = 0.0; ...` | Unparseable report silently = 0.0 |
| 3 | `telemetry/parser.py` | 600-601 | `setup_wns = 0.0; setup_tns = 0.0` | Unparseable report silently = 0.0 |
| 4 | `telemetry/parser.py` | 615 | `setup_wns is not None and setup_wns >= 0` | `is not None` is dead code (always True) |
| 5 | `openroad_adapter.py` | 2797 | `self._parse_tns_from_report(setup_report) or 0.0` | TNS parsing failure → 0.0 |
| 6 | `openroad_adapter.py` | 2801 | `self._parse_ths_from_report(hold_report) or 0.0` | THS parsing failure → 0.0 |
| 7 | `readiness_correlation.py` | 12-13 | `telemetry.get("wns", 0)` | Missing WNS/TNS → 0 |
| 8 | `failure_atlas/repository.py` | 277-278 | `.get("wns", 0) or 0` | Double-default → 0 |
| 9 | `backend/server.py` | 861-862 | `.get("wns", 0) or 0` | Double-default → 0 |
| 10 | `prediction/similarity.py` | 29-30, 42-43 | `.get("wns", 0)` | Missing timing → 0 in similarity |
| 11 | `explanation_engine.py` | 307 | `if wns is None or wns == 0: return None` | WNS=0.0 conflated with missing data |

Total: **11 distinct fallback locations** that can silently convert missing/broken timing data into a zero value.

### Most Dangerous

Items #2 and #3 (`= 0.0` initialization in timing parsers): If `signoff_setup.rpt` exists and is readable but contains no matching WNS/TNS lines, the parser returns `setup_wns_ns=0.0`, `setup_tns_ns=0.0`, and `setup_satisfied=True` — a perfect signoff pass — when in reality timing data was never read.

---

## Phase 8 — Negative Slack Test

### Design
counter (8-bit register-based) with 2.0ns clock period (fmax = 500 MHz target).

### SDC
```
create_clock -name clk -period 2.000 [get_ports clk]
```

### Results

| Metric | Expected | Actual | Source |
|--------|----------|--------|--------|
| WNS (ORFS flow) | < 0 | **-0.85** | `reports/6_finish.rpt` |
| TNS (ORFS flow) | < 0 | **-6.48** | `reports/6_finish.rpt` |
| Worst Slack | < 0 | **-0.85** | `reports/6_finish.rpt` |
| Setup Violations | > 0 | **8** | `reports/metrics.csv` |
| WNS (Signoff STA) | should be -0.85 | **0.00000** | `signoff_setup.rpt` ❌ |
| TNS (Signoff STA) | should be -6.48 | **0.00000** | `signoff_setup.rpt` ❌ |
| Worst Slack (Signoff STA) | should be -0.85 | **INF** | `signoff_hold.rpt` |

### Verdict: Negative slack detected by ORFS flow, **NOT detected by signoff STA**

The correct path (`reports/6_finish.rpt` → `metrics.csv` → `runs.wns`) correctly captures the negative slack.
The broken path (`signoff.tcl` → `signoff_setup.rpt` → `runs.setup_wns_ns`) fails to detect it.

### Pipeline survival test

| Stage | WNS | TNS | Survived? |
|-------|-----|-----|-----------|
| OpenSTA (ORFS flow, correct) | -0.85 | -6.48 | ✅ |
| `reports/6_finish.rpt` | -0.85 | -6.48 | ✅ |
| `reports/metrics.csv` | -0.85 | -6.48 | ✅ |
| `TelemetryParser.parse_timing()` | -0.85 | -6.48 | ✅ |
| `orchestrator._extract_metrics()` | -0.85 | -6.48 | ✅ |
| Database `runs.wns` / `runs.tns` | -0.85 | -6.48 | ✅ |
| Telemetry `metrics.wns` / `metrics.tns` | -0.85 | -6.48 | ✅ |
| OpenSTA (signoff, broken) | **0.0** | **0.0** | ❌ |
| `signoff_setup.rpt` | **0.00000** | **0.00000** | ❌ |
| `sta_corners.json` | **0.0** | **0.0** | ❌ |
| Database `runs.setup_wns_ns` | **0.0** | **0.0** | ❌ |
| Telemetry `corner_results.setup_wns` | **0.0** | **0.0** | ❌ |

---

## Phase 9 — Telemetry Timing Audit

The telemetry payload (`telemetry/metrics.json`) contains **both** timing values in different sections:

### Counter (2ns) Telemetry Extract

```json
{
  "metrics": {
    "wns": -0.85,
    "tns": -6.48,
    ...
  },
  "corner_results": [
    {
      "setup_satisfied": true,
      "hold_satisfied": true,
      "setup_wns": 0.0,
      "setup_tns": 0.0,
      "hold_wns": Infinity,
      "hold_tns": 0.0
    }
  ]
}
```

**Correct in `metrics`**: wns=-0.85, tns=-6.48 — from ORFS flow-stage path
**Wrong in `corner_results`**: setup_wns=0.0, setup_tns=0.0, setup_satisfied=true — from broken signoff STA path

The telemetry upload (`telemetry_audit_log`) confirms successful upload, meaning the corrupted data was transmitted to the server.

### Telemetry Audit Log

| Run | Timestamp | Status |
|-----|-----------|--------|
| counter (10ns) | 06:06:53 | success |
| gcd (10ns) | 06:09:35 | success |
| uart (10ns) | 06:12:48 | success |
| counter (2ns) | Not uploaded (server not running) | — |

---

## Phase 10 — Final Verdict

### Classification: **FAILED** ❌

### Success Criteria Evaluation

| Criterion | Result |
|-----------|--------|
| OpenSTA reports exist | ✅ `signoff_setup.rpt` exists for all runs |
| Timing values originate from reports | ❌ Signoff report values originate from missing `read_liberty`, not actual timing |
| No hidden fallback-to-zero behavior | ❌ **11 fallback-to-zero locations found** (items 1-11 in Phase 7) |
| `metrics.csv` matches reports | ❌ `metrics.csv` matches `6_finish.rpt` (correct), but signoff reports disagree |
| Dashboard matches metrics | ⚠️ Dashboard API not verified (server not running) |
| Telemetry matches reports | ❌ Telemetry `corner_results` contradicts telemetry `metrics` within the same payload |
| Negative slack survives entire pipeline | ❌ Negative slack survives ORFS path but is lost in signoff STA path |

### Evidence Summary

1. **`_write_signoff_tcl` is missing `read_liberty`** (`openroad_adapter.py:2739-2772`). Without the timing library, OpenSTA always returns WNS=0, TNS=0.

2. **The ORFS flow-stage path is correct** — `reports/6_finish.rpt` contains accurate timing from OpenROAD's internal STA (which has the `.lib` loaded). `metrics.csv` correctly extracts these values.

3. **The negative slack test proves the bug**: Counter@2ns has WNS=-0.85 (from ORFS), but signoff STA says WNS=0.00000.

4. **For the 3 certified designs, the values happen to be correct** because all have positive slack. The mechanism is broken but the numbers happen to be right by coincidence.

5. **Telemetry contains contradictory timing data inside the same payload** — `metrics.wns=-0.85` while `corner_results.setup_wns=0.0`.

### Recommendations

1. **Add `read_liberty` to `_write_signoff_tcl`**: Include the PDK liberty file (`.lib`) to enable proper STA timing analysis during signoff.

2. **Add `read_db` support**: Alternatively, use OpenDB's `.db` library format which bundles LEF, liberty, and other data.

3. **Audit the `or 0.0` fallback pattern**: Replace silent fallback-to-zero with explicit error propagation for TNS/THS parsing (consistent with how WNS/WHS already raise errors on `None`).

4. **Fix `telemetry/parser.py` initialization**: Replace `setup_wns = 0.0` with `setup_wns = None` so that parsing failures produce `None` rather than `0.0`.

5. **Validate consistency between the two timing paths**: Add a cross-check that warns if `runs.wns` and `runs.setup_wns_ns` disagree.
