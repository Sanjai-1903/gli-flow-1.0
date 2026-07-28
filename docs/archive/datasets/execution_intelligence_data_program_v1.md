# GLI Execution Intelligence Data Acquisition Program v1

**Generated**: 2026-06-16T05:53:28.746767+00:00
**Data Source**: `~/.gli_flow/gli_flow.db`

---

## Executive Summary

| Metric | Value |
|---|---|
| Atlas Signatures | 27 / 100 |
| Coverage | 27.0% |
| Execution Records | 882 |
| Readiness Score | 75/100 |
| Readiness Level | FUNCTIONAL |
| Milestone Level | 2 |

---

## Phase 1 — Failure Atlas Growth Tracker

| Metric | Value |
|---|---|
| Current Signatures | 27 |
| Target Signatures | 100 |
| Growth Rate | 5.82/day |
| Coverage % | 27.0% |
| Distinct Failure Types | ['CONGESTION', 'CROSS_TOOL_DRC_DISAGREEMENT', 'DESIGN_DRC_VIOLATION', 'DRC', 'DRC_SPACING', 'FLOW_EXTRACTION_TIMEOUT', 'LIBRARY', 'LOGIC', 'LVS_DEVICE_MISMATCH', 'PIPELINE_FAILURE', 'POWER', 'ROUTING', 'SIGNOFF_FAILURE', 'TIMING'] |
| Distinct Designs | [] |
| Remaining to Target | 73 |

**Assessment**: NEEDS WORK — far from 100-signature target

---

## Phase 2 — Resolution Harvesting

| Metric | Value |
|---|---|
| FAILED→SUCCESS Pairs Found | 6 |
| Resolution Patterns Proposed | 5 |
| Resolution Patterns Inserted | 5 |

---

## Phase 3 — Execution Record Expansion

| Metric | Value |
|---|---|
| Before Expansion | 10 |
| After Expansion | 882 |
| Generated | 874 |
| Target | 1000 |

---

## Phase 4 — Synthetic Campaign Planner

| Metric | Value |
|---|---|
| Category Coverage | 10.0% |
| Design Coverage | 0.0% |
| Missing Categories | ['Timing', 'Routing', 'CTS', 'LVS', 'Power', 'IR Drop', 'Antenna', 'Extraction', 'Tool Failures'] |
| Missing Designs | ['counter', 'gcd', 'uart', 'gpio', 'fir', 'picorv32', 'ibex', 'serv', 'opentitan_ibex', 'tinyml_accel', 'sram_controller', 'aes_cipher'] |
| Recommended Campaigns | 22 |
| Total Seed Runs | 591 |

### Recommended Campaigns

| Campaign | Priority | Focus | Estimated Runs |
|---|---|---|---|
| COVER_TIMING | HIGH | Generate Timing failure signatures | 25 |
| COVER_LVS | HIGH | Generate LVS failure signatures | 25 |
| DESIGN_COUNTER | HIGH | Generate entries for counter design | 30 |
| DESIGN_GCD | HIGH | Generate entries for gcd design | 30 |
| DESIGN_UART | HIGH | Generate entries for uart design | 30 |
| DESIGN_GPIO | HIGH | Generate entries for gpio design | 30 |
| DESIGN_FIR | HIGH | Generate entries for fir design | 30 |
| DESIGN_PICORV32 | HIGH | Generate entries for picorv32 design | 30 |
| DESIGN_IBEX | HIGH | Generate entries for ibex design | 30 |
| DESIGN_SERV | HIGH | Generate entries for serv design | 30 |
| DESIGN_OPENTITAN_IBEX | HIGH | Generate entries for opentitan_ibex design | 30 |
| DESIGN_TINYML_ACCEL | HIGH | Generate entries for tinyml_accel design | 30 |
| DESIGN_SRAM_CONTROLLER | HIGH | Generate entries for sram_controller design | 30 |
| DESIGN_AES_CIPHER | HIGH | Generate entries for aes_cipher design | 30 |
| COVER_ROUTING | MEDIUM | Generate Routing failure signatures | 25 |
| COVER_CTS | MEDIUM | Generate CTS failure signatures | 25 |
| COVER_POWER | MEDIUM | Generate Power failure signatures | 25 |
| COVER_IR_DROP | MEDIUM | Generate IR Drop failure signatures | 25 |
| COVER_ANTENNA | MEDIUM | Generate Antenna failure signatures | 25 |
| COVER_EXTRACTION | MEDIUM | Generate Extraction failure signatures | 25 |
| COVER_TOOL_FAILURES | MEDIUM | Generate Tool Failures failure signatures | 25 |
| EXPAND_DRC | MEDIUM | Expand DRC coverage (2 current) | 15 |

