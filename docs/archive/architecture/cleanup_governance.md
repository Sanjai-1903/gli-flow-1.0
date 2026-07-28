# GLI-FLOW Cleanup Governance

## Goal

GLI-FLOW generates:
- reports
- telemetry
- snapshots
- runtime artifacts
- packaging outputs
- observability metadata

This document defines cleanup philosophy during MVP stabilization.

---

# Repository Philosophy

GLI-FLOW prioritizes:
- reproducibility
- observability
- deterministic infrastructure
- replayable execution state
- CI/CD compatibility

Cleanup operations should NEVER compromise:
- reproducibility
- observability integrity
- execution replayability
- historical diagnostics

---

# Artifact Categories

| Category | Lifecycle |
|---|---|
| Source code | Permanently tracked |
| Documentation | Permanently tracked |
| Report schemas | Permanently tracked |
| Runtime reports | Generated artifacts |
| Telemetry outputs | Generated artifacts |
| Execution snapshots | Historical artifacts |
| CI observability reports | Generated artifacts |

---

# Cleanup Principles

Cleanup should aim to:
- reduce repository entropy
- preserve reproducibility
- avoid destructive deletion
- maintain observability continuity
- preserve onboarding simplicity

---

# Transitional Infrastructure

The following may evolve during stabilization:
- runs/
- snapshots/
- telemetry/
- openroad_runs/

Migration should occur incrementally to avoid:
- breaking reproducibility
- invalidating observability
- losing historical diagnostics

---

# Long-Term Direction

Future versions may support:
- artifact retention policies
- automatic snapshot archival
- distributed artifact storage
- cloud-native observability retention
- dashboard-driven cleanup policies

---

# MVP Stabilization Priorities

Current stabilization prioritizes:
- maintainability
- architectural consistency
- deterministic structure
- reproducible observability
- external-user usability

Feature growth should remain secondary to:
- repository coherence
- infrastructure integrity
- governance quality
