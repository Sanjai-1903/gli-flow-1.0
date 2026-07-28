# Import Integrity Report

## Audit Date: 2026-06-17

Python import audit following repository reorganization (config/→configs/, telemetry/→outputs/telemetry/, execution_history/→outputs/execution_history/, etc.)

---

## CRITICAL — ModuleNotFoundError Risks

### 1. `backend/server.py:1233` — `from telemetry.telemetry_manager import TelemetryManager`

**Problem:** Top-level `telemetry/` directory was moved to `outputs/telemetry/`. This import will raise `ModuleNotFoundError` when the `toggle_important_run()` endpoint is called.

**Fix:** Change to `from gli_flow.telemetry.manager import TelemetryManager`

---

## HIGH — Broken Config Paths

### 2. `gli_flow/investigation/availability.py:28`
```python
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "ai_investigation.yaml"
```
**Problem:** `config/` renamed to `configs/`. Should be `configs/ai_investigation.yaml`.

### 3. `gli_flow/investigation/investigator.py:33`
```python
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "ai_investigation.yaml"
```
**Problem:** Same as above.

### 4. `tests/investigation/test_investigation_layer.py:169`
```python
actual_config = Path(__file__).parent.parent.parent / "config" / "ai_investigation.yaml"
```
**Problem:** Same as above.

### 5. `gli_flow/cli/main.py:1802`
```python
files_to_include.append((str(p), f"config/{cfg_file}"))
```
**Problem:** Should be `configs/{cfg_file}`.

---

## HIGH — Broken Execution History / Telemetry Paths

### 6. `manifests/generate_manifest.py:63,67`
```python
os.makedirs("execution_history", exist_ok=True)
filename = f"execution_history/manifest_{timestamp}.json"
```
**Problem:** Will create/use wrong directory. Should be `outputs/execution_history/`.

### 7. `environment/reproducibility_check.py:6,8,17,18`
```python
"execution_history", "telemetry",
"execution_history/correlate_runs.py", "telemetry/collect_metrics.py"
```
**Problem:** References root-level directories. Files now at `outputs/execution_history/` and `outputs/telemetry/`.

### 8. `gli_flow/cli/main.py:348,369`
```python
exec_hist_dir = project_root / "execution_history"
"execution_history/run_index.json": [],
```
**Problem:** CLI reset command references old path. Should be `outputs/execution_history/`.

---

## HIGH — User-Facing Messages with Old Paths

### 9. `gli_flow/investigation/availability.py:118,161,175`
- `config/ai_investigation.yaml (set enabled: true)`
- `config/ai_investigation.yaml under provider.model`
- `config/ai_investigation.yaml`

### 10. `gli_flow/investigation/investigator.py:133,276`
- `config/ai_investigation.yaml`

---

## HIGH — Hardcoded Absolute User Paths

### 11. `scripts/inject_test_failures.py:5`
```python
DB_PATH = "/home/gli/.gli_flow/gli_flow.db"
```

### 12. `outputs/snapshots/create_snapshot.py:6`
```python
ROOT_DIR = Path.home() / "GLI" / "tapeitout.com" / "gli-flow"
SNAPSHOT_ROOT = ROOT_DIR / "snapshots"  # plus telemetry, execution_history refs
```

### 13. `examples/uart/run_uart.py:11`
```python
ORFS = Path(os.environ.get("ORFS_ROOT", "/home/gli/OpenROAD-flow-scripts"))
```

---

## MEDIUM — Dashboard Route Missing

### 14. `dashboard/src/RunDetail.jsx:286`
```javascript
fetch(`${API_BASE}/runs/${run.run_id}/failures?${params}`)
```
**Problem:** No backend route `GET /runs/{run_id}/failures` exists. Closest: `GET /failures` (all failures) or `GET /runs/{run_id}/investigation`.

---

## MEDIUM — Stale Documentation Cross-References

| File | Lines | Old Path | New Path |
|------|-------|----------|----------|
| `dashboard/src/HelpPage.jsx:5` | 5 | `docs/USER_MANUAL.md` | `docs/user_guide/USER_MANUAL.md` |
| `docs/setup/quickstart.md` | 111-113 | `docs/USER_MANUAL.md`, `docs/telemetry_pipeline_audit.md` | `docs/user_guide/`, `docs/developer/` |
| `docs/reliability/external_beta_readiness_v1.md` | 175-203 | 11 refs to old `docs/` paths | Various subdirs |
| `docs/reliability/documentation_truth_audit.md` | 90-112 | 10 refs to old `docs/` paths | Various subdirs |
| `docs/audit/ONBOARDING_READINESS_REPORT.md` | 16,22 | `docs/getting-started.md` | `docs/user_guide/getting-started.md` |
| `docs/reliability/magic_8_3_105_audit.md:31` | 31 | `FIRST_PASS_REPORT.md` | `docs/audit/FIRST_PASS_REPORT.md` |
| `failure_atlas/records/INF-MAGIC-001.json:10` | 10 | `MAGIC_ROOT_CAUSE.md`, `FIRST_PASS_REPORT.md` | `docs/audit/` |
| `docs/productization/mvp_certification.md:164` | 164 | `run_systolic.py` | `scripts/run_systolic.py` |
| `docs/user_guide/user_manual.md:7` | 7 | `docs/setup/installation.md` | Relative link needs verification |
| `docs/user-guide/riscv_project_structure.md` | 11,54 | `config/`, `telemetry/` | `configs/`, `outputs/telemetry/` |

---

## LOW — `.gli_flow/` vs `.gli-flow/` Inconsistency

**11 files** use `~/.gli_flow/` (underscore), **1 file** `~/.gli-flow/` (hyphen):
- Default config: `gli_flow/config/defaults.py:17` → `~/.gli-flow/gli_flow.db`
- All others: → `~/.gli_flow/gli_flow.db`

This is a data split-brain risk.

---

## Summary

| Severity | Count | Key Issues |
|----------|-------|------------|
| CRITICAL | 1 | Broken import in `backend/server.py` |
| HIGH | 13 | Config paths, execution_history paths, hardcoded absolute paths |
| MEDIUM | 2 | Dashboard missing route, stale doc refs |
| LOW | 20+ | Documentation cross-references, name inconsistency |
