# Failure Atlas Dataset Integrity Review

**Date:** 2026-06-12
**Scope:** Impact of incident duplication on data quality and downstream consumers

---

## Current State

The database has 5 entries across 2 runs:

| Run | ROOT_CAUSE | DERIVED | CONSEQUENCE | Total |
|---|---|---|---|---|
| gcd | 1 | 0 | 0 | 1 |
| uart_top | 1 | 1 | 2 | 4 |
| **Total** | **2** | **1** | **2** | **5** |

Without hierarchy: 5 entries = 5 "failures"
With hierarchy: 2 root causes, 3 additional entries

---

## occurrence_count Impact

### Current Behavior
`occurrence_count` is incremented per-entry. Each of the 5 entries gets its own occurrence count. For the UART run, 4 entries mean 4× the occurrence count for what is 1 root cause.

### With Root-Cause Counting
`occurrence_count` would be computed as:

```sql
-- Per-root-cause count:
SELECT COUNT(DISTINCT run_id || failure_type || signature)
FROM failure_atlas_entries
WHERE incident_role = 'ROOT_CAUSE'
```

Or with the computed hierarchy:

```python
summary = get_root_summary(entries)
occurrence_count = summary["root_count"]  # 1 instead of 4
```

### Verdict

| Metric | Flat counting | Root-cause counting | Difference |
|---|---|---|---|
| UART run | 4 failures | 1 root cause | 4× over-count |
| All runs | 5 failures | 2 root causes | 2.5× over-count |
| Trend accuracy | Distorted | Accurate | — |

**Counting root causes only would improve data quality** by eliminating the 4× inflation. But root-cause-only counting loses resolution detail (e.g., how many signoff failures happened). **Both counts should be tracked separately**: `root_cause_count` and `total_entry_count`.

---

## Historical Intelligence Impact

### Current Risk
Cross-design queries (e.g., "how many runs had INF-MAGIC-002?") would count 4 entries for UART when only 1 root cause exists. Over time, this inflates trend data and masks the true frequency of the pattern.

### With Hierarchy
- `signature = "inf_magic_002_cross_tool_disagreement"` → 2 runs affected (gcd, uart_top)
- `failure_type = "CROSS_TOOL_DRC_DISAGREEMENT"` → 2 occurrences
- Filtering by `incident_role = ROOT_CAUSE` gives the true historical count

### Verdict
**Root-cause counting improves historical intelligence.** The `signature` field is the most reliable aggregation key — all occurrences of INF-MAGIC-002 share the same signature `inf_magic_002_cross_tool_disagreement`.

---

## Resolution Intelligence Impact

### Current Risk
If an engineer marks the cross-tool entry as `fix_applied = True` but leaves the DRC_SPACING, SIGNOFF_FAILURE, and PIPELINE_FAILURE entries unresolved, the resolution tracking shows 25% resolved when in fact 100% of the root cause is addressed.

### With Hierarchy
Resolution should cascade:
- Fix root cause → auto-resolve all DERIVED and CONSEQUENCE entries
- Resolution percentage computed as `fix_applied_root_causes / total_root_causes`

### Verdict
**Derived/consequence entries distort resolution analytics** if counted independently. Cascade semantics are needed, either via computed logic (check if parent-level signature is resolved) or schema-level `parent_id`.

---

## Important Run Telemetry Impact

### Current Risk
The "important run" detection heuristic uses entry count as a signal. A UART run with 4 entries appears 4× more significant than a GCD run with 1 entry, even though both have the same root cause.

### With Hierarchy
Important run detection should use:
- Primary: root cause count (number of distinct failure patterns)
- Secondary: consequence severity (worst downstream impact)
- Tertiary: total entry count (information density)

### Verdict
**Derived/consequence entries distort importance scoring.** Using root-cause count as the primary signal would produce more accurate importance rankings.

---

## Future GLI-SDI Dataset Impact

### Current Risk
Machine learning models trained on Failure Atlas data would learn spurious correlations from duplicate entries. For example:
- 80% of rows have `domain = "DRC"` and `severity = "TAPEOUT_BLOCKING"` — but most are DERIVED/CONSEQUENCE of the same event
- A model might learn "DRC failure → signoff failure → pipeline failure" as a sequence of distinct events when they happen simultaneously

### With Hierarchy
Training data should:
- Include `incident_role` as a feature column
- Down-weight or exclude `CONSEQUENCE` entries where the ROOT_CAUSE is also present
- Use root-cause-level granularity for failure-type classification

### Verdict
**Without hierarchy, GLI-SDI datasets would contain ~75% redundant entries** (3 of 4 UART entries are derived/consequence). This would:
- Inflate model confidence in false patterns
- Reduce signal-to-noise ratio
- Make cross-validation unreliable (same root cause appearing in train and test splits)

---

## Integrity Scorecard

| Component | Current Risk | With Hierarchy | Recommendation |
|---|---|---|---|
| occurrence_count | 4× over-count for UART | Accurate per-root-cause | Track both `root_cause_count` and `entry_count` |
| Historical intelligence | Cross-design queries count duplicates | Accurate per-signature | Use `signature` as aggregation key |
| Resolution intelligence | Fragmented resolution tracking | Cascade fix_applied | Computed cascade until schema supports `parent_id` |
| Important run telemetry | Entry count inflates importance | Use root cause count | Weighted scoring: root causes > consequences |
| GLI-SDI datasets | 75% redundant rows | Clean training data | Include `incident_role` feature; filter CONSEQUENCE rows for training |

---

## Answers to Audit Questions

### Would counting root causes only improve data quality?

**Yes, for aggregate metrics** (occurrence count, cross-design frequency, trend analysis). No, for forensic analysis — the derived and consequence entries contain valuable timing and severity data. **Best practice: count both, report both.**

### Would derived/consequence entries distort analytics?

**Yes, for 4 specific use cases** (occurrence count, historical trends, resolution tracking, ML training). The distortion is measurable: 4× inflation on the UART run. **Mitigation:** Use `incident_role` to filter or weight entries appropriately for each use case.
