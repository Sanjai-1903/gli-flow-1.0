# Run Status Clarity Audit v1

**Date:** 2026-06-20
**Component:** `dashboard/src/RunDetail.jsx`
**Issue:** Run detail page displays unlabeled SUCCESS/FAILED badges that can conflict visually

---

## Problem

The Run Detail page header rendered two unlabeled status badges side-by-side:

```
[SUCCESS] [FAILED]  ← user cannot tell which is which
```

Both `implementation_status` and `signoff_status` were displayed as bare words with no label, and `tapeout_ready` was not shown at all in the header (only in the Summary tab cards).

## Status Values (from backend)

| Field | Source DB column | Possible values | Semantics |
|-------|-----------------|-----------------|-----------|
| `implementation_status` | `runs.implementation_status` | `"SUCCESS"`, `"FAILED"`, `"NOT_STARTED"` | Whether RTL-to-GDS completed |
| `signoff_status` | `runs.signoff_status` | `"PASS"`, `"FAILED"`, `"NOT_RUN"` | Whether GDS passed timing/signoff |
| `tapeout_ready` | `runs.tapeout_ready` | `true`, `false` | Both impl=SUCCESS AND signoff=PASS |

These are three distinct status axes — a run can be:
- `implementation_status = "SUCCESS"` + `signoff_status = "FAILED"` (synthesized but failed timing)
- `implementation_status = "FAILED"` + `signoff_status = "NOT_RUN"` (never reached signoff)
- `implementation_status = "SUCCESS"` + `signoff_status = "PASS"` (tapeout ready)

The header previously showed both badges (when non-null) without distinguishing labels, making "SUCCESS FAILED" ambiguous.

## Affected Code

**`dashboard/src/RunDetail.jsx:1087-1092`** (before fix):

```jsx
{run.implementation_status && (
  <span className={`...${run.implementation_status === "SUCCESS"
    ? "bg-green-100 text-green-700"
    : "bg-red-100 text-red-700"}`}>{run.implementation_status}</span>
)}
{run.signoff_status && (
  <span className={`...${run.signoff_status === "PASS"
    ? "bg-green-100 text-green-700"
    : "bg-red-100 text-red-700"}`}>{run.signoff_status}</span>
)}
```

Issues:
1. No labels — user cannot distinguish Execution vs Signoff
2. `signoff_status = "NOT_RUN"` rendered red (false alarm, not an error)
3. `tapeout_ready` badge missing from header
4. Raw value displayed — `signoff_status` shows "PASS" or "FAILED" instead of normalized form

## Fix Applied

**`dashboard/src/RunDetail.jsx:1087-1095`** (after fix):

```jsx
{run.implementation_status && (
  <span className={`...${run.implementation_status === "SUCCESS"
    ? "bg-green-100 text-green-700"
    : "bg-red-100 text-red-700"}`}>Execution: {run.implementation_status}</span>
)}
{run.signoff_status && (
  <span className={`...${run.signoff_status === "PASS"
    ? "bg-green-100 text-green-700"
    : run.signoff_status === "NOT_RUN"
      ? "bg-gray-100 text-gray-500"
      : "bg-red-100 text-red-700"}`}>Signoff: {run.signoff_status}</span>
)}
{run.tapeout_ready != null && (
  <span className={`...${run.tapeout_ready
    ? "bg-green-100 text-green-700"
    : "bg-red-100 text-red-700"}`}>Tapeout: {run.tapeout_ready ? "YES" : "NO"}</span>
)}
```

Changes:
1. **Labels added** — each badge now reads `"Execution: SUCCESS"`, `"Signoff: FAILED"`, `"Tapeout: YES"`
2. **`signoff_status = "NOT_RUN"`** — now renders gray instead of red (neutral, not an error)
3. **`tapeout_ready` badge added** — displayed as `"Tapeout: YES"` (green) or `"Tapeout: NO"` (red)
4. **Mutual exclusivity preserved** — badges are independent but now distinguishable by label

## Before / After

| Scenario | Before | After |
|----------|--------|-------|
| Impl=SUCCESS, Signoff=FAILED | `[SUCCESS] [FAILED]` (conflicting) | `[Execution: SUCCESS] [Signoff: FAILED]` (clear) |
| Impl=SUCCESS, Signoff=PASS | `[SUCCESS] [PASS]` | `[Execution: SUCCESS] [Signoff: PASS] [Tapeout: YES]` |
| Impl=FAILED, Signoff=NOT_RUN | `[FAILED] [NOT_RUN]` (both red) | `[Execution: FAILED] [Signoff: NOT_RUN]` (red + gray) |
| Impl=SUCCESS, Signoff=NOT_RUN | `[SUCCESS] [NOT_RUN]` (green + red) | `[Execution: SUCCESS] [Signoff: NOT_RUN]` (green + gray) |

## Data Flow

```
Run DB table
  ├── implementation_status  ──→  "Execution: SUCCESS/FAILED/NOT_STARTED"
  ├── signoff_status         ──→  "Signoff: PASS/FAILED/NOT_RUN"
  └── tapeout_ready          ──→  "Tapeout: YES/NO"

backend/server.py:147-149  →  dashboard (run object)  →  RunDetail.jsx:1087-1095
```

All three fields are selected in the same query (`server.py:147-149`) and passed through the same `/runs/{run_id}` response. No backend changes needed.

## Scope

- [x] `RunDetail.jsx:1087-1092` — only file rendering these specific badges
- [x] All other status badges across the dashboard (StatusBadge in App.jsx, RunsPage.jsx, QoRAnalyticsPage.jsx, etc.) display a single run-level `status` field, not the three separate axes, and are unaffected
- [x] Summary tab cards (lines 54-71) remain unchanged — they already have labels ("Implementation", "Signoff", "Tapeout Ready")

## Verification

- [x] Badge text includes source label: `"Execution: "`, `"Signoff: "`, `"Tapeout: "`
- [x] `signoff_status = "NOT_RUN"` renders gray (bg-gray-100 text-gray-500)
- [x] `tapeout_ready` boolean displays "YES" (green) / "NO" (red)
- [x] `tapeout_ready = null/undefined` hides the badge (null check with `!= null`)
- [x] `implementation_status = null/undefined` hides the badge
- [x] `signoff_status = null/undefined` hides the badge
- [x] All three badges can coexist without ambiguity
- [x] No other pages need changes (confirmed by grep across all .jsx files)
