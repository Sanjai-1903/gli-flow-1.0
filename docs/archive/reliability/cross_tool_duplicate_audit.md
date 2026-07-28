# Cross-Tool DRC Duplicate Audit

**Audit Date:** 2026-06-12
**Database:** `~/.gli_flow/gli_flow.db`
**Table:** `failure_atlas_entries`

---

## Idempotency Protection Assessment

### Existing Guard

The `CrossToolDRCAnalyzer._create_disagreement_incident()` uses `FailureAtlasRepository.insert_entry_if_not_exists()` (cross_tool_drc.py:185):

```python
repo.insert_entry_if_not_exists(entry)
```

This method (repository.py:90-99) checks for existing entries with the same `(run_id, failure_type, signature)` triple:

```python
def insert_entry_if_not_exists(self, entry: Dict[str, Any]) -> str:
    existing = self._fetchone(
        "SELECT id FROM failure_atlas_entries WHERE run_id = ? AND failure_type = ? AND signature = ?",
        (entry.get("run_id", ""), entry.get("failure_type", ""), entry.get("signature", "")),
    )
    if existing:
        return existing["id"]
    return self.insert_entry(entry)
```

### Composite Key

The uniqueness key is `(run_id, failure_type, signature)`:

- `run_id`: Unique per pipeline execution (e.g., `run_1781246066_3c483cb5_uart_top`)
- `failure_type`: `CROSS_TOOL_DRC_DISAGREEMENT` (hardcoded in cross_tool_drc.py:149)
- `signature`: `inf_magic_002_cross_tool_disagreement` (hardcoded in cross_tool_drc.py:159)

**Effect:** Within a single run, the same disagreement can only produce one FA entry.

---

## Database Duplicate Check

### Query

```sql
SELECT run_id, failure_type, signature, COUNT(*) as cnt
FROM failure_atlas_entries
GROUP BY run_id, failure_type, signature
HAVING cnt > 1;
```

### Result

```
(no rows returned)
```

**No duplicate CROSS_TOOL_DRC_DISAGREEMENT entries exist.**

### All Entries in Database

| run_id | failure_type | signature | entry_level |
|---|---|---|---|
| run_1781181168_884e85cf_gcd | CROSS_TOOL_DRC_DISAGREEMENT | inf_magic_002_cross_tool_disagreement | WARNING |
| run_1781246066_3c483cb5_uart_top | CROSS_TOOL_DRC_DISAGREEMENT | inf_magic_002_cross_tool_disagreement | WARNING |
| run_1781246066_3c483cb5_uart_top | DRC_SPACING | DRC failed: 2 violations, categories: [] | FAILURE |
| run_1781246066_3c483cb5_uart_top | SIGNOFF_FAILURE | signoff_magic_drc:_not_run,_error,_or_violations_found | FAILURE |
| run_1781246066_3c483cb5_uart_top | PIPELINE_FAILURE | pipeline_failure_FAILED | FAILURE |

**Total: 5 entries, 0 duplicates.** Each entry has a unique `(run_id, failure_type, signature)` combination.

---

## Duplication Risk Analysis

### Risk 1: Pipeline Replay

If the same pipeline is executed again with the same `run_id`, the DRC stage would re-invoke `CrossToolDRCAnalyzer.analyze()`, which would call `insert_entry_if_not_exists()` — this would find the existing entry and return its ID without creating a duplicate.

**Verdict:** Protected by `insert_entry_if_not_exists`. ✅

### Risk 2: Multiple DRC Stage Executions

If the DRC stage handler is modified to run multiple times, or if the `try/except` block catches an exception and re-runs:

```python
try:
    analyzer = CrossToolDRCAnalyzer(...)
    analysis = analyzer.analyze(magic_data, klayout_data)
except Exception as x:
    print(f"  [SKIP] Cross-tool DRC analysis: {x}")
```

The current code does NOT retry on failure — it just skips. If it DID retry, the `insert_entry_if_not_exists` guard would still prevent duplicates.

**Verdict:** Protected by `insert_entry_if_not_exists`. ✅

### Risk 3: Manual Database Insertion

A direct SQL `INSERT` bypassing the repository would skip the uniqueness check.

**Verdict:** Not protected — schema-level UNIQUE constraint does not exist on `(run_id, failure_type, signature)`. ⚠️

### Risk 4: Schema Migration Without Dedup

If the `failure_type` or `signature` field naming changes, the composite key would no longer match, allowing a second entry with semantically identical content.

**Verdict:** No protection — rename risk exists. ⚠️

### Risk 5: Same Run Executed on Different Machines

If the same `run_id` is generated on different machines (different databases), each would have its own FA entry with the same key. This is acceptable behavior — each database is its own authority.

**Verdict:** Not a risk — expected distributed behavior. ✅

---

## Scorecard

| Requirement | Status | Evidence |
|---|---|---|
| Same `run_id` + `failure_type` + `signature` must never duplicate | ✅ PASS | `insert_entry_if_not_exists` guard in place |
| No existing duplicates in database | ✅ PASS | SQL query confirms 0 duplicates |
| API/dashboard re-invocation cannot create duplicates | ✅ PASS | API/dashboard are read-only |
| Race condition protection | ✅ PASS | Single-threaded pipeline execution |
| Schema-level UNIQUE constraint | ❌ MISSING | Not implemented; application-layer only |
| Cross-database dedup | N/A | Each DB is independent |

---

## Recommendation

The application-layer `insert_entry_if_not_exists` guard is sufficient for the current single-pipeline/single-database architecture. A schema-level UNIQUE constraint on `(run_id, failure_type, signature)` would add defense-in-depth but is not urgent.

**No code changes needed for idempotency protection.** The existing guard works correctly.
