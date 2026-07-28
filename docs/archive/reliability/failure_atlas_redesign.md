# Failure Atlas Redesign

## Problem

Current Failure Atlas entries are symptom-level, flat, and noisy:

```
Entry 1: DRC failed (severity: TAPEOUT_BLOCKING)
Entry 2: Magic DRC failed (severity: TAPEOUT_BLOCKING)
Entry 3: KLayout DRC failed (severity: TAPEOUT_BLOCKING)
Entry 4: LVS failed (severity: TAPEOUT_BLOCKING)
Entry 5: Signoff failed (severity: TAPEOUT_BLOCKING)
Entry 6: Pipeline failed (severity: HIGH)
```

These 6 entries describe 2 actual root causes:
1. 6 DRC violations (4 real, 2 tool false-positive)
2. LVS extraction timed out

The rest are downstream consequences.

## Solution: Root Cause + Consequence Hierarchy

### New Entry Level System

| Level | Meaning | Example |
|-------|---------|---------|
| `ROOT_CAUSE` | Primary failure | "6 DRC violations detected" |
| `CONSEQUENCE` | Downstream effect | "Signoff blocked by DRC" |
| `EVIDENCE` | Supporting data point | "li.3 spacing = 0.16um < 0.17um" |
| `INFO` | Contextual note | "INF-MAGIC-002: licon.8a is tool false-positive" |

### Hierarchy in Database

New column: `parent_id TEXT DEFAULT NULL`

A `CONSEQUENCE` entry has `parent_id` pointing to its `ROOT_CAUSE`.
An `EVIDENCE` entry has `parent_id` pointing to its root cause.

### Deduplication

New dedup key: `SHA256(level + root_cause_type + primary_evidence)`

- Across all runs of the same design
- Across all runs of different designs
- Knowledge base lookup for known patterns

### Dashboard Display

```
ROOT CAUSE: DRC Violations (6 total)
├── Real: li.3 spacing (4 violations) — TAPEOUT_BLOCKING
├── False Positive: licon.8a (2 violations) — INF-MAGIC-002
├── CONSEQUENCE: Magic DRC FAIL (6 violations)
├── CONSEQUENCE: KLayout DRC FAIL (4 violations)
└── CONSEQUENCE: Signoff blocked
    └── Recommended: Fix li.3 spacing in routing, waive licon.8a

ROOT CAUSE: LVS Extraction Timeout (620s > 600s limit)
├── EVIDENCE: picorv32.ext = 40.2MB
├── EVIDENCE: return_code = -1 (killed)
├── CONSEQUENCE: LVS comparison not completed
├── CONSEQUENCE: Signoff blocked
└── Recommended: Increase extraction timeout, reduce fill cell extraction
```

### Implementation

1. New `entry_level` column in `failure_atlas_entries` (already exists via migration 7)
2. New `parent_id` column in `failure_atlas_entries` (already exists via migration 2)
3. Root Cause Engine creates ROOT_CAUSE entries
4. Existing detector still creates CONSEQUENCE entries but links to parent
5. Repository query filters: `get_root_causes_for_run()`, `get_consequences()`

### Migration of Existing Data

For existing runs, run a one-time migration that:
1. Groups all entries by run_id
2. Identifies the earliest pipeline failure as root cause
3. Links all downstream entries as consequences
4. Preserves original severity and evidence
