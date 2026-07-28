# Signoff Decision Engine Audit

**Date**: 2026-06-20  
**Scope**: Full trace of `signoff_status`, `execution_status`, `tapeout_ready` computation  

---

## 1. Architecture Overview

```
Orchestrator.run()
  │
  ├── SignoffGate (dataclass)
  │     ├── 15 boolean fields (synth_ok, gds_present, ..., formal_pass)
  │     ├── tapeout_ready property (all() check)
  │     └── blocking_failures() (list of reasons)
  │
  ├── Stage runners (DRC, LVS, TIMING_ANALYSIS, etc.)
  │     └── Set SignoffGate fields via direct assignment
  │
  ├── RootCauseEngine.analyze()
  │     └── _check_signoff_status() — OVERWRITES signoff_status
  │
  ├── update_run() → SQLite DB
  │
  ├── API endpoints (backend/server.py)
  │     └── SELECT tapeout_ready, implementation_status, signoff_status
  │
  └── Dashboard (RunDetail.jsx)
        └── Renders PASS/FAILED/NOT_RUN with color badges
```

---

## 2. Status Values Currently in Use

| Field | Possible Values | Source |
|---|---|---|
| `implementation_status` | `NOT_STARTED`, `SUCCESS`, `FAILED` | orchestrator.py |
| `signoff_status` | `NOT_RUN`, `PASS`, `FAILED` | root_cause_engine.py + orchestrator.py |
| `tapeout_ready` | `True`, `False` | SignoffGate.tapeout_ready property |

**Missing**: `CONDITIONAL_PASS`, `INCOMPLETE`

---

## 3. Decision Path Trace

### 3.1 SignoffGate Definition
**File**: `gli_flow/core/orchestrator.py:113-163`

```python
@dataclass
class SignoffGate:
    synth_ok: bool = False
    gds_present: bool = False
    def_present: bool = False
    netlist_present: bool = False
    setup_pass: bool = False
    hold_pass: bool = False
    magic_drc_pass: bool = False
    klayout_drc_pass: bool = False
    antenna_pass: bool = False
    density_pass: bool = False
    lvs_pass: bool = False
    em_pass: bool = False
    si_pass: bool = False
    power_pass: bool = False
    formal_pass: bool = False

    @property
    def tapeout_ready(self) -> bool:
        return all([...15 bools...])
```

**Problem**: `all()` returns `False` if ANY check is `NOT_RUN`, `ERROR`, or a false-positive failure. There is no distinction between:
- Check ran and found real violations → FAIL
- Check never ran → INCOMPLETE
- Check ran but found only false positives → CONDITIONAL

### 3.2 DRC Gate Setting
**File**: `gli_flow/core/orchestrator.py:1041-1048`

```python
if magic_data.get("run"):
    self.signoff_gate.magic_drc_pass = magic_data.get("violations", -1) == 0
else:
    self.signoff_gate.magic_drc_pass = False
```

**Problem**: If Magic DRC reports 2 violations (even known false positives like `licon.8a`), `magic_drc_pass = False`. There's no false-positive filtering. KLayout DRC is set independently but the `all()` gate ANDs them.

### 3.3 LVS Gate Setting
**File**: `gli_flow/core/orchestrator.py:1084-1087`

```python
if (lvs_result.status == LVSStatus.PASS
        and lvs_result.comparison_completed
        and lvs_result.report_exists):
    self.signoff_gate.lvs_pass = True
```

**Problem**: If LVS times out (status = NOT_RUN), `lvs_pass` stays `False` (default). The timeout is indistinguishable from a failed comparison.

### 3.4 Timing Gate Setting
**File**: `gli_flow/core/orchestrator.py:1147-1148`

```python
self.signoff_gate.setup_pass = True
self.signoff_gate.hold_pass = True
```

Only set to True when timing completes without raising `TapeoutBlockingError`. If timing is skipped (no adapter, exception), both stay `False` (default). Again, no distinction from actual violations.

### 3.5 Main Signoff Assignment
**File**: `gli_flow/core/orchestrator.py:1373-1391`

```python
tapeout_ready = self.signoff_gate.tapeout_ready
signoff_was_run = drc_lvs_path.exists() or magic_drc.rpt exists

if not gds_generated:
    signoff_status = "NOT_RUN"
elif tapeout_ready:
    signoff_status = "PASS"
elif signoff_was_run:
    signoff_status = "FAILED"     # <-- conflates all non-PASS into FAILED
else:
    signoff_status = "NOT_RUN"
```

**Problem**: `signoff_was_run` is true if DRC or LVS report exists → even if LVS timed out, signoff_status = "FAILED".

### 3.6 RootCauseEngine Overwrite
**File**: `gli_flow/reliability/root_cause_engine.py:1398-1399`

