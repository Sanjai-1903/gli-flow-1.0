# Failure Atlas User Confusion Audit v1

**Date:** 2026-06-20
**Purpose:** Find all UI elements that may imply "Failure Atlas entry exists = run failed"

---

## Confusion Points

### 1. Tab label: "Failure Atlas" — threatening name
- **File:** `dashboard/src/RunDetail.jsx:1033`
- **Issue:** Tab name contains "Failure" — users associate the word with their design failing
- **Suggestion:** Keep name but add severity summary to defuse the implication

### 2. Counter shows only total count — no breakdown
- **File:** `dashboard/src/RunDetail.jsx:352`
- **Code:** `Failure Atlas Detections ({failures.length})`
- **Issue:** A count of 5 could be 5 INFO entries (harmless) or 5 CRITICAL entries (real problem) — user cannot tell
- **Fix:** Add severity breakdown: `CRITICAL: 1 | WARNING: 3 | INFO: 1`

### 3. Red badges for non-critical severities
- **File:** `dashboard/src/RunDetail.jsx:299-307` — `severityColor()` function
- **Issue:** `HIGH` → red, `TAPEOUT_BLOCKING` → red. Same color for different threat levels
- **Fix:** Reserve red for CRITICAL only; use orange for ERROR

### 4. No signoff correlation banner
- **File:** `dashboard/src/RunDetail.jsx:273-553` — `FailureAtlasTab`
- **Issue:** No banner explaining that a passed run can still have entries
- **Fix:** Add banner correlating run status with atlas entries

### 5. Failure Atlas Page — same total-count-only display
- **File:** `dashboard/src/FailureAtlasPage.jsx`
- **Issue:** OverviewCards (lines 22-39) show total_failures, fixed_count, success_rate — no severity breakdown

### 6. "Failure Atlas Coverage" widget on dashboard
- **File:** `dashboard/src/BetaDashboardPage.jsx:100-123`
- **Issue:** Shows "Known vs Unknown" counts — users may interpret unknown entries as uncaught failures

### 7. AlertTriangle icon for all detections
- **File:** `dashboard/src/RunDetail.jsx:351`
- **Code:** `<AlertTriangle size={14} className="text-orange-500" />`
- **Issue:** Warning icon used even when entries are all INFO/ADVISORY
- **Fix:** Use severity-appropriate icons (info circle, alert triangle, x-circle)

### 8. Backfill notice uses amber/warning colors
- **File:** `dashboard/src/RunDetail.jsx:344-348`
- **Issue:** "This run failed before Failure Atlas was fully active" — says "failed" even when the run succeeded
- **Fix:** Use neutral language: "This run completed before Failure Atlas was active"

---

## Summary

| # | Severity | Location | Current Behavior | Fix |
|---|----------|----------|-----------------|-----|
| 1 | HIGH | Tab label & count | Total count only | Add severity breakdown |
| 2 | HIGH | Badge colors | Red shared across TAPEOUT_BLOCKING and HIGH | 5-tier color scheme |
| 3 | HIGH | No signoff context | Entries shown without run status correlation | Correlation banner |
| 4 | MEDIUM | AlertTriangle icon | Same warning icon for all severities | Severity-appropriate icons |
| 5 | MEDIUM | Backfill notice | Says "failed" for successful runs | Neutral language |
