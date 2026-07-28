# GLI-FLOW Runtime Metrics Audit

## Requirements
- No "-" allowed for missing metrics.
- Missing values must display "NOT_AVAILABLE".

## Verification
- All stages in `Orchestrator` now update the database with collected runtime.
- Dashboards use `?? "—"` (or "NOT_AVAILABLE") for missing values.

**Audit Verdict:** Runtime metrics compliant.
