# Mock Mode Inventory v1

**Date:** 2026-06-21
**Scope:** Full repository audit of all mock, synthetic, and fake execution code paths
**Auditor:** Automated codebase analysis

## Classification System

| Class | Definition |
|---|---|
| `user-requested mock` | User explicitly passes `--mock` to activate |
| `fallback mock` | Code silently falls back to synthetic data when real tools fail |
| `hidden mock` | Mock invoked indirectly without user awareness |
| `certification risk` | Path that could silently invalidate certification |
| `test-only` | Only used in tests (acceptable) |

---

## 1. User-Requested Mock

### 1.1 CLI Argument Definition
**File:** `gli_flow/cli/main.py:2489-2490`
```python
run_parser.add_argument("--mock", action="store_true",
    help="Run with mock EDA adapter (no real tools required)")
```

### 1.2 CLI Handler Chains
**File:** `gli_flow/cli/main.py`
- Line 546: `if not getattr(args, 'mock', False):` — conditional behavior
- Line 556: `backend = "mock" if getattr(args, 'mock', False) else "local"`
- Line 558-577: Validates design path only when not mock
- Line 577: `mock=getattr(args, 'mock', False)` — passed to orchestrator

### 1.3 Orchestrator Mock Mode
**File:** `gli_flow/core/orchestrator.py:190-208`
```python
def __init__(self, ..., mock: bool = False, ...):
    self._mock_mode = mock
```

**Line 222-225:** Adapter selection
```python
if mock:
    from gli_flow.testing.mock_adapter import MockEDAAdapter
    self.adapter = MockEDAAdapter(pdk_root=self.pdk_root, pdk=self.pdk)
```

**Lines 1442-1453:** FORCES all signoff gates to PASS
```python
if self._mock_mode:
    self.signoff_gate.magic_drc_pass = True
    self.signoff_gate.klayout_drc_pass = True
    self.signoff_gate.antenna_pass = True
    self.signoff_gate.density_pass = True
    self.signoff_gate.em_pass = True
    self.signoff_gate.si_pass = True
    self.signoff_gate.power_pass = True
    self.signoff_gate.formal_pass = True
    self._check_results = {k: CheckResult.PASS for k in [...]}
```

### 1.4 MockEDAAdapter
**File:** `gli_flow/testing/mock_adapter.py` (367 lines, 30+ methods)

Every method returns synthetic/hardcoded results. Key examples:

| Method | Line | Returns |
|---|---|---|
| `run()` | 75 | Writes `fake_gds_data`, `// mock netlist` |
| `run_drc()` | 272 | `DRCResult(0, {}, [], True)` — clean |
| `run_lvs()` | 280 | `LVSResult(status=LVSStatus.PASS, ...)` |
| `run_antenna_check()` | 194 | `AntennaResult(0, [], 0.0, True)` |
| `run_density_check()` | 239 | `DensityResult(45.0, 20.0, 85.0, 0)` |
| `run_timing_signoff()` | 347 | `TimingSignoffResult(setup_satisfied=True, hold_satisfied=True)` |
| `run_klayout_drc()` | 326 | `DRCResult(0, {}, [], True)` |

---

## 2. Fallback Mock (Certification Risk)

All in `gli_flow/backends/openroad_adapter.py` — the **production** adapter silently returns synthetic results when real EDA tools fail:

### 2.1 Antenna Check (Line 2600)
```python
return AntennaResult(0, [], 0.0, True, runtime_seconds=time.time() - t_start)
```
**Risk:** `check_antennas` command not supported → returns `is_clean=True` (PASS)

### 2.2 Density Check (Line 2731)
```python
return DensityResult(0.0, 15.0, 85.0, 0, runtime_seconds=runtime)
```
**Risk:** `check_density` command not found → returns hardcoded PASS with PDK min/max values

### 2.3 Post-Fill Density (Line 2695)
```python
return DensityResult(0.0, 0.0, 0.0, 0, runtime_seconds=time.time() - t_start)
```

### 2.4 EM Check (Line 1721)
```python
return EMCheckResult(0, [], 0.0, 0.0, True, runtime_seconds=time.time() - t_start)
```
**Risk:** Failure returns `is_clean=True`

### 2.5 SI Analysis (Line 2128)
```python
return SIResult(0, [], 0.0, 0, True, runtime_seconds=time.time() - t_start)
```
**Risk:** Failure returns `is_clean=True`

### 2.6 Formal Verification (Line 2506)
```python
return FormalResult(0, 0, 0, True, runtime_seconds=time.time() - t_start)
```
**Risk:** Failure returns `is_equivalent=True`

### 2.7 Power Analysis (Lines 1616-1619)
```python
return PowerResult(total_power_mw=0.0, leakage_mw=0.0, ...)
```

