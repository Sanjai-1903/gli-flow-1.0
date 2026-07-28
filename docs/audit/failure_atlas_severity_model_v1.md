# Failure Atlas Severity Model v1

**Date:** 2026-06-20
**Purpose:** Define a strict 5-tier severity hierarchy that replaces the current 9-level schema for UI presentation

---

## Hierarchy

| Level | Color | CSS | Meaning | Action Required |
|-------|-------|-----|---------|-----------------|
| `INFO` | Blue | `bg-blue-100 text-blue-700` | Observation only, no action required | None |
| `ADVISORY` | Slate | `bg-slate-100 text-slate-700` | Worth reviewing, not a flow failure | Review when convenient |
| `WARNING` | Yellow | `bg-yellow-100 text-yellow-700` | Engineering concern, may reduce QoR or increase risk | Review before tapeout |
| `ERROR` | Orange | `bg-orange-100 text-orange-700` | Actual implementation issue, requires investigation | Investigate |
| `CRITICAL` | Red | `bg-red-100 text-red-700` | Signoff blocker — design cannot be considered ready | Must resolve |

## Mapping: Old → New

| Old Severity (FailureSeverity) | New Level | Rationale |
|-------------------------------|-----------|-----------|
| `INFO` | `INFO` | Direct mapping |
| `LOW` | `ADVISORY` | Low-level observations, non-blocking |
| `WARNING` | `WARNING` | Already labeled as warning |
| `MEDIUM` | `WARNING` | Medium severity = engineering concern |
| `PERFORMANCE_DEGRADATION` | `WARNING` | Performance concern, not a failure |
| `FUNCTIONAL_RISK` | `ERROR` | Functional risk requires investigation |
| `HIGH` | `ERROR` | High severity = actual issue |
| `UNDER_REVIEW` | `ERROR` | Under review because it looks like an error |
| `TAPEOUT_BLOCKING` | `CRITICAL` | Tapeout blocker = critical |

## Visual Design Principles

1. **No severity shares a color** — each of the 5 tiers gets a unique color band
2. **Red reserved for CRITICAL only** — not shared with ERROR
3. **Orange for ERROR** — distinct from yellow (WARNING) and red (CRITICAL)
4. **Gray/slate for ADVISORY** — low visual weight, non-alarming
5. **Blue for INFO** — informational, neutral
6. **All severity labels human-readable** — "INFO" not "LOW", "CRITICAL" not "TAPEOUT_BLOCKING"

## Sort Order

Entries are sorted by severity, highest first:

```
CRITICAL → ERROR → WARNING → ADVISORY → INFO
```

Within the same severity level, sort by `detected_at` descending (newest first).

## Filter Options

```
All → Critical → Errors → Warnings → Advisory → Info
```

Each filter includes all entries at or above the selected level:
- "Critical" = CRITICAL only
- "Errors" = CRITICAL + ERROR
- "Warnings" = CRITICAL + ERROR + WARNING
- etc.

Or equivalently: exact-match filter to each level.
