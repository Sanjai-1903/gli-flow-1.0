# Failure Atlas Hierarchy & Duplication Audit

**Audit Date:** 2026-06-12
**Scope:** DRC-related Failure Atlas entries for UART run `run_1781246066_3c483cb5_uart_top`
**Design:** uart_top

---

## PHASE 3 — Incident Duplication Analysis

### Classification Framework

| Category | Definition |
|---|---|
| **ROOT_CAUSE** | The original detection that identifies the underlying issue. Fixing this prevents the issue. |
| **CONSEQUENCE** | Downstream result of the root cause. Automatically resolves when root cause is fixed. |
| **DERIVED** | Repackages same information in different terms. No new diagnostic value. |
| **DUPLICATE** | Exact duplicate — same failure_type, same signature, same trigger. Should be eliminated. |

### UART Entry Classification

| # | Entry Title | failure_type | signature | Classification | Rationale |
|---|---|---|---|---|---|
| 4 | Cross-tool DRC disagreement: Magic=2 KLayout=0 | `CROSS_TOOL_DRC_DISAGREEMENT` | `inf_magic_002_cross_tool_disagreement` | **ROOT_CAUSE** | First detection of tool mismatch. Directly identifies the licon.8a false-positive pattern. |
| 3 | DRC failed: 2 violations | `DRC_SPACING` | `DRC failed: 2 violations, categories: [...]` | **DERIVED** | Summarizes same violations from metric data. No new diagnostic information beyond Entry 4. |
| 2 | Magic DRC: NOT_RUN, ERROR, or violations found | `SIGNOFF_FAILURE` | `signoff_magic_drc_not_run_error_or_violations_found` | **CONSEQUENCE** | Direct result of Magic DRC failure at signoff gate. Automatically clears if root cause is fixed. |
| 1 | Signoff gate failed: Magic DRC: NOT_RUN, ERROR, or violations found | `PIPELINE_FAILURE` | `pipeline_failure_SIGN_OFF` | **CONSEQUENCE** | Pipeline-level terminal failure record. Aggregates all signoff failures. |

### Relationship Graph

```
INF-MAGIC-002 (licon.8a false positive)
  │
  └── Entry 4: Cross-tool disagreement ── ROOT_CAUSE
        │
        ├── Entry 3: DRC failed ── DERIVED (same violation data, different detector)
        │
        └── Entry 2: Magic DRC signoff failure ── CONSEQUENCE
              │
              └── Entry 1: Signoff gate pipeline failure ── CONSEQUENCE (aggregate)
```

### Duplication Verdict

| Relationship | Verdict |
|---|---|
| Entry 3 vs Entry 4 | **Not duplicate**, but derived. Different failure_type, different signature, different creator. Same underlying data. |
| Entry 2 vs Entry 4 | **Not duplicate**. Genuinely different domain (SIGNOFF vs DRC). |
| Entry 1 vs Entry 2 | **Not duplicate**. Entry 1 is an aggregate pipeline wrapper around Entry 2. |
| Entry 1 vs Entry 4 | **Not duplicate**. Different domains entirely. |

**Net assessment:** 4 entries for 1 root cause is **legitimate but suboptimal**. The entries are technically distinct but an engineer must mentally connect them. The system provides no hierarchy.

---

## PHASE 4 — Failure Atlas UX Review

### Current State: Flat List

```
Failure Atlas Entries
├─ Signoff gate failed: Magic DRC: ...   [TAPEOUT_BLOCKING]
├─ Magic DRC: NOT_RUN, ERROR, ...        [TAPEOUT_BLOCKING]
├─ DRC failed: 2 violations              [TAPEOUT_BLOCKING]
├─ Cross-tool DRC disagreement: ...      [MEDIUM]
```

**Engineer experience:** Poor. Four entries, all different severity/type. Not clear that entries 1-3 and 4 describe the same issue.

### Proposed: Hierarchical View

```
Failure Atlas Entries
└─ Cross-tool DRC disagreement: Magic=2 KLayout=0  [HIGH confidence INF-MAGIC-002]
    ├─ Related: DRC failed: 2 violations
    ├─ Signoff consequence: Magic DRC blocking
    └─ Pipeline result: Signoff gate failed
```

