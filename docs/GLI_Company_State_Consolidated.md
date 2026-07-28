# Green Lantern Industries (GLI) — Consolidated Company State

*This document compiles everything decided across the strategy review, the beachhead exercise, and the node-roadmap discussion. It does not add new ideas. Where something was proposed and later superseded, that is marked explicitly rather than silently dropped.*

---

## 1. Company Vision & Thesis — The Original Five Documents (Unchanged — Not Rewritten)

Per the instruction that vision/philosophy should not be rewritten, only product/business/GTM strategy. This is the fuller vision as it was actually written across the five founding documents (Vision, Thesis, Problem, Product Strategy, Technology), kept intact.

**Why GLI exists (Thesis).** Engineering is shifting from tools that execute to systems that understand. The limitation on engineering progress is no longer computational capability — it is engineering intelligence. Knowledge remains fragmented across execution logs, reports, metrics, artifacts, constraints, design history, tool outputs, and individual human expertise, so organizations repeatedly re-solve the same problems and lose knowledge as people and projects turn over. GLI's fundamental belief: engineering intelligence will become foundational infrastructure for engineering organizations, the way operating systems coordinated hardware and cloud platforms coordinated computational resources. The long-term opportunity is not better engineering tools — it is the intelligence layer that lets every tool, workflow, and engineer operate with greater understanding. Success condition: engineering organizations transition from software that merely performs tasks to systems that continuously understand, improve, and amplify engineering work.

**The problem GLI addresses (Problem).** Engineering complexity is growing faster than human capacity to manage it. Computation is not the bottleneck — organizations already simulate, synthesize, optimize, and verify at scale. The real bottleneck is that engineering data accumulates faster than engineering *knowledge*: information exists, understanding does not. AI increases the importance of engineering intelligence rather than reducing it, because autonomous systems must first reliably understand the environments they act in. Success condition: engineering organizations no longer rely primarily on fragmented information and individual memory to make critical decisions — knowledge becomes continuously observable, understandable, reusable, and capable of improving future work.

**What GLI sells (Product Strategy).** GLI sells engineering intelligence delivered through software, not execution for its own sake. Products are not the company — products are temporary expressions of the thesis, evaluated by their impact on engineering velocity, quality, confidence, consistency, and organizational learning. Every product should be outcome-oriented, workflow-native, platform-connected, trustworthy, scalable, and extensible. Expansion follows a fixed progression: solve one problem exceptionally well → extend to adjacent problems in the same workflow → connect related workflows → enable organization-wide engineering intelligence → support broader engineering disciplines. Success condition: customers stop evaluating GLI as individual software products and start recognizing it as the engineering intelligence layer running underneath their organization.

**How technology serves the thesis (Technology).** GLI is not defined by AI, EDA, or automation as technologies — those are implementation choices. Engineering intelligence is the core primitive, not execution. The stack is layered: Execution Runtime (interfaces with tools, performs no reasoning) → Execution Intelligence (turns activity into structured knowledge — execution history, telemetry, provenance) → Decision Intelligence (turns knowledge into understanding — causal reasoning, confidence, alternatives, planning) → Autonomous Engineering (turns understanding into safe, policy-governed action) → Engineering Experience (the human-facing layer). Core reusable capabilities: Observe, Understand, Reason, Plan, Execute, Verify, Learn. CCR and SEG are named as specialized *engines* within Decision Intelligence — reasoning and planning respectively — explicitly not the architecture or the platform itself, so future reasoning/execution engines can be added without redesign. Enduring principle: technology should continuously transform engineering activity into understanding, understanding into better decisions, and better decisions into continuously improving outcomes. Explicit competitive stance: GLI should not compete to build the smartest semiconductor AI agent — it should compete to build the most trustworthy autonomous engineering platform, with differentiation coming from a decision-intelligence layer (SEG, CCR, provenance, telemetry, governance) that lets agents make explainable, auditable, policy-aware decisions.

