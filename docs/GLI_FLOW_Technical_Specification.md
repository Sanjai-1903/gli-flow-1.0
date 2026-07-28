# GLI-FLOW Technical Specification
### Product 1 — Deterministic Timing-Closure Root-Cause Attribution
### Including SEG and CCR Component Roadmaps

*This spec builds on the frozen decisions in the Consolidated Company State document (Product 1 definition, node roadmap, pricing) and the Validation Playbook (benchmark discipline). Where this document makes a new engineering choice not previously decided (tech stack, exact scoring formula, storage technology), it is explicitly marked as a **recommendation**, not a frozen fact — consistent with how prior documents distinguished "decided" from "proposed."*

---

## 0. One Clarification This Spec Resolves

The original five founding documents actually define SEG **three different ways**, not two — a more significant ambiguity than initially described:

1. **The Technology document** defines SEG as "the execution-planning capability... transforms engineering understanding into structured engineering action" — this is the Plan primitive.
2. **The Vision Document's Layer 3 (Decision Intelligence) section** defines SEG as "constructs engineering semantics, represents engineering meaning rather than syntax" — closer to a Represent primitive.
3. **The Vision Document's "Placement of Existing GLI Technologies" section** states "SEG → Representation + Reasoning" — combining both, and adding Reasoning on top.

None of these three agree with each other, and this was flagged as a real inconsistency back in the first strategic review. **For GLI-FLOW's actual build, this spec picks one of the three and states that choice plainly, rather than inheriting the ambiguity:**

- **SEG = Representation.** Turns raw signoff report syntax into a structured, semantic graph. Does not reason about causes.
- **CCR = Reasoning.** Operates entirely on SEG's output graph to determine causal ranking. Never touches raw report text directly.

