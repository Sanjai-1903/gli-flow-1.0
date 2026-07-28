# Direct SQLite Usage Audit

## Runtime Critical (must be refactored)

| # | File | Line | Component |
|---|------|------|-----------|
| 2 | gli_flow/database/sqlite.py | 16, 21 | DatabaseManager (orchestrator run storage) |
| 2 | failure_atlas/repository.py | 37, 43 | FailureAtlasRepository (FA entry storage) |
| 2 | gli_flow/database/manager.py | 12, 23 | DatabaseManager (legacy, used by some CLI) |
| 1 | gli_flow/database/migrations.py | 556, 561 | MigrationEngine (schema management) |
| 1 | gli_flow/database/sqlite_provider.py | 18, 24 | SQLiteProvider (the provider wrapper) |
| 3 | gli_flow/cli/main.py | 312, 1872, 1893 | CLI commands (reset, support bundle) |

## Telemetry / Ingestion

| # | File | Line |
|---|------|------|
| 1 | cloud_ingestion/database.py | 91 | Ingestion server storage |

## Failure Atlas Subsystem

| # | File | Line |
|---|------|------|
| 1 | failure_atlas/correlation_engine.py | 12 |
| 1 | failure_atlas/coverage_engine.py | 11 |
| 2 | failure_atlas/prediction/risk.py | 29 |
| 1 | failure_atlas/prediction/readiness.py | 33 |
| 1 | failure_atlas/run_trust_engine.py | 9 |
| 2 | failure_atlas/ai_assistant/feedback.py | 65, 72 |
| 2 | failure_atlas/ai_assistant/resolution_capture.py | 38, 45 |
| 2 | failure_atlas/community_intelligence/export.py | 34, 115 |
| 2 | failure_atlas/community_intelligence/escalation.py | 76, 83 |
| 2 | failure_atlas/community_intelligence/telemetry.py | 46, 53 |
| 2 | failure_atlas/community_intelligence/dataset.py | 43, 50 |
| 1 | failure_atlas/community_intelligence/health.py | 15 |

## Dashboard Backend / Outputs

| # | File | Line |
|---|------|------|
| 1 | outputs/execution_history/history_api.py | 11 |
| 1 | outputs/execution_history/live_status.py | 11 |
| 1 | outputs/metrics/qor_api.py | 9 |

## Analytics

| # | File | Line |
|---|------|------|
| 1 | analytics/regression.py | 13 |
| 1 | analytics/trend_analyzer.py | 7 |

## Intelligence / Data Programs

| # | File | Line |
|---|------|------|
| 2 | intelligence/warehouse.py | 24 |
| 2 | intelligence/recommendation_engine.py | 48, 55 |
| 2 | gli_flow/design_intel/feature_extractor.py | 58, 74 |
| 1 | gli_flow/design_intel/quality_audit.py | 21 |
| 1 | gli_flow/design_intel/design_classifier.py | 68 |
| 2 | gli_flow/design_intel/profile_engine.py | 60, 81 |
| 1 | gli_flow/design_intel/similarity_engine.py | 37 |
| 2 | gli_flow/synthetic/readiness_engine.py | 24, 115 |
| 1 | gli_flow/synthetic/failure_coverage_matrix.py | 43 |
| 2 | gli_flow/data_program/growth_tracker.py | 24, 111 |
| 1 | gli_flow/data_program/dashboard.py | 25 |
| 1 | gli_flow/data_program/campaign_planner.py | 51 |
| 1 | gli_flow/data_program/resolution_harvest.py | 33 |

## Scripts (Tooling)

| # | File | Line |
|---|------|------|
| 1 | scripts/migrate_sqlite_to_postgres.py | 201 |
| 1 | scripts/validate_postgres_migration.py | 93 |
| 1 | scripts/inject_test_failures.py | 9 |
| 1 | scripts/audit_run_trust.py | 10 |
| 1 | scripts/audit_intelligence_accuracy.py | 33 |
| 1 | scripts/design_intelligence_program.py | 40 |
| 1 | scripts/execution_intelligence_data_program.py | 54 |

## Tests

| # | File | Line |
|---|------|------|
| ~15 | tests/*.py | Various |
| ~5 | tests/failure_atlas/*.py | Various |
| ~3 | tests/integration/*.py | Various |

## Classification

- **Phase 2 target:** `gli_flow/database/sqlite.py` — DatabaseManager (orchestrator)
- **Phase 3 target:** `failure_atlas/repository.py` — FailureAtlasRepository
- **Not in scope for cutover (tooling/scripts):** analytics/, outputs/, scripts/, tests/
- **Not in scope (downstream consumers):** All failure_atlas/community_intelligence, ai_assistant, prediction modules — they read from FailureAtlasRepository which will use provider
- **Not in scope (data programs):** gli_flow/data_program/, gli_flow/design_intel/, gli_flow/synthetic/
- **Not in scope (migration scripts know SQLite):** sqlite_provider.py, migrations.py