---

## Phase 5 — Failure Coverage Expansion

| Metric | Value |
|---|---|
| Failure Type Coverage | 270.0% |
| Design Coverage | 8.3% |
| Stage Coverage | 16.7% |
| Missing Designs | ['aes_cipher', 'counter', 'fir', 'gcd', 'gpio', 'ibex', 'opentitan_ibex', 'picorv32', 'serv', 'sram_controller', 'tinyml_accel', 'uart'] |

### Target Categories (10)

| Category | Status |
|---|---|
| Timing | MISSING |
| Routing | MISSING |
| CTS | MISSING |
| DRC | MISSING |
| LVS | MISSING |
| Power | MISSING |
| IR Drop | MISSING |
| Antenna | MISSING |
| Extraction | MISSING |
| Tool Failures | MISSING |

---

## Phase 6 — Design Diversity Program

**Total Designs**: 12

| Tier | Designs |
|---|---|

**New Designs Added**: serv, opentitan_ibex, tinyml_accel, sram_controller, aes_cipher

| Design | Type | Cells | Tags |
|---|---|---|---|
| serv | medium | 3000 | medium, cpu, sky130, riscv |
| opentitan_ibex | large | 50000 | large, soc, sky130, sram |
| tinyml_accel | medium | 5000 | medium, ml, sky130, sram |
| sram_controller | medium | 2000 | medium, memory, sky130, sram |
| aes_cipher | medium | 3500 | medium, crypto, sky130 |

---

## Phase 7 — Resolution Validation

| Metric | Value |
|---|---|
| Total Patterns | 10 |
| High-Trust Patterns | 0 |
| Avg Success Rate | 1.0 |
| Types With Tracking | 0 |

---

## Phase 8 — Dataset Scale Dashboard

| Component | Metric | Value |
|---|---|---|
| Atlas | Signatures | 899 |
| Atlas | Coverage | 899.0% |
| Records | Total Intel | 882 |
| Records | Resolution Patterns | 10 |
| Quality | Avg Trust | 0.3 |
| Quality | Avg Success | 1.0 |
| Coverage | Prediction | 60.7% |

---

## Phase 9 — Quality Gates

| Gate | Status |
|---|---|
| Atlas Entries | 908 |
| Resolution Patterns | 10 |
| Execution Records | 872 |
| Duplicate Signatures | 4 |
| Duplicate Resolutions | 5 |
| Quality Status | WARN |

---

## Phase 10 — Prediction Readiness

| Metric | Value |
|---|---|
| Readiness Score | 75/100 |
| Readiness Level | FUNCTIONAL |
| Atlas Signatures | 899 |
| Resolution Patterns | 10 |
| Execution Records | 882 |

### Score Breakdown

- 100+ atlas signatures (+30)
- 5+ resolution patterns (+10)
- 500+ execution records (+20)
- Minimal prediction possible (+15)

---

## Phase 11 — Dataset Milestones

| Level | Target | Current | Status |
|---|---|---|---|
| Level 1 | 100 signatures | Sigs:899 Recs:882 | ACHIEVED |
| Level 2 | 500 signatures | Sigs:899 Recs:882 | ACHIEVED |
| Level 3 | 1000 signatures | Sigs:899 Recs:882 | PENDING |
| Level 4 | 10000 records | Sigs:899 Recs:882 | PENDING |

---

## Success Criteria

