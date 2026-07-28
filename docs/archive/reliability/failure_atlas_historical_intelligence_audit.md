# Failure Atlas Historical Intelligence Audit

This document outlines the existing capabilities and gaps for implementing historical correlation and resolution lineage in the Failure Atlas.

## 1. Existing Capabilities

The `failure_atlas_entries` table is already well-structured for historical intelligence:

| Capability | Supported Fields | Status |
| :--- | :--- | :--- |
| **Occurrence Tracking** | `occurrence_count` | Exists |
| **Resolution Tracking** | `fix_applied`, `fix_type`, `fix_description`, `fix_run_id` | Exists |
| **Lineage** | `parent_run_id`, `run_id` | Exists |
| **Trend Metrics** | `first_seen`, `last_seen` | Exists |
| **Failure Classification** | `failure_type`, `severity` | Exists |

## 2. Identified Gaps

1.  **Correlation Logic**: While the data exists, there is currently no backend logic to efficiently aggregate `occurrence_count`, `first_seen`, `last_seen`, or resolution statistics per `failure_type` or `rule_id` across different designs.
2.  **Resolution History Exposure**: The current `FailureDetail` UI component in the dashboard does not surface the `resolution_attempts` or historical outcomes recorded in the database.
3.  **Cross-Design Analysis**: Queries need to be implemented to provide the list of "Affected Designs" for a given failure type.

## 3. Recommended Implementation Path

1.  **Backend Correlation**: Add a new API endpoint `/failures/correlation/{failure_type}` that aggregates stats from the database based on existing columns.
2.  **Dashboard Enhancement**: Extend `FailureDetail` to query this new endpoint and render the "Historical Statistics" and "Resolution Lineage" tables.
3.  **Data Integrity**: Ensure all future failure entries correctly populate `occurrence_count`, `first_seen`, and `last_seen` during insertion/update.
