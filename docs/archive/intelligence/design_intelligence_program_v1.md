# GLI Design Intelligence & Feature Extraction Program v1

**Generated**: 2026-06-16T09:06:36.335531+00:00
**Data Source**: `~/.gli_flow/gli_flow.db`

---

## Executive Summary

| Metric | Value |
|---|---|
| Design Identity Coverage | 100.0% |
| Design Profiles Built | 15 |
| Feature Vectors Extracted | 15 |
| Design Classes | 6 |
| Entry Coverage | 100.0% |
| Design Readiness Score | 100.0/100 |
| Design Readiness Level | PRODUCTION_READY |

| Designs Without Atlas Entries | 3 |

---

## Phase 1 — Design Identity Recovery

| Metric | Before | After |
|---|---|---|
| Missing design_name | 0 | 0 |
| Coverage | 0% | 100.0% |
| Designs Discovered | -- | 14 |

### Designs Discovered

| Design | Atlas Entries | Runs |
|---|---|---|
| aes_cipher | 61 | 0 |
| counter | 65 | 10 |
| fir | 82 | 0 |
| fir_top | 0 | 1 |
| gcd | 59 | 3 |
| gpio | 64 | 0 |
| ibex | 164 | 0 |
| picorv32 | 109 | 2 |
| serv | 82 | 0 |
| sram_controller | 68 | 0 |
| tiny_or | 0 | 8 |
| tinyml_accel | 81 | 0 |
| uart | 65 | 0 |
| uart_top | 8 | 4 |

**Data sources**: `runs.design_name` (direct), run ID pattern inference, fallback to `run_id`

---

## Phase 2 — Design Profile Engine

**Profiles built**: 15

| Design | Type | Cells | Memory Ratio | Control Ratio | Compute Ratio |
|---|---|---|---|---|---|
| aes_cipher | medium | 3500 | 2% | 25% | 73% |
| counter | tiny | 100 | 2% | 10% | 88% |
| fir | medium | 2000 | 5% | 15% | 80% |
| fir_top | tiny | 20 | 10% | 30% | 60% |
| gcd | tiny | 200 | 2% | 10% | 88% |
| gpio | medium | 400 | 2% | 25% | 73% |
| ibex | large | 20000 | 15% | 35% | 50% |
| opentitan_ibex | large | 50000 | 15% | 25% | 60% |
| picorv32 | large | 15000 | 2% | 35% | 63% |
| serv | medium | 3000 | 2% | 35% | 63% |
| sram_controller | medium | 2000 | 45% | 25% | 30% |
| tiny_or | tiny | 100 | 10% | 30% | 60% |
| tinyml_accel | medium | 5000 | 15% | 15% | 70% |
| uart | medium | 800 | 2% | 25% | 73% |
| uart_top | tiny | 52 | 10% | 30% | 60% |

**Profile fields**: `design_name`, `design_type`, `rtl_size`, `module_count`, `memory_ratio`, `control_ratio`, `compute_ratio`

---

## Phase 3 — Structural Feature Extraction

**Feature records**: 15

| Design | Logic Depth | Register Density | Memory Density | DSP Density |
|---|---|---|---|---|
| aes_cipher | 47 | 30% | 2% | 1% |
| counter | 13 | 8% | 2% | 1% |
| fir | 54 | 25% | 2% | 15% |
| fir_top | 8 | 20% | 2% | 1% |
| gcd | 15 | 8% | 2% | 1% |
| gpio | 17 | 20% | 2% | 1% |
| ibex | 42 | 35% | 20% | 1% |
| opentitan_ibex | 31 | 20% | 20% | 1% |
| picorv32 | 41 | 35% | 2% | 1% |
| serv | 34 | 35% | 2% | 1% |
| sram_controller | 10 | 10% | 50% | 1% |
| tiny_or | 13 | 20% | 2% | 1% |
| tinyml_accel | 61 | 25% | 20% | 25% |
| uart | 19 | 45% | 2% | 1% |
| uart_top | 11 | 20% | 2% | 1% |

**Feature fields**: `fanout_histogram[10]`, `logic_depth`, `register_density`, `memory_density`, `dsp_density`

---

## Phase 4 — Design Classification