| Criteria | Status | Detail |
|---|---|---|
| GLI knows exactly what data exists | ✅ | Dashboard captures all dataset dimensions |
| GLI knows exactly what data is missing | ✅ | Missing: 9 categories, 12 designs |
| GLI knows exactly how to acquire it | ✅ | 22 campaigns recommended |
| GLI knows how much is needed before prediction quality improves | ✅ | Readiness score 75/100 — need 73 more sigs, 118 more records |

---

## Appendix: Seed Execution Plan

| Design | Category | Campaign | Priority | Runs |
|---|---|---|---|---|
| fir | Timing | COVER_TIMING | HIGH | 8 |
| picorv32 | Timing | COVER_TIMING | HIGH | 8 |
| ibex | Timing | COVER_TIMING | HIGH | 8 |
| gcd | LVS | COVER_LVS | HIGH | 8 |
| uart | LVS | COVER_LVS | HIGH | 8 |
| aes_cipher | LVS | COVER_LVS | HIGH | 8 |
| counter | ALL | DESIGN_COUNTER | HIGH | 30 |
| gcd | ALL | DESIGN_GCD | HIGH | 30 |
| uart | ALL | DESIGN_UART | HIGH | 30 |
| gpio | ALL | DESIGN_GPIO | HIGH | 30 |
| fir | ALL | DESIGN_FIR | HIGH | 30 |
| picorv32 | ALL | DESIGN_PICORV32 | HIGH | 30 |
| ibex | ALL | DESIGN_IBEX | HIGH | 30 |
| serv | ALL | DESIGN_SERV | HIGH | 30 |
| opentitan_ibex | ALL | DESIGN_OPENTITAN_IBEX | HIGH | 30 |
| tinyml_accel | ALL | DESIGN_TINYML_ACCEL | HIGH | 30 |
| sram_controller | ALL | DESIGN_SRAM_CONTROLLER | HIGH | 30 |
| aes_cipher | ALL | DESIGN_AES_CIPHER | HIGH | 30 |
| uart | Routing | COVER_ROUTING | MEDIUM | 8 |
| gpio | Routing | COVER_ROUTING | MEDIUM | 8 |
| counter | Routing | COVER_ROUTING | MEDIUM | 8 |
| fir | CTS | COVER_CTS | MEDIUM | 8 |
| picorv32 | CTS | COVER_CTS | MEDIUM | 8 |
| ibex | CTS | COVER_CTS | MEDIUM | 8 |
| ibex | Power | COVER_POWER | MEDIUM | 8 |
| tinyml_accel | Power | COVER_POWER | MEDIUM | 8 |
| picorv32 | Power | COVER_POWER | MEDIUM | 8 |
| ibex | IR Drop | COVER_IR_DROP | MEDIUM | 8 |
| picorv32 | IR Drop | COVER_IR_DROP | MEDIUM | 8 |
| tinyml_accel | IR Drop | COVER_IR_DROP | MEDIUM | 8 |
| counter | Antenna | COVER_ANTENNA | MEDIUM | 8 |
| gcd | Antenna | COVER_ANTENNA | MEDIUM | 8 |
| sram_controller | Antenna | COVER_ANTENNA | MEDIUM | 8 |
| aes_cipher | Extraction | COVER_EXTRACTION | MEDIUM | 8 |
| tinyml_accel | Extraction | COVER_EXTRACTION | MEDIUM | 8 |
| serv | Extraction | COVER_EXTRACTION | MEDIUM | 8 |
| serv | Tool Failures | COVER_TOOL_FAILURES | MEDIUM | 8 |
| opentitan_ibex | Tool Failures | COVER_TOOL_FAILURES | MEDIUM | 8 |
| sram_controller | Tool Failures | COVER_TOOL_FAILURES | MEDIUM | 8 |
| counter | DRC | EXPAND_DRC | MEDIUM | 5 |
| gcd | DRC | EXPAND_DRC | MEDIUM | 5 |
| sram_controller | DRC | EXPAND_DRC | MEDIUM | 5 |

*Report generated by GLI Execution Intelligence Data Acquisition Program*