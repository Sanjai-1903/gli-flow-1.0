# RESET EXECUTION REPORT

**Date:** 2026-06-11 12:22:14
**Command:** gli-flow reset-runs

## Records Removed

| Table | Records |
|-------|--------|
| `runs` | 0 |
| `failure_atlas_entries` | 0 |

## Files/Directories Removed

| Category | Count |
|----------|-------|
| Run directories | 0 |
| Individual files | 0 |

## Reports/Data Files Reset to Clean State

- trends/historical_trends.json
- trends/predictive_report.json
- analytics/execution_report.json
- analytics/reliability_report.json
- regression/regression_report.json
- ppa/metrics_history.json
- execution_history/run_index.json
- dashboard/health_report.json
- provenance/provenance_graph.json

## Tables Preserved

- `schema_version` (migration tracking)
- `failure_atlas_entries` (table structure preserved, execution records cleared)
- `runs` (table structure preserved, execution records cleared)

## Directories Preserved

- `failure_atlas/signatures/` — Failure Atlas intelligence
- `failure_atlas/records/` — Knowledge base & resolution data (non-execution records preserved)
- `failure_atlas/knowledge_base.json` — Resolution knowledge
- `failure_atlas/qor_playbook.json` — QoR improvement strategies
- `examples/` — Design examples
- `outputs/examples/` — Example output references
- `~/.gli-flow/pdk/` — PDK installation
- `~/.gli-flow/orfs/` — ORFS installation
- `~/.gli-flow/config.json` — User settings
- `gli_flow/`, `backend/`, `dashboard/` — Source code

## Infrastructure Intact

- Database schema & migrations
- Failure Atlas signatures & knowledge base
- PDK & ORFS installations
- Configuration & settings
- Design examples
- Dashboard & backend source code
