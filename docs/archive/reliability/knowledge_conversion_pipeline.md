# Community Intelligence — Knowledge Conversion Pipeline

## Overview

The Knowledge Conversion Pipeline transforms engineering responses into
Failure Atlas assets. Every escalation that receives an engineer response
has the opportunity to produce:

- **Signature Library entries** — so future occurrences are recognized
- **Knowledge Base entries** — so future users get remediation guidance
- **Historical Intelligence entries** — so correlation engine tracks
  occurrence frequency

## Pipeline Flow

```
Escalation Created (open)
    │
    ▼
Escalation Submitted to BharatCode
    │
    ▼
Engineer Responds
    │
    ├──► record_engineer_response()
    │       │
    │       ├──► status → resolved
    │       ├──► engineer_response JSON stored
    │       └──► atlas_id_created set
    │
    ▼
Knowledge Conversion
    │
    ├──► EngineeringResponse.to_signature_entry()
    │       └──► Produces signature library entry candidate
    │             {atlas_id, category, observed_signature,
    │              remediation, confidence: 0.7, public: true}
    │
    ├──► EngineeringResponse.to_knowledge_entry()
    │       └──► Produces knowledge base entry candidate
    │             {failure_type, description, common_causes,
    │              remediation_strategies, verification_steps}
    │
    └──► KnowledgeContribution metadata tracks what was created
            {new_signature_created, new_historical_intelligence,
             new_resolution_intelligence, atlas_id_assigned}
```

## Conversion Triggers

| Event | Action |
|---|---|
| `record_engineer_response()` | Status → `resolved`, stores response JSON |
| `to_signature_entry()` called | Returns `{}` if `signature=""` (no conversion) |
| `to_knowledge_entry()` called | Always returns a valid entry (graceful degradation) |

## Signature Entry Schema

Output of `to_signature_entry()`:

```json
{
  "atlas_id": "FA-XXXXX",
  "category": "<failure_type>",
  "severity": "MEDIUM",
  "observed_signature": "<signature>",
  "remediation": "<fix_description>",
  "description": "<description>",
  "confidence": 0.7,
  "public": true
}
```

## Knowledge Entry Schema

Output of `to_knowledge_entry()`:

```json
{
  "failure_type": "<failure_type>",
  "description": "<description>",
  "common_causes": ["<description>"],
  "remediation_strategies": [
    {
      "technique": "<fix_description>",
      "description": "<fix_description>"
    }
  ],
  "verification_steps": ["<steps>"],
  "references": ["<references>"],
  "confidence": "MEDIUM"
}
```

## Conversion Rate (Measured)

| Metric | Value |
|---|---|
| `to_signature_entry()` with non-empty signature | Returns valid entry |
| `to_signature_entry()` with empty signature | Returns `{}` |
| `to_knowledge_entry()` always | Returns valid entry |
| `escalation_id` persists through entire pipeline | Verified |
| `atlas_id_created` stored in DB after response | Verified |
| Historical tracking in dataset via `frequency` | Verified |

## Atlas Integration

When a new signature is added to `KNOWN_SIGNATURES` (or the signature library):

1. `should_use_ai()` checks `KNOWN_SIGNATURES` set first
2. If match found, returns `use_ai=False` — no AI investigation
3. `should_escalate()` calls `should_use_ai()` — returns False
4. Future failures matching this signature skip both AI and escalation

This was verified for all three known signatures (`licon.8a`,
`hold_violation`, `power_analysis_failed`) and for newly added signatures.

**Critical Path:** An engineer's response must be manually or automatically
added to `KNOWN_SIGNATURES` (or the signature library on disk) for the
block to take effect. `record_engineer_response()` does not automatically
update the signature library — it only stores the response data.

## Recommendations

1. **High:** Add an auto-ingest step after `record_engineer_response()`
   that calls `to_signature_entry()` and writes the result to the
   signature library, so new knowledge is immediately usable
2. **Medium:** Add `severity` field from escalation to signature entry
   (currently hardcoded to `MEDIUM`)
3. **Low:** Add `confidence` scaling based on engineer's historical
   accuracy or team reputation
