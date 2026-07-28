# GLI-FLOW Reset Audit

Generated: 2026-06-12

## Purpose

Document all runtime-generated data locations targeted for deletion during a clean reset. Only execution artifacts, cached state, and historical records are removed. Source code, configuration, PDK, toolchain, Failure Atlas signatures, knowledge base, and dashboard code are preserved.

---

## 1. Run Output Directories

| Location | Contents | Size |
|----------|----------|------|
| `outputs/runs/` | 170 run directories, 13,021 files | 144 MB |

Each run directory contains:
- `artifacts/` — generated GDS, LEF, DEF files
- `logs/` — tool execution logs
- `reports/` — 24 report types (.rpt, .txt, .csv, .json)
- `results/` — final result outputs
- `telemetry/` — ~30 staged JSON files per run (metrics, synthesis, placement, routing, DRC, LVS, timing, etc.)
- `snapshots/` — runtime snapshots
- `config.json`, `drc_lvs_summary.json`, `reproducibility.json`, `sta_corners.json`, etc.

**Action:** Delete all contents of `outputs/runs/`. Keep the directory itself.

---

## 2. Database Records

### Database: `~/.gli_flow/gli_flow.db` (primary, 384 KB)

| Table | Records | Action |
|-------|---------|--------|
| `runs` | 169 | DELETE all rows |
| `failure_atlas_entries` | 473 | DELETE all rows |
| `schema_version` | 28 | PRESERVE (schema metadata) |

Schema, migrations, and table definitions are **preserved** in full.

### Database: `./gli_flow.db` (project-local, 56 KB)

| Table | Records | Action |
|-------|---------|--------|
| `runs` | 89 | DELETE all rows |
| `failure_atlas_entries` | 25 | DELETE all rows |
| `schema_version` | 11 | PRESERVE (schema metadata) |

### Run Status Distribution (home DB — most complete)
| Status | Count |
|--------|-------|
| SUCCESS | 100 |
| FAILED | 62 |
| RUNNING | 7 |

### Failure Type Distribution (home DB)
| Failure Type | Count |
|-------------|-------|
| TIMING | 108 |
| LOGIC | 64 |
| SIGNOFF_FAILURE | 53 |
| PIPELINE_FAILURE | 52 |
| DRC | 43 |
| CONGESTION | 43 |
| ROUTING | 42 |
| DRC_SPACING | 40 |
| POWER | 21 |
| LVS_OPEN_NET | 4 |
| LVS_DEVICE_MISMATCH | 3 |

**Important runs column (`is_important`):** Not present in either database (migration was never applied). No important run data exists.

---

## 3. Dashboard Cached Reports

| File | Size | Action |
|------|------|--------|
| `dashboard/health_report.json` | 388 B | DELETE (runtime-generated health summary) |
| `analytics/execution_report.json` | 87 B | DELETE (runtime-generated execution report) |
| `analytics/reliability_report.json` | 90 B | DELETE (runtime-generated reliability report) |
| `regression/regression_report.json` | 53 B | DELETE (runtime-generated regression state) |

---

## 4. Intelligence Runtime State

| File | Action |
|------|--------|
| `intelligence/adaptive_orchestration_report.json` | DELETE (run history report) |
| `intelligence/anomaly_history.json` | DELETE (execution anomaly history) |
| `intelligence/execution_confidence.json` | DELETE (cached confidence score) |
| `intelligence/execution_recommendations.json` | DELETE (empty runtime state) |
| `intelligence/latest_diagnostics.json` | DELETE (empty runtime state) |
| `intelligence/learning_memory.json` | DELETE (execution pattern memory) |

**Preserved (configuration/knowledge base):**
- `intelligence/orchestration_policy.json`
- `intelligence/scoring_policy.json`
- `intelligence/recommendation_db.json`
- `intelligence/warning_signatures.json`

---

## 5. Execution History & Provenance

| File | Action |
|------|--------|
| `execution_history/run_index.json` | DELETE (empty array — runtime index) |
| `provenance/provenance_graph.json` | DELETE (empty graph — runtime state) |

---

## 6. Preserved Items (NOT Modified)

| Category | Items |
|----------|-------|
| Source code | All `.py` files, `cli/`, `core/`, `database/`, `config/`, `runtime/`, `telemetry/` Python packages |
| Configuration files | `configs/runtime/default.json`, `gli_flow/config/defaults.py`, dashboard configs |
| PDK installation | `~/.gli-flow/pdk/` |
| Toolchain installation | `~/.gli-flow/orfs/` |
| Failure Atlas signatures | `failure_atlas/signatures/` (6 files), `failure_atlas/signatures.json`, `failure_atlas/knowledge_base.json` |
| Failure Atlas records | `failure_atlas/records/` (5 documented failure records) |
| Failure Atlas static data | `failure_atlas/remediation_db.json`, `failure_atlas/qor_playbook.json`, `failure_atlas/stale_venv_interpreter.json`, `failure_atlas/failure_schema_v1.json`, `failure_atlas/schemas/` |
| Dashboard code | `dashboard/` (Vite + React app), `backend/server.py` |
| Documentation | `docs/` directory contents |
| Database schema & migrations | Table definitions, `schema_version` records |
| Intelligence config | `orchestration_policy.json`, `scoring_policy.json`, `recommendation_db.json`, `warning_signatures.json` |

---

## Summary of Deletions

| Item | Quantity | Size |
|------|----------|------|
| Run output directories | 170 | 144 MB |
| Database run records | 258 (169 + 89) | — |
| Database failure atlas entries | 498 (473 + 25) | — |
| Dashboard cache files | 4 | ~618 B |
| Intelligence state files | 6 | ~900 B |
| Other runtime state files | 2 | ~4 B |
| Telemetry JSON files | ~4,689 | included in run dirs |
| **Total** | **~13,000+ files** | **~144 MB** |
