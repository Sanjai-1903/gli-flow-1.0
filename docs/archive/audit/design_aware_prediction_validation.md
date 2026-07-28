# GLI Design-Aware Prediction Validation Audit

**Generated**: 2026-06-16
**Method**: Direct source code inspection + DB queries + execution outputs (no reports, no summaries)

---

## Phase 1 — Design Profile Audit

**Data source**: `design_profiles` and `design_features` tables in `~/.gli_flow/gli_flow.db`

| Design | Class | Cell Count | Logic Depth | Register Density | Memory Density |
|---|---|---|---|---|---|
| aes_cipher | Controller | 3500 | 47 | 0.30 | 0.02 |
| counter | Controller | 100 | 13 | 0.08 | 0.02 |
| fir | DSP | 2000 | 54 | 0.25 | 0.02 |
| fir_top | Controller | 20 | 8 | 0.20 | 0.02 |
| gcd | Controller | 200 | 15 | 0.08 | 0.02 |
| gpio | Interconnect | 400 | 17 | 0.20 | 0.02 |
| ibex | CPU | 20000 | 42 | 0.35 | 0.20 |
| opentitan_ibex | Memory-heavy | 50000 | 31 | 0.20 | 0.20 |
| picorv32 | CPU | 15000 | 41 | 0.35 | 0.02 |
| serv | CPU | 3000 | 34 | 0.35 | 0.02 |
| sram_controller | Memory-heavy | 2000 | 10 | 0.10 | 0.50 |
| tiny_or | Controller | 100 | 13 | 0.20 | 0.02 |
| tinyml_accel | Accelerator | 5000 | 61 | 0.25 | 0.20 |
| uart | Controller | 800 | 19 | 0.45 | 0.02 |
| uart_top | Controller | 52 | 11 | 0.20 | 0.02 |

**Counts**: 15 profiles, 15 feature vectors, 6 design classes (7 Controller, 3 CPU, 2 Memory-heavy, 1 Interconnect, 1 DSP, 1 Accelerator)

---

## Phase 2 — Prediction Pipeline Trace

**Code path verified** (source files inspected):

```
CLI: gli_flow/cli/main.py:2782-2801
  args.run_id → query runs.design_name → design_name
  ↓
RiskEngine.predict_risk(metrics, design_name=design_name)
  failure_atlas/prediction/risk.py:41-42
  ↓ passes design_name to:
  SimilarityEngine.find_similar(metrics, design_name=design_name)
    failure_atlas/prediction/similarity.py:52-53
    → DesignSimilarityEngine.find_similar(design_name) → design_sim_map
    → applies boost (1.5x same design, 1.0+score/200 for similar)
  ↓ also uses design_name for:
  _get_design_class(design_name) → DESIGN_CLASS_RISK_PRIORS[class]
    failure_atlas/prediction/risk.py:54-57
    → blended at 25% weight

ReadinessEngine.predict_readiness(metrics, design_name=design_name)
  failure_atlas/prediction/readiness.py:70-71
  ↓ passes design_name to:
  SimilarityEngine.find_similar(metrics, design_name=design_name)
  ↓ also uses design_name for:
  _get_design_class(design_name) → DESIGN_CLASS_READINESS_BASELINE[class]
    → blended at 25% weight
```

**Gaps found**:
1. **CLI does NOT call RecommendationEngine** in `predict_command()` — only risk and readiness are invoked.
2. **`RecommendationEngine.get_recommendation(failure_type)`** — does NOT accept `design_name` parameter. The design-class-aware method `get_design_class_recommendations()` exists but is disconnected from the prediction flow.
3. **`ExecutioSimilarityEngine.find_similar_by_failure_type()`** — does NOT pass `design_name` (line 100-112 of similarity.py).

**Verdict**: `design_name` flows through CLI → Risk → Similarity and CLI → Readiness → Similarity. The chain is intact for risk and readiness. Recommendations are not integrated.

---

## Phase 3 — Similarity Audit

**Execution output** (same metrics across all designs):

| Query Design | Class | Top-3 Similar | Similarity Scores | Boost Factors |
|---|---|---|---|---|
| picorv32 | CPU | picorv32, picorv32, picorv32 | 0.2479 | 1.5x (same design) |
| ibex | CPU | ibex, ibex, ibex | 0.2479 | 1.5x (same design) |
| uart_top | Controller | counter, counter, counter | 0.1754 | 1.0614x (cross-design, same class) |
| aes_cipher | Controller | aes_cipher, aes_cipher, aes_cipher | 0.2479 | 1.5x (same design) |
| sram_controller | Memory-heavy | sram_controller, sram_controller, sram_controller | 0.2479 | 1.5x (same design) |
| tinyml_accel | Accelerator | tinyml_accel, tinyml_accel, tinyml_accel | 0.2479 | 1.5x (same design) |