### Pros / Cons / Impact

| Aspect | Assessment |
|---|---|
| **Pros** | Single line item per root cause; engineer sees 1 issue not 4; hierarchy conveys causation; resolution tracking maps to root cause |
| **Cons** | Loses individual entry granularity; migration requires schema change; CONSEQUENCE entries need auto-clear logic |
| **Migration impact** | Medium. Requires `parent_id` field in schema + API hierarchy query + UI tree rendering |
| **Schema impact** | Add `parent_id` (UUID, nullable FK to self), add `incident_role` ENUM (`ROOT_CAUSE` \| `CONSEQUENCE` \| `DERIVED`). Existing entries get `parent_id = NULL` |
| **Telemetry impact** | `occurrence_count` should aggregate at root cause level, not per-entry. Resolution telemetry should reference root cause ID |

### Dashboard Recommendations

1. **Group by signature**: If `signature` contains `inf_magic_002`, group all entries under an expandable parent
2. **Severity rollup**: Show max severity of any child entry (TAPEOUT_BLOCKING in this case)
3. **Count rollup**: Show "1 root cause" instead of "4 incidents"
4. **Resolution UI**: Fix applied at root cause level auto-resolves all child entries

---

## PHASE 5 — Dataset Integrity Review

### Risk Assessment

| Risk | Impact | Severity |
|---|---|---|
| **occurrence_count inflation** | Counting 4 entries instead of 1 occurrence inflates trend data. `occurrence_count` must be computed per-signature or per-root-cause, not per-row | **HIGH** |
| **Resolution fragmentation** | An engineer might mark only Entry 4 (cross-tool) as `fix_applied`, leaving 3 entries unresolved. Fragmented resolution = unreliable intelligence | **HIGH** |
| **Historical intelligence degradation** | Cross-design queries (e.g., "how many runs had INF-MAGIC-002?") count 4× the true number. Trends show artifactual spikes | **MEDIUM** |
| **Important run telemetry corruption** | If "important run" detection uses entry count as a signal, runs with the same root cause appear 4× worse than they are | **MEDIUM** |
| **Future GLI-SDI dataset contamination** | Training data for ML models includes 75% redundant entries (3 of 4 are consequences/derived). Models learn spurious correlations | **HIGH** |

### Specific Data Fields at Risk

| Field | Risk |
|---|---|
| `occurrence_count` | Over-counted if incremented per entry. Must be per `signature` or per `(failure_type, signature)` |
| `fix_applied` | Must cascade: fixing the ROOT_CAUSE should mark all CONSEQUENCE/DERIVED entries as fixed |
| `detected_at` / `last_seen` | Valid per-entry but misleading in aggregate — 3 different timestamps for 1 issue |
| `severity` rollup | Dashboard shows MEDIUM (from cross-tool entry) instead of TAPEOUT_BLOCKING (from consequence entries) |

### Mitigation Recommendations

1. **Add `parent_id` and `incident_role`** to schema
2. **occurrence_count**: Compute as `COUNT(DISTINCT signature)` for root-cause-level accuracy, or `COUNT(*)` for raw entry count
3. **fix_applied cascade**: If root cause entry is fixed → auto-set `fix_applied = True` on all child entries
4. **delete_failure_level_entries_for_run**: Ensure this cascades to child entries, or exclude WARNING-level root causes from cleanup
5. **Dashboard aggregation**: Group by `parent_id IS NULL` for root-cause view; show child count as badge

### Positive Findings

| Property | Status |
|---|---|
| Deduplication guard (`insert_entry_if_not_exists`) | Prevents exact duplicates — no two entries with same `(run_id, failure_type, signature)` |
| Entry timestamps | All entries correctly timestamped |
| Evidence fields | Each entry carries appropriate evidence for its creator |
| Schema fields exist | `fix_applied`, `parent_run_id`, etc. are present in schema (though `parent_id` and `incident_role` are missing) |