**Classes used**: CPU, CONTROLLER, DSP, ACCELERATOR, MEMORY_HEAVY, INTERCONNECT

| Design | Classification |
|---|---|
| aes_cipher | Controller |
| counter | Controller |
| fir | DSP |
| fir_top | Controller |
| gcd | Controller |
| gpio | Interconnect |
| ibex | CPU |
| opentitan_ibex | Memory-heavy |
| picorv32 | CPU |
| serv | CPU |
| sram_controller | Memory-heavy |
| tiny_or | Controller |
| tinyml_accel | Accelerator |
| uart | Controller |
| uart_top | Controller |

**Distribution**:
- Accelerator: 1
- CPU: 3
- Controller: 7
- DSP: 1
- Interconnect: 1
- Memory-heavy: 2

---

## Phase 5 — Design Similarity Engine

The `DesignSimilarityEngine` compares designs by class, cell count, memory/control/compute ratio, logic depth, and register density.

**Designs with similarity data**: See `design_intelligence_program_v1.json` for full matrix

---

## Phase 6 — Feature-Aware Prediction

Prediction engine now uses design features alongside historical outcomes:
- Design class influences risk priors
- Feature vectors enable design-level (not just run-level) similarity
- `DesignSimilarityEngine` provides per-design nearest neighbors

---

## Phase 7 — Feature-Aware Recommendations

| Design Class | Recommendation Focus |
|---|---|
| CPU | Clock frequency, branch prediction, register file |
| DSP | MAC chain timing, bit-width, pipeline balancing |
| Accelerator | Data movement, weight-stationary, systolic array |
| Memory-heavy | SRAM placement, BIST, power gating |
| Controller | FSM encoding, reset/enable tree, partitioning |
| Interconnect | Bus width, arbitration, I/O pad placement |

---

## Phase 8 — Design Knowledge Graph

| Metric | Value |
|---|---|
| Design Entities Added | 15 |
| Same-Class Relationships | 12 |

---

## Phase 9 — Design Coverage Engine

| Metric | Value |
|---|---|
| Total Atlas Entries | 908 |
| Covered Entries (w/ design_name) | 908 |
| Entry Coverage | 100.0% |

### Coverage by Class
- Accelerator: 1 designs
- CPU: 3 designs
- Controller: 5 designs
- DSP: 1 designs
- Interconnect: 1 designs
- Memory-heavy: 1 designs

### Gaps — Designs Without Atlas Entries
- fir_top
- opentitan_ibex
- tiny_or

---

## Phase 10 — Dataset Quality Audit

**failure_atlas**:
- table: failure_atlas_entries
- total_records: 908
- with_design_name: 908
- design_name_pct: 100.0
- with_failure_type: 908
- failure_type_pct: 100.0
- with_severity: 908
- with_signature: 908
- distinct_designs: 12

**runs**:
- table: runs
- total_records: 28
- with_design_name: 28
- design_name_pct: 100.0
- with_cell_count: 27
- with_wns: 27
- distinct_designs: 6

**design_profiles**:
- table: design_profiles
- total_records: 15
- with_design_type: 15
- with_classification: 15
- with_cell_count: 15

**design_features**:
- table: design_features
- total_records: 15
- with_fanout_histogram: 15
- with_logic_depth: 15

**execution_records**:
- execution_intelligence_count: 872
- telemetry_execution_count: 0

All records have design identity: **True**
All records have feature vector: **True**

---

## Phase 11 — Readiness Recalculation

| Component | Score |
|---|---|
| Design Identity Coverage | 100.0% |
| Profiles Built | 15/12 |
| Feature Vectors | 15/12 |
| Classifications | 15/6 classes |
| **Design Readiness Score** | **100.0/100** |
| **Design Readiness Level** | **PRODUCTION_READY** |

---

## Success Criteria

| Criteria | Status | Evidence |
|---|---|---|
| GLI can answer: "What type of design is this?" | ✅ | 15/6 design classes populated |
| GLI can answer: "What historical designs most resemble it?" | ✅ | DesignSimilarityEngine with 15 design entities |
| GLI uses design features before making predictions | ✅ | 15 feature vectors extracted |

*Report generated by GLI Design Intelligence & Feature Extraction Program*