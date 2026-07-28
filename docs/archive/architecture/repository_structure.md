# GLI-FLOW Repository Structure

## Purpose

This document defines the canonical ownership model for the GLI-FLOW repository.

The goal is to maintain:
- architectural clarity
- deterministic structure
- separation of source and runtime state
- maintainability
- contributor friendliness

---

# Core Principles

## 1. Source Code vs Runtime State

GLI-FLOW strictly separates:

- source code
- generated artifacts
- runtime outputs
- telemetry
- packaging artifacts

Generated artifacts must NEVER pollute source directories.

---

## 2. Canonical Ownership

Each subsystem owns a specific responsibility.

No duplicated ownership should exist.

---

# Repository Ownership Map

| Directory | Responsibility |
|---|---|
| analytics/ | QoR analytics and metrics intelligence |
| configs/ | Runtime, toolchain, and policy configuration |
| docs/ | Documentation system |
| examples/ | Golden onboarding designs |
| execution/ | OpenROAD/LibreLane orchestration |
| failure_atlas/ | Failure intelligence systems |
| governance/ | Release governance and validation |
| intelligence/ | Higher-level execution intelligence |
| outputs/ | Generated runtime artifacts |
| packaging/ | Packaging logic and release bundling |
| provenance/ | Execution provenance tracking |
| regression/ | Regression analysis systems |
| replay/ | Execution replay systems |
| scheduler/ | Scheduling and orchestration systems |
| telemetry/ | Runtime telemetry collection |
| trends/ | Historical trend analysis |

---

# Output Ownership

## outputs/reports/

Generated reports:
- QoR reports
- execution summaries
- validation reports
- scoring outputs

---

## outputs/packages/

Generated packaging artifacts:
- tar.gz bundles
- release packages

---

## outputs/runs/

Execution runtime artifacts:
- OpenROAD runs
- logs
- intermediate artifacts

---

## outputs/telemetry/

Generated telemetry snapshots.

---

## outputs/snapshots/

Historical execution snapshots.

---

# Repository Hygiene Rules

The following must NEVER be committed:

- __pycache__/
- *.egg-info/
- runtime outputs
- generated telemetry
- OpenROAD execution artifacts
- temporary files

These are enforced through .gitignore.

---

# MVP Stabilization Objective

The repository structure must support:

- maintainability
- external contributors
- deterministic builds
- CI/CD readiness
- reproducibility
- future dashboard integration
- future industrialization (v2)

without architectural ambiguity.
