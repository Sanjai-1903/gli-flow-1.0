# Failure Atlas Resolution Intelligence Audit

This document outlines the existing data availability for Resolution Intelligence based on the `failure_atlas_entries` schema and telemetry.

## 1. Existing Resolution Tracking Fields
| Field | Purpose | Status |
| :--- | :--- | :--- |
| `fix_applied` | Binary flag for resolution attempt | Exists |
| `fix_type` | Categorization of fix (e.g., "Reduce Utilization") | Exists |
| `fix_description`| Detailed explanation of the fix | Exists |
| `fix_run_id` | Lineage to the follow-up run | Exists |
| `before_metrics` | Metrics prior to resolution | Exists |
| `after_metrics` | Metrics in the follow-up run | Exists |

## 2. Capability Assessment
* **Successful Fix Identification**: Can be determined by checking `fix_applied == 1` combined with analyzing `before_metrics` vs `after_metrics` (e.g., `drc_total` reduction or `is_clean` improvement).
* **Important Run Correlation**: Can be derived by joining the `runs` table (checking `tags` or severity-based indicators) with `failure_atlas_entries`.
* **Resolution Sequences**: Possible via `fix_run_id` lineage tracking.

## 3. Recommended Implementation Path
1. **Correlation Engine Extension**: Update `correlation_engine.py` to aggregate `fix_type` performance metrics (Attempts, Success Rate, Important Run Usage).
2. **Success Definition**: Define success objectively as `fix_applied == 1` AND `after_metrics.drc_total == 0` (for DRC) or equivalent for other domains.
3. **Dashboard Update**: Extend `FailureDetail` to display a "Resolution Intelligence" table based on the new aggregated data.

**Audit Verdict:** Data infrastructure is adequate for Phase 4.
