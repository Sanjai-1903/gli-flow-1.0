# Community Intelligence Network — Architecture

## Overview

The Community Intelligence Network transforms unknown failures into future
Failure Atlas knowledge using BharatCode email infrastructure as a
human-assisted escalation path.

This is **not** a support ticket system.  
This is a **Failure Atlas knowledge acquisition system**.

## Vision

```
Today:                           Future:
Unknown Failure                  Unknown Failure
       │                               │
       ▼                               ▼
  User stuck              AI Investigation Assistant
                                  │
                                  ▼
                          Escalate to GLI
                                  │
                                  ▼
                          Engineer reviews
                                  │
                                  ▼
                          Resolution captured
                                  │
                                  ▼
                          Failure Atlas grows
                                  │
                                  ▼
                          Future users get instant answer
```

## Escalation Point

The escalation point is **after** the AI Investigation Assistant:

```
Failure detected
    │
    ▼
┌─────────────────────┐
│  Signature Engine    │───── Match? ──► Known → Normal Path
└─────────┬───────────┘
          │ No match
          ▼
┌─────────────────────┐
│  AI Investigation    │
│  Assistant           │───── Generates guidance
└─────────┬───────────┘
          │ Still unknown / User wants help
          ▼
┌─────────────────────────────────────┐
│  Community Intelligence Escalation  │
│  ┌───────────────────────────────┐  │
│  │  Escalation Trigger           │  │
│  │  • No signature exists        │  │
│  │  • No historical intelligence │  │
│  │  • User explicitly requests   │  │
│  └───────────┬───────────────────┘  │
│              ▼                      │
│  ┌───────────────────────────────┐  │
│  │  Failure Package Builder      │  │
│  │  • Sanitized (no RTL/GDS/IP)  │  │
│  │  • Tool, stage, error, metrics│  │
│  │  • AI suggestions, comments   │  │
│  │  • Consent record             │  │
│  └───────────┬───────────────────┘  │
│              ▼                      │
│  ┌───────────────────────────────┐  │
│  │  BharatCode Email API          │  │
│  │  → Submit to GLI engineers     │  │
│  └───────────┬───────────────────┘  │
└──────────────┼────────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  Engineering Response               │
│  ┌───────────────────────────────┐  │
│  │  Structured Response          │  │
│  │  → Failure Atlas Signature    │  │
│  │  → Historical Intelligence    │  │
│  │  → Resolution Intelligence    │  │
│  └───────────────────────────────┘  │
│  Every resolution must be:          │
│  • Reusable • Structured • Searchable
└─────────────────────────────────────┘
```

## Escalation Trigger

Escalation is allowed ONLY when:
- No signature exists in the signature library
- OR no historical intelligence for this failure type
- OR user explicitly requests help (opt-in)

Escalation must NOT automatically trigger for:
- `licon.8a` (DRC enclosure)
- `hold_violation` (timing)
- `power_analysis_failed` (power)
- Any FA-XXXX entry with matching signature

## Failure Package Schema

```json
{
  "package_version": "1.0",
  "consent_record": {
    "consent_given": true,
    "consent_timestamp": "2026-01-01T00:00:00Z",
    "user_acknowledged_no_sensitive_data": true
  },
  "failure": {
    "tool": "openroad",
    "stage": "SYNTHESIS",
    "failure_type": "UNKNOWN_SYNTHESIS_ERROR",
    "error_text": "Error message from tool",
    "log_excerpt": "Last 100 lines of relevant log",
    "metrics": { "wns": -0.45, "tns": -12.3 },
    "design_metadata": { "design_name": "gcd", "pdk": "sky130A" },
    "run_metadata": { "run_id": "run_1234", "timestamp": "..." }
  },
  "ai_suggestions": {
    "summary": "...",
    "possible_causes": ["..."],
    "investigation_steps": ["..."],
    "references": ["..."]
  },
  "user_notes": "Additional context from user",
  "feedback": {
    "ai_was_helpful": true,
    "user_resolved": false
  }
}
```

### Excluded Fields

The following must NEVER be included:
- RTL source code (.v, .sv files)
- GDS / OASIS layout data
- Netlists (verilog, SPICE, DEF)
- Customer IP or proprietary modules
- Full project directory structure
- License keys or credentials

## Engineering Response Format

