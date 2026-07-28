# Production Gap Audit

**Date:** 2026-06-13
**Auditor:** Principal Staff Engineer, ASIC Infrastructure
**Scope:** All user-facing workflows in GLI-FLOW v1.0.0

---

## CLI

### `gli-flow run`

| Issue | Type | Details |
|-------|------|---------|
| Single binary pass/fail status | Misleading | A run that produces valid GDS but fails DRC is marked `FAILED` with no distinction between implementation failure and signoff failure. `run_summary.md` line 4: `Status: FAILED` collapses both outcomes. |
| QoR = 0 on signoff failure | Misleading | `qor_score.py` computes a legitimate score but orchestrator stores it even when signoff fails, yet the run is `FAILED` and the score is displayed as `0.0` in `run_summary.md` line 8. |
| No implementation summary | Missing | CLI never reports "Synthesis OK", "Routing OK", "GDS generated" separately from signoff. User cannot tell if the RTL is bad or if only signoff checks failed. |
| Backend duration not shown per stage | Missing | Only total runtime is reported. No per-ORFS-stage timing. |

### `gli-flow history`

| Issue | Type | Details |
|-------|------|---------|
| Status column shows only FAILED/SUCCESS | Missing | No implementation_status or signoff_status columns. User cannot filter by "implementation succeeded but signoff failed". |
| QoR shown as 0.0 for failed runs | Misleading | `output.py` line 108-113 prints QoR regardless of context, creating false impression of zero quality. |

### `gli-flow status`

| Issue | Type | Details |
|-------|------|---------|
| Identical data to history | Duplicate | `status_command()` (line 596) is a subset of `history_command()` (line 586). |
| No live run progress | Missing | No elapsed time, no estimated remaining, no sub-stage visibility. |

### `gli-flow diagnose`

| Issue | Type | Details |
|-------|------|---------|
| Falls through to AI on known failures | Confusing | `diagnose_command()` line 1350-1362: tries regex patterns first, then falls through to AI assistant. But `trigger.py` line 44 explicitly skips AI for known signatures like `licon.8a`. User gets neither pattern match nor AI explanation. |
| Returns raw log snippets | Missing | Outputs raw log text without structured root cause summary. User must read logs. |
| No action prioritization | Missing | Lists findings without ordering by impact or recommended first step. |

### `gli-flow ai-assist`

| Issue | Type | Details |
|-------|------|---------|
| Only triggers for UNKNOWN failures | Bug | `trigger.py` line 25-117: AI bypassed for all known signatures, historical matches, and patterns with >= 60% confidence. This means the AI assistant explicitly excludes the most common, reproducible failures. |
| Heuristic fallback is generic | Missing | `response_schema.py` line 47-120: fallback responses do not reference actual report files, log snippets, or violation counts. |
| No citation of evidence | Missing | AI response does not include which specific file was read, what line, what value. |
| Confidence capped at MEDIUM | Missing | `response_schema.py` line 14: `confidence` limited to `LOW` or `MEDIUM`. Even when exact violations are known, confidence is artificially suppressed. |
| Response says "Possible causes" not "Likely cause" | Missing | Line 8-9: "Never return 'Root cause is...', 'This will fix it.'" — but when evidence is definitive, the system should assert with appropriate confidence. |

### `gli-flow dashboard`

| Issue | Type | Details |
|-------|------|---------|
| Run status shows only FAILED/SUCCESS | Misleading | `backend/server.py` line 253-321 returns `status` field only. No `implementation_status` or `signoff_status`. |
| Live runs have no sub-stage info | Missing | `backend/server.py` line 165-188: `/live_runs` returns only stage name, no elapsed time, no ORFS sub-stage, no routing iteration. |
| No AI explanation on dashboard | Missing | Dashboard never shows AI-generated failure explanations for failed runs. |
| QoR trends include failed runs | Misleading | QoR = 0.0 runs pollute trend charts, making improvements invisible. |

---

## Dashboard Pages

### Run Summary

| Issue | Type | Details |
|-------|------|---------|
| "FAILED" status ambiguous | Confusion | App.jsx line 486-775: status shown as single badge. User cannot distinguish "implementation failed" from "signoff failed" without clicking through. |
| No root cause summary | Missing | No "What went wrong" section. User must manually inspect DRC/LVS/timing sections. |
| No "What to do next" | Missing | No recommended next-action steps. |

