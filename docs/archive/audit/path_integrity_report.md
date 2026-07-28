# Path Integrity Report

## Audit Date: 2026-06-17

File path audit following repository reorganization. Searches codebase for `open()`, `Path()`, `os.path.*` references that point to moved or deleted locations.

---

## Blocking Issues (Will Cause Runtime Failure)

| # | File | Line | Path Reference | Status |
|:-:|:-----|:----:|:---------------|:-------|
| 1 | `backend/server.py` | 1233 | `from telemetry.telemetry_manager import TelemetryManager` | BROKEN — telemetry moved to outputs/ |
| 2 | `dashboard/src/RunDetail.jsx` | 286 | `fetch(\`/runs/${run_id}/failures\`)` | BROKEN — no backend route |
| 3 | `gli_flow/investigation/availability.py` | 28 | `Path(...) / "config" / "ai_investigation.yaml"` | BROKEN — config → configs/ |
| 4 | `gli_flow/investigation/investigator.py` | 33 | `Path(...) / "config" / "ai_investigation.yaml"` | BROKEN — config → configs/ |
| 5 | `tests/investigation/test_investigation_layer.py` | 169 | `Path(...) / "config" / "ai_investigation.yaml"` | BROKEN — config → configs/ |
| 6 | `gli_flow/cli/main.py` | 348 | `project_root / "execution_history"` | BROKEN → outputs/execution_history/ |
| 7 | `manifests/generate_manifest.py` | 63 | `os.makedirs("execution_history", ...)` | BROKEN → outputs/execution_history/ |
| 8 | `manifests/generate_manifest.py` | 67 | `f"execution_history/manifest_..."` | BROKEN → outputs/execution_history/ |
| 9 | `environment/reproducibility_check.py` | 6 | `"execution_history"` in string list | BROKEN → outputs/execution_history/ |
| 10 | `environment/reproducibility_check.py` | 8 | `"telemetry"` in string list | BROKEN → outputs/telemetry/ |
| 11 | `environment/reproducibility_check.py` | 17 | `"execution_history/correlate_runs.py"` | BROKEN → outputs/execution_history/ |
| 12 | `environment/reproducibility_check.py` | 18 | `"telemetry/collect_metrics.py"` | BROKEN → outputs/telemetry/ |
| 13 | `outputs/snapshots/create_snapshot.py` | 6 | `ROOT_DIR = Path.home() / "GLI" ...` | BROKEN — hardcoded user path |
| 14 | `scripts/inject_test_failures.py` | 5 | `DB_PATH = "/home/gli/.gli_flow/gli_flow.db"` | BROKEN — hardcoded user path |

---

## Misleading User-Facing Strings

| # | File | Line | String | Status |
|:-:|:-----|:----:|:-------|:-------|
| 15 | `availability.py` | 118 | `config/ai_investigation.yaml` | MISLEADING → configs/ |
| 16 | `availability.py` | 161 | `config/ai_investigation.yaml` | MISLEADING → configs/ |
| 17 | `availability.py` | 175 | `config/ai_investigation.yaml` | MISLEADING → configs/ |
| 18 | `investigator.py` | 133 | `config/ai_investigation.yaml` | MISLEADING → configs/ |
| 19 | `investigator.py` | 276 | `config/ai_investigation.yaml` | MISLEADING → configs/ |

---

## Stale Documentation Links

| # | File | Line | Old Reference | New Location |
|:-:|:-----|:----:|:--------------|:-------------|
| 20 | `dashboard/src/HelpPage.jsx` | 5 | `/docs/USER_MANUAL.md` | `docs/user_guide/USER_MANUAL.md` |
| 21 | `docs/setup/quickstart.md` | 111 | `docs/USER_MANUAL.md` | `docs/user_guide/` |
| 22 | `docs/setup/quickstart.md` | 113 | `docs/telemetry_pipeline_audit.md` | `docs/developer/` |
| 23 | `docs/reliability/external_beta_readiness_v1.md` | 175-203 | 11 refs to old paths | Various |
| 24 | `docs/reliability/documentation_truth_audit.md` | 90-112 | 10 refs to old paths | Various |
| 25 | `docs/audit/ONBOARDING_READINESS_REPORT.md` | 16,22 | `docs/getting-started.md` | `docs/user_guide/` |
| 26 | `docs/reliability/magic_8_3_105_audit.md` | 31 | `FIRST_PASS_REPORT.md` | `docs/audit/` |
| 27 | `failure_atlas/records/INF-MAGIC-001.json` | 10 | `FIRST_PASS_REPORT.md` | `docs/audit/` |
| 28 | `docs/productization/mvp_certification.md` | 164 | `run_systolic.py` | `scripts/` |
| 29 | `docs/user_guide/user_manual.md` | 7 | `docs/setup/installation.md` | needs verification |
| 30 | `docs/user-guide/riscv_project_structure.md` | 11,54 | `config/`, `telemetry/` | `configs/`, `outputs/telemetry/` |

---

## Legacy / Informational Only (No Fix Needed)

These paths document the reorganization but don't cause functional issues:
- `docs/audit/repository_inventory.md` — lists what was moved
- `docs/audit/repository_structure_certification_v1.md` — documents metrics
- `docs/audit/repository_refactor_certification_v1.md` — (this document)
- `.gitignore` — `handover.md` rule (file no longer exists)

---

## Summary

| Category | Count | Status |
|:---------|:-----:|:-------|
| Blocking (will crash) | 14 | Must fix |
| Misleading strings | 5 | Should fix |
| Stale doc links | 11 | Should fix |
| Informational | 4 | No fix needed |
| **Total** | **34** | |