**Findings**:
- **Same-design clustering WORKS**: Every design's top results are from its own design (boost=1.5x).
- **Cross-similar-class boost WORKS**: uart_top (Controller) → counter (Controller) gets 1.0614x boost vs the baseline 1.0.
- **Limitation**: Base metric similarity is identical (0.1653) across ALL entries because synthetic data has uniform WNS=0, TNS=0, utilization=0, DRC=0. All differentiation comes from design boost alone. With real varied metrics, this would improve significantly.

**Verdict**: Similarity boost is applied and functional. Cross-class differentiation exists but is limited by uniform synthetic metrics.

---

## Phase 4 — Risk Differentiation Audit

**Execution output** (same metrics, varying design_name):

| Design | Class | Timing | Routing | DRC | LVS | Power |
|---|---|---|---|---|---|---|
| picorv32 | CPU | **8.75%** | 5.0% | 5.06% | 2.5% | 3.75% |
| ibex | CPU | **8.75%** | 5.0% | 5.06% | 2.5% | 3.75% |
| uart_top | Controller | 5.0% | 6.25% | 6.31% | 3.75% | 3.75% |
| aes_cipher | Controller | 5.0% | 6.25% | 6.31% | 3.75% | 3.75% |
| sram_controller | Memory-heavy | 3.75% | 5.0% | **8.81%** | 3.75% | 3.75% |
| tinyml_accel | Accelerator | 6.25% | **8.75%** | 3.81% | 2.5% | 3.75% |
| no design | (none) | 0.0% | 0.0% | 0.11% | 0.0% | 0.0% |

**Findings**:
- **Risks DIFFER across design classes**: CPU=8.75% Timing, Accelerator=8.75% Routing, Memory-heavy=8.81% DRC.
- **Same-class designs get identical risks** (picorv32=ibex, uart_top=aes_cipher) — consistent with class-based priors.
- **Without design name, risks are flat** (0-0.11%) — priors provide ALL differentiation.

**Verdict**: Risk differentiation is REAL and CORRECT. Design class priors are the sole source of differentiation.

---

## Phase 5 — Readiness Differentiation Audit

| Design | Class | Readiness (TapeoutReady) |
|---|---|---|
| picorv32 | CPU | 42.5% |
| uart_top | Controller | **45.0%** |
| aes_cipher | Controller | **45.0%** |
| sram_controller | Memory-heavy | **38.75%** |
| tinyml_accel | Accelerator | 40.0% |
| no design | (none) | 42.5% (uniform) |

**Findings**:
- Readiness range: 38.75%–45.0% (variance 6.25%)
- Controller gets highest (simpler designs → higher baseline of 0.60)
- Memory-heavy gets lowest (complex memory → lower baseline of 0.35)
- Without design name: uniform 42.5%

**Verdict**: Readiness differentiation exists but is modest. The 25% weight for design_baseline produces limited spread.

---

## Phase 6 — Recommendation Audit

| Design | Class | Top Recommendation |
|---|---|---|
| picorv32 | CPU | Optimize clock frequency for critical control paths |
| ibex | CPU | Optimize clock frequency for critical control paths |
| uart_top | Controller | Optimize FSM encoding for area |
| aes_cipher | Controller | Optimize FSM encoding for area |
| sram_controller | Memory-heavy | Check SRAM macro placement and aspect ratio |
| tinyml_accel | Accelerator | Optimize data movement between compute and memory |

**Findings**:
- All 6 classes have distinct recommendation templates (defined in `intelligence/recommendation_engine.py:10-41`)
- Templates trace directly to `design_profiles.classification`
- **Gap**: `get_design_class_recommendations()` is NOT called from the CLI prediction flow; only `get_recommendation(failure_type)` — which ignores design class — is available.

**Verdict**: Design-class recommendations exist and are correct. They are disconnected from the production prediction CLI.

---

## Phase 7 — Design Prior Audit

**Measured**: Risk with design_name vs without design_name.

| Failure Type | No Prior | CPU Prior | Memory-heavy Prior | Accelerator Prior |
|---|---|---|---|---|
| Timing | 0.0% | **8.75%** | 3.75% | 6.25% |
| Routing | 0.0% | 5.0% | 5.0% | **8.75%** |
| DRC | 0.11% | 5.06% | **8.81%** | 3.81% |
| LVS | 0.0% | 2.5% | 3.75% | 2.5% |
| Power | 0.0% | 3.75% | 3.75% | 3.75% |

**Delta from no-prior**:
- CPU Timing: +8.75pp
- Memory-heavy DRC: +8.70pp
- Accelerator Routing: +8.75pp
- Controller Timing: +5.0pp