```python
self.record.signoff_status = root_cause_report.signoff_status
self.record.tapeout_ready = root_cause_report.tapeout_ready
```

The RootCauseEngine **overwrites** the orchestrator's assignment. Its `_check_signoff_status()` method (lines 425-476) recomputes signoff_status from `drc_lvs_summary.json` independently. This creates a dual-source-of-truth problem.

### 3.7 RootCauseEngine `_check_signoff_status`
**File**: `gli_flow/reliability/root_cause_engine.py:425-476`

```python
has_lvs_result = "status" in lvs    # True even if status is "NOT_RUN"!
all_pass = drc_clean and lvs_clean if has_drc_result and has_lvs_result else False
if has_drc_result and not has_lvs_result:
    all_pass = False

if signoff_checks_run:
    if all_pass:
        signoff_status = "PASS"
    else:
        signoff_status = "FAILED"
```

**Critical bugs**:
1. `has_lvs_result` is True when LVS status is "NOT_RUN" (the key exists in the JSON)
2. `all_pass = drc_clean and lvs_clean` → both must be True. But for picorv32: drc_clean=False (2 violations), lvs_clean=False (NOT_RUN) → all_pass=False → FAILED
3. No LVS → all_pass forced False → FAILED (even if DRC is clean)
4. No check for timing files at all in the signoff_status decision

### 3.8 Tapeout Ready Computation (RootCauseEngine)
**File**: `gli_flow/reliability/root_cause_engine.py:469-473`

```python
has_blocking_root_cause = any(rc.severity == "TAPEOUT_BLOCKING" for rc in report.root_causes)
report.tapeout_ready = (
    report.implementation_status == "SUCCESS"
    and report.signoff_status == "PASS"
    and not has_blocking_root_cause
)
```

**Problem**: tapeout_ready requires signoff_status == "PASS", but there's no path for CONDITIONAL_PASS. If false positives exist, signoff_status = "FAILED" → tapeout_ready = False.

### 3.9 Database Storage
**File**: `gli_flow/database/sqlite.py:94-169`

The `update_run()` method stores `signoff_status` as TEXT and `tapeout_ready` as INTEGER (0/1). No additional columns for evidence_gaps, blocking_reasons, or failure classification.

### 3.10 API Layer
**File**: `backend/server.py:130-194, 298-333`

Both `GET /runs` and `GET /runs/{run_id}` return:
- `tapeout_ready` (bool)
- `implementation_status` (string)
- `signoff_status` (string)
- `signoff_score` (float)

No evidence_gaps, blocking_reasons, or classification detail.

### 3.11 Dashboard Rendering
**File**: `dashboard/src/RunDetail.jsx:21-70, 1137-1144`

```javascript
const signoffColor = run.signoff_status === "PASS" ? "text-green-600" 
    : run.signoff_status === "FAILED" ? "text-red-600" 
    : "text-[#6B7280]"
const tapeoutColor = run.tapeout_ready ? "text-green-600" : "text-red-600"
```

Header badges (lines 1140-1144):
```javascript
{run.signoff_status === "PASS" ? "bg-green-100 text-green-700" 
    : run.signoff_status === "NOT_RUN" ? "bg-gray-100 text-gray-500" 
    : "bg-red-100 text-red-700"}
{run.tapeout_ready ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}
```

**Problems**:
1. No rendering for `CONDITIONAL_PASS` or `INCOMPLETE` statuses
2. tapeout_ready is binary green/red — no CONDITIONAL display
3. No evidence gaps shown in the UI
4. No blocking reasons shown in the header

---

## 4. Ground Truth Comparison

### GCD (run_1781952813_5f415aee_gcd)

| Check | Result | True Status | Real Blocker? | Current Classification |
|---|---|---|---|---|
| Magic DRC (licon.8a) | 2 violations | FALSE POSITIVE | NO | FAILED |
| KLayout DRC | 0 violations | TRUE PASS | NO | PASS |
| LVS | PASS | TRUE PASS | NO | PASS |
| Setup Timing | WNS=0.0 | TRUE PASS | NO | PASS |
| Hold Timing | 0.452ns slack | TRUE PASS | NO | PASS |
| Antenna | PASS | TRUE PASS | NO | PASS |
| Density | CMD NOT FOUND | FLOW BUG | NO | FAILED |
| EM/IR | PASS | TRUE PASS | NO | PASS |
| Formal | PASS | TRUE PASS | NO | PASS |
| **Composite** | — | **CONDITIONAL PASS** | **NO** | **FAILED** |

### PicoRV32 (run_1781952921_92ee0437_picorv32)

