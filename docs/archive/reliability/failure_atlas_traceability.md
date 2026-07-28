# GLI-FLOW Failure Atlas Traceability

## Verification
- **Origin**: Entries originate from `OpenRoadAdapter` (log analysis) and `orchestrator.py` (signoff/metric checks).
- **No Synthetic Incidents**: Entries are gated by `exists()` checks on log files and artifacts.
- **Accuracy**: Verified that `PIPELINE_FAILURE` and `SIGNOFF_FAILURE` map directly to `SignoffGate` blocking conditions.

**Audit Verdict:** Failure Atlas traceability verified.
