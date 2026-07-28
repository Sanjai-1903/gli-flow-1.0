# Failure Atlas Coverage Intelligence Audit

This document outlines the existing data availability for Coverage Intelligence based on telemetry and the `failure_atlas_entries` schema.

## 1. Existing Telemetry Sources
| Metric | Source | Status |
| :--- | :--- | :--- |
| **Knowledge Views** | `logs/gli-flow.log` (via `[TELEMETRY]` prints) | Exists (needs parsing) |
| **Missing Signatures**| `logs/gli-flow.log` (via `[TELEMETRY]` prints) | Exists (needs parsing) |
| **Important Runs** | `telemetry/metrics.json` | Exists |
| **Occurrence Count** | `failure_atlas_entries.occurrence_count` | Exists |

## 2. Capability Assessment
* **Popularity Measurement**: Can be computed by parsing `rule_knowledge_viewed` events from logs.
* **Coverage Gap Analysis**: Can be computed by parsing `signature_missing` events.
* **Failure Prioritization**: Can be measured by aggregating `occurrence_count` and joining with `important_run` flags from run metrics.
* **Unresolved Failures**: Can be measured by identifying entries with `fix_applied == 0` or `resolution_success_rate == 0`.

## 3. Recommended Implementation Path
1. **Coverage Engine**: Create `failure_atlas/coverage_engine.py` to parse telemetry logs and aggregate failure table statistics.
2. **Dashboard Integration**: Add a "Coverage Intelligence" section to `FailureAtlasPage.jsx` using the existing UI patterns.
3. **Telemetry Robustness**: Ensure log parsing is efficient and respects project boundaries.
4. **Signature Coverage**: Systematically add signatures for `antenna_violation`, `density_violation`, `timing` rules, and `power` rules.

**Audit Verdict:** Data infrastructure is sufficient for Coverage Intelligence.
