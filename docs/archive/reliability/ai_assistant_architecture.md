# AI Investigation Assistant — Architecture

## Overview

The AI Investigation Assistant provides guidance when the Failure Atlas cannot
resolve a failure through known knowledge. It must never present output as
fact, never override signoff, and always be clearly labeled as AI-generated.

## Decision Flow

```
Failure detected
    │
    ▼
┌─────────────────────┐
│  Failure Atlas       │
│  Signature Engine    │───── Match? ──► Known → Route to Normal Path
│  & Detector          │
└─────────┬───────────┘
          │ No match / Low confidence
          ▼
┌─────────────────────┐
│  Historical          │
│  Intelligence        │───── Match? ──► Known → Route to Normal Path
│  (Correlation Engine)│
└─────────┬───────────┘
          │ No historical data / Low confidence
          ▼
┌─────────────────────┐
│  Resolution          │
│  Intelligence        │───── Match? ──► Known → Route to Normal Path
│  (Knowledge Base)    │
└─────────┬───────────┘
          │ No resolution data
          ▼
┌─────────────────────────────────────┐
│  AI Investigation Assistant         │
│  ┌───────────────────────────────┐  │
│  │  Context Collection            │  │
│  │  • Tool & Stage                │  │
│  │  • Error text / Log snippet   │  │
│  │  • Failure type & metrics     │  │
│  │  • Design & Run metadata      │  │
│  │  • Known evidence              │  │
│  └───────────┬───────────────────┘  │
│              ▼                      │
│  ┌───────────────────────────────┐  │
│  │  AI Provider (LLM / Heuristic)│  │
│  │  → Possible causes            │  │
│  │  → Investigation steps        │  │
│  │  → References                 │  │
│  └───────────┬───────────────────┘  │
│              ▼                      │
│  ┌───────────────────────────────┐  │
│  │  Response Contract            │  │
│  │  • Confidence: LOW            │  │
│  │  • Disclaimer: true           │  │
│  │  • No root cause claims       │  │
│  └───────────┬───────────────────┘  │
└──────────────┼────────────────────────┘
               ▼
        CLI / Dashboard Display
        ═══════════════════════
        AI GENERATED · EXPERIMENTAL · NOT VERIFIED
        ─────────────────────────────────────────
        Possible causes, suggested investigations
```

## Where AI Enters the Workflow

The AI Assistant is invoked *after* all deterministic knowledge sources
have been exhausted:

1. **Signature Engine** — no matching signature
2. **Historical Intelligence** — no historical correlation data
3. **Resolution Intelligence** — no known resolution data

Or when:

4. **Classification Confidence** is below threshold (< 0.6)

## Trigger Conditions

| Condition | When AI is Allowed |
|-----------|-------------------|
| No matching signature | `signature_engine.scan_file()` returns empty |
| No historical intelligence | `correlation_engine` returns zero occurrences |
| Low-confidence classification | `confidence < 0.6` |
| Unknown error (no FA entry) | `failure_type` not in knowledge base |

AI is **NOT** triggered for known signatures:
- `licon.8a` (DRC enclosure)
- `hold_violation` (timing)
- `power_analysis_failed` (power)
- Any FA-XXXX entry with confidence ≥ 0.6

## Context Package

Built by `context.py`, contains:

| Field | Description | Included |
|-------|-------------|----------|
| `tool` | EDA tool that failed (openroad, magic, etc.) | Always |
| `stage` | Pipeline stage at failure | Always |
| `error_text` | Error message from tool or run log | Always |
| `log_snippet` | Last N lines of relevant log | Last 100 lines |
| `failure_type` | Failure type classification | Always |
| `metrics` | Key execution metrics | WNS, TNS, utilization, etc. |
| `design_metadata` | Design name, top module, PDK | Always |
| `run_metadata` | Run ID, timestamp, backend | Always |
| `known_evidence` | Evidence already collected | Always |

**Excluded from context:**
- RTL source code
- GDS / layout data
- Netlists
- Customer IP
- Full project files

## AI Response Contract

```json
{
  "confidence": "LOW",
  "summary": "Brief summary of the investigation guidance",
  "possible_causes": [
    "Cause 1 description",
    "Cause 2 description"
  ],
  "investigation_steps": [
    "Step 1: ...",
    "Step 2: ..."
  ],
  "references": [
    "Reference 1",
    "Reference 2"
  ],
  "disclaimer": true
}
```

### Strict Rules

- ❌ Never return: "Root cause is..."
- ❌ Never return: "This will fix it."
- ✅ Instead: "Possible causes"
- ✅ Instead: "Suggested investigations"

## Safety Requirements

AI output must NEVER:
- Override signoff decisions
- Override DRC results
- Override LVS results
- Override STA results
- Change severity of a failure
- Mark failures as resolved
- Modify tapeout readiness

## User Feedback Loop

After AI guidance is shown, users may mark:

| Feedback | Action |
|----------|--------|
| Helpful | Store feedback type + timestamp |
| Not Helpful | Store feedback type + timestamp |
| Resolved Issue | Store + update resolution capture |
| Did Not Resolve | Store + keep failure active |

Feedback is stored in `ai_investigation_feedback` table.

## Resolution Capture

When a user resolves an issue that was guided by the AI assistant:

```json
{
  "failure_type": "SETUP_VIOLATION",
  "tool": "openroad",
  "fix_description": "Reduced clock frequency from 50MHz to 40MHz",
  "resolution_outcome": "WNS improved from -0.45 to +0.12"
}
```

This data becomes candidate for:
- Future Signature Library entries
- Future Historical Intelligence
- Future GLI-SDI training data

## Email Workflow (Optional)

Using the BharatCode API, users may submit unknown failures to
Green Lantern Industries for expert analysis.

- Requires explicit user consent
- Includes: failure metadata, AI suggestions, resolution outcome
- No automatic uploads

## Dashboard Integration

The AI Investigation Assistant appears in the Failure Atlas view as:

```
┌─────────────────────────────────────────────┐
│  🖄 AI Investigation Assistant              │
│  ⚡ EXPERIMENTAL · AI GENERATED · NOT VERIFIED │
│                                             │
│  Confidence: LOW                            │
│  ─────────────────────────────────────────  │
│  Possible Causes:                           │
│  • ...                                      │
│                                             │
│  Suggested Investigation Steps:             │
│  • ...                                      │
│                                             │
│  ┌────────────────────────────────────┐     │
│  │  Helpful?  [Yes] [No]              │     │
│  │  Resolved? [Yes] [No]              │     │
│  └────────────────────────────────────┘     │
└─────────────────────────────────────────────┘
```

Displayed in a distinct card with:
- Different color scheme (purple/amber)
- Border label: "AI GENERATED"
- Card sublabel: "EXPERIMENTAL · NOT VERIFIED"

## Success Criteria

| Failure Type | Route |
|-------------|-------|
| Known failures (FA-XXXX) | Failure Atlas |
| Known historical failures | Historical Intelligence |
| Known successful fixes | Resolution Intelligence |
| Unknown / novel failures | AI Investigation Assistant |

All AI output is visibly labeled:
- `AI GENERATED`
- `EXPERIMENTAL`
- `NOT VERIFIED`

Trust and signoff integrity remain unchanged.
