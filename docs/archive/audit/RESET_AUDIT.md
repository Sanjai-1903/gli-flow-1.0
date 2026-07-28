# RESET AUDIT — GLI-FLOW Run History Clean Slate

**Date:** 2026-06-11  
**Auditor:** GLI-FLOW Developer Tooling

---

## 1. Database

### SQLite Database
| Property | Value |
|----------|-------|
| Location | `~/.gli-flow/gli_flow.db` |
| Size | 0 bytes (empty) |
| Engine | SQLite3 |

### Current Table State
| Table | Record Count | Status |
|-------|-------------|--------|
| `runs` | 0 (table does not exist) | Empty |
| `failure_atlas_entries` | 0 (table does not exist) | Empty |
| `schema_version` | 0 (table does not exist) | Empty |

> **Note:** The database file exists but no migrations have been applied. All tables are absent.

---

## 2. Filesystem — Run Outputs

### `outputs/runs/`
| Metric | Count |
|--------|-------|
| Run directories | 147 |
| Total disk usage | 307 MB |
| Image files (webp/png/jpg) | 710 |
| Report files (.rpt) | 1,016 |
| Telemetry-related files | 4,319 |

Each run directory contains:
- `config.json` — run configuration
- `drc_lvs_summary.json` — DRC/LVS results
- `sta_corners.json` — STA corner results
- `reproducibility.json` — Reproducibility manifest
- `run_summary.md` — Human-readable summary
- `logs/` — Stage logs
- `reports/` — Reports and images (`.rpt`, `.json`, `.webp`, `.png`)
- `artifacts/` — Artifact manifest and outputs
- `results/` — GDS, DEF, etc.
- `snapshots/` — Intermediate snapshots
- `telemetry/` — Telemetry metrics JSON files

---

## 3. Filesystem — Aggregated Reports & Analytics

### Trend Data
| File | Size | Content |
|------|------|---------|
| `trends/historical_trends.json` | 436 B | 2 historical snapshots (5 runs each) |
| `trends/predictive_report.json` | ~80 B | Empty header, no risk detected |

### Analytics Reports
| File | Size | Content |
|------|------|---------|
| `analytics/execution_report.json` | 87 B | `total_runs: 5`, no failures |
| `analytics/reliability_report.json` | 90 B | `score: 100`, `STABLE` |

### Regression Reports
| File | Size | Content |
|------|------|---------|
| `regression/regression_report.json` | 53 B | No regressions detected |

### Execution History
| File | Size | Content |
|------|------|---------|
| `execution_history/run_index.json` | 957 B | 5 archived runs (run_001–run_005) |
| `execution_history/manifest_20260512_122626.json` | — | Run manifest |
| `execution_history/manifest_20260512_123606.json` | — | Run manifest |

### PPA Metrics
| File | Size | Content |
|------|------|---------|
| `ppa/metrics_history.json` | 208 B | 1 run entry |

### Dashboard
| File | Size | Content |
|------|------|---------|
| `dashboard/health_report.json` | 388 B | `total_runs: 5`, STABLE |

### Provenance
| File | Size | Content |
|------|------|---------|
| `provenance/provenance_graph.json` | 10 KB | DAG with 29 nodes referencing old runs |

### Root-level Generated Images
| File | Description |
|------|-------------|
| `final_all.png` | Final chip layout |
| `final_clocks.png` | Clock tree visualization |
| `final_ir_drop.png` | IR drop analysis |
| `final_placement.png` | Placement visualization |
| `final_routing.png` | Routing visualization |
| `uart_gds.png` | UART GDS visualization |

---

## 4. Output Reports

### `outputs/reports/`
| File | Type |
|------|------|
| `lvs_command_integrity_validation.json` | Validation report |
| `lvs_command_integrity_validation.md` | Validation report |
| `lvs_integrity_validation_report.json` | Validation report |
| `lvs_integrity_validation_report.md` | Validation report |
| `release_validation_report_v2.json` | Release report |
| `tool_discovery_integrity_validation_report.json` | Validation report |

---

## 5. Failure Atlas — PRESERVED

| Resource | Location | Status |
|----------|----------|--------|
| Signature libraries | `failure_atlas/signatures/` (7 dirs) | **PRESERVE** |
| Failure records | `failure_atlas/records/` (8 JSON files) | **PRESERVE** (includes knowledge/analysis) |
| Knowledge base | `failure_atlas/knowledge_base.json` (11.7 KB) | **PRESERVE** |
| QoR playbook | `failure_atlas/qor_playbook.json` (3.1 KB) | **PRESERVE** |

> Note: `failure_atlas/records/` contains 3 `analysis_run_*.json` files tied to specific runs — these are analysis records, not signature data. Evaluate whether to clear.

---

## 6. Infrastructure — PRESERVED

| Resource | Location | Status |
|----------|----------|--------|
| PDK installation | `~/.gli-flow/pdk/` | **PRESERVE** |
| ORFS installation | `~/.gli-flow/orfs/` | **PRESERVE** |
| Tool installations | `~/.gli-flow/tools/` | **PRESERVE** |
| Library files | `~/.gli-flow/lib/` | **PRESERVE** |
| User config | `~/.gli-flow/config.json` | **PRESERVE** |
| Design storage | `~/.gli-flow/designs/` | **PRESERVE** |
| Log files | `~/.gli-flow/logs/` | **PRESERVE** |

---

## 7. Directories to Preserve

| Directory | Reason |
|-----------|--------|
| `failure_atlas/signatures/` | Failure Atlas intelligence |
| `failure_atlas/records/` | Knowledge base & resolution data |
| `failure_atlas/knowledge_base.json` | Resolution knowledge |
| `failure_atlas/qor_playbook.json` | QoR improvement strategies |
| `examples/` | Design examples |
| `outputs/examples/` | Example output references |
| `docs/` | Documentation |
| `configs/` | Configuration templates |
| `backend/` | Dashboard backend (source code) |
| `dashboard/` | Dashboard frontend (except `health_report.json`) |
| `gli_flow/` | Application source code |
| `~/.gli-flow/pdk/` | PDK installation |
| `~/.gli-flow/orfs/` | ORFS installation |
| `~/.gli-flow/config.json` | User settings |
| `~/.gli-flow/designs/` | User designs |

---

## 8. Data to Delete

### Database
- None (DB is already empty)

### Filesystem Directories
| Target | Count/Size |
|--------|-----------|
| `outputs/runs/*` | 147 dirs / 307 MB |
| `outputs/reports/*` | 6 files (validation reports) |

### Aggregated Report Files
| Target | Description |
|--------|-------------|
| `trends/historical_trends.json` | Replace with empty array |
| `trends/predictive_report.json` | Replace with empty header |
| `analytics/execution_report.json` | Replace with zeroed stats |
| `analytics/reliability_report.json` | Replace with zeroed stats |
| `regression/regression_report.json` | Replace with clean state |
| `ppa/metrics_history.json` | Replace with empty |
| `execution_history/run_index.json` | Replace with empty array |
| `execution_history/manifest_*.json` | Delete |
| `dashboard/health_report.json` | Replace with zeroed stats |
| `provenance/provenance_graph.json` | Replace with empty graph |

### Root-level Generated Images
| Target | Description |
|--------|-------------|
| `final_*.png` | 6 generated images |

### Failure Atlas Analysis Records (optional)
| Target | Description |
|--------|-------------|
| `failure_atlas/records/analysis_run_*.json` | 3 run-linked analysis files |