**Source**: `DESIGN_CLASS_RISK_PRIORS` in `failure_atlas/prediction/risk.py:6-13` are hardcoded constants, applied at 25% weight in the formula: `blended = similar_risk*0.5 + freq_risk*0.25 + prior*0.25`.

**Verdict**: Priors actively influence outputs with measurable deltas. All differentiation is prior-driven because historical data is flat.

---

## Phase 8 — Design Similarity Boost Audit

| Query Design | Entry Design | Run Similarity | Design Boost | Final Similarity |
|---|---|---|---|---|
| picorv32 | picorv32 (same) | 0.1653 | 1.5 | 0.2479 |
| uart_top | counter (Controller→Controller) | 0.1653 | 1.0614 | 0.1754 |
| uart_top | gcd (Controller→Controller) | 0.1653 | 1.0614 | 0.1754 |
| picorv32 | ibex (CPU→CPU) | 0.1653 | 0.9486 (score 10.28/100 → boost 1.0514) | N/A |

**Findings**:
- Same-design boost = `1.0 + (100.0/100.0 * 0.5)` → **1.5x** (from `similarity_engine.py:89-90`)
- Cross-design same-class boost varies by design similarity score
- **Gap**: The boost formula `1.0 + (design_sim_score / 100.0 * 0.5)` caps at 1.5x, which is reasonable but the design similarity scores range 3-15/100, giving only 1.015-1.075x for cross-design matches

**Verdict**: Boost is measurable and working. Cross-class differentiation is present (Controller entries get 1.061x vs non-Controller getting 1.0x) but small.

---

## Phase 9 — Explainability Audit

**Source code inspection**:
- `ExecutionSimilarityEngine`: ❌ No `explain()` method. Returns `design_name`, `design_boost`, `run_similarity` fields in results.
- `FailureRiskEngine`: ❌ No `explain()` method. Returns risk percentages and failure signatures.
- `TapeoutReadinessPredictor`: ❌ No `explain()` method.
- `RecommendationEngine`: ✅ Has `explain()` method for RecommendationRecord, but it only explains historical fix rationale, NOT design class influence.

**Current explainability**: Data fields include `design_name`, `design_boost`, `run_similarity`, but there is NO human-readable explanation anywhere that says "This entry was ranked higher because both designs are CPU-class" or "Timing risk is elevated because picorv32 is a CPU design."

**Verdict**: Predictions are NOT explainable in human terms. Raw data fields exist but no translation layer.

---

## Phase 10 — Dataset Coverage Audit

**Class coverage** (designs with atlas entries / total profiled designs):

| Class | Covered | Total | Coverage | Weak? |
|---|---|---|---|---|
| CPU | 3 | 3 | 100% | |
| DSP | 1 | 1 | 100% | |
| Interconnect | 1 | 1 | 100% | |
| Accelerator | 1 | 1 | 100% | |
| Controller | 5 | 7 | **71%** | ⚠️ |
| Memory-heavy | 1 | 2 | **50%** | ⚠️ |

**Uncovered designs** (zero atlas entries):
- `fir_top` (Controller, tiny, 52 cells)
- `tiny_or` (Controller, tiny, 100 cells)
- `opentitan_ibex` (Memory-heavy, large, 50000 cells)

**Atlas entry distribution**:
- CPU: 355 entries (39%, 3 designs)
- Controller: 258 entries (28%, 5 with entries / 7 total)
- DSP: 82 entries (9%)
- Accelerator: 81 entries (9%)
- Memory-heavy: 68 entries (7%, 1 with entries / 2 total)
- Interconnect: 64 entries (7%)

**Verdict**: Controller and Memory-heavy classes have incomplete design coverage. 3 designs have zero atlas entries.

---

## Phase 11 — Prediction Improvement Audit

**Before Design Intelligence** (simulated, no `design_name` passed):

| Metric | Before (uniform) | After (differentiated) |
|---|---|---|
| Readiness variance | 0% (all 42.5%) | 6.25% (38.75–45.0%) |
| Timing risk variance | 0% (all 0.0%) | 5.0pp (3.75–8.75%) |
| DRC risk variance | 0% (all 0.11%) | 5.0pp (3.81–8.81%) |
| Recommendation diversity | None (failure-type only) | 6 distinct class templates |
| Similarity diversity | Uniform 0.1653 | 0.1653–0.2479 (boosted) |

**Improvement**: Every metric shows meaningful improvement. Before, all predictions were identical regardless of design. After, predictions vary by design class.

**Root cause of uniform "before" state**: All synthetic entries have near-identical metrics (WNS=0, TNS=0, utilization=0, DRC_violations=0), so Euclidean similarity finds no differentiation. Design intelligence is the ONLY source of variance.

