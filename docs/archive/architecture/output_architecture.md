# GLI-FLOW Output Architecture

## Goal

GLI-FLOW centralizes machine-generated runtime artifacts under:

```text
outputs/
```

This improves:
- reproducibility
- observability
- CI/CD compatibility
- dashboard ingestion
- deterministic artifact discovery

---

# Output Structure

| Directory | Purpose |
|---|---|
| outputs/reports/ | Machine-readable reports |
| outputs/runs/ | Runtime execution outputs |
| outputs/snapshots/ | Historical observability snapshots |
| outputs/telemetry/ | Runtime telemetry artifacts |
| outputs/packages/ | Portable distribution artifacts |

---

# Design Principles

GLI-FLOW output architecture prioritizes:
- deterministic paths
- machine-readable artifacts
- replay-friendly observability
- CI/CD compatibility
- dashboard discoverability

---

# Historical Compatibility

Legacy directories may still exist during MVP stabilization:

- runs/
- snapshots/
- telemetry/
- openroad_runs/

Migration toward centralized outputs/ architecture will occur incrementally to avoid breaking reproducibility.

---

# Long-Term Direction

Future versions aim to support:
- distributed artifact storage
- cloud-native observability
- remote execution telemetry
- dashboard-native artifact discovery
- large-scale execution analytics
