# Dataset Readiness Report

> Score current readiness, data quality, data quantity, and privacy risk for each dataset type.
> Generated: 2026-06-15

---

## Scoring Rubric

| Score | Meaning |
|-------|---------|
| 1 — Not Started | No data collection, no schema |
| 2 — Early Development | Schema defined, prototype collection |
| 3 — Collecting Data | Active collection, low volume |
| 4 — Established | Regular collection, growing volume, basic quality checks |
| 5 — Production Ready | High volume, automated quality, validation pipeline |

---

## 1. Failure Atlas Intelligence

**Use case**: Classifying failures by type, severity, root cause, and recommended fix.

### Readiness Score: **4/5 — Established**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Schema | 5 | 39 columns, well-defined, migrations |
| Collection | 5 | Automated via orchestrator + manual entry via API |
| Data volume | 3 | ~thousands of entries accumulated through testing |
| Data quality | 3 | Evidence field is unvalidated JSON; signature quality varies |
| Privacy risk | 4 | Evidence field may contain tool output with design-specific information |
| Indexing | 3 | Missing (failure_type, last_seen) index for common queries |
| Deduplication | 2 | Partial — only CROSS_TOOL_DRC_DISAGREEMENT has unique constraint |

### Key Gaps
- Evidence field needs sanitization at write time
- Unique constraint needed across ALL failure types
- Snapshot columns should be consolidated
- No validation pipeline for data quality

### Training Record Schema

```python
@dataclass
class FailureAtlasTrainingRecord:
    # Identifiers (hashed before upload)
    run_id_hash: str                    # SHA-256 truncated to 16 chars
    design_name_hash: str               # SHA-256 truncated to 16 chars

    # Failure classification
    tool: str                           # SAFE — tool name
    stage: str                          # SAFE — flow stage
    failure_type: str                   # SAFE — standardized type
    failure_signature: str              # SAFE — already derived hash
    severity: str                       # SAFE — LOW/MEDIUM/HIGH/BLOCKING
    confidence: float                   # SAFE — 0.0-1.0

    # Resolution metadata
    resolution_outcome: str             # SAFE — success/failure/unknown
    resolution_attempts: int            # SAFE — count
    resolution_success_rate: float      # SAFE — derived

    # Runtime context
    runtime_sec: float                  # SAFE — duration
    tool_versions: str                  # SAFE — version strings
    gli_version: str                    # SAFE — GLI version

    # DO NOT INCLUDE
    # - evidence (could contain IP)
    # - log excerpts (could contain paths)
    # - RTL, netlists, GDS
    # - error text (could contain file paths)
```

---

## 2. Resolution Intelligence

**Use case**: Learning which fixes work for which failures; trust scoring.

### Readiness Score: **4/5 — Established**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Schema | 5 | 22 columns, well-structured, trust scoring |
| Collection | 4 | Automated via capture + manual feedback |
| Data volume | 3 | Accumulated through testing/captures |
| Data quality | 4 | Structured numeric data; resolution text is free-form |
| Privacy risk | 5 | All numeric/aggregate; design names tracked but stored locally |
| Indexing | 4 | Missing UNIQUE(failure_fingerprint, resolution) |
| Deduplication | 2 | No unique constraint — Python-level dedup only |

### Key Gaps
- UNIQUE(failure_fingerprint, resolution) constraint needed
- JSON tracking columns (tracked_run_ids, tracked_design_names) should be normalized
- Resolution text is free-form — may need normalization for ML

### Training Record Schema

```python
@dataclass
class ResolutionTrainingRecord:
    # Identifiers (hashed before upload)
    failure_fingerprint_hash: str       # SHA-256 of fingerprint string

    # Resolution metadata
    resolution_type: str                # SAFE — config_change, parameter_tweak, etc.
    resolution_text: str                # REDACT — remove paths/specifics before upload
    success: bool                       # SAFE — outcome
    attempt_count: int                  # SAFE — total attempts
    success_count: int                  # SAFE — successful attempts
    failure_count: int                  # SAFE — failed attempts

    # Trust scores
    trust_score: float                  # SAFE — composite trust 0.0-1.0
    trust_level: str                    # SAFE — HIGH/MEDIUM/LOW
    engineer_confirmations: int         # SAFE — count
    contradictory_reports: int          # SAFE — count

    # Breadth
    unique_runs: int                    # SAFE — count
    unique_designs: int                 # SAFE — count

    # DO NOT INCLUDE
    # - tracked_run_ids (raw run IDs)
    # - tracked_design_names (raw design names)
    # - root_cause (may contain design-specific details)
```

---

## 3. QoR Prediction

**Use case**: Predicting final QoR from early-stage metrics; identifying optimal flow configurations.

