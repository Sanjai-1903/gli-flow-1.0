# AI Failure Explanation System Design

## Problem

The AI Investigation Assistant (`failure_atlas/ai_assistant/`) currently:
- Only activates for UNKNOWN failures (trigger.py line 44: skips known signatures)
- Returns generic "Possible causes" without evidence citation
- Capped at MEDIUM confidence even with definitive evidence
- Never references actual report files, line numbers, or violation counts
- Not integrated into dashboard or CLI output for failed runs

A user running `gli-flow diagnose` on a picorv32 failure gets:
1. No pattern match (known failures are skipped)
2. AI not triggered (known signatures)
3. No root cause explanation
4. Must read raw logs

## Solution: Universal AI Activation

### Trigger Reform

Eliminate the "unknown only" filter. New rules:

| Condition | Action |
|-----------|--------|
| Any failed run | Generate AI failure explanation |
| Known signature (INF-MAGIC-002) | Generate explanation with citation to knowledge base |
| Known pattern (hold violation) | Generate explanation with specifics (WNS, TNS values) |
| Unknown pattern | Generate explanation with lower confidence |
| Success + regression | Generate explanation of regression |

### Response Model (Expanded)

```python
@dataclass
class AIFailureExplanation:
    summary: str                          # "6 DRC violations found, LVS timed out"
    evidence: list[EvidenceItem]          # Specific files and line numbers
    likely_cause: str                     # "Magic DRC detected licon.8a (tool false positive) 
                                           #  and li.3 spacing violations (real); LVS extraction 
                                           #  exceeded 600s timeout on 40MB .ext file"
    recommended_actions: list[str]        # Ordered, actionable
    confidence: str                       # LOW, MEDIUM, or HIGH
    disclaimer: str                       # "AI GENERATED — EXPERIMENTAL — NOT VERIFIED"
    knowledge_base_citations: list[str]   # INF-MAGIC-002, etc.

@dataclass
class EvidenceItem:
    file: str                             # Relative path from run_dir
    line: int                             # Line number (or 0)
    content: str                          # Relevant line or snippet
    source: str                           # magic_drc, klayout_drc, lvs, timing, error_log
```

### Confidence Reforms

| Evidence Quality | Confidence |
|-----------------|------------|
| Exact violation counts from report | HIGH |
| Known pattern with exact match | HIGH |
| Known pattern without exact match | MEDIUM |
| No pattern match, inferred | LOW |

### Integration Points

1. **After any failed run** (orchestrator.py): Generate explanation automatically
2. **Run detail dashboard**: Show AI explanation section
3. **`gli-flow diagnose`**: Show AI explanation as primary output
4. **Run summary markdown**: Include AI explanation section
5. **Failure Atlas**: Link root cause entries to AI explanation

### File: `failure_atlas/ai_assistant/explanation_engine.py`

New module that:
1. Reads all evidence files (DRC reports, LVS summary, timing reports, logs)
2. Builds structured evidence list
3. Matches patterns (known issues)
4. Generates deterministic explanation without external AI API
5. Returns `AIFailureExplanation` with full evidence tracking
