# Community Intelligence — Beta Readiness Review

## Audit Date

2026-06-13

## Question

> Can 10 beta testers generate useful knowledge without overwhelming engineers?

## Architecture Constraints

The system is designed as a **knowledge acquisition system**, not a support
ticket system. Key throttles:

1. **Signature gate:** `should_escalate()` blocks known signatures
   (`licon.8a`, `hold_violation`, `power_analysis_failed`, and any
   signature in the library). Only truly unknown failures escalate.
2. **AI gate:** Escalation is only offered after AI Investigation
   Assistant runs. The AI must first determine the failure is unknown.
3. **Consent gate:** Every escalation requires explicit user consent
   with a checkbox. No automatic uploads.
4. **UI gate:** Escalation is a two-click action after viewing AI results.
   It is not automatic and not the default path.

## Expected Escalation Volume

**Assumptions for 10 beta testers:**

- Each tester runs 1 design per week
- Each design has 2–3 unique failure modes
- Of those, 40% are unknown (no signature, no historical data)
- Of unknown failures, 50% get escalated (user views AI, decides to escalate)

**Calculation:**

| Parameter | Value |
|---|---|
| Testers | 10 |
| Designs/week | 1 |
| Failures/design | 2.5 (average) |
| Unknown fraction | 40% |
| Escalation rate | 50% |
| **Escalations/week** | **5** |

**Worst case** (all failures unknown, all escalated):

| Parameter | Value |
|---|---|
| Failures/week | 25 |
| Escalations/week | 25 |

**Realistic estimate:** 3–8 escalations per week.

## Expected Resolution Workload

**Per escalation, engineer effort:**

| Task | Time |
|---|---|
| Read failure package | 5 min |
| Investigate logs/metrics | 15 min |
| Write response (signature, fix, steps) | 10 min |
| **Total per escalation** | **30 min** |

| Scenario | Escalations/week | Engineer hours/week |
|---|---|---|
| Realistic | 5 | 2.5 |
| Upper bound | 25 | 12.5 |

A single engineer spending 2–3 hours per week can realistically handle the
expected volume. At the upper bound, a dedicated half-day is sufficient.

## Expected Signature Growth

**Assumptions:**

- 70% of escalated failures produce a useful signature
- Signatures cover the specific `(tool, failure_type, signature)` triple
- Automatic dedup via the dataset's upsert mechanism

| Period | Escalations | New Signatures | Signature Library Size |
|---|---|---|---|
| Week 1 | 5 | 3 | 6 (3 new + 3 existing) |
| Week 4 | 20 | 12 | 15 |
| Week 12 | 60 | 36 | 39 |

After 12 weeks, ~36 new signatures. This is manageable.

## Knowledge Generation Rate

| Type | Per escalation | Per week (realistic) |
|---|---|---|
| Signature entries | 0.7 | 3.5 |
| Knowledge base entries | 1.0 | 5.0 |
| Dataset frequency increments | 1.0 | 5.0 |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Engineer overwhelmed by noise | Low | High | Signature + AI + consent gates |
| Users escalate known failures | Low | Medium | Known signature block verified |
| Duplicate escalations | Medium | Low | Dataset upsert deduplicates |
| Users expect SLA | Medium | High | Label: "Not a support ticket" |
| Empty/incomplete escalations | Medium | Medium | Failure package auto-populates |
| Engineers ignore queue | Low | Medium | Dashboard shows open count |

## Gates Verified

| Gate | Location | Status |
|---|---|---|
| Known signature block | `should_escalate()` → `should_use_ai()` | PASS |
| AI investigation first | Escalation appears after AI card | PASS |
| Explicit consent required | `create_community_escalation()` HTTP 400 | PASS |
| Privacy validation | `validate_sanitized()` scan | PASS |
| Failure package filtering | Whitelist-based metadata extraction | PASS |
| Status lifecycle | open → submitted → resolved | PASS |
| Conversion format | `to_signature_entry()` / `to_knowledge_entry()` | PASS |

## Pre-Beta Checklist

| Item | Done |
|---|---|
| All 8 phases of quality audit pass | ✓ |
| Consent cannot be bypassed | ✓ |
| No sensitive data in escalation packages | ✓ |
| Known failures cannot be escalated | ✓ |
| Dataset deduplication works | ✓ |
| Engineering dashboard shows open queue | ✓ |
| Engineer response recording works | ✓ |
| Knowledge conversion format is well-defined | ✓ |
| Existing documents cross-reference correctly | ✓ |

## Recommendations Before Beta Launch

1. **Add `UNIQUE(tool, failure_type, signature)` constraint** to prevent
   race conditions in dataset upsert
2. **Add auto-ingest of new signatures** from engineer response to
   signature library (currently manual)
3. **Add a maximum daily escalation rate** per user (e.g., 5/day) to
   prevent spam
4. **Add escalation queue notification** (email or dashboard badge) so
   engineers know when new items arrive
5. **Document expected response time** — recommend stating "no SLA,
   best effort within 1 week"

## Verdict

**READY FOR BETA**

The system will generate useful knowledge without overwhelming engineers.
The triple gate (signature → AI → consent) ensures that only truly unknown,
user-approved failures appear in the engineering queue. At the expected
volume of 3–8 escalations per week, a single engineer with 2–3 hours per
week can maintain the queue and grow the Failure Atlas by ~3 signatures
per week.