```json
{
  "escalation_id": "ESC-2026-0001",
  "response_version": "1.0",
  "created_at": "2026-01-01T00:00:00Z",
  "engineer": {
    "name": "Engineer Name",
    "email": "engineer@greenlantern.com"
  },
  "resolution": {
    "failure_type": "SETUP_VIOLATION",
    "signature": "wns_below_threshold_after_routing",
    "atlas_id": "FA-0021",
    "description": "...",
    "fix_description": "Increased clock period",
    "verification_steps": ["..."],
    "references": ["..."]
  },
  "knowledge_contribution": {
    "new_signature_created": true,
    "new_historical_intelligence": true,
    "new_resolution_intelligence": true,
    "atlas_id_assigned": "FA-0021"
  }
}
```

## Telemetry Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `escalation_created` | User initiates escalation | escalation_id, failure_type, tool |
| `escalation_sent` | Email successfully sent | escalation_id, bharatcode_submission_id |
| `escalation_resolved` | Engineer responds | escalation_id, atlas_id |
| `knowledge_created` | New FA entry created | atlas_id, failure_type |
| `signature_created` | New signature added | signature_id, failure_type |

## Dashboard Integration

### Failure Atlas View — Escalate Button

```
┌────────────────────────────────────────────┐
│  AI Investigation Assistant                │
│  ⚡ EXPERIMENTAL · AI GENERATED            │
│                                            │
│  ┌────────────────────────────────────┐    │
│  │  Still stuck? Submit to GLI        │    │
│  │  engineers for analysis.           │    │
│  │                                    │    │
│  │  [Submit to Green Lantern]         │    │
│  │                                    │    │
│  │  Only diagnostic metadata sent.    │    │
│  │  No RTL, GDS, or source code.     │    │
│  └────────────────────────────────────┘    │
└────────────────────────────────────────────┘
```

### Escalation Confirmation Dialog

```
╔══════════════════════════════════════════╗
║  Submit to Green Lantern Industries     ║
║                                          ║
║  This submission contains ONLY:          ║
║  ✓ Tool & stage information              ║
║  ✓ Error text and log excerpts           ║
║  ✓ AI-generated investigation guidance   ║
║  ✓ Execution metrics                     ║
║                                          ║
║  ✗ NO RTL source code                   ║
║  ✗ NO GDS / layout data                 ║
║  ✗ NO netlists                          ║
║  ✗ NO customer IP                       ║
║  ✗ NO full project files                ║
║                                          ║
║  Additional notes (optional):            ║
║  ┌──────────────────────────────────┐   ║
║  │                                  │   ║
║  │                                  │   ║
║  └──────────────────────────────────┘   ║
║                                          ║
║  [Cancel]  [I Consent — Submit]         ║
╚══════════════════════════════════════════╝
```

### Engineering Dashboard

```
┌──────────────────────────────────────────────┐
│  Engineering Dashboard — Community Network   │
├──────────────────────────────────────────────┤
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌──────────┐ │
│  │ Open  │ │Resolved│ │Con-   │ │Top       │ │
│  │Escala-│ │Escala- │ │verted │ │Unknown   │ │
│  │tions  │ │tions   │ │Sig's  │ │Failures  │ │
│  │ 12    │ │ 45     │ │ 8     │ │ CONGEST… │ │
│  └───────┘ └───────┘ └───────┘ └──────────┘ │
│                                              │
│  Open Escalations Queue                      │
│  ┌──────────────────────────────────────┐   │
│  │ ESC-2026-001 │ SYNTHESIS │ 2d ago   │   │
│  │ ESC-2026-002 │ ROUTING   │ 5d ago   │   │
│  │ ...          │           │          │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  Knowledge Gaps                              │
│  ┌──────────────────────────────────────┐   │
│  │ Failure Type           │ Frequency  │   │
│  │ UNKNOWN_SYNTHESIS_ERR  │ 12         │   │
│  │ MAGIC_DRC_PARSE_FAIL   │ 8          │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

## Dataset Creation

An internal dataset of unknown failures is maintained with fields:

| Field | Description |
|-------|-------------|
| `tool` | EDA tool that failed |
| `failure_type` | Classified failure type |
| `signature` | Observed signature string |
| `frequency` | How often this failure occurs |
| `ai_helpfulness` | Was AI guidance marked helpful? |
| `resolution_outcome` | Resolution if issue was solved |
| `consent_given` | Was consent provided for escalation |

This becomes training data for:
- Future Failure Atlas entries
- Future GLI-SDI (Supervised Design Intelligence)
- Future LCM (Lifecycle Management)

## Success Criteria

| Before | After |
|--------|-------|
| Unknown failure → user stuck alone | Unknown failure → AI guidance → escalate → engineer → FA grows |
| Engineer effort is one-off | Engineer effort compounds across users |
| Knowledge is lost after email reply | Knowledge is captured as structured, reusable data |
| Failure Atlas is static | Failure Atlas grows with each escalation |
| BharatCode is just email | BharatCode is a knowledge acquisition channel |
