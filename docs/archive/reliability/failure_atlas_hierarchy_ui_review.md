# Failure Atlas Hierarchy UI Review

**Date:** 2026-06-12
**Scope:** Proposal for root-cause hierarchy in existing dashboard (no production changes)

---

## Current UI (Failure Atlas Tab)

### Flat List Display

```
┌──────────────────────────────────────────────────────────────┐
│  Failure Atlas Detections (4)                                │
│                                                              │
│  ⚠ Signoff gate failed: Magic DRC: ...  [TAPEOUT_BLOCKING]  │
│  ⚠ Magic DRC: NOT_RUN, ERROR, ...       [TAPEOUT_BLOCKING]  │
│  ⚠ DRC failed: 2 violations            [TAPEOUT_BLOCKING]   │
│  ⚠ Cross-tool DRC disagreement: ...    [MEDIUM]             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Problem:** 4 separate entries, different severities, no indication they are related. Engineer must read all 4 to understand it's 1 issue.

---

## Proposed UI (Hierarchical Tree)

### Root Cause View

```
┌──────────────────────────────────────────────────────────────┐
│  Failure Atlas Detections: 1 root cause, 3 related entries   │
│                                                              │
│  ▼ Cross-tool DRC disagreement         [MEDIUM]  ROOT_CAUSE │
│    ├─ DRC failed: 2 violations         [BLOCKING] DERIVED    │
│    ├─ Magic DRC signoff failure        [BLOCKING] CONSEQUENCE│
│    └─ Signoff gate failed              [BLOCKING] CONSEQUENCE│
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Expanded Root Cause Details

```
┌──────────────────────────────────────────────────────────────┐
│  Failure Atlas Detections: 1 root cause, 3 related entries   │
│                                                              │
│  ▼ Cross-tool DRC disagreement         [MEDIUM]  ROOT_CAUSE │
│  │  KB: INF-MAGIC-002 | Rule: licon.8a                     │
│  │  Magic=2 KLayout=0 | citation: inf_magic_002             │
│  │                                                          │
│  ├─ DRC failed: 2 violations         [BLOCKING] DERIVED     │
│  ├─ Magic DRC signoff failure        [BLOCKING] CONSEQUENCE │
│  └─ Signoff gate failed              [BLOCKING] CONSEQUENCE │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Multiple Root Causes

```
┌──────────────────────────────────────────────────────────────┐
│  Failure Atlas Detections: 2 root causes, 5 total entries    │
│                                                              │
│  ▼ Cross-tool DRC disagreement         [MEDIUM]  ROOT_CAUSE │
│    ├─ DRC failed: 2 violations         [BLOCKING] DERIVED    │
│    ├─ Magic DRC signoff failure        [BLOCKING] CONSEQUENCE│
│    └─ Signoff gate failed              [BLOCKING] CONSEQUENCE│
│                                                              │
│  ▼ Setup timing violated (WNS=-0.5ns) [BLOCKING] ROOT_CAUSE │
│    └─ Signoff gate failed              [BLOCKING] CONSEQUENCE│
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation Approach (No Schema Changes)

The hierarchy is computed at the API layer:

```
Backend server.py
  │
  ├─ GET /runs/{run_id}/failures
  │    ├─ returns: {entries: [...], hierarchy: {...}}  ← add hierarchy
  │    └─ backward compatible: entries field unchanged
  │
  └─ GET /failures
       └─ adds hierarchy summary fields
```

### API Response Change

Current:
```json
{
  "results": [
    {"id": "1", "failure_type": "CROSS_TOOL_DRC_DISAGREEMENT", ...},
    {"id": "2", "failure_type": "DRC_SPACING", ...},
    ...
  ],
  "total": 4
}
```

Proposed:
```json
{
  "results": [...],  // unchanged (backward compatible)
  "total": 4,
  "hierarchy": {
    "roots": [
      {
        "failure_type": "CROSS_TOOL_DRC_DISAGREEMENT",
        "incident_role": "ROOT_CAUSE",
        "children": [
          {"failure_type": "DRC_SPACING", "incident_role": "DERIVED"},
          {"failure_type": "SIGNOFF_FAILURE", "incident_role": "CONSEQUENCE"},
          {"failure_type": "PIPELINE_FAILURE", "incident_role": "CONSEQUENCE"}
        ]
      }
    ],
    "summary": {
      "root_count": 1,
      "total_entries": 4,
      "consequence_count": 2,
      "derived_count": 1
    }
  }
}
```

---

## Evaluation

### Engineer Usability

| Aspect | Score | Rationale |
|---|---|---|
| Clarity | **HIGH** | 1 root cause instead of 4 entries. Engineer immediately sees the issue and its consequences. |
| Actionability | **HIGH** | Root cause is the fix target. Consequences are understood as downstream effects. |
| Cognitive load | **LOW** | Tree structure conveys causality. No mental assembly required. |
| Familiarity | **MEDIUM** | Tree/hierarchy is a common UI pattern. Engineers familiar with JIRA, bug trackers, etc. |

### Information Density

| Aspect | Current | Proposed |
|---|---|---|
| Entries shown | 4 | 1 (expandable) |
| Lines of text | 8+ | 4 (collapsed) |
| Causality conveyed | No | Yes (indentation + role badges) |
| Severity rollup | Per-entry | Root-level + worst-child |
| KB integration | None | Root cause links to INF-MAGIC-002 |

**More information in less space.** The tree structure is denser without being noisier.

### Backward Compatibility

| Concern | Status |
|---|---|
| Existing API consumers | ✅ `results` field unchanged. `hierarchy` is additive. |
| Existing dashboard | ✅ Current UI continues to work. Hierarchy is opt-in. |
| Existing database | ✅ No schema changes. Hierarchy is computed at query time. |
| Existing tests | ✅ No test changes needed. New tests cover hierarchy. |

### Migration Complexity

| Task | Complexity | Effort |
|---|---|---|
| Add hierarchy computation to API | **Low** | 1 import + 3 lines per endpoint |
| Add `incident_role` to FA detail view | **Low** | UI conditional rendering |
| Add tree expand/collapse | **Medium** | React state management |
| Add role badge styling | **Low** | CSS classes |
| Add severity rollup | **Low** | Max() over children |
| KB integration | **Medium** | Link root cause type to KB |

---

## Recommendation

**Proceed with computed hierarchy in the API layer.** The `incident_hierarchy.py` module is already implemented and tested (14/14 tests passing). Integration requires:

1. **Backend** (`server.py`): Add `hierarchy` field to failure atlas endpoints using `build_hierarchy()`
2. **Dashboard** (`FailureAtlasPage.jsx`): When `hierarchy` is present, render tree view; fall back to flat list for backward compatibility
3. **Run Detail** (`RunDetail.jsx`): Show `incident_role` badge on each entry in the Failure Atlas tab

**Do not add `parent_id` yet.** The computed hierarchy is sufficient for current data volume (5 entries). Re-evaluate when entries exceed 100.

### UI Mockup (Text)

```
Current:                                      Future:
┌──────────────────────┐                    ┌──────────────────────┐
│ 4 failures            │                    │ 1 root cause         │
│                       │                    │ ▼ Cross-tool DRC     │
│ • Pipeline failure    │                    │   ├─ DRC failed      │
│ • Signoff failure     │         →         │   ├─ Signoff fail    │
│ • DRC failed         │                    │   └─ Pipeline fail   │
│ • Cross-tool DRC     │                    │                      │
└──────────────────────┘                    └──────────────────────┘
```
