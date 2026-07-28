# Failure Atlas Severity Certification v1

**Date:** 2026-06-20
**Scope:** Severity classification redesign, UI clarity improvements, signoff correlation

---

## Changes Summary

### Files Modified

| File | Changes |
|------|---------|
| `dashboard/src/RunDetail.jsx` | New 5-tier severity color mapping; severity breakdown counts in tab header; severity sorting (CRITICAL→INFO); signoff correlation banner; badge text shows new level name |
| `dashboard/src/FailureAtlasPage.jsx` | New `SeverityBadge` with 5-tier colors; new `SeveritySummary` component (breakdown cards); client-side severity filter + sort; filter dropdown uses new levels; removed broken `failures.results` / `failures.total` references |

### Documents Generated

| Doc | Contents |
|-----|----------|
| `docs/audit/failure_atlas_severity_inventory_v1.md` | All 8 entry creation points, 12 detection rules, trigger conditions, current severities |
| `docs/audit/failure_atlas_severity_model_v1.md` | 5-tier hierarchy design: INFO / ADVISORY / WARNING / ERROR / CRITICAL |
| `docs/audit/failure_atlas_severity_classification_v1.md` | Classification of all 33+ failure categories into new tiers |
| `docs/audit/failure_atlas_user_confusion_audit_v1.md` | 5 confusion points where entries imply run failure |

### Severity Mapping (Old → New)

| Old | New | Color | CSS |
|-----|-----|-------|-----|
| `INFO` | INFO | Blue | `bg-blue-100 text-blue-700` |
| `LOW` | ADVISORY | Slate | `bg-slate-100 text-slate-700` |
| `WARNING` | WARNING | Yellow | `bg-yellow-100 text-yellow-700` |
| `MEDIUM` | WARNING | Yellow | `bg-yellow-100 text-yellow-700` |
| `PERFORMANCE_DEGRADATION` | WARNING | Yellow | `bg-yellow-100 text-yellow-700` |
| `FUNCTIONAL_RISK` | ERROR | Orange | `bg-orange-100 text-orange-700` |
| `HIGH` | ERROR | Orange | `bg-orange-100 text-orange-700` |
| `UNDER_REVIEW` | ERROR | Orange | `bg-orange-100 text-orange-700` |
| `TAPEOUT_BLOCKING` | CRITICAL | Red | `bg-red-100 text-red-700` |

### Signoff Correlation Banner Logic

| Run State | Banner |
|-----------|--------|
| `impl=SUCCESS`, `signoff=PASS`, `tapeout=YES` | "Run passed signoff. Failure Atlas contains engineering observations and historical learning signals." |
| `impl=SUCCESS`, `signoff=FAILED` | "Run completed but signoff blockers remain." |
| `impl=FAILED` | "Run terminated before successful completion." |
| All other states | No banner |

---

## Verification

### 1. Signoff PASS + Failure Atlas entries

- **Before:** Badges showed conflicting raw severity names like "TAPEOUT_BLOCKING" in red next to green "PASS" signoff badge with no context
- **After:** Signoff correlation banner shows "Run passed signoff. Failure Atlas contains engineering observations and historical learning signals." Severity badges show human-readable levels (INFO/ADVISORY/WARNING/ERROR/CRITICAL). Severity count header shows breakdown so users can see that entries are non-critical.

**Verdict:** No longer contradictory.

### 2. Severity counts correct

- RunDetail tab header shows: `CRITICAL: X ERROR: X WARNING: X ADVISORY: X INFO: X`
- FailureAtlasPage shows `SeveritySummary` component with per-level count cards
- Mapping from old→new is 1-to-1 per entry, no entries lost or miscounted

**Verdict:** PASS

### 3. Critical issues appear first

- RunDetail: `sorted` array uses `_severityOrder = { CRITICAL: 4, ERROR: 3, WARNING: 2, ADVISORY: 1, INFO: 0 }`, sorted descending
- FailureAtlasPage: `sortedFailures` same sort order
- Within same severity: sorted by `detected_at` descending

**Verdict:** PASS

### 4. Filtering works

- FailureAtlasPage filter dropdown: All Levels / Critical / Error / Warning / Advisory / Info
- Client-side filtering via `_severityLevel(f.severity) === severityFilter`
- Exact matching: each level maps to its old-severity group

**Verdict:** PASS

### 5. No regressions

| Check | Status |
|-------|--------|
| `SeverityBadge` renders all 5 levels with correct colors | PASS |
| Unknown severity falls back to WARNING (yellow) | PASS |
| RunDetail tab: severityColor returns valid classes for all levels | PASS |
| Signoff correlation banner shows only for matching run states | PASS |
| Backfill notice uses neutral language ("completed before Failure Atlas was active") | PASS |
| Backfill notice no longer says "failed" for successful runs | PASS |
| Empty state "No Failures Detected" remains unchanged | PASS |
| Loading state remains unchanged | PASS |
| All tab navigation unchanged | PASS |

---

## Final Verdict

**PASS** — All 8 phases complete. Severity hierarchy is now 5 distinct tiers with unique colors, labels, and sort order. Run detail shows severity breakdown and signoff correlation context.
