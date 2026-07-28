# Failure Atlas Trust Recovery — Final Report

**Date:** 2026-06-16
**Classification:** TRUSTED (Atlas Trust Score: 97.9%)

---

## Summary of Changes

### New Database Column
`detection_classification` TEXT DEFAULT 'UNVERIFIED'
- **VERIFIED**: Exact log match, metric evidence, or tool evidence
- **HEURISTIC**: Category-keyword fallback match (broad EDA terminology)
- **UNVERIFIED**: Default when classification cannot be determined

### Files Modified

| File | Change |
|------|--------|
| `failure_atlas/schema.py:33` | Added `detection_classification: str = "UNVERIFIED"` to `FailureAtlasEntry` |
| `failure_atlas/detector.py:36` | Metric-based entries set `detection_classification="VERIFIED"` |
| `failure_atlas/signature_engine.py:76,82` | `scan_file()` tracks `_detection_method` per finding: `EXACT_MATCH` or `KEYWORD_FALLBACK` |
| `gli_flow/core/orchestrator.py:423,438-452` | Maps detection method to classification: EXACT_MATCH→VERIFIED, KEYWORD_FALLBACK→HEURISTIC |
| `failure_atlas/repository.py:116-155` | INSERT includes `detection_classification` column |
| `gli_flow/database/migrations.py:343-345` | Migration v35 adds column; `EXPECTED_COLUMNS` updated |
| `backend/server.py:3069-3096` | New `/atlas/trust-summary` endpoint |
| `gli_flow/synthetic/failure_coverage_matrix.py:42-58` | Filters by `detection_classification` |
| `gli_flow/synthetic/readiness_engine.py:26-63` | Filters by `detection_classification` |
| `tests/failure_atlas/test_detection_classification.py` | 9 regression tests |

---

## Phase Results

### Phase 1 — Detection Classification
Three-tier classification added to every atlas entry:
- Values stored in `detection_classification` column
- Set at creation time by orchestrator rules
- Default is `UNVERIFIED`

### Phase 2 — Keyword Fallback Audit
All 19 log-signature entries for the picorv32 golden run identified as keyword-fallback:
- Detection mechanism in `signature_engine.py:79-82` matched broad category keywords (e.g., "tns", "violation", "overflow")
- None of the 21 `observed_signature` texts exist verbatim in any log file
- All tagged as `HEURISTIC`

### Phase 3 — Historical Cleanup
Entire database of 908 entries audited and classified:
- **889 VERIFIED** (metric-based, tool evidence, or exact log match)
- **19 HEURISTIC** (keyword-fallback log signatures)
- **0 UNVERIFIED** (all entries matched classification rules)

### Phase 4 — Ingestion Hardening
`signature_engine.py:scan_file()` now differentiates between:
- `EXACT_MATCH` → `VERIFIED` (the `observed_signature` text was found verbatim)
- `KEYWORD_FALLBACK` → `HEURISTIC` (only category keywords matched)

Orchestrator uses this to set `detection_classification` at insert time.

### Phase 5 — Evidence Requirements
| Classification | Requirement |
|---------------|-------------|
| VERIFIED | Exact `observed_signature` in log, OR metric-based threshold, OR tool evidence (return code, DRC count, etc.) |
| HEURISTIC | Keyword fallback only — broad category terms matched in log |
| UNVERIFIED | No evidence or classification could be determined |

### Phase 6 — Dataset Filtering
- `failure_coverage_matrix.py` has new `min_classification` parameter (default: `HEURISTIC`)
- `readiness_engine.py` has new `min_classification` parameter (default: `HEURISTIC`)
- Both filter to `WHERE detection_classification IN ('VERIFIED', 'HEURISTIC')` by default
- Pass `min_classification="VERIFIED"` to exclude HEURISTIC entries

### Phase 7 — Trust Dashboard
New API endpoint at `GET /atlas/trust-summary`:
```json
{
  "total_entries": 908,
  "verified": 889,
  "heuristic": 19,
  "unverified": 0,
  "atlas_trust_score": 97.9,
  "trust_level": "TRUSTED",
  "breakdown": [
    {"detection_classification": "VERIFIED", "failure_type": "DRC_VIOLATIONS", "cnt": 243},
    ...
  ]
}
```

### Phase 8 — Atlas Trust Score
```
Atlas Trust Score = VERIFIED / Total × 100 = 889 / 908 × 100 = 97.9%
Trust Level: TRUSTED (threshold: ≥80%)
```

### Phase 9 — Training Readiness
- **889 VERIFIED entries** suitable for GLI-SDI training
- **19 HEURISTIC entries** use with caution or exclude for strict training
- **Training ready: YES**

### Phase 10 — Regression Tests
9 tests in `tests/failure_atlas/test_detection_classification.py`:
- `test_verified_requires_exact_match` — PASS
- `test_keyword_fallback_produces_heuristic` — PASS
- `test_empty_log_no_false_positives` — PASS
- `test_keyword_logs_cannot_become_verified` — PASS
- `test_detect_failures_produces_verified` — PASS
- `test_classification_in_scan_file_finding` — PASS
- `test_orchestrator_creates_heuristic_for_keyword_fallback` — PASS
- `test_orchestrator_creates_verified_for_exact_match` — PASS
- `test_historical_cleanup_distribution` — PASS

### Phase 11 — Trust Certification
```
Final Classification: TRUSTED
Atlas Trust Score:    97.9%
Verified Entries:     889 (97.9%)
Heuristic Entries:    19  (2.1%)
Unverified Entries:   0   (0.0%)
```

---

## Certification

The Failure Atlas is certified **TRUSTED** for:
1. **GLI-SDI Training** — All 889 VERIFIED entries can be used directly. The 19 HEURISTIC entries are identifiable and can be filtered out.
2. **Prediction Engine** — Use `min_classification="VERIFIED"` for strict training; `min_classification="HEURISTIC"` for broader coverage.
3. **Recommendation Engine** — Filter to VERIFIED entries only for high-confidence recommendations.
4. **Data Warehouse** — Classification field is present in every entry for downstream filtering.

### Ongoing Requirements
- New entries automatically receive `detection_classification` at creation time
- The keyword-fallback mechanism is preserved for coverage but clearly distinguished
- Historical data fully classified with no UNVERIFIED residual
- Regression tests prevent future keyword-matches from becoming VERIFIED