### Readiness Score: **2/5 — Early Development**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Schema | 2 | Run metrics exist (~20 numeric columns) but no dedicated QoR schema |
| Collection | 3 | Metrics collected per run telemetry |
| Data volume | 2 | Limited runs with complete metric sets |
| Data quality | 3 | Numeric data is clean; coverage varies by stage |
| Privacy risk | 5 | All numeric — no IP concerns |

### Key Gaps
- No standardized QoR training record schema
- No structural metadata collected (needed for prediction)
- No stage-by-stage metric history (only final metrics)
- Limited data volume for training models

### Required New Signals
- Stage-by-stage QoR metrics (not just final)
- Structural metadata (logic depth, fanout, macro count)
- Flow configuration parameters (what knobs were used)
- Tool version information

---

## 4. Flow Optimization

**Use case**: Recommending optimal flow settings based on design characteristics and historical outcomes.

### Readiness Score: **1/5 — Not Started**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Schema | 1 | No flow optimization schema exists |
| Collection | 1 | Not collecting flow parameters and outcomes |
| Data volume | 1 | No data |
| Data quality | N/A | No data |
| Privacy risk | N/A | Not applicable |

### Key Gaps
- Comprehensive — no data collected
- Need: flow configuration (strategy, effort, thresholds)
- Need: stage outcomes per configuration
- Need: design characteristics to correlate with optimal flow

---

## 5. Agentic EDA

**Use case**: Autonomous EDA flow agents that learn from past outcomes to make decisions.

### Readiness Score: **1/5 — Not Started**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Schema | 1 | No agent schema |
| Collection | 1 | Agents don't exist yet |
| Data volume | 1 | No data |
| Data quality | N/A | No data |
| Privacy risk | N/A | Not applicable |

### Requirements (from architecture)
- Resolution Intelligence feeds agent knowledge
- Failure Atlas provides failure context
- Trust scores guide agent confidence
- All agent decisions must be auditable
- Agents never touch customer IP

---

## 6. Structural Graph Learning

**Use case**: Learning design structure-property relationships without seeing the design.

### Readiness Score: **1/5 — Not Started**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Schema | 1 | No structural metadata collected |
| Collection | 1 | Structural metadata study completed (see separate doc) |
| Data volume | 1 | No data |
| Data quality | N/A | No data |
| Privacy risk | N/A | Requires privacy review for each metric |

### Required Data
- Structural metadata (logic depth, fanout, congestion, Rent exponent)
- Must be computed locally, only aggregates uploaded
- Cannot upload netlist adjacency or connectivity

---

## 7. Future LCM Research

**Use case**: Large Concept Models for EDA — learning high-level flow and failure concepts.

### Readiness Score: **1/5 — Conceptual Only**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Schema | 1 | No schema |
| Collection | 1 | No data |
| Data volume | 1 | No data |
| Data quality | N/A | No data |
| Privacy risk | N/A | Foundational privacy research needed |

### Prerequisites
- Failure Atlas dataset maturity (4+)
- Resolution Intelligence dataset maturity (4+)
- Structural graph learning data (3+)
- QoR prediction data (3+)

---

## 8. OVERALL READINESS MATRIX

| Dataset | Current | Target (6mo) | Target (12mo) | Key Dependency |
|---------|---------|--------------|---------------|----------------|
| Failure Atlas Intelligence | **4/5** | 5/5 | 5/5 | Evidence sanitization |
| Resolution Intelligence | **4/5** | 5/5 | 5/5 | Normalize tracking columns |
| QoR Prediction | **2/5** | 3/5 | 4/5 | Structural metadata collection |
| Flow Optimization | **1/5** | 2/5 | 3/5 | Flow parameter tracking |
| Agentic EDA | **1/5** | 1/5 | 2/5 | Resolution Intelligence maturity |
| Structural Graph Learning | **1/5** | 2/5 | 3/5 | Metadata pipeline development |
| Future LCM Research | **1/5** | 1/5 | 2/5 | All above datasets mature |

---

## 9. RECOMMENDATIONS

### Immediate (Week 1-2)
1. Sanitize evidence field in failure_atlas_entries
2. Add unique constraints to resolution_patterns and failure_atlas_entries
3. Normalize resolution_patterns tracking columns

### Short-term (Month 1-2)
4. Add timing path distribution to telemetry collection
5. Add resource utilization breakdown
6. Add clock domain structure metadata
7. Consolidate TelemetryManager/TelemetryParser implementations

### Medium-term (Month 3-6)
8. Add structural metadata collection (logic depth, fanout, congestion)
9. Build QoP prediction training dataset
10. Design flow optimization experiment framework
11. Implement telemetry Transparency Center

### Long-term (Month 6-12)
12. Begin agentic EDA knowledge base construction
13. Research LCM feasibility for EDA failure analysis
14. Scale structural graph learning pipeline
