# GLI-FLOW Benchmark Test Protocol
### CCR v0.1 — Stage 0 Pre-Registered Accuracy Validation

*This protocol makes the Validation Playbook's Section 3.1 requirements and the Tech Spec's M2 milestone literally executable. It is scoped to CCR v0.1 (topological proximity + local impact magnitude only, per the Tech Spec's CCR Roadmap) — not the full v1.0 system. Follow it in order. Do not skip the pre-registration step, even under time pressure — it is the entire point.*

---

## 1. Purpose and Scope

**What this protocol produces:** the first real, defensible, publishable number for GLI-FLOW — a measured top-1 and top-3 accuracy of CCR's root-cause ranking on Sky130/GF180 timing-closure failures, under blind and held-out conditions.

**Why this is urgent, not just correct process:** per the Consolidated Company State document (Section 10), ArchGen AI — a similarly early-stage, closely-scoped competitor — has already published a verified, third-party-judged benchmark result. The credibility gap this protocol closes is no longer just "a proof point doesn't exist yet" in the abstract; it's now measured against a direct competitor that already has one. That doesn't change anything about how this protocol should be run — rigor shouldn't be traded for speed — but it is the reason this is the single most time-sensitive document produced so far.

**What it explicitly does not test:** explanatory-breadth scoring (CCR v0.2), Failure Atlas historical-precedent scoring (CCR v0.3), or any commercial-node (28–90nm) data. Those get their own, later benchmark runs once CCR reaches those versions and Stage 1 partners exist. Testing v0.1's narrower scope first is deliberate — a clean result on a narrow claim is worth more than a muddy result on an overclaimed one.

---

## 2. Step One: The Pre-Registration Document (Fill In and Freeze Before Any Testing)

Copy the block below into its own file, fill in every blank, date it, and do not edit it after testing begins. This is the single most important artifact in this protocol.

```
GLI-FLOW CCR v0.1 BENCHMARK — PRE-REGISTRATION
Date frozen: ______________
Frozen by: ______________ (must be before Section 4's test set is run through CCR even once)

1. Test set size: _____ cases (minimum 30; target 50+, see Section 3)
2. Test set composition: _____ synthetic fault-injection cases / _____ natural historical cases
   (see Section 3.1 and 3.2 for how each category is built)
3. Primary success metric: CCR's top-1 ranked candidate matches the true root cause
   in ≥ _____ % of cases
4. Secondary success metric: the true root cause appears in CCR's top-3 ranked
   candidates in ≥ _____ % of cases
5. Match criterion definition (see Section 5.2 — pick ONE before freezing):
   [ ] Exact match — same design object/constraint identifier
   [ ] Category match — same type of cause (e.g., "clock uncertainty change")
       even if the exact instance differs
6. Grader: ______________ (must be someone who did not write CCR's scoring code —
   see Section 4)
7. What happens if the primary metric is not met: ______________
   (write this down now, not after seeing the result — see Section 7)
```

**Why the match criterion matters enough to force a choice now:** "exact match" is the harder, more defensible bar and the one to prefer if the test set allows it. "Category match" is more forgiving and easier to hit — deciding this after seeing results would let the softer bar get chosen only when the harder one fails, which is exactly the self-deception this protocol exists to prevent.

---

## 3. Step Two: Building the Test Set

**Target: 50+ cases if achievable, 30 as an absolute floor.** Below 30, any accuracy percentage has a confidence interval wide enough to be close to meaningless (see Section 6).

### 3.1 Synthetic Fault-Injection Cases (build these first — they give unambiguous ground truth)

**Note on why this category exists:** the Validation Playbook's Section 3.1 originally specified "real timing-closure failure cases" only. This protocol deliberately extends that with synthetic fault-injection cases, for a specific reason: with no large natural regression history yet, real-case ground truth would rest entirely on one expert's judgment call. Synthetic cases remove that ambiguity by construction. This is a refinement of the original spec, not a departure from it — both case types are used together (Section 3.2 still covers real cases), and the synthetic category should never fully replace real-world validation.

Because there isn't yet a large natural history of Sky130/GF180 regressions to mine, the fastest way to a rigorous initial test set is to **construct cases where the ground truth is known by design**, not by human judgment:

1. Take a stable, passing Sky130 or GF180 design as the baseline run.
2. Introduce exactly **one** deliberate, logged change per case, drawn from this list (aim for coverage across categories, not repeats of the same type):
   - A clock uncertainty value change in the SDC.
   - A false-path or multicycle-path exception added or removed.
   - A single buffer/cell removed or resized in the netlist (simulating a CTS-driven change).
   - A macro or block shifted in the floorplan (simulating a placement-driven congestion/routing effect).
   - An input/output delay constraint modified.
3. Re-run the flow, producing a new report with one or more timing violations.
4. **Because exactly one change was introduced, the ground truth root cause is known with certainty** — no human judgment call required for these cases. This eliminates grader subjectivity entirely for this portion of the set.
5. Log each case with: the exact injected change, the resulting violated path(s), and a case ID. This log is the ground-truth key — keep it separate from whatever CCR sees.

**Target: 30–35 of these** — roughly 6–7 cases per category across the five change types above, not just one pass of 4–5 each. Hitting the overall 50+ target depends primarily on this category, since natural cases (Section 3.2) are realistically fewer at this stage. If time or design variety only supports the floor (4–5 per category, ~20–25 total), that's acceptable **but must be stated honestly in the pre-registration document as a 30-case run, not silently presented as having hit the 50+ target.**

### 3.2 Natural Historical Cases (build these second — they test real-world validity)

Pull any genuinely occurring failures from actual Sky130/GF180 iteration history done so far during PoC development, where more than one thing plausibly changed between runs (the messier, more realistic case fault-injection can't fully simulate).

**Target: at least 10–15 of these**, if that many naturally exist. If fewer exist, note the actual count honestly in the pre-registration document rather than padding the set with synthetic cases mislabeled as natural — the whole point of this category is testing against real-world messiness, and a smaller-but-honest count is more useful than an inflated one.

**Realistic total, stated plainly:** 30–35 synthetic + 10–15 natural gives a realistic range of 40–50 cases. If the true achievable number lands at 30–40 rather than 50+, that is an acceptable, honest outcome under this protocol's own floor (Section 1) — the pre-registration document must record the actual number used, not the aspirational target.

### 3.3 Held-Out Discipline

Before CCR v0.1's scoring logic is finalized, **set aside at least 30% of the assembled test set and do not look at it, run it, or use it for any debugging or tuning of CCR's scoring formula.** Use the remaining ~70% freely during development. Only the held-out portion counts toward the final pre-registered benchmark number. Mixing development and test cases is the single easiest way to produce a number that looks good and means nothing.

---

## 4. Step Three: Recruiting and Briefing the Blind Grader

**Who:** someone with genuine STA/physical-design expertise who did **not** write CCR's scoring code — a mentor through the IITM ecosystem, a contact from the EDA-veteran advisor network, or a qualified peer. The founder grading their own tool's output is not a valid substitute; this is non-negotiable for the result to mean anything to an outside reader.

**Blinding procedure:**
1. For the natural historical cases (Section 3.2), the grader independently determines what they believe the true root cause was, using only the raw reports and diffs — **before** ever seeing CCR's output for that case.
2. For the synthetic fault-injection cases (Section 3.1), blinding the grader isn't necessary for establishing ground truth (it's already known by construction) — but the grader should still independently score whether CCR's output matches that known ground truth, without seeing the founder's own assessment first.
3. Only after the grader's independent judgment is recorded should CCR's actual ranked output be revealed and compared against it.

**If feasible, use a second grader on a 10–15 case subset** to check inter-rater agreement — if two independent experts disagree with each other on what the "true" cause was for a meaningful fraction of natural cases, that's itself an important, honestly-reportable finding about how ambiguous real-world root-causing is, not a flaw in the protocol.

---

## 5. Step Four: Running the Benchmark

1. Feed each held-out test case's two reports (baseline, current) through SEG → CCR v0.1 exactly as a real user would — no manual intervention, no case-specific tuning.
2. Record CCR's full ranked output (all candidates, not just the top one) for every case.
3. Compare against the grader's independent ground-truth determination, using the match criterion frozen in the pre-registration document (Section 2, item 5).
4. Tabulate: for each case, did the top-1 candidate match? Did the true cause appear anywhere in the top 3?

### 5.1 What Counts as a Valid Run

The entire test set must be run in a single pass with one frozen version of CCR — not "run it, tweak the formula, run it again, keep the better number." If a bug is found mid-run, fix it, then **re-run the entire set from scratch**, not just the failing cases.

### 5.2 Recording Evidence

For every case, retain CCR's full evidence trail (Tech Spec Section 4, step 5) alongside the grader's verdict. This becomes the appendix of the results report (Section 8) and is what makes the eventual claim auditable rather than a bare percentage.

---

## 6. Statistical Honesty at Small Sample Sizes

With a test set of 30–50 cases, a raw accuracy percentage alone is misleading without a confidence interval. Report results as, for example, "34 of 40 cases correct (85%), 95% confidence interval approximately 70–94%" rather than just "85% accurate." At this sample size, the interval will be wide — that's a true fact about the evidence, not a weakness to hide. Anyone with real technical diligence experience will ask for this interval; providing it unprompted is a credibility signal, not a liability.

---

## 7. What Happens Based on the Result (Decided Now, Per the Pre-Registration Document)

- **If the primary metric is met:** this is the number referenced everywhere — the pitch deck, the design-partner conversations, the incubation application. Report it with the confidence interval, the exact match criterion used, and the full case-category breakdown (synthetic vs. natural), not just the headline percentage.
- **If the primary metric is not met:** do not quietly redefine the match criterion or shrink the test set after the fact — that defeats the entire purpose of this protocol. Instead, use the per-case evidence trails to diagnose *why* (Are failures concentrated in one change category? Is the scoring formula underweighting local impact magnitude relative to topological proximity?), revise the CCR v0.1 scoring formula with a stated reason, and **re-run the full protocol from a freshly frozen pre-registration**, treating it as a new benchmark, not a patch to the old one.
- **Either way, report the true result first**, in whatever internal or external document references it, before deciding what to build next.

---

## 8. Results Report Template (Fill In After Running)

```
GLI-FLOW CCR v0.1 BENCHMARK RESULTS
Date run: ______________
Pre-registration reference: [link/filename to the frozen document from Section 2]

Test set: _____ total cases (_____ synthetic, _____ natural), _____ held out and scored
Grader: ______________
Match criterion used: ______________

Primary metric (top-1 accuracy): _____ / _____ correct = _____ %
  95% confidence interval: _____ % – _____ %
Secondary metric (top-3 accuracy): _____ / _____ correct = _____ %
  95% confidence interval: _____ % – _____ %

Breakdown by category:
  Clock uncertainty changes: _____ / _____
  False/multicycle path changes: _____ / _____
  CTS-driven (cell resize/removal): _____ / _____
  Floorplan/placement-driven: _____ / _____
  I/O delay constraint changes: _____ / _____
  Natural historical cases: _____ / _____

Pre-registered bar met? [ ] Yes [ ] No
If no, diagnosis and next step: ______________
```

This is the exact document that produces the number the one-pager states doesn't exist yet — and it's the one artifact every other document built so far (pitch deck, design-partner conversations, the incubation ask) is waiting on.