This is a clean separation of concerns, is fully deterministic end-to-end, and matches the "no layer duplicates another's responsibility" principle already in the original Technology document. **Note honestly:** this choice follows the Vision Document's Layer 3 framing (definition 2 above) and explicitly diverges from the Technology document's "execution-planning" framing (definition 1) — the Consolidated Company State document's Section 1 summary still accurately reflects the Technology document's original wording (SEG as a planning engine) as a description of the *original vision text*; this spec is a deliberate, stated departure from that specific wording for GLI-FLOW's build, not a claim that the original wording was wrong.

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ Engineering Experience                                    │
│ CLI (v0) → API (v1) → Dashboard (v1+)                     │
└─────────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────────┐
│ LLM Interface (grounded, citation-constrained)             │
│ Translates CCR's structured output into explanation and Q&A│
│ NEVER alters or generates the causal ranking itself         │
└─────────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────────┐
│ Failure Atlas (persistent memory)                          │
│ Pattern fingerprint → confirmed cause → resolution history │
└─────────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────────┐
│ CCR — Constraint Causality Resolver (Reasoning)             │
│ Deterministic graph-diff + ranking algorithm                │
└─────────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────────┐
│ SEG — Semantic Execution Graph builder (Representation)     │
│ Parses raw reports into a versioned, canonical graph         │
└─────────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────────┐
│ Execution Runtime (read-only adapters)                     │
│ OpenSTA (Sky130/OpenROAD) → PrimeTime/Tempus (commercial)   │
└─────────────────────────────────────────────────────────┘
```

**Design principle carried from the original architecture doc:** every layer is replaceable and exposes a stable interface to the layer above it. In practice, this means the Execution Runtime adapter is the *only* layer that needs to change when GLI-FLOW moves from the Sky130/OpenROAD proof-of-concept to commercial PrimeTime/Tempus signoff — SEG, CCR, Failure Atlas, and the LLM interface should not need to be rebuilt for that transition, only fed a new adapter's output. Getting this boundary right is itself the first real architectural test of the whole platform thesis.

---

## 2. Data Model & Schema

**Core entities, common to every tool adapter:**

- **Run** — a single signoff execution: timestamp, tool + version, design/block identifier, reference to the prior run it's being compared against (or none, if it's a baseline).
- **Constraint** — an SDC-derived entity: clock definition, clock uncertainty, false path, multicycle path, input/output delay, exception. Each constraint is versioned per run.
- **Design Object** — net, cell, pin, macro instance, clock tree node — canonicalized to a stable hierarchy identifier so the same physical object can be matched across runs even if report formatting differs slightly between tool versions.
- **Timing Path** — startpoint, endpoint, arrival time, required time, slack, and the ordered sequence of design objects the path traverses.
- **Diff Event** — a detected change between two runs: constraint added/removed/modified, or a design-object-level change (placement, routing, CTS-derived delay change) inferred from report deltas.
- **Causal Edge** — CCR's output: a link from a Diff Event to a specific timing degradation, carrying a rank, a deterministic confidence score, and the evidence trail (which graph nodes/edges support the link).

**Determinism requirement, non-negotiable:** identical input reports must always produce a byte-identical graph. No entity in this schema is populated by an LLM or a trained model — every field is extracted by deterministic parsing rules. This is what makes the Stage 0 benchmark (Validation Playbook Section 3.1) actually testable and reproducible.

---

## 3. SEG — Technical Spec and Roadmap

**Responsibility:** parse raw, tool-specific report text into the canonical schema above. Nothing more. SEG never infers a cause — it only represents what the report actually says, faithfully and completely, matching the original architecture's "Observation is passive... nothing is inferred" principle, extended here to representation as well.

**Pipeline:**
1. **Format-specific parser (per adapter).** A grammar/regex-based extractor for each tool's report format — not a general-purpose LLM-based parser, because signoff report formats are fixed and fully specifiable, and determinism is non-negotiable here.
2. **Canonical ID resolution.** Map every design-object reference in the raw report to a stable hierarchy identifier, so cross-run diffing is reliable even across minor formatting or naming differences between tool versions.
3. **Graph construction.** Emit a versioned, append-only graph for the run — never mutate a prior run's graph, since historical accuracy of past runs is part of what the Failure Atlas depends on.
4. **Validation gate.** Every SEG output must pass a self-consistency check (e.g., every path's arrival/required/slack values are internally consistent) before being handed to CCR — malformed input should fail loudly, not silently produce a partial graph.

**SEG Roadmap:**

| Version | Scope | Gate to ship |
|---|---|---|
| **v0.1** | OpenSTA report parser (Sky130/OpenROAD flow) — the tool the existing PoC actually uses. **Important build note:** the current Sky130 PoC runs on OpenROAD, whose default timing engine is OpenSTA, not PrimeTime/Tempus — the one-pager's "instruments PrimeTime/Tempus" description applies to the Stage 1 commercial-node adapter, not the Stage 0 proof-of-concept. Two separate parser adapters are needed from day one, unified into the same canonical schema — this is a Day 1 architecture requirement, not a later nice-to-have. | Parses a real Sky130/GF180 regression's OpenSTA output into a valid, self-consistent graph |
| **v0.2** | Constraint (SDC) diff support — added/removed/modified constraints correctly detected across two runs | Diff output matches a manually-verified ground truth on the same held-out test set used for the Stage 0 benchmark |
| **v0.3** | PrimeTime/Tempus report parser adapter (commercial nodes, Stage 1) | Parses a real 28–90nm commercial signoff report set without requiring changes to CCR, Failure Atlas, or the LLM interface — this is the direct test of the layer-boundary principle above |
| **v1.0** | Calibre (DRC/LVS) and additional commercial adapters, feeding the same canonical schema — this is the technical foundation for products beyond Product 1, including **Product 2 (Regression & Failure Intelligence, once its gate opens)**, and eventually TAPEOUT OS's cross-vendor ambition. (Not the node roadmap's Stage 2 — that refers to 7–16nm node expansion of GLI-FLOW itself, a separate axis from the product build sequence.) | Cross-vendor graph construction demonstrated on ≥2 distinct toolchains without rebuilding CCR (this is also the company-level "moat" validation milestone from the Validation Playbook, Section 5) |

---

## 4. CCR — Technical Spec and Roadmap

**Responsibility:** given two (or more) SEG-produced graphs, determine which upstream diff events most likely caused a given timing degradation, and rank them — deterministically, auditable, reproducibly.

**Algorithm, step by step:**

1. **Graph diff.** Compute the structural delta between the baseline and current graph: every Diff Event, typed and localized to specific design objects and constraints.
2. **Violation identification.** Identify every timing path with negative or worsened slack in the current run relative to baseline.
3. **Candidate generation.** For each violation, walk the timing path backward through the graph and collect every Diff Event that touches a design object or constraint on that path — this is the candidate cause set.
4. **Deterministic scoring, per candidate.** A fixed, published formula — not a learned weighting — combining:
   - **Topological proximity:** does the diff event sit directly on the failing path, or several hops upstream? Direct presence scores highest.
   - **Local timing impact magnitude:** the measurable delta the diff event introduces at its own location (e.g., a clock uncertainty change's direct contribution to arrival/required time), computed from the graph's own timing values — not estimated.
   - **Explanatory breadth:** how many independently failing paths does this single candidate explain? A change that accounts for many failures ranks above one that only explains one, on a minimum-description-length logic — the simplest sufficient explanation is preferred.
   - **Historical precedent (from the Failure Atlas):** if this diff-event pattern has been previously confirmed as a root cause by a human engineer, its score is adjusted according to a fixed, published boost rule — this is a deterministic lookup against stored history, not a trained model's prediction.
5. **Ranked output with full evidence trail.** Every candidate's score is broken down into its four components above, and every component cites the specific graph nodes/edges that produced it — this is what makes the output auditable rather than a black-box ranking, directly satisfying the "every decision explainable" governing principle.

**What CCR explicitly does not do in v1:** propose a fix, apply a change, or use any statistical/learned model anywhere in the scoring path. That capability boundary is deliberate and matches the current frozen scope (Stage 0–1 is diagnostic, not corrective).

**CCR Roadmap:**

| Version | Scope | Gate to ship |
|---|---|---|
| **v0.1** | Single-cause ranking on Sky130/GF180 graphs — topological proximity + local impact magnitude only (components 1–2) | Passes the pre-registered, blind, held-out benchmark defined in the Validation Playbook Section 3.1 |
| **v0.2** | Add explanatory-breadth scoring (component 3) — multi-failure clustering to a shared root cause | Demonstrated reduction in "distinct causes reported" vs. "distinct failures reported" on the same benchmark set, verified by the same blind grader |
| **v0.3** | Failure Atlas integration — historical precedent scoring (component 4) enabled, single-project scope only | Confirmed improvement in top-1 accuracy on a benchmark set that includes repeat-pattern failures, versus v0.2 without Atlas lookup |
| **v1.0** | Commercial-node validated — re-run the full benchmark discipline (blind, held-out, pre-registered bar) on real 28–90nm PrimeTime/Tempus data at a design partner, per Stage 1 of the node roadmap | 3–5 design partners confirm CCR's top-ranked hypothesis meets or exceeds the pre-agreed pilot performance bar (Validation Playbook Section 3.2) |
| **v2.0 (deferred)** | Cross-vendor causal reasoning spanning Synopsys/Cadence/Siemens report boundaries — the technical core of TAPEOUT OS itself | Not gated yet; explicitly Stage 5, out of scope until v1.0 is proven |

---

## 5. Failure Atlas — Technical Spec

**Responsibility:** persistent, append-only memory of confirmed cause-and-resolution history, scoped per project/customer by default (cross-customer corpus is the explicit, separately priced, opt-in Enterprise add-on — never silently pooled).

**Schema:**
- **Pattern fingerprint:** a normalized signature of a Diff Event type + its structural context (strips run-specific noise like timestamps, keeps the structural shape of the change).
- **Occurrence count:** how many times this fingerprint has appeared.
- **Confirmation status:** set only when a human engineer explicitly confirms or rejects CCR's proposed cause for an instance of this pattern — this human-confirmation loop is the actual learning mechanism in this system, not model retraining, and it directly satisfies the "humans remain accountable" governing principle.
- **Resolution notes:** what fix, if any, was applied and whether it worked — free text plus a structured outcome flag, feeding directly into Product 2's design (regression/failure clustering) when that gate opens.

**Critical constraint:** the Atlas only ever *adjusts a score* within CCR's fixed formula (component 4 above) — it never becomes a second, separate model making its own prediction. This keeps the entire causal reasoning path deterministic and auditable end-to-end, which is the whole point of the determinism bet.

---

## 6. LLM Interface — Technical Spec

**Responsibility:** translate CCR's structured, already-final output into natural-language explanation and support conversational Q&A — strictly downstream, strictly grounded.

**Hard constraints:**
- The LLM receives CCR's structured JSON output (ranked causes, scores, evidence trail) as its only source of truth for a given query — it does not re-derive or reweight the ranking.
- Every generated sentence that makes a factual claim about the design must cite a specific graph node/edge ID from the input; claims without a citable source are rejected by a post-generation validation check before being shown to the user.
- **Consistency guardrail:** if the LLM's prose output would ever contradict CCR's structured ranking (e.g., mischaracterizing which candidate ranked first), the structured ranking is authoritative, and the interface must surface that discrepancy rather than silently trusting the generated text. This is a testable requirement, not a hope — it should have its own regression test suite separate from CCR's own benchmark.
- The LLM interface is the *only* place in the entire GLI-FLOW pipeline where a language model is used — it must not be reachable from SEG or CCR's internal computation path, so the "zero ML in the core" claim remains literally true and auditable, not just a marketing description.

---

## 7. Non-Functional Requirements

- **Determinism & reproducibility:** identical inputs must always produce identical outputs across SEG and CCR; every graph and every CCR output should be checksummed so a customer or auditor can independently verify reproducibility — this is the concrete engineering implementation of "every action is reversible... every decision explainable."
- **Security & deployment:** read-only by design — no write access to any design, tool configuration, or file outside GLI-FLOW's own storage. Must support fully on-prem or customer-VPC deployment with no outbound telemetry for the open-source Layer 1, consistent with the stated pricing/trust model ("no telemetry, no procurement, fully auditable").
- **Performance & scale:** commercial-node designs can have tens to hundreds of thousands of timing paths per run; SEG's parsing and graph construction must handle this within a practical turnaround (recommend targeting completion within the same operational window as the signoff run itself, so triage is available same-day, not next-day).
- **Extensibility:** new tool adapters must plug into SEG without requiring changes to CCR, Failure Atlas, or the LLM interface — this boundary is the single most important thing to get right early, since it's both a technical requirement and the direct test of whether the "modular, vendor-replaceable" architectural claim actually holds.
- **Auditability:** every CCR output must be exportable as a self-contained evidence report (which graph nodes, which scoring components, which historical precedent) suitable for an engineer or auditor to review independently of the tool itself.

---

## 8. Recommended Tech Stack (Recommendation, Not a Frozen Decision)

Stated explicitly as engineering judgment, open to revision — nothing here has been decided the way the product scope and node roadmap have been:

- **Parsing layer (SEG adapters):** a systems language with strong text-processing performance (Rust or Go) for the report parsers, given large report file sizes and the need for fast, memory-efficient deterministic parsing; Python is a reasonable alternative for v0.1 speed-of-development if performance isn't yet a bottleneck at Sky130/GF180 scale.
- **Graph storage:** start with an in-process graph representation for Stage 0 (simplicity, no infrastructure dependency, easy to reason about for a solo founder); move to an embedded or lightweight graph database once commercial-node scale (Stage 1) requires indexed traversal performance beyond what fits comfortably in memory.
- **CCR scoring engine:** implement the scoring formula as a pure, stateless function over the graph — this makes it trivially unit-testable and keeps the determinism guarantee easy to verify in CI.
- **Failure Atlas storage:** a simple structured store (even a well-indexed local database is sufficient at Stage 0–1 scale) — no need for anything more sophisticated until the cross-customer Enterprise tier is actually being built.
- **LLM interface:** any capable LLM API, used strictly as described in Section 6 — the choice of model matters far less here than the citation/grounding constraint architecture around it.

---

## 9. Build Milestones (Tied to the Frozen Node Roadmap)

| Milestone | Corresponds to | Deliverable |
|---|---|---|
| M0 | Stage 0 | SEG v0.1 (OpenSTA parser) + basic graph schema + graph diff engine |
| M1 | Stage 0 | CCR v0.1 (topological + local-impact scoring) with full evidence trail output |
| M2 | Stage 0 | Pre-registered, blind, held-out benchmark harness built and run (Validation Playbook 3.1) — **this produces the accuracy number that does not exist yet** |
| M3 | Stage 0 → 1 transition | CCR v0.2–v0.3 (explanatory breadth + Failure Atlas integration), single-project scope |
| M4 | Stage 0 → 1 transition | LLM interface v1, with citation-constraint validation tests passing |
| M5 | Stage 1 | SEG v0.3 (PrimeTime/Tempus adapter) — built without modifying CCR/Atlas/LLM layers, testing the architecture's own core claim |
| M6 | Stage 1 | CCR v1.0 — re-validated on real commercial signoff data at 3–5 design partners, per the pilot performance bar in the Validation Playbook |
| M7 | Stage 1 → 2 gate | Packaging for pilot deployment: on-prem/VPC install, audit-log export, policy-engine stub reserved for Product 2's eventual guardrails |

---

## 10. Open Engineering Decisions (Not Yet Made — Flagged Honestly)

- Exact numeric weights in CCR's scoring formula (Section 4, step 4) — these need to be set and then tested against the benchmark, not designed in the abstract; expect at least one revision cycle after M2's first real benchmark run.
- Graph storage technology choice for Stage 1 scale (Section 8) — a real engineering decision that should be made based on actual Sky130/GF180 profiling data from M0–M1, not guessed in advance.
- Whether SEG's canonical ID resolution (Section 3) needs fuzzy matching for commercial-node naming conventions, which may differ more than expected from the open-source Sky130 flow's naming — this is the concrete technical form of the already-flagged "Sky130→commercial-node transfer risk."
- LLM provider/model selection for Section 6 — deliberately deferred, since the grounding architecture matters more than the specific model choice.