### 2.8 LVS (Lines 1152-1166)
```python
return LVSResult(status=LVSStatus.NOT_RUN, ...)
return LVSResult(status=LVSStatus.ERROR, ...)
```
**Risk:** GDS not found, extraction failure, netgen missing — all return NOT_RUN instead of failing

### 2.9 Magic DRC (Line 815)
```python
return DRCResult(0, {}, [], False, runtime_seconds=time.time() - t_start)
```
**Risk:** Timeout returns zero violations, does NOT mark as failure

### 2.10 LVS Timeout (Lines 1231-1232)
```python
return LVSResult(status=LVSStatus.ERROR, runtime_seconds=time.time() - t_start,
                  return_code=-2, parser_status="timeout")
```
**Risk:** Returns ERROR instead of FAIL, does NOT raise or block tapeout

### 2.11 Orchestrator Mock Gate Force (Lines 1442-1453)
```python
if self._mock_mode:
    self.signoff_gate.magic_drc_pass = True
    ...
```
**Risk:** ALL signoff gates force PASS regardless of actual results

### 2.12 Orchestrator Mock Gate Suppression (Line 1456)
```python
if gate_errors and not self._mock_mode:
```
**Risk:** Release gate errors are suppressed

---

## 3. Hidden Mock

| Count | Location | Risk |
|---|---|---|
| 1 | `orchestrator.py:1442-1453` — `if self._mock_mode:` block | `certification risk` |

---

## 4. Test-Only

| File | Line(s) | Content |
|---|---|---|
| `tests/test_mock_adapter.py` | 1-72 | MockEDAAdapter tests |
| `tests/e2e/test_mock_pipeline.py` | 1-127 | Mock pipeline tests (includes `mock=True` orchestrator) |
| `tests/integration/test_e2e_counter.py` | 36, 70-154 | `--mock` CLI invocation; synthetic result assertions |
| `tests/adversarial/lvs/test_lvs_adversarial.py` | 5 | `MockResult` class |
| `tests/signoff/test_lvs_comparison_evidence_required.py` | 16 | `MockResult` class |
| `tests/reliability/test_lvs_false_clean_prevention.py` | 6 | `MockResult` class |
| `tests/test_installer.py` | 10, 171-247 | `unittest.mock` usage |
| `tests/investigation/test_investigation_layer.py` | 7, 155-158 | `unittest.mock` usage |
| `tests/investigation/test_availability.py` | 7, 161-335 | `unittest.mock` usage |
| `tests/resolution_intelligence/test_resolution.py` | 8 | `unittest.mock` usage |
| `tests/regressions/test_magic_version_selection.py` | 19-87 | Mock magic binaries |
| `tests/regressions/test_path_shadowing_prefers_functional_binary.py` | 32-269 | Mock magic binaries |
| `.github/workflows/ci.yml` | 81-104 | Mock adapter import validation |
| `scripts/beta_simulation.py` | 14, 19-76 | Imports MockEDAAdapter, uses hardcoded QoR |
| `gli_flow/synthetic/` | All files | ML dataset generation (not production flow) |

---

## 5. Critical Certification Risks (Must Fix)

| Priority | File | Line | Issue | Current Behavior |
|---|---|---|---|---|
| P0 | `openroad_adapter.py` | 2731 | Density unsupported → fake PASS | Returns `DensityResult(0.0, 15.0, 85.0, 0)` |
| P0 | `openroad_adapter.py` | 2600 | Antenna unsupported → fake PASS | Returns `is_clean=True` |
| P0 | `openroad_adapter.py` | 1721 | EM check fail → fake PASS | Returns `is_clean=True` |
| P0 | `openroad_adapter.py` | 2128 | SI analysis fail → fake PASS | Returns `is_clean=True` |
| P0 | `openroad_adapter.py` | 2506 | Formal fail → fake clean | Returns `is_equivalent=True` |
| P0 | `openroad_adapter.py` | 1152-1166 | LVS fail → NOT_RUN | Silently skips LVS |
| P0 | `openroad_adapter.py` | 815 | DRC timeout → zero violations | Returns clean result |
| P0 | `orchestrator.py` | 1442-1453 | Mock mode forces ALL PASS | Overrides signoff gates |
| P0 | `orchestrator.py` | 1456 | Mock mode suppresses gate errors | Hides release gate failures |

---

## 6. Remediation Plan

1. **Add `--certify` flag** and `CERTIFICATION_MODE` env var
2. **In certification mode:**
   - Reject `--mock` with hard error
   - All fallback mocks raise `CertificationError` instead of returning synthetic data
   - Validate all EDA tools and PDK upfront
3. **Fix global fallback mocks** (even outside certification mode):
   - Change density uncheckable → `FLOW_BUG` not `PASS`
   - Change antenna uncheckable → `FLOW_BUG` not `PASS`
   - Change LVS failures → raise `StageFailure` not `NOT_RUN`
4. **Never use `--mock` for certification** — add automated guard
