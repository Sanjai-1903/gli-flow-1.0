# Failure Atlas Consumer Inventory

This inventory tracks all consumers of Failure Atlas data and whether they respect the `detection_classification` field.

| Consumer | Location | Respects `detection_classification`? | Notes |
| :--- | :--- | :--- | :--- |
| **Backend API** | `backend/server.py` | **NO** | Multiple endpoints query `failure_atlas_entries` without filtering. |
| **Coverage Engine** | `gli_flow/synthetic/failure_coverage_matrix.py` | **YES** | Filters by `min_classification` param (default HEURISTIC). |
| **Readiness Engine** | `gli_flow/synthetic/readiness_engine.py` | **YES** | Filters by `min_classification` param (default HEURISTIC). |
| **Campaign Planner** | `gli_flow/data_program/campaign_planner.py` | **NO** | Aggregates all entries. |
| **Atlas Growth Tracker** | `gli_flow/data_program/growth_tracker.py` | **NO** | Counts all signatures and entries. |
| **Dataset Dashboard** | `gli_flow/data_program/dashboard.py` | **NO** | Aggregates all entries. |
| **Profile Engine** | `gli_flow/design_intel/profile_engine.py` | **NO** | Reads all run IDs from atlas entries. |
| **Quality Audit** | `gli_flow/design_intel/quality_audit.py` | **NO** | Counts all entries. |
| **Resolution Repository** | `gli_flow/resolution_intelligence/repository.py` | **NO** | Uses `NOT EXISTS` subquery without filtering. |
| **Dashboard (UI)** | `dashboard/src/FailureAtlasPage.jsx` | Unknown | Likely relies on backend, but check if it has frontend filters. |
| **Dashboard (UI)** | `dashboard/src/RunDetail.jsx` | Unknown | Likely relies on backend. |
| **Dashboard (UI)** | `dashboard/src/BetaDashboardPage.jsx` | Unknown | Likely relies on backend. |
| **Dashboard (UI)** | `dashboard/src/RegressionDetectorPage.jsx` | Unknown | Likely relies on backend. |
| **CLI Diagnose** | `gli_flow/cli/main.py` | **YES** | Mentions FA IDs in hardcoded patterns, but doesn't query DB for atlas entries directly for main diagnosis logic. |
| **Database Migrations** | `gli_flow/database/migrations.py` | N/A | Schema management. |

## Detailed Audit of Backend Endpoints (backend/server.py)

The following endpoints query `failure_atlas_entries` without filtering:

- `/analytics/summary`
- `/analytics/failures/run/{run_id}`
- `/analytics/common-failures`
- `/analytics/failure-types`
- `/analytics/fix-effectiveness`
- `/analytics/failure-details/{failure_id}`
- `/analytics/similar-failures/{failure_id}`
- `/runs/{run_id}/failures`
- `/beta/operations/growth`
