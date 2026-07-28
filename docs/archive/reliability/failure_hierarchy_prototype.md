# Failure Atlas Computed Hierarchy Prototype

**Date:** 2026-06-12
**Implementation:** `gli_flow/core/incident_hierarchy.py`
**Tests:** `tests/test_incident_hierarchy.py`
**Schema Changes:** None (computed at query time)

---

## Design Decision

**No schema changes.** The hierarchy is computed dynamically by classifying entries based on:

- `failure_type` (e.g., `CROSS_TOOL_DRC_DISAGREEMENT`, `DRC_SPACING`, `SIGNOFF_FAILURE`)
- `signature` (e.g., `inf_magic_002_cross_tool_disagreement`)
- Inter-entry relationships (e.g., does this run have a `CROSS_TOOL_DRC_DISAGREEMENT`?)

This avoids migrations, backfills, and database schema changes. The hierarchy is a **view** over existing data, not new data.

---

## Classification Rules

### Entry-Level Classification

| failure_type | Role | Rationale |
|---|---|---|
| `CROSS_TOOL_DRC_DISAGREEMENT` | ROOT_CAUSE | Detects the underlying tool mismatch. Fixing this eliminates the issue. |
| `DRC_SPACING` | DERIVED | Same violations detected by metrics. No new diagnostic value. |
| `DRC_WIDTH` | DERIVED | Same pattern — metric-derived DRC summary. |
| `DRC_ENCLOSURE` | DERIVED | Same pattern. |
| `DRC_ANTENNA` | DERIVED | Same pattern. |
| `DRC_DENSITY` | DERIVED | Same pattern. |
| `SIGNOFF_FAILURE` | CONSEQUENCE | Downstream result of a root cause blocking signoff. |
| `PIPELINE_FAILURE` | CONSEQUENCE | Pipeline-level terminal failure record. |
| Everything else | UNCLASSIFIED | No hierarchy rule matches. Standalone incident. |

### Run-Level Classification

When classifying all entries for a single run:

1. If a `CROSS_TOOL_DRC_DISAGREEMENT` exists → it is the **ROOT_CAUSE** for all DRC/SIGNOFF/PIPELINE entries
2. Any `DRC_*` entries → **DERIVED** (same violations, metric-based detector)
3. `SIGNOFF_FAILURE` + `PIPELINE_FAILURE` → **CONSEQUENCE** (downstream)
4. If no `CROSS_TOOL_DRC_DISAGREEMENT` but `DRC_*` exists → the `DRC_*` entry becomes the ROOT_CAUSE
5. Unrelated entries (e.g., `SETUP_VIOLATION`) remain **UNCLASSIFIED**

---

## UART Example

### Input (4 entries from database)

```json
[
  {"failure_type": "CROSS_TOOL_DRC_DISAGREEMENT", "severity": "MEDIUM"},
  {"failure_type": "DRC_SPACING", "severity": "TAPEOUT_BLOCKING"},
  {"failure_type": "SIGNOFF_FAILURE", "severity": "TAPEOUT_BLOCKING"},
  {"failure_type": "PIPELINE_FAILURE", "severity": "HIGH"}
]
```

### Output (hierarchy tree)

```json
{
  "root_count": 1,
  "total_entries": 4,
  "derived_count": 1,
  "consequence_count": 2,
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
  ]
}
```

---

## API Integration

The hierarchy module can be called from the backend API without modifying the database:

```python
from gli_flow.core.incident_hierarchy import (
    classify_run_entries, build_hierarchy, get_root_summary
)

# From API endpoint:
entries = repo.get_entries_for_run(run_id)
tree = build_hierarchy(entries)
summary = get_root_summary(entries)
```

The API response would include both the flat entries (backward compatible) and the computed hierarchy (new):

```json
{
  "failure_atlas_entries": [...],        // existing flat list
  "hierarchy": {                         // new computed field
    "roots": [...],
    "summary": {"root_count": 1, ...}
  }
}
```

---

## Classification Mapping Table

| Entry Title (UART) | failure_type | Rule Match | Role |
|---|---|---|---|
| Cross-tool DRC disagreement | `CROSS_TOOL_DRC_DISAGREEMENT` | ROOT_CAUSE_TYPES | ROOT_CAUSE |
| DRC failed: 2 violations | `DRC_SPACING` | DERIVED_TYPES | DERIVED |
| Magic DRC signoff failure | `SIGNOFF_FAILURE` | CONSEQUENCE_TYPES | CONSEQUENCE |
| Signoff gate failed | `PIPELINE_FAILURE` | CONSEQUENCE_TYPES | CONSEQUENCE |

**4 entries → 1 root cause, 1 derived, 2 consequences.**

---

## Limitation

The computed hierarchy has no persistence — every query re-classifies. This is acceptable for the current data volume (5 entries total). If the Failure Atlas grows to thousands of entries, consider:

1. Adding a `parent_id` and `incident_role` column to the schema
2. Pre-computing during entry insertion
3. Adding an index on `(run_id, incident_role)`

For the current scale, the computed approach is sufficient and avoids migration risk.

---

## Test Results

```
14 passed in 0.02s
```

All classification patterns covered:
- UART 4-entry pattern → 1 ROOT_CAUSE, 1 DERIVED, 2 CONSEQUENCE
- Single cross-tool entry → ROOT_CAUSE
- No root cause with DRC → DRC becomes ROOT_CAUSE
- Unrelated entries → UNCLASSIFIED
- Empty list → empty tree
