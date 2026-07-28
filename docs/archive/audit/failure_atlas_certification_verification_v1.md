# Failure Atlas Certification Verification v1

## Final Verdict: PARTIAL

| Dimension | Score | Status |
|-----------|-------|--------|
| Classification Enforcement | 28/100 | FAIL |
| Database Constraint | 30/100 | FAIL |
| Consumer Filtering | 33/100 | FAIL |
| Historical Counts | 100/100 | PASS |
| False Verification Rate | 100/100 | PASS |
| Heuristic Misclassification | 100/100 | PASS |
| Unverified Entries | 100/100 | PASS |
| Regression Test Quality | 100/100 | PASS |
| Attack Resistance | 100/100 | PASS |
| Dataset Readiness | 100/100 | PASS |

**The data is trustworthy. The infrastructure is not.**

---

## Findings

### 1. Classification Enforcement — FAIL (Score: 28/100)
- 5 of 7 entry paths (71%) do not set `detection_classification` explicitly.
- They rely on `insert_entry()` defaulting to `UNVERIFIED`.
- Vulnerable paths: pipeline failures, root causes, signoff failures, cross-tool DRC, resolution candidates.
- Only 2 paths (orchestrator failure mapping and synthetic generation) set classification correctly.
- **Current entries are fine** because the historical cleanup script ran. New entries will silently degrade.

### 2. Database Constraint — FAIL (Score: 30/100)
- `ALTER TABLE` migration added column with `DEFAULT 'UNVERIFIED'` but no `NOT NULL`.
- SQLite allows explicit NULL insertion.
- The Python-side default in `insert_entry()` is the only protection.

### 3. Consumer Filtering — FAIL (Score: 33/100)
- Only `failure_coverage_matrix.py` and `readiness_engine.py` filter by classification.
- `growth_tracker.py`, `dashboard.py`, `quality_audit.py`, `profile_engine.py`, `resolution_intelligence/repository.py` — all ignore classification.
- `backend/server.py` has 30+ queries against `failure_atlas_entries` — none filter.

### 4. Historical Counts — PASS (Score: 100/100)
- VERIFIED: 889 (884 synthetic/campaign, 3 pipeline, 2 cross-tool DRC)
- HEURISTIC: 19 (all picorv32 golden run keyword-fallback)
- TOTAL: 908. Counts match the certification claim exactly.

### 5. False Verification Rate — PASS (Score: 100/100)
- 20 random VERIFIED entries audited. All have real metric evidence (wns, tns, drc_violations, lvs_status, area, stage/error).
- 0 false verifications. 0% false verification rate.

### 6. Heuristic Misclassification — PASS (Score: 100/100)
- All 19 HEURISTIC entries have keyword-fallback pattern: `log_file` + `atlas_id` in evidence, title starts with "Log signature:".
- No metric evidence. Correctly classified as HEURISTIC.

### 7. Unverified Entries — PASS (Score: 100/100)
- Zero entries with NULL, empty string, unknown, or malformed classification.
- Only two distinct values: VERIFIED and HEURISTIC.

### 8. Regression Test Quality — PASS (Score: 100/100)
- 9 mutation-sensitive tests. Mutation (KEYWORD_FALLBACK → EXACT_MATCH) causes 2 test failures.
- Tests properly enforce the distinction between keyword-only logs and exact matches.

### 9. Attack Resistance — PASS (Score: 100/100)
- Log with only EDA keywords → `_detection_method: KEYWORD_FALLBACK` → `detection_classification: HEURISTIC`.
- Keyword-only attack logs cannot infiltrate the VERIFIED pool.

### 10. Dataset Readiness — PASS (Score: 100/100)
- `failure_coverage_matrix.py` and `readiness_engine.py` both filter by `detection_classification`.
- Coverage engine has `min_classification` parameter with WHERE clause injection.
- Readiness engine uses the same pattern. Correct behavior.

---

## Per-Run Analysis: picorv32 Golden Run (run_1781586782)

The certification claims 97.9% Trusted globally, but the picorv32 golden run — the only real (non-synthetic) run in the dataset — tells a different story:

- 7 VERIFIED entries (pipeline failures with real metric evidence)
- 19 HEURISTIC entries (keyword-fallback from unstructured log scraping)
- **26.9% Trusted** at the per-run level

**This run is NOT TRUSTED.** The aggregate 97.9% figure is achieved only because synthetic campaign data (884 entries with perfect metric evidence) dominates the database. A practitioner relying on this data for the picorv32 flow would find ~73% of entries are heuristic.

The certification should have disclosed this per-run breakdown.

---

## Code-Traceable Evidence

All findings are verified through source code analysis, database queries, and runtime tests — not documentation.

Key evidence files:
- `failure_atlas/signature_engine.py:76,85` — Detection method assignment
- `failure_atlas/repository.py` — `insert_entry()` default fallback
- `gli_flow/database/migrations.py:343-345` — Migration v35 (no NOT NULL)
- `gli_flow/core/orchestrator.py:835-931` — 3 vulnerable entry paths
- `gli_flow/core/cross_tool_drc.py:186` — Vulnerable entry path
- `gli_flow/resolution_intelligence/candidate.py:42` — Vulnerable entry path
- `gli_flow/synthetic/failure_coverage_matrix.py:42-54` — Correct filter
- `gli_flow/synthetic/readiness_engine.py:27-61` — Correct filter
- `tests/failure_atlas/test_detection_classification.py` — 9 regression tests

---

## Recommendation

**Accept the certification as PARTIAL.** The aggregate data is trustworthy for training and analysis, but:

1. Fix classification enforcement on the 5 vulnerable paths
2. Add `NOT NULL` constraint on `detection_classification`
3. Add classification filters to all consumers
4. Disclose per-run trust ratios alongside the aggregate

Until these are fixed, new entries entering through vulnerable paths will silently degrade to UNVERIFIED.
