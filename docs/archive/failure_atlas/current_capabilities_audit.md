# GLI-FLOW Failure Atlas Current Capabilities Audit

This document outlines the current state of Failure Atlas and DRC diagnostics based on an audit of the schema and database access layer.

## 1. DRC Data Capture Analysis

| Field | Captured? | Location | Status |
| :--- | :--- | :--- | :--- |
| **Rule Name** | Yes | `FailureAtlasEntry` (as part of `level3_signature`) | Surfaced as Title/ID |
| **Tool** | Yes | `FailureAtlasEntry` (via `detection_stage` or metadata) | Surfaced in details |
| **Total Violations** | Yes | `pre_failure_metrics` (in `FailureAtlasEntry`) | Stored in evidence |
| **Coordinates** | Yes | `spatial_locations` (in `FailureAtlasEntry`) | Available but not surfaced in UI |
| **Layer** | Yes | `spatial_locations` (in `FailureAtlasEntry`) | Available but not surfaced in UI |
| **Rule Description**| No | N/A | Missing |
| **Investigation Checklist**| No | N/A | Missing |
| **Historical Resolutions** | Partial | `resolution_history` (in `FailureAtlasEntry`) | Field exists but empty |
| **Similar Failures** | No | N/A | Missing (requires query logic) |

## 2. Infrastructure Assessment

### Schema (`failure_atlas/schema.py`)
- The `FailureAtlasEntry` dataclass already includes fields for remediation: `fix_applied`, `fix_type`, `fix_description`, `fix_run_id`, `failure_explanation`, `root_cause_candidates`, `recommended_actions`, `resolution_history`, `fix_attempt_count`, and `effective_fixes`.
- **Finding**: The database schema is **already capable** of storing everything required by the remediation engine. No schema extension is required.

### Database Access (`gli_flow/database/sqlite.py`)
- The database is currently used primarily for tracking run status and QoR.
- **Finding**: We need to ensure that the `Repository` (not fully audited yet) has the necessary query capability to expose `similar_failures` and `resolution_history` to the backend.

### Dashboard UX (`dashboard/src/FailureAtlasPage.jsx`)
- The dashboard currently surfaces severity, title, and generic stage info.
- **Finding**: The UI is designed to be extensible. It uses `FailureDetail` component, which is the perfect place to add the requested investigation checklist and historical resolution history without redesigning the overall view.

## 3. Conclusions
- **Redesign Required?**: **NO**. The existing architecture is surprisingly close to meeting all requirements.
- **Strategy**: Focus on populating the existing remediation fields during the `detect_failures` stage and exposing them in the `FailureDetail` component.