| Check | Result | True Status | Real Blocker? | Current Classification |
|---|---|---|---|---|
| Magic DRC (licon.8a) | 2 violations | FALSE POSITIVE | NO | FAILED |
| KLayout DRC | 0 violations | TRUE PASS | NO | PASS |
| LVS | TIMEOUT (NOT_RUN) | INCOMPLETE | NEEDS INVESTIGATION | FAILED |
| Setup Timing | WNS=0.0 | TRUE PASS | NO | PASS |
| Hold Timing | 0.079ns slack | TRUE PASS | NO | PASS |
| Antenna | PASS | TRUE PASS | NO | PASS |
| Density | CMD NOT FOUND | FLOW BUG | NO | FAILED |
| CDC | NOT PERFORMED | INCOMPLETE | NEEDS EXTERNAL TOOL | NOT TRACKED |
| EM/IR | PASS | TRUE PASS | NO | PASS |
| Formal | PASS | TRUE PASS | NO | PASS |
| **Composite** | — | **INCOMPLETE** | **LVS & CDC gaps** | **FAILED** |

---

## 5. Specific Bugs Found

### Bug 1: NOT_RUN Conflated with FAILED
- **File**: `root_cause_engine.py:441`
- **Code**: `has_lvs_result = "status" in lvs`
- **Effect**: LVS status key exists with value "NOT_RUN" → `has_lvs_result = True` → forces `all_pass = False` → signoff_status = "FAILED"
- **Severity**: HIGH

### Bug 2: Dual Source of Truth
- **File**: `orchestrator.py:1397-1399`
- **Code**: `self.record.signoff_status = root_cause_report.signoff_status`
- **Effect**: RootCauseEngine independently recomputes and overwrites the orchestrator's assignment
- **Severity**: MEDIUM

### Bug 3: No False-Positive Filtering
- **File**: `orchestrator.py:1041-1042`
- **Code**: `magic_drc_pass = magic_data.get("violations", -1) == 0`
- **Effect**: Known false-positive licon.8a violations block signoff
- **Severity**: HIGH

### Bug 4: Timing Not Required for Signoff Status
- **File**: `root_cause_engine.py:452-466`
- **Effect**: `_check_signoff_status` only checks DRC and LVS, not timing
- **Severity**: MEDIUM

### Bug 5: CDC Gap Not Tracked
- **File**: `orchestrator.py` (no CDC awareness)
- **Effect**: CDC analysis is mentioned in the console output but never affects signoff status
- **Severity**: MEDIUM

### Bug 6: Density Command Bug Treated as Failure
- **File**: `orchestrator.py:1198-1199`
- **Code**: `self.signoff_gate.density_pass = result.is_clean`
- **Effect**: When `check_density` command doesn't exist, `result.is_clean` defaults to False
- **Severity**: LOW (only affects educational runs)

### Bug 7: Binary Score Mapping
- **File**: `root_cause_engine.py:475-476`
- **Code**: `signoff_score = 1.0 if signoff_status == "PASS" else 0.0`
- **Effect**: No partial credit — CONDITIONAL_PASS and INCOMPLETE both get 0.0
- **Severity**: LOW

---

## 6. Data Flow Diagram

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│ Stage       │     │ SignoffGate       │     │ RootCause    │
│ Runners     │────>│ (15 bools)        │────>│ Engine       │
│ (DRC, LVS,  │     │ tapeout_ready()   │     │ overrides    │
│  STA, ...)  │     │ blocking_failures │     │ status again │
└─────────────┘     └────────┬─────────┘     └──────┬───────┘
                             │                      │
                             ▼                      ▼
                     ┌────────────────────────────────┐
                     │    Orchestrator.run()           │
                     │    (lines 1366-1493)            │
                     │                                 │
                     │ if tapeout_ready → PASS         │
                     │ elif signoff_was_run → FAILED   │
                     │ else → NOT_RUN                  │
                     │                                 │
                     │ THEN overwritten by             │
                     │ RootCauseEngine result          │
                     └───────────────┬─────────────────┘
                                     │
                                     ▼
                            ┌────────────────┐
                            │  SQLite DB      │
                            │  runs table     │
                            │  signoff_status │
                            │  tapeout_ready  │
                            └───────┬────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │  Backend API      │
                          │  GET /runs/{id}   │
                          └───────┬──────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Dashboard       │
                         │  RunDetail.jsx   │
                         │  Green/Red badge │
                         └─────────────────┘
```

---

## 7. Recommended Changes

1. **New status model**: PASS, CONDITIONAL_PASS, INCOMPLETE, FAIL
2. **Centralized classifier**: Single `SignoffClassifier` class
3. **Evidence-based decisions**: Track false positives, flow bugs, evidence gaps
4. **CDC awareness**: Track CDC status explicitly
5. **NOT_RUN vs FAILED separation**: Check actual completion status, not just key existence
6. **Dashboard updates**: Show evidence gaps and blocking reasons in addition to status badge
7. **tapeout_ready**: CONDITIONAL_PASS → tapeout_ready = CONDITIONAL (not just YES/NO)