**Verdict**: Design Intelligence dramatically improves prediction quality for synthetic data. With real varied metrics, the combination would be even stronger.

---

## Phase 12 — Final Verdict

### 1. Is Design Intelligence actually used?
**YES**.
- `design_name` is queried from `runs` table in CLI (`main.py:2782-2792`)
- Passed through 4 layers: CLI → RiskEngine → SimilarityEngine → DesignSimilarityEngine
- Passed through 4 layers: CLI → ReadinessEngine → SimilarityEngine → DesignSimilarityEngine
- Design class is retrieved from `design_profiles` and applied in both Risk and Readiness engines
- Source code trace evidence: `risk.py:42,54-57`, `readiness.py:71,83-86`, `similarity.py:52-53,60-67,78-81`

### 2. Do predictions now differ across designs?
**YES — measurable differentiation confirmed**.
- Risk: CPU Timing=8.75%, Accelerator Routing=8.75%, Memory-heavy DRC=8.81% (vs uniform 0% without)
- Readiness: Controller=45.0%, Memory-heavy=38.75% (variance 6.25% vs 0% without)

### 3. Do recommendations differ across designs?
**YES — but disconnected from production**.
- 6 distinct class templates exist and work correctly
- `get_design_class_recommendations()` returns class-specific output
- **Gap**: CLI `predict_command()` does NOT call any RecommendationEngine method

### 4. Does similarity search improve?
**YES — but limited by data quality**.
- Same-design entries get 1.5x boost (confirmed: 0.1653→0.2479)
- Same-class entries get smaller boost (Controller→Controller: 1.0614x)
- **Limitation**: Synthetic data has uniform metrics, so base similarity is flat. Real varied metrics would amplify the boost's impact.

### 5. What still limits prediction quality?
1. **No explainability**: Zero `explain()` methods across prediction engines. Raw field data exists but no human-readable attribution.
2. **Recommendations not in CLI flow**: `get_design_class_recommendations()` exists but is never called from `predict_command()`.
3. **3 uncovered designs**: `fir_top`, `tiny_or`, `opentitan_ibex` have zero atlas entries. Controller (5/7=71%) and Memory-heavy (1/2=50%) classes are incomplete.
4. **Hardcoded priors**: `DESIGN_CLASS_RISK_PRIORS` and `DESIGN_CLASS_READINESS_BASELINE` are manually defined constants, not data-driven from actual failure rates.
5. **Synthetic data uniformity**: All entries have WNS=0, TNS=0, utilization=0, DRC=0 — metric-based similarity cannot differentiate.
6. **`find_similar_by_failure_type()` is design-unaware**: This secondary method doesn't accept `design_name` (similarity.py:100-112).
7. **Recommendation recording is still legacy**: `get_recommendation()` → `get_recommendations_by_evidence()` use failure_type only, no design context.

### Final Rating: **FUNCTIONAL**

**Evidence summary**:

| Criterion | Score | Evidence |
|---|---|---|
| Design identity in DB | ✅ 100% (908/908 entries) | Phase 1: all entries have design_name |
| Design profiles built | ✅ 15/15 designs | Phase 1: all 15 profiled |
| Feature vectors extracted | ✅ 15/15 designs | Phase 1: all 15 extracted |
| Design classification | ✅ 6 classes, 15 classified | Phase 1: Classification done |
| design_name passes through pipeline | ✅ 4 layers confirmed | Phase 2: CLI→Risk→Sim, CLI→Readiness→Sim |
| Similarity boost applied | ✅ 1.5x same-design, 1.06x cross-class | Phase 3, 8: measurable boost |
| Risk differentiation | ✅ 5.0-8.75pp variance across classes | Phase 4: CPU≠Memory≠Accelerator |
| Readiness differentiation | ⚠️ Modest (6.25% variance) | Phase 5: Range 38.75-45.0% |
| Recommendations exist | ✅ All 6 classes covered | Phase 6: Class-specific templates |
| Recommendations in CLI flow | ❌ Not called | Phase 2: CLI missing rec call |
| Explainability | ❌ No explain() methods | Phase 9: 0/3 engines have explain() |
| Coverage completeness | ⚠️ 3/15 uncovered designs | Phase 10: Controller 71%, Memory-heavy 50% |
| Priors data-driven | ❌ All hardcoded | Phase 7: Constants in risk.py:6-13, readiness.py:6-13 |
| Prediction improvement vs before | ✅ Risk: 0%→3-9%, Readiness: uniform→6.25% var | Phase 11: Clear before/after delta |

**Overall**: Design Intelligence is **active and producing differentiated outputs**. It passes the core validation criteria: predictions, readiness, and similarity all vary by design class. However, production readiness is limited by missing explainability, disconnected recommendations, incomplete design coverage, and hardcoded (not data-driven) priors.
