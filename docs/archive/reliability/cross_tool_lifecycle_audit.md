# Cross-Tool DRC Analyzer Lifecycle Audit

**Audit Date:** 2026-06-12
**Analyzer:** `CrossToolDRCAnalyzer` (gli_flow/core/cross_tool_drc.py)
**Scope:** All invocation points across execution, dashboard, and API layers

---

## Invocation Map

```
┌──────────────────────────────────────────────────────────────────┐
│                    INVOCATION POINTS                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  EXECUTION TIME  ─── orchestrator.py:891-896 (ONLY once)         │
│                         │                                        │
│                         ├─ Creates FA incident (WARNING level)   │
│                         └─ Writes drc_agreement.json            │
│                                                                  │
│  DASHBOARD TIME  ─── RunDetail.jsx:123 (READ ONLY)               │
│                         │                                        │
│                         └─ Reads run.drc_analysis from API       │
│                                                                  │
│  API TIME         ─── server.py:303-306, 331-333 (READ ONLY)     │
│                         │                                        │
│                         └─ Reads drc_agreement.json from disk    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Touchpoint 1: Execution Time (orchestrator.py:891-896)

**File:** `gli_flow/core/orchestrator.py`
**Lines:** 891-896
**Context:** Inside DRC stage handler, after `run_dual_drc()` returns

```python
analyzer = CrossToolDRCAnalyzer(
    run_dir=str(self.run_dir),
    design_name=self.manifest.get("top_module", self.design_name),
    run_id=self.run_id,
)
analysis = analyzer.analyze(magic_data, klayout_data)
print(f"  Cross-tool DRC analysis: {analysis.get('tool_agreement')}")
```

**Guards:**
- Wrapped in `try/except Exception` — exceptions are caught and printed as `[SKIP]`
- Only executes if `gds_path.exists()` AND `drc_result is not None`
- Only executes during the DRC stage of the pipeline

**Side effects when triggered:**
1. `_compare_results()` determines agreement type
2. If `TOOL_DISAGREEMENT`: `_create_disagreement_incident()` creates FA entry via `insert_entry_if_not_exists`
3. `_record_telemetry()` writes `telemetry/drc_agreement.json`

**Frequency:** Exactly once per pipeline run (DRC stage runs once)

---

## Touchpoint 2: Dashboard Time (RunDetail.jsx:123)

**File:** `dashboard/src/RunDetail.jsx`
**Line:** 123
**Context:** DRC/LVS tab component

```javascript
const analysis = run.drc_analysis || {}
```

**Guards:** None needed — read-only access to pre-computed analysis data

**Side effects:** None. The dashboard:
- Does NOT import `CrossToolDRCAnalyzer`
- Does NOT call `analyze()`
- Does NOT create FA incidents
- Only renders the `ToolAgreementBadge` component and the disagreement warning box

**Data flow:** `run.drc_analysis` comes from the API response, which reads `telemetry/drc_agreement.json`.

---

## Touchpoint 3: API Time (server.py:303-306, 331-333)

**File:** `backend/server.py`
**Lines:** 303-306 (run detail endpoint), 331-333 (DRC detail endpoint)
**Context:** Two endpoints read the persisted analysis

### Endpoint 1: `/runs/{run_id}`
```python
drc_agreement_path = run_dir / "telemetry" / "drc_agreement.json"
if drc_agreement_path.exists():
    result["drc_analysis"] = _sanitize(json.loads(drc_agreement_path.read_text()))
```

### Endpoint 2: `/runs/{run_id}/drc`
```python
drc_agreement_path = run_dir / "telemetry" / "drc_agreement.json"
if drc_agreement_path.exists():
    analysis = json.loads(drc_agreement_path.read_text())
```

**Guards:**
- File existence check before reading
- `try/except` on JSON parsing (run detail endpoint only)
- `_sanitize()` strips non-serializable fields

**Side effects:** None. Both endpoints:
- Do NOT import `CrossToolDRCAnalyzer`
- Do NOT write to the database
- Do NOT create FA incidents
- Only read and return pre-existing data

---

## Verification: No Hidden Invocations

| Location | CrossToolDRCAnalyzer found? | Risk |
|---|---|---|
| `gli_flow/core/cross_tool_drc.py` | Yes (definition) | Not an invocation |
| `gli_flow/core/orchestrator.py` | Yes (line 891) | **Primary invocation** |
| `backend/server.py` | No | Read-only |
| `dashboard/src/RunDetail.jsx` | No | Read-only |
| `dashboard/src/FailureAtlasPage.jsx` | No | Read-only |
| `tests/test_cross_tool_drc.py` | Yes (tests) | Test-only |
| Any other `.py` file | No | — |

---

## Conclusion

| Property | Status |
|---|---|
| Cross-tool analysis runs exactly once per run | ✅ YES — DRC stage in orchestrator.py runs once |
| API endpoints are read-only | ✅ YES — both endpoints only read files |
| Dashboard is read-only | ✅ YES — only renders API data |
| No re-analysis at dashboard time | ✅ YES — no analyzer instantiation |
| No re-analysis at API time | ✅ YES — no analyzer instantiation |
| Failure Atlas writes at API/dashboard time | ✅ NO — writes only occur at execution time |

**Lifecycle is correct.** The `CrossToolDRCAnalyzer` is instantiated and invoked exactly once per pipeline run during the DRC stage. All downstream consumers (dashboard, API) are read-only consumers of the pre-computed telemetry file.

**No lifecycle changes needed.**
