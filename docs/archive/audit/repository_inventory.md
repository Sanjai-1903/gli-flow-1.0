# Repository Inventory

Inventory and classification of all top-level items in the `gli-flow-asic` repository.

## Classification Categories

- **SOURCE_CODE**: Core application logic and modules.
- **DOCUMENTATION**: Manuals, guides, and readme files.
- **GENERATED_ARTIFACT**: Files produced by build or runtime (gitignored).
- **DATABASE**: Persistent storage files (gitignored).
- **TEST_DATA**: Data used for testing purposes.
- **TEMPORARY_FILE**: Intermediate, cache, or temporary files (gitignored).
- **AUDIT_REPORT**: Audit, compliance, and investigative reports.
- **RELEASE_ASSET**: Files related to release management.
- **CONFIG**: Configuration files and policies.
- **RUNTIME**: Directories that store runtime outputs (gitignored).
- **TESTING**: Directories and files related to testing infrastructure.
- **SCRIPTS**: Automation and utility scripts.

## Inventory (Post-Cleanup)

| Item | Classification | Notes |
| :--- | :--- | :--- |
| `.github/` | CONFIG | CI/CD workflows and issue templates |
| `.gitignore` | CONFIG | Git ignore rules |
| `CHANGELOG.md` | DOCUMENTATION | Project changelog |
| `CONTRIBUTING.md` | DOCUMENTATION | Contribution guidelines |
| `Dockerfile` | CONFIG | Production container build |
| `Dockerfile.dev` | CONFIG | Development container build |
| `LICENSE` | DOCUMENTATION | Apache License 2.0 |
| `README.md` | DOCUMENTATION | Project overview and quickstart |
| `SECURITY.md` | DOCUMENTATION | Security policy |
| `adapters/` | SOURCE_CODE | Tool adapters (OpenRAM) |
| `analytics/` | SOURCE_CODE | Execution analytics, QoR scoring, regression detection |
| `backend/` | SOURCE_CODE | FastAPI REST API backend |
| `cloud_ingestion/` | SOURCE_CODE | Cloud telemetry ingestion service |
| `configs/` | CONFIG | Toolchain, runtime, policy, and template configs |
| `contracts/` | SOURCE_CODE | Execution contract engine |
| `dashboard/` | SOURCE_CODE | React/Vite frontend dashboard |
| `designs/` | TEST_DATA | Design configs and technology files |
| `docs/` | DOCUMENTATION | All documentation (audit, user guide, developer, release) |
| `environment/` | SOURCE_CODE | Environment validation and reproducibility checks |
| `examples/` | DOCUMENTATION | 10 example ASIC designs with manifests |
| `execution/` | SOURCE_CODE | Execution pipeline scripts |
| `failure_atlas/` | SOURCE_CODE | Failure detection, AI assistant, prediction engine |
| `gli_flow/` | SOURCE_CODE | Core Python package (CLI, orchestrator, telemetry) |
| `governance/` | SOURCE_CODE | Policy engine |
| `intelligence/` | SOURCE_CODE | AI prediction, anomaly detection, recommendation engine |
| `manifests/` | CONFIG | Toolchain manifest definitions |
| `outputs/` | RUNTIME | Runtime outputs (run data, telemetry, reports) |
| `package-lock.json` | CONFIG | npm lockfile |
| `package.json` | CONFIG | npm package config |
| `packaging/` | SOURCE_CODE | Execution bundle and packaging utilities |
| `ppa/` | SOURCE_CODE | Power/Performance/Area intelligence |
| `provenance/` | SOURCE_CODE | Build provenance graph and manifests |
| `pytest.ini` | CONFIG | pytest configuration |
| `regression/` | SOURCE_CODE | Regression detection and comparison engine |
| `release/` | SOURCE_CODE | Release validation tools |
| `reliability/` | SOURCE_CODE | Reliability scoring and trend analysis |
| `scheduler/` | SOURCE_CODE | Execution scheduler with dependency graph |
| `scripts/` | SCRIPTS | Utility scripts (install, test, validation, examples) |
| `setup.py` | CONFIG | Python package setup |
| `tests/` | TESTING | pytest test suite (unit, integration, e2e) |
| `trends/` | SOURCE_CODE | Trend analysis and predictive diagnostics |

## Cleanup Summary

| Category | Count |
| :--- | :--- |
| Top-level entries before | 61 |
| Top-level entries after | 36 |
| Entries removed | 25 |
| Reduction | 41% |

### Removed Items

| Item | Reason |
| :--- | :--- |
| `-zz` | Magic VLSI session file (dev clutter) |
| `.coverage` | Python coverage data (gitignored) |
| `.pytest_cache/` | pytest cache (gitignored) |
| `config/` | Merged into `configs/` |
| `coverage_taxonomy.json` | Generated artifact (gitignored) |
| `D2DInterfaceResult.tmp` | Temporary file (gitignored) |
| `designs/examples/*.ext` | Generated parasitic extraction files (gitignored) |
| `generate_golden_design_catalog.py` | Moved to `scripts/` |
| `golden_design_catalog.json` | Generated artifact (gitignored) |
| `golden_telemetry_export.json` | Generated artifact (gitignored) |
| `handover.md` | Internal session notes (dev clutter) |
| `home/` | Workspace mirror (dev clutter) |
| `install/` | Moved to `scripts/` |
| `latest.json` | Generated artifact (gitignored) |
| `run_systolic.py` | Moved to `scripts/` |
| `systolic-parsed/` | Moved to `examples/systolic_array/` |
| `test_design/` | Moved to `tests/data/` |
| `tmp/` | Temporary directory with databases (dev clutter) |
| `tools/` | Moved to `scripts/` |
| `execution_history/` | Moved to `outputs/execution_history/` |
| `metrics/` | Moved to `outputs/metrics/` |
| `replay/` | Moved to `outputs/replay/` |
| `snapshots/` | Moved to `outputs/snapshots/` |
| `telemetry/` | Moved to `outputs/telemetry/` |
| Root-level report files | Moved to `docs/audit/`, `docs/release/`, `docs/user_guide/` |