**The end state (Vision Document).** The semiconductor industry doesn't primarily lack tools — it lacks engineering understanding. No system today continuously understands what happened, why, what changed, what should happen next, whether an action succeeded, and how that should improve future decisions. GLI does not aspire to build a better timing tool, router, EDA application, AI chatbot, or workflow wrapper — it aspires to build the trusted operating layer that enables autonomous semiconductor engineering. Fundamental philosophy: automation without understanding creates unreliable systems; understanding without execution creates passive systems; execution without verification creates dangerous systems; learning without evidence creates hallucination — the future requires understanding, reasoning, execution, and verification together, with continuous learning emerging from all four. The company models engineering as an evolving system of *decisions*, not a sequence of tool invocations. The nine irreducible capabilities of any true autonomous engineering system: **Observe → Understand → Represent → Reason → Plan → Execute → Verify → Learn → Govern** — every future architecture or product decision should derive from these. Governing principles: trust before autonomy, evidence before recommendation, deterministic reasoning where possible and AI only where uncertainty genuinely exists, humans remain accountable, every decision explainable, every action reversible, every execution produces knowledge, every workflow improves the platform. Ultimate destination: GLI does not aspire to become another EDA vendor or another AI startup — it aspires to be the system through which engineering work is understood, coordinated, automated, verified, and continuously improved, with semiconductor engineering as the first realization of that vision, not the limit of it.

**Long-term vision beyond semiconductor.** The architecture is described as fundamentally an *engineering* architecture, not an EDA architecture — the only domain-specific portion is the execution runtime that interfaces with tools; everything above operates on universal engineering concepts (observations, knowledge, relationships, decisions, plans, execution, verification, learning, governance). Semiconductor engineering is the proving ground precisely because of its extreme technical complexity, heterogeneous toolchains, long execution cycles, and high-value decisions — if the architecture succeeds there, it becomes credible for FPGA development, PCB design, embedded software/firmware, hardware/software co-design, mechanical CAD, robotics engineering, manufacturing engineering, and systems engineering. This expansion is explicitly stated as long-term and aspirational, not a near-term roadmap item.

### Relationship Between This Vision and TAPEOUT OS