### Timing

| Issue | Type | Details |
|-------|------|---------|
| Shows N/A when timing not run | Confusion | WNS/TNS shown as N/A when LVS/DRC blocked before timing analysis, but no explanation of WHY timing wasn't run. |

### Area & Power

| Issue | Type | Details |
|-------|------|---------|
| Shows N/A when data missing | Missing | No explanation of whether stage wasn't reached, or data wasn't parsed. |

### DRC/LVS

| Issue | Type | Details |
|-------|------|---------|
| Only shows pass/fail counts | Missing | No violation breakdown by rule. `backend/server.py` line 322-340: `/runs/{run_id}/drc` returns minimal data. |
| No cross-tool comparison | Missing | User cannot see which violations are real (both tools agree) vs tool-specific. |
| LVS timeout not explained | Missing | User sees "FAIL" without explanation of whether extraction timed out, netgen failed, or comparison failed. |

### Layout Images

| Issue | Type | Details |
|-------|------|---------|
| Placeholder images | Missing | `orchestrator.py` line 1183: `generate_placeholder_images()` creates dummy PNGs. User cannot visually inspect layout. |
| No DRC marker overlay | Missing | Violation coordinates from magic_drc.rpt are not rendered on layout images. |

### Reports

| Issue | Type | Details |
|-------|------|---------|
| Raw text display only | Missing | Reports shown as text blocks; no structured analysis. |

### Failure Atlas

| Issue | Type | Details |
|-------|------|---------|
| Symptom flooding | Duplicate | `orchestrator.py` line 807-838: `_record_signoff_failures()` creates one entry per signoff failure. A run with 6 DRC violations + LVS timeout generates 8+ entries, all symptoms, no root cause. |
| No root cause grouping | Missing | `FailureAtlasEntry` has no "parent" root cause field. All entries are flat. |
| Dedup only by (run, type, signature) | Missing | `repository.py` line 90: `insert_entry_if_not_exists()` dedup is too narrow — same root cause can have different signatures. |

### Reproducibility

| Issue | Type | Details |
|-------|------|---------|
| JSON manifest present but not visible | Missing | `provenance/manifest.py` generates data but dashboard doesn't render it prominently. |

---

## Production Readiness Gaps Summary

| Gap | Severity | Impact |
|-----|----------|--------|
| No implementation vs signoff separation | P0 | Users cannot tell if RTL is bad or flow is misconfigured |
| AI assistant skips known failures | P0 | Most common failures have no AI explanation |
| QoR collapses to 0 on signoff failure | P0 | Scoring meaningless for failed runs, trend charts polluted |
| No root cause hierarchy in Failure Atlas | P1 | Symptom flooding obscures actionable information |
| No live ORFS sub-stage visibility | P1 | Users think flow is frozen during long runs |
| No per-rule DRC breakdown in dashboard | P1 | Users must read raw reports |
| Placeholder layout images | P2 | Cannot visually inspect layout |
| diagnose command gaps for known failures | P2 | Falls through without actionable output |
| No "what to do next" anywhere | P2 | Users must know the flow internals to take action |

---

## Files Audited

- `gli_flow/core/orchestrator.py` (1297 lines)
- `gli_flow/cli/main.py` (2187 lines)
- `gli_flow/cli/output.py` (370 lines)
- `gli_flow/models/execution_record.py` (24 lines)
- `gli_flow/analytics/qor_score.py` (83 lines)
- `gli_flow/database/sqlite.py` (301 lines)
- `gli_flow/database/migrations.py` (479 lines)
- `failure_atlas/schema.py` (48 lines)
- `failure_atlas/detector.py` (146 lines)
- `failure_atlas/repository.py` (493 lines)
- `failure_atlas/ai_assistant/trigger.py` (122 lines)
- `failure_atlas/ai_assistant/context.py` (140 lines)
- `failure_atlas/ai_assistant/response_schema.py` (173 lines)
- `dashboard/src/App.jsx` (797 lines)
- `dashboard/src/RunDetail.jsx`
- `backend/server.py` (1516+ lines)