TAPEOUT OS is the concrete, physical-design-first realization of this thesis — not a separate or competing vision. It inherits the same philosophy directly (trust before autonomy, deterministic reasoning where possible, explainability, human accountability) and the same "operating layer beneath fragmented tools" framing. It diverges from the original five documents in three specific ways, all deliberate narrowings rather than departures: (1) scope — physical design and signoff only, not the full RTL-to-signoff lifecycle described above; (2) posture — positioned as a neutral audit/trust layer *underneath* autonomous agents (including possibly incumbents' own agents), rather than GLI building the full agent stack itself as the original six-product portfolio implied; (3) concreteness — a real named product (GLI-FLOW), a real PoC, and a real build sequence exist, where the original five documents had none. The cross-domain (FPGA/PCB/robotics/manufacturing) ambition from the original vision is preserved only as long-term aspiration and is not part of TAPEOUT OS's near-term scope.

---

## 2. Current Company Reality (As of the GLI One-Pager)

Stated plainly, as the founding document itself states it:

- **Company:** Green Lantern Industries — positioned publicly as "TAPEOUT OS."
- **Stage:** Pre-revenue. Pre-incorporation. Solo founder. This is the single largest execution risk identified across every stage of this analysis and remains unresolved.
- **Current proof of concept:** An open-source Sky130 RTL-to-GDSII flow (Yosys/OpenROAD/Magic/Netgen/KLayout), shipping publicly. GitHub traction currently minimal (single-digit stars, pre-launch).
- **No accuracy claims published yet.** No CCR accuracy — deterministic or otherwise — has been benchmarked yet.
- **Incubation context:** IITM Research Park incubation application in progress via existing referral; formal faculty mentorship not yet finalized. This anchors the company in the Indian semiconductor design ecosystem, which materially informed the node/customer decision below.
- **The ask (as stated):** Incubation support (lab space, continued academic Synopsys/Cadence EDA license access), introductions toward a technical or business co-founder, and a pre-seed check if available — specifically to compress the 60–90 day window to a published, benchmarked CCR accuracy result.

---

## 3. Product 1 — GLI-FLOW (Frozen)

**Definition:** A deterministic, graph-based Constraint Causality Resolver (CCR) for timing-closure root-cause attribution. Instruments PrimeTime/Tempus signoff via report parsing. Zero ML in the core — reproducible, auditable. Read-only; no write access to any design.

**Why timing-closure attribution was chosen over the earlier regression/failure-intelligence idea (superseded — see Section 7):** it is buildable by a solo founder now (report parsing over a structured causal space — constraints, floorplan, CTS, routing deltas), it is independently validated by Siemens EDA's own May 2026 public position that Calibre deliberately keeps deterministic algorithms for signoff-critical calculations, and it is more clearly differentiated from ChipAgents (whose edge is probabilistic, exploratory search over RTL code/waveforms for functional bugs — a different, less structured problem space).

### Frozen Node Roadmap (v2)

| Stage | Nodes | Target customer | Gate to proceed |
|---|---|---|---|
| **0 — Proof** | Sky130 (130nm), GF180 (180nm), open-source PDKs | None — public benchmark | A real, **published, benchmarked** CCR accuracy result (not a demo) |
| **1 — Paid beachhead** | Commercial mature nodes, 28–90nm | Non-automotive mature-node design houses (power management, display drivers, RF/analog-mixed-signal, general IoT) **plus** India DLI-funded chip design startups. **Automotive is explicitly not the lead wedge** — automotive requires AEC-Q100/ISO 26262 qualification and is a slower, more conservative adopter than the "fast-moving, budget-flexible" profile this beachhead needs. | 3–5 paying pilots; CCR accuracy **re-validated on real commercial signoff reports**, not assumed to transfer from Sky130 |
| **2 — Expansion** | Mid-range, 7–16nm | Fast-moving fabless AI-chip / networking-chip startups (the original ideal customer profile from the beachhead exercise) | Stage 1 revenue + sufficient corpus depth |
| **3+ — Deferred** | Sub-7nm / sub-3nm | Out of scope for now — Apple/Nvidia/Qualcomm/hyperscaler-tier customers | Not gated yet; revisit only once team, capital, and corpus exist |

**Open, explicitly unresolved items (not glossed over):**
- Whether the Sky130/GF180 benchmark accuracy actually transfers to real 28–90nm commercial signoff complexity (larger designs, multi-corner/multi-mode analysis) is unverified. This is the specific risk the Stage 0→1 transition is designed to test, not assume.
- **Last open question, not yet answered:** whether to skip Sky130 and go straight to a 28–90nm pilot. Recommendation stands as **do not skip Sky130** — it is the only fast, controllable path to evidence before asking a customer to trust an unproven tool with real data — *unless* a warm relationship with a specific 28–90nm design house willing to share real signoff data pre-benchmark already exists. That fact was requested from the user and has not yet been confirmed either way. **This is not frozen — it is pending that answer.**
- Pricing realism: likely lower end of the $35K–$300K/yr band at Stage 1 (mature-node customers have smaller respin costs and smaller CAD budgets than the sub-3nm figures cited in the problem framing), which stretches the original $1M ARR / 12–18-month estimate — more logos needed, or Stage 2 needs to arrive sooner than planned.
- Solo-founder / co-founder gap remains completely unresolved by any product or node decision made so far.

---

## 4. Product 2 and the Expansion Ladder (As Stated in the One-Pager's Build Sequence)

The frozen build sequence, each stage independently revenue-generating, none skippable, corpus depth from Stage 1 being the critical path to Stages 3+:

1. **Timing Closure Intelligence** — GLI-FLOW itself (Product 1, above).
2. **Regression & Failure Intelligence, with an optional self-correcting agent (Product 2)** — **redefined by explicit decision, replacing the original one-pager's placeholder name "PD Intelligence" at this position in the sequence.** Extends GLI-FLOW's data discipline (dedup, cluster, classify) across the broader regression farm — simulation, formal, emulation — building on the same Failure Atlas concept already named in the original Technology document. Adds an opt-in, user-triggered agent that can act on a diagnosed failure (e.g., re-run, apply a known fix) only when the user asks it to.
   **Two explicit guardrails, stated as conditions, not yet met:**
   - **Sequencing gate:** this should not be built while GLI-FLOW is still solo-founder and pre-revenue. The gate is Product 1 having real paying pilots *and* a team (co-founder or hires) in place — starting Product 2 before that repeats the exact integration-sprawl and buildability risk that ruled out regression intelligence as *Product 1* in the first place, one stage later.
   - **Determinism guardrail:** the self-correcting agent should be rule-based and policy-bound, triggered by explicit user confirmation of a diagnosis — not an ML model deciding and acting autonomously. GLI-FLOW's differentiation and its Siemens EDA validation rest on "zero ML in the core, deterministic, auditable." An autonomous ML-driven agent at Product 2 would partially undercut that story; a user-confirmed, deterministic trigger extends it instead.
3. **Predictive Engine (Product 3)** — named in the build sequence; no further detail exists in any source document.
4. **Autonomous Agent (Product 4)** — named in the build sequence; no further detail exists in any source document. Note: this is distinct from the *opt-in* self-correcting agent now attached to Product 2 — Product 4's autonomous agent remains undefined and should not be assumed to inherit Product 2's guardrails automatically; that needs its own decision when reached.
5. **TAPEOUT OS (terminal product)** — the one stage with real technical specificity in the source. See Section 5 for its actual described mechanism (Tcl proc override, filesystem interception, report parsing, surgical rollback directives, cross-vendor boundaries) — these details belong to TAPEOUT OS specifically, not to Stages 2–4.

**Note on accuracy:** the one-pager states each stage is independently revenue-generating and that none is skippable, with corpus depth from Stage 1 being the critical path to Stages 3+. That structural claim is decided. Product 2 now has a real, decided definition (above); Stages 3–4's internal mechanics remain undecided and should not be pitched or built against invented specifics.

---

## 5. Final Platform Vision — TAPEOUT OS

The terminal product, as stated in the one-pager: **a neutral, cross-vendor causal execution layer for chip physical design**, extending the causal graph built by GLI-FLOW across the full flow via Tcl proc override, filesystem interception, and report parsing — issuing surgical rollback directives instead of full re-runs, across Synopsys/Cadence/Siemens boundaries — and becoming **"the audit and trust layer underneath autonomous EDA agents."** Not a replacement for Synopsys's, Cadence's, or Siemens's own agentic tools, but the neutral causal record and governance layer sitting beneath and across them. These are the only technical specifics the source document gives for the terminal product — everything else about *how* it works beyond this is undecided.

This is consistent with, and a specific narrowing of, the broader company vision in Section 1 (Decision Intelligence + Autonomous Engineering layers, governance, cross-vendor neutrality) — it is the concrete, physical-design-specific instantiation of that broader "trusted operating layer" thesis, not a departure from it.

---

## 6. Competitive Positioning (Frozen Understanding)

- **Synopsys** (AgentEngineer, Synopsys.ai Copilot — 40+ customers, 20,000+ active users, 50–70% reported time-to-solution gains) and **Cadence** (ChipStack acquisition, ViraStack/InnoStack, "Super Agent" direction) are both real, shipping, and moving into agentic/decision-intelligence territory — but native to their own single-vendor tool stacks, with a structural disincentive to be vendor-neutral or to reason well over a competitor's tool outputs.
- **Siemens EDA** publicly stated in May 2026 that Calibre deliberately keeps deterministic algorithms for signoff-critical calculations, layering AI only around that core — this directly and independently validates GLI-FLOW's founding principle (determinism before intelligence), arrived at separately by the industry's most conservative signoff vendor.
- **ChipAgents** — $74M total raised (including a $50M round, Feb 2026), backed by Matter Venture Partners, Bessemer, Micron, MediaTek, Ericsson; 80 semiconductor customers; 140x YoY ARR growth; publishes a benchmark of 3x+ higher accuracy than generic AI agents on commercial IP; running three sessions at DAC 2026. A serious, well-funded, real operator — not a distant player. Its edge is probabilistic, exploratory reasoning over RTL code and waveform data for functional/logic bugs — a different, less structured problem space than timing-closure causal attribution.
- **Silimate** — YC-backed, already in production with Fortune 500 companies and chip unicorns; wedge is an RTL-development-time copilot for functional/PPA bugs, not a standing causal-attribution or triage layer.
- **The actual unbuilt, contestable asset:** not "root-cause explanation" in the abstract (multiple players are pursuing versions of that) — it is **cross-vendor commercial-tool schema normalization**, i.e., the ability to reason causally across Synopsys/Cadence/Siemens tool boundaries at all, which the incumbents are structurally excluded from building by conflict of interest, and which ChipAgents has not built either.
- **ArchGen AI (Newton)** — the closest scope-overlap competitor found to date, closer than ChipAgents or Silimate because it targets the *exact same* backend PD niche: timing, congestion, DRC, root-cause diagnosis, iterative fix proposals, and persistent memory across runs. Founded by Hariharan Ayappane and Naveen Venkat (with Jishnu Madhav on their flagship technical result), backed by Entrepreneurs First — a 3-person team, not solo, which is already ahead of GLI on team risk. Positioned nearly identically to TAPEOUT OS: "an autonomous backend engineering layer around physical design and EDA flows, not a replacement for existing tools." Critically, ArchGen has already produced a real, verified, third-party-judged proof point — ranked first on the HRT (Hudson River Trading) and Partcl Macro Placement Challenge 2026 leaderboard on the IBM benchmark suite, with a detailed published technical write-up — exactly the kind of evidence the Validation Playbook says GLI-FLOW still needs to produce and currently lacks. They also ship a live open-source tool (RTLViz, on PyPI), ahead of GLI's pre-launch open-source traction.
  **Approach:** not a classic "mine historical data, train a model, deploy statically" pipeline — their demonstrated methodology (from the published macro-placement write-up) is a **search-and-verify optimization loop**: propose a candidate change, score it exactly against the real objective, accept only on measured improvement, repeat at scale with GPU-accelerated candidate generation (explicitly inspired by an "auto-research" experiment-loop framing). Their broader Newton product likely layers an LLM-agent with accumulated episodic memory on top of this (reasoning over structured run evidence, storing outcomes as precedent for future similar failures) — though this part is inferred from their public language, not confirmed by a published technical breakdown the way the placement benchmark was.
  **Strategic significance:** a genuine third architectural philosophy alongside GLI's determinism bet and the incumbents' native-agent approach — ArchGen is explicitly self-learning/ML-first where GLI-FLOW is explicitly zero-ML/deterministic-first. That contrast is GLI's real differentiation opportunity here, *if* it can be proven with evidence — right now ArchGen has the proof point and GLI does not.

---

## 7. Superseded Analysis (Kept for Completeness — Partially Superseded, Not Fully)

Before the one-pager was shared, an earlier first-principles beachhead exercise (scored across 25+ candidate problems) recommended **"Regression & Failure Intelligence"** as **Product 1** — a cross-tool triage/dedup layer over nightly regression farms, with a different expansion ladder (Regression Intelligence → Root-Cause Copilot → Fix Recommendation → Autopilot → Governance Platform).

That recommendation was superseded **in its Product 1 role** once the real founder/company facts (solo founder, existing Sky130 PoC, pre-incorporation stage, the specific determinism bet) were introduced — GLI-FLOW is more buildable by a solo founder immediately, and better differentiated from ChipAgents specifically.

**Update:** the underlying idea was not discarded — it has since been **redefined and adopted as Product 2** (see Section 4), extended with an opt-in, deterministic self-correcting agent, and gated behind Product 1 traction and team growth. The original scoring logic that made it the *strongest single idea* in the beachhead exercise (frequency=5, pain=5, buyer accessibility=4) is exactly why it was reasonable to bring back at Product 2 rather than discard entirely — it was deprioritized for Product 1 on buildability grounds specific to a solo founder, not because the underlying pain was weak.

---

## 8. Pricing & Business Model (As Stated)

| Layer | Model |
|---|---|
| Layer 1 — capture scripts + open-source Sky130 flow (GLI-FLOW-ASIC) | Free, Apache 2.0, forever — no telemetry, no procurement, fully auditable |
| SEG core, CCR attribution, Failure Atlas, LLM interface | Paid, per active tapeout project — $35K–$300K/yr (Stage 1 realistic pricing likely toward the lower end of this band — see Section 3 open items) |
| Cross-customer corpus benchmark | Paid add-on, +$40K/yr, Enterprise tier only |

**Logic (as stated):** the extraction layer stays open because it must be auditable to be trusted inside a tapeout-critical compute farm; monetization sits one layer up, at cross-iteration intelligence the open flow alone cannot produce.

---

## 9. Go-to-Market (As Stated)

Open-source Sky130 flow as the zero-friction wedge → free timing audits (10 targeted, no procurement) → forward-deployed engagements → 90-day non-refundable paid pilots → annual license ($35K–$300K/yr, priced per active tapeout project) → cross-vendor corpus add-on and platform/API tier.

Refined by the node-roadmap discussion: Stage 1 outreach should prioritize non-automotive mature-node design houses and India DLI-funded design startups over automotive suppliers, for adoption-speed reasons stated in Section 3.

---

## 10. What Remains Genuinely Open (Not Decided)

- Whether to skip Sky130 for a direct 28–90nm pilot — pending confirmation of a specific warm customer relationship.
- Product 2 (Regression & Failure Intelligence + optional self-correcting agent) has a real definition now, but its two guardrails are unmet as of this writing: no paying pilots or team exist yet for Product 1, so the sequencing gate is not satisfied — Product 2 should not start being built yet.
- Detailed specification of Products 3 and 4 (Predictive Engine, Autonomous Agent) — only their names and position in the sequence are decided.
- Whether Sky130-benchmarked accuracy will hold on real commercial signoff data.
- **ArchGen AI's published, verified benchmark result raises the urgency of GLI-FLOW's own Stage 0 benchmark** — the credibility gap between "a proof point exists" and "a proof point doesn't exist yet" is now measured against a direct, similarly-staged competitor, not just against well-funded incumbents.
- The co-founder/team gap — flagged repeatedly as the largest execution risk, not addressed by any decision above, and now also a hard prerequisite for starting Product 2.
- Realistic Stage 1 ARR timeline, given the likely-lower pricing at mature nodes.
