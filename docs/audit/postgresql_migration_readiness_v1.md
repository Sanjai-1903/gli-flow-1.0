# PostgreSQL Migration Readiness Audit v1

**Generated:** 2026-06-23
**Project:** GLI-FLOW ASIC
**Scope:** Full database audit for PostgreSQL (Supabase) migration

---

## 1. Database Discovery

### 1.1 Every `import sqlite3` Occurrence

| # | File | Line | Purpose |
|---|------|------|---------|
| 1 | `gli_flow/database/sqlite.py` | 2 | Core `DatabaseManager` — runs CRUD |
| 2 | `gli_flow/database/manager.py` | 1 | Legacy `DatabaseManager` + `get_runs()` |
| 3 | `gli_flow/database/migrations.py` | 2 | `MigrationEngine` — schema versioning + all migrations |
| 4 | `gli_flow/cli/main.py` | 310 | `db reset` — list tables, delete rows |
| 5 | `gli_flow/cli/main.py` | 326 | `db reset` — error handling |
| 6 | `gli_flow/cli/main.py` | 1871 | Support bundle — read `failure_atlas_entries` |
| 7 | `gli_flow/cli/main.py` | 1892 | Support bundle — read `telemetry_audit_log` |
| 8 | `gli_flow/telemetry/upload_queue.py` | 3 | `UploadQueue` — separate queue DB |
| 9 | `gli_flow/design_intel/feature_extractor.py` | 3 | `DesignFeatureExtractor` — design_features table |
| 10 | `gli_flow/design_intel/profile_engine.py` | 2 | `DesignProfileEngine` — design_profiles table |
| 11 | `gli_flow/design_intel/quality_audit.py` | 2 | `DatasetQualityAudit` — audit all tables |
| 12 | `gli_flow/design_intel/design_classifier.py` | 2 | `DesignClassifier` — reads design_profiles |
| 13 | `gli_flow/design_intel/similarity_engine.py` | 3 | `SimilarityEngine` — reads design features |
| 14 | `gli_flow/data_program/growth_tracker.py` | 1 | `AtlasGrowthTracker` — atlas entry statistics |
| 15 | `gli_flow/data_program/dashboard.py` | 3 | `DatasetDashboard` — dataset metrics |
| 16 | `gli_flow/data_program/campaign_planner.py` | 3 | `SyntheticCampaignPlanner` — coverage analysis |
| 17 | `gli_flow/data_program/resolution_harvest.py` | 3 | `ResolutionHarvestEngine` — resolution pairs |
| 18 | `gli_flow/synthetic/readiness_engine.py` | 1 | `CoverageEngine` — failure coverage metrics |
| 19 | `gli_flow/synthetic/failure_coverage_matrix.py` | 4 | `FailureCoverageMatrix` — coverage matrix |
| 20 | `gli_flow/infrastructure/repair_actions.py` | 3 | `SchemaMigrationRepair` — DB repair actions |
| 21 | `failure_atlas/repository.py` | 4 | `FailureAtlasRepository` — failure_atlas_entries CRUD |
| 22 | `failure_atlas/ai_assistant/feedback.py` | 2 | `FeedbackEntry` — AI feedback CRUD |
| 23 | `failure_atlas/ai_assistant/resolution_capture.py` | 2 | `ResolutionCapture` — resolution CRUD |
| 24 | `failure_atlas/community_intelligence/escalation.py` | 3 | `CommunityEscalation` — escalation CRUD |
| 25 | `failure_atlas/community_intelligence/telemetry.py` | 1 | `EscalationTelemetry` — community telemetry |
| 26 | `failure_atlas/community_intelligence/audit.py` | 3 | `TelemetryAuditLog` — audit log |
| 27 | `failure_atlas/community_intelligence/dataset.py` | 2 | `UnknownFailureDataset` — unknown failures |
| 28 | `failure_atlas/community_intelligence/health.py` | inline | Community health checks |
| 29 | `failure_atlas/community_intelligence/export.py` | 7 | `TelemetryExporter` / `PrivacyValidator` |
| 30 | `failure_atlas/community_intelligence/snapshot.py` | inline | `DatasetSnapshot` — snapshot creation |
| 31 | `failure_atlas/community_intelligence/replay.py` | inline | `TelemetryReplayEngine` — data replay |
| 32 | `failure_atlas/run_trust_engine.py` | 1 | `RunTrustEngine` — trust score computation |
| 33 | `intelligence/warehouse.py` | 2 | `TelemetryWarehouse` — execution/recommendation records |
| 34 | `intelligence/recommendation_engine.py` | 8 | `RecommendationEngine` |
| 35 | `cloud_ingestion/database.py` | 3 | `IngestionDatabase` — cloud-side SQLite |
| 36 | `backend/server.py` | 13 | FastAPI backend — all REST endpoints |
| 37 | `outputs/execution_history/history_api.py` | 1 | Legacy `ExecutionHistoryAPI` |
| 38 | `outputs/execution_history/live_status.py` | 1 | Legacy `LiveExecutionStatus` |
| 39 | `outputs/metrics/qor_api.py` | 1 | Legacy QOR metrics |

### 1.2 Every Database Connection Point

| File | Line | Class/Function | DB Path Resolution |
|------|------|----------------|-------------------|
| `gli_flow/database/sqlite.py` | 16 | `DatabaseManager.__init__()` | `_get_db_path()` |
| `gli_flow/database/manager.py` | 12 | `DatabaseManager.execute_query()` | Constructor arg `db_path` |
| `gli_flow/database/manager.py` | 23 | `get_runs()` | Function arg `db_path` |
| `gli_flow/database/migrations.py` | 556 | `MigrationEngine.__init__()` | `_get_db_path()` |
| `failure_atlas/repository.py` | 37 | `FailureAtlasRepository.__init__()` | `_get_db_path()` |
| `backend/server.py` | 48 | `get_connection()` | `_get_db_path()` |
| `gli_flow/cli/main.py` | 312 | `db reset` inline | `db_path` from args |
| `gli_flow/cli/main.py` | 1872 | Support bundle inline | `db_path` from args/env |
| `gli_flow/cli/main.py` | 1893 | Support bundle inline | `db_path` from args/env |
| `cloud_ingestion/database.py` | 90 | `IngestionDatabase._get_connection()` | `config.database.url` (sqlite:///path) |
| `gli_flow/telemetry/upload_queue.py` | 43 | `UploadQueue._get_connection()` | `~/.gli-flow/upload_queue.db` |
| `outputs/execution_history/history_api.py` | 11 | `ExecutionHistoryAPI.__init__()` | Hardcoded `"gli_flow.db"` |
| `outputs/execution_history/live_status.py` | 11 | `LiveExecutionStatus.__init__()` | Hardcoded `"gli_flow.db"` |
| `outputs/metrics/qor_api.py` | 9 | `get_connection()` | Hardcoded `"gli_flow.db"` |

### 1.3 Every DB Helper / Repository Class

| File | Class | Table(s) | Pattern |
|------|-------|----------|---------|
| `gli_flow/database/sqlite.py` | `DatabaseManager` | `runs` | Direct cursor methods |
| `gli_flow/database/manager.py` | `DatabaseManager` | `runs` | Direct cursor (legacy) |
| `failure_atlas/repository.py` | `FailureAtlasRepository` | `failure_atlas_entries`, `execution_intelligence` | `_fetchone`, `_fetchall`, `_execute`, `_raw_execute` helpers |
| `gli_flow/resolution_intelligence/repository.py` | `ResolutionRepository` | `resolution_patterns`, `resolution_feedback` | Direct cursor on injected `conn` |
| `cloud_ingestion/database.py` | `IngestionDatabase` | `telemetry_events`, `failure_atlas_events`, `upload_audit`, `consent_records` | Direct connection per op |
| `gli_flow/telemetry/upload_queue.py` | `UploadQueue` | `upload_queue` | Direct connection per op |
| `intelligence/warehouse.py` | `TelemetryWarehouse` | `telemetry_execution_records`, `telemetry_recommendation_records` | Direct connection per op |
| `failure_atlas/community_intelligence/audit.py` | `TelemetryAuditLog` | `telemetry_audit_log` | Direct connection per op |
| `failure_atlas/community_intelligence/telemetry.py` | `EscalationTelemetry` | `community_telemetry` | Direct connection per op |
| `failure_atlas/community_intelligence/dataset.py` | `UnknownFailureDataset` | `community_unknown_dataset` | Direct connection per op |
| `failure_atlas/community_intelligence/escalation.py` | `CommunityEscalation` | `community_escalations` | Direct connection per op |
| `failure_atlas/ai_assistant/feedback.py` | `FeedbackEntry` | `ai_investigation_feedback` | Direct connection per op |
| `failure_atlas/ai_assistant/resolution_capture.py` | `ResolutionCapture` | `ai_resolution_capture` | Direct connection per op |
| `gli_flow/design_intel/feature_extractor.py` | `DesignFeatureExtractor` | `design_features` | Direct connection per op |
| `gli_flow/design_intel/profile_engine.py` | `DesignProfileEngine` | `design_profiles` | Direct connection per op |

### 1.4 Migration System

| Component | File | Lines | Details |
|-----------|------|-------|---------|
| `RUNS_MIGRATIONS` | `migrations.py` | 35–98 | 8 migrations (v1–v8) for `runs` table |
| `FAILURE_ATLAS_MIGRATIONS` | `migrations.py` | 100–360 | 36 migrations (v1–v36) for failure atlas + related tables |
| `BETA_MIGRATIONS` | `migrations.py` | 363–418 | 3 migrations for feedback, journey, tracking |
| `RESOLUTION_MIGRATIONS` | `migrations.py` | 644–646 | Subset v31+ from FAILURE_ATLAS_MIGRATIONS |
| `MigrationEngine` | `migrations.py` | 553–641 | State + migrate + repair + validate |
| `migrate_if_needed()` | `migrations.py` | 656–667 | Auto-migrate all sources at startup |
| `_get_db_path()` | `migrations.py` | 486–501 | DB path resolution logic |
| `EXPECTED_COLUMNS` | `migrations.py` | 420–483 | Column validation dict for 8 tables |

### 1.5 Tables Created Outside Migration Engine (Auto-Init)

| Table | File | Line | Init Location |
|-------|------|------|---------------|
| `telemetry_audit_log` | `failure_atlas/community_intelligence/audit.py` | 9 | `TelemetryAuditLog._ensure_table()` |
| `design_profiles` | `gli_flow/design_intel/profile_engine.py` | 62 | `DesignProfileEngine._init_tables()` |
| `design_features` | `gli_flow/design_intel/feature_extractor.py` | 60 | `DesignFeatureExtractor._init_tables()` |
| `telemetry_execution_records` | `intelligence/warehouse.py` | 32 | `TelemetryWarehouse._init_tables()` |
| `telemetry_recommendation_records` | `intelligence/warehouse.py` | 44 | `TelemetryWarehouse._init_tables()` |
| `upload_queue` | `gli_flow/telemetry/upload_queue.py` | 13 | `UploadQueue._ensure_table()` (separate DB) |

### 1.6 Cloud Ingestion Tables (Separate Database)

| Table | File | Line | Details |
|-------|------|------|---------|
| `telemetry_events` | `cloud_ingestion/database.py` | 11 | Ingestion server, SQLite |
| `failure_atlas_events` | `cloud_ingestion/database.py` | 26 | Ingestion server, SQLite |
| `upload_audit` | `cloud_ingestion/database.py` | 43 | Ingestion server, SQLite |
| `consent_records` | `cloud_ingestion/database.py` | 57 | Ingestion server, SQLite |

---

## 2. Database Path Audit

### 2.1 Primary Database

| Property | Value |
|----------|-------|
| **Default path** | `~/.gli_flow/gli_flow.db` |
| **Env override** | `GLI_FLOW_DB` or `GLI_FLOW_DB_PATH` |
| **Fallback** | `$PWD/gli_flow.db` |
| **Resolution code** | `gli_flow/database/migrations.py:486–501` (`_get_db_path()`) |

### 2.2 Secondary Databases

| DB | Default Path | Used By | Operations |
|----|-------------|---------|------------|
| **Upload queue** | `~/.gli-flow/upload_queue.db` | `UploadQueue` | enqueue, dequeue, mark_completed, mark_failed, flush, stats |
| **Cloud ingestion** | `sqlite:///` from config or `/tmp/cloud_ingestion_dev.db` | `IngestionDatabase` | insert telemetry, failures, audit, consent |

### 2.3 Legacy Hardcoded Paths

| File | Path | Status |
|------|------|--------|
| `outputs/execution_history/history_api.py:4` | `"gli_flow.db"` (CWD) | Deprecated |
| `outputs/execution_history/live_status.py:4` | `"gli_flow.db"` (CWD) | Deprecated |
| `outputs/metrics/qor_api.py:4` | `"gli_flow.db"` (CWD) | Deprecated |

### 2.4 Data Flow Trace

```
Component          → DB Path              → Read Ops             → Write Ops
────────────────────────────────────────────────────────────────────────────
CLI (main.py)      → _get_db_path()       → sqlite_master,        → DELETE FROM runs,
                                            failure_atlas_entries,   DELETE FROM
                                            telemetry_audit_log      failure_atlas_entries
FlowOrchestrator   → _get_db_path()       → runs,                 → INSERT/UPDATE runs,
                                            failure_atlas_entries    INSERT failure_atlas
DatabaseManager    → _get_db_path()       → runs                  → INSERT/UPDATE runs
FailureAtlasRepo   → _get_db_path()       → failure_atlas_entries → INSERT/UPDATE/DELETE
ResolutionRepo     → conn (injected)      → resolution_patterns,  → INSERT/UPDATE/DELETE
                                            resolution_feedback
Backend API        → _get_db_path()       → ALL tables            → INSERT/UPDATE
TelemetryWarehouse → _get_db_path()       → telemetry_exec/rec    → INSERT
UploadQueue        → ~/.gli-flow/queue.db → upload_queue          → INSERT/UPDATE/DELETE
IngestionDatabase  → config URL           → telemetry_events,     → INSERT
                                            failure_atlas_events,
                                            upload_audit,
                                            consent_records
```

---

## 3. Table Inventory

### 3.1 `runs` — Primary run records

| Column | Type | Constraints | Migrated |
|--------|------|-------------|----------|
| run_id | TEXT | PRIMARY KEY | v1 |
| design_name | TEXT | NOT NULL | v1 |
| status | TEXT | DEFAULT 'PENDING' | v1 |
| current_stage | TEXT | DEFAULT 'INITIALIZING' | v1 |
| progress | INTEGER | DEFAULT 0 | v1 |
| wns | REAL | | v1 |
| tns | REAL | | v1 |
| hold_wns | REAL | | v1 |
| hold_tns | REAL | | v1 |
| utilization | REAL | | v1 |
| runtime_sec | REAL | | v1 |
| cell_count | INTEGER | | v1 |
| qor_score | REAL | | v1 |
| timestamp | TEXT | DEFAULT datetime('now') | v1 |
| run_dir | TEXT | | v1 |
| regression | INTEGER | DEFAULT 0 | v1 |
| drc_violations | INTEGER | | v1 |
| drc_magic_violations | INTEGER | | v1 |
| drc_klayout_violations | INTEGER | | v1 |
| drc_is_clean | INTEGER | DEFAULT 0 | v1 |
| lvs_result | TEXT | | v1 |
| lvs_is_clean | INTEGER | DEFAULT 0 | v1 |
| setup_wns_ns | REAL | | v1 |
| hold_whs_ns | REAL | | v1 |
| signoff_setup_pass | INTEGER | DEFAULT 0 | v1 |
| signoff_hold_pass | INTEGER | DEFAULT 0 | v1 |
| signoff_gate_json | TEXT | | v1 |
| tapeout_ready | INTEGER | DEFAULT 0 | v1 |
| created_at | TEXT | | v2 |
| updated_at | TEXT | | v3 |
| tags | TEXT | | v4 |
| is_important | INTEGER | DEFAULT 0 | v5 |
| important_marked_at | TEXT | | v5 |
| important_source | TEXT | | v5 |
| implementation_status | TEXT | DEFAULT 'NOT_STARTED' | v6 |
| signoff_status | TEXT | DEFAULT 'NOT_RUN' | v6 |
| implementation_score | REAL | | v6 |
| signoff_score | REAL | | v6 |
| root_cause_summary | TEXT | | v6 |
| llm_investigation_available | INTEGER | DEFAULT 0 | v7 |
| llm_investigation_status | TEXT | | v7 |
| llm_investigation_summary | TEXT | | v7 |
| llm_investigation_timestamp | TEXT | | v7 |
| llm_investigation_failed_attempts | TEXT | DEFAULT '{"attempts":[]}' | v8 |

**Indexes:** None explicitly created (PRIMARY KEY index on run_id)
**Foreign Keys:** None
**Row count source:** Not available (no production data inspected)

### 3.2 `failure_atlas_entries` — Failure records

| Column | Type | Constraints | Migrated |
|--------|------|-------------|----------|
| id | TEXT | PRIMARY KEY | v1 |
| run_id | TEXT | NOT NULL | v1 |
| failure_id | TEXT | | v1 |
| failure_type | TEXT | NOT NULL | v1 |
| severity | TEXT | NOT NULL | v1 |
| title | TEXT | | v1 |
| description | TEXT | | v1 |
| recommended_fix | TEXT | | v1 |
| confidence | REAL | DEFAULT 0.8 | v1 |
| signature | TEXT | | v1 |
| domain | TEXT | | v1 |
| category | TEXT | | v1 |
| evidence | TEXT | | v1 |
| detected_at | TEXT | DEFAULT datetime('now') | v1 |
| created_at | TEXT | DEFAULT datetime('now') | v1 |
| parent_run_id | TEXT | | v1, v2 |
| fix_applied | INTEGER | DEFAULT 0 | v1 |
| fix_type | TEXT | | v1 |
| fix_description | TEXT | | v1 |
| fix_run_id | TEXT | | v1 |
| before_metrics | TEXT | | v1, v3 |
| after_metrics | TEXT | | v1, v4 |
| resolution_confidence | TEXT | | v1, v5 |
| entry_level | TEXT | DEFAULT 'FAILURE' | v7 |
| failure_hash | TEXT | | v8 |
| tool_name | TEXT | | v9 |
| tool_version | TEXT | | v10 |
| tool_stage | TEXT | | v11 |
| first_seen | TEXT | | v12 |
| last_seen | TEXT | | v13 |
| occurrence_count | INTEGER | DEFAULT 1 | v14 |
| environment_fingerprint | TEXT | | v15 |
| resolution_attempts | INTEGER | DEFAULT 0 | v16 |
| resolution_success_rate | REAL | DEFAULT 0.0 | v17 |
| regression_detected | INTEGER | DEFAULT 0 | v18 |
| artifact_snapshot | TEXT | | v19 |
| execution_snapshot | TEXT | | v20 |
| timing_snapshot | TEXT | | v21 |
| utilization_snapshot | TEXT | | v22 |
| congestion_snapshot | TEXT | | v23 |
| runtime_snapshot | TEXT | | v24 |
| detection_classification | TEXT | DEFAULT 'UNVERIFIED' | v35 |
| design_name | TEXT | DEFAULT '' | v36 |

**Indexes:**
- `idx_fa_unique_run_type_sig` — UNIQUE on (run_id, failure_type, signature) (v25)

**Foreign Keys:** None (run_id references runs.run_id logically)

### 3.3 `schema_version` — Migration tracker

| Column | Type | Constraints |
|--------|------|-------------|
| source | TEXT | PRIMARY KEY (composite) |
| version | INTEGER | PRIMARY KEY (composite) |
| applied_at | TEXT | DEFAULT datetime('now') |
| description | TEXT | |

### 3.4 `ai_investigation_feedback`

| Column | Type | Constraints |
|--------|------|-------------|
| id | TEXT | PRIMARY KEY |
| investigation_id | TEXT | NOT NULL |
| feedback_type | TEXT | NOT NULL |
| resolved | INTEGER | DEFAULT 0 |
| comment | TEXT | DEFAULT '' |
| created_at | TEXT | NOT NULL |
| run_id | TEXT | DEFAULT '' |
| failure_type | TEXT | DEFAULT '' |

**Indexes:** `idx_ai_feedback_investigation`, `idx_ai_feedback_failure`

### 3.5 `ai_resolution_capture`

| Column | Type | Constraints |
|--------|------|-------------|
| id | TEXT | PRIMARY KEY |
| investigation_id | TEXT | NOT NULL |
| failure_type | TEXT | NOT NULL |
| tool | TEXT | NOT NULL |
| stage | TEXT | DEFAULT '' |
| fix_description | TEXT | NOT NULL |
| resolution_outcome | TEXT | DEFAULT '' |
| design_name | TEXT | DEFAULT '' |
| pdk | TEXT | DEFAULT '' |
| metrics_before | TEXT | DEFAULT '{}' |
| metrics_after | TEXT | DEFAULT '{}' |
| created_at | TEXT | NOT NULL |

**Indexes:** `idx_ai_resolution_failure`, `idx_ai_resolution_investigation`

### 3.6 `community_escalations`

| Column | Type | Constraints |
|--------|------|-------------|
| id | TEXT | PRIMARY KEY |
| run_id | TEXT | DEFAULT '' |
| failure_type | TEXT | NOT NULL |
| tool | TEXT | DEFAULT '' |
| stage | TEXT | DEFAULT '' |
| status | TEXT | NOT NULL DEFAULT 'open' |
| consent_given | INTEGER | DEFAULT 0 |
| consent_timestamp | TEXT | DEFAULT '' |
| bharatcode_submission_id | TEXT | DEFAULT '' |
| bharatcode_status | TEXT | DEFAULT '' |
| ai_summary | TEXT | DEFAULT '' |
| user_notes | TEXT | DEFAULT '' |
| engineer_response | TEXT | DEFAULT '{}' |
| atlas_id_created | TEXT | DEFAULT '' |
| created_at | TEXT | NOT NULL |
| sent_at | TEXT | DEFAULT '' |
| resolved_at | TEXT | DEFAULT '' |

**Indexes:** `idx_esc_failure_type`, `idx_esc_status`, `idx_esc_created`

### 3.7 `community_telemetry`

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| event | TEXT | NOT NULL |
| escalation_id | TEXT | DEFAULT '' |
| failure_type | TEXT | DEFAULT '' |
| tool | TEXT | DEFAULT '' |
| atlas_id | TEXT | DEFAULT '' |
| details | TEXT | DEFAULT '{}' |
| created_at | TEXT | NOT NULL |

**Indexes:** `idx_ct_event`, `idx_ct_esc`

### 3.8 `community_unknown_dataset`

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| tool | TEXT | NOT NULL |
| failure_type | TEXT | NOT NULL |
| signature | TEXT | DEFAULT '' |
| frequency | INTEGER | DEFAULT 1 |
| ai_helpfulness | TEXT | DEFAULT 'unknown' |
| resolution_outcome | TEXT | DEFAULT '' |
| consent_given | INTEGER | DEFAULT 0 |
| escalation_id | TEXT | DEFAULT '' |
| last_seen | TEXT | NOT NULL |

**Indexes:** `idx_ud_failure`, `idx_ud_tool`, `idx_ud_freq`

### 3.9 `resolution_patterns`

| Column | Type | Constraints |
|--------|------|-------------|
| id | TEXT | PRIMARY KEY |
| failure_fingerprint | TEXT | NOT NULL |
| failure_type | TEXT | NOT NULL |
| root_cause | TEXT | |
| resolution | TEXT | NOT NULL |
| resolution_type | TEXT | |
| success_count | INTEGER | DEFAULT 0 |
| failure_count | INTEGER | DEFAULT 0 |
| confidence | REAL | DEFAULT 0.0 |
| first_seen | TEXT | |
| last_seen | TEXT | |
| created_at | TEXT | DEFAULT datetime('now') |
| updated_at | TEXT | DEFAULT datetime('now') |
| unique_runs | INTEGER | DEFAULT 0 |
| unique_designs | INTEGER | DEFAULT 0 |
| engineer_confirmations | INTEGER | DEFAULT 0 |
| contradictory_reports | INTEGER | DEFAULT 0 |
| trust_score | REAL | DEFAULT 0.0 |
| trust_level | TEXT | DEFAULT 'UNVERIFIED' |
| trust_reason | TEXT | |
| tracked_run_ids | TEXT | DEFAULT '[]' |
| tracked_design_names | TEXT | DEFAULT '[]' |

**Indexes:** `idx_rp_fingerprint`, `idx_rp_type`, `idx_rp_confidence`

### 3.10 `resolution_feedback`

| Column | Type | Constraints |
|--------|------|-------------|
| id | TEXT | PRIMARY KEY |
| pattern_id | TEXT | NOT NULL |
| run_id | TEXT | NOT NULL |
| feedback_type | TEXT | NOT NULL |
| created_at | TEXT | DEFAULT datetime('now') |

**Indexes:** `idx_rf_pattern`, `idx_rf_run`

### 3.11 `execution_intelligence`

| Column | Type | Constraints |
|--------|------|-------------|
| id | TEXT | PRIMARY KEY |
| event_type | TEXT | NOT NULL |
| tool | TEXT | NOT NULL |
| stage | TEXT | NOT NULL |
| severity | TEXT | NOT NULL |
| fingerprint | TEXT | NOT NULL |
| timestamp | TEXT | NOT NULL |
| failure_context | TEXT | NOT NULL DEFAULT '{}' |
| root_cause_analysis | TEXT | NOT NULL DEFAULT '{}' |
| resolution | TEXT | NOT NULL DEFAULT '{}' |
| trust_score | REAL | DEFAULT 0.0 |
| outcome | TEXT | NOT NULL |

**Indexes:** `idx_ei_fingerprint`, `idx_ei_event_type`

### 3.12 `feedback_records`

| Column | Type | Constraints |
|--------|------|-------------|
| id | TEXT | PRIMARY KEY |
| feedback_type | TEXT | NOT NULL |
| title | TEXT | DEFAULT '' |
| description | TEXT | DEFAULT '' |
| gli_version | TEXT | DEFAULT '' |
| os | TEXT | DEFAULT '' |
| tool_versions | TEXT | DEFAULT '{}' |
| recent_run_id | TEXT | DEFAULT '' |
| failure_fingerprint | TEXT | DEFAULT '' |
| telemetry_health_summary | TEXT | DEFAULT '{}' |
| priority_score | REAL | DEFAULT 0.0 |
| priority_level | TEXT | DEFAULT 'MEDIUM' |
| status | TEXT | DEFAULT 'open' |
| created_at | TEXT | DEFAULT datetime('now') |
| updated_at | TEXT | DEFAULT datetime('now') |

**Indexes:** `idx_feedback_type`, `idx_feedback_status`, `idx_feedback_priority`, `idx_feedback_created`

### 3.13 `user_journey_events`

| Column | Type | Constraints |
|--------|------|-------------|
| id | TEXT | PRIMARY KEY |
| session_id | TEXT | DEFAULT '' |
| stage | TEXT | NOT NULL |
| event_type | TEXT | DEFAULT '' |
| details | TEXT | DEFAULT '{}' |
| duration_sec | REAL | DEFAULT 0.0 |
| created_at | TEXT | DEFAULT datetime('now') |

**Indexes:** `idx_journey_session`, `idx_journey_stage`, `idx_journey_created`

### 3.14 `resolution_tracking`

| Column | Type | Constraints |
|--------|------|-------------|
| id | TEXT | PRIMARY KEY |
| run_id | TEXT | DEFAULT '' |
| failure_fingerprint | TEXT | DEFAULT '' |
| resolution_suggested | TEXT | DEFAULT '' |
| suggested_at | TEXT | DEFAULT datetime('now') |
| accepted_at | TEXT | |
| rejected_at | TEXT | |
| success_verified | INTEGER | DEFAULT 0 |
| failure_type | TEXT | DEFAULT '' |
| created_at | TEXT | DEFAULT datetime('now') |

**Indexes:** `idx_rt_run`, `idx_rt_fingerprint`, `idx_rt_success`

### 3.15 `telemetry_audit_log` (auto-init)

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| event_type | TEXT | NOT NULL |
| event_name | TEXT | DEFAULT '' |
| status | TEXT | NOT NULL |
| reason | TEXT | DEFAULT '' |
| payload_hash | TEXT | DEFAULT '' |
| recorded_at | TEXT | NOT NULL |

**Indexes:** `idx_tal_event_type`, `idx_tal_status`, `idx_tal_recorded`

### 3.16 `design_features` (auto-init)

| Column | Type | Constraints |
|--------|------|-------------|
| design_name | TEXT | PRIMARY KEY |
| fanout_histogram | TEXT | DEFAULT '[0,...]' |
| logic_depth | INTEGER | DEFAULT 0 |
| register_density | REAL | DEFAULT 0.0 |
| memory_density | REAL | DEFAULT 0.0 |
| dsp_density | REAL | DEFAULT 0.0 |
| combinational_depth | INTEGER | DEFAULT 0 |
| sequential_depth | INTEGER | DEFAULT 0 |
| created_at | TEXT | DEFAULT datetime('now') |

### 3.17 `design_profiles` (auto-init)

| Column | Type | Constraints |
|--------|------|-------------|
| design_name | TEXT | PRIMARY KEY |
| design_type | TEXT | DEFAULT 'unknown' |
| rtl_size | INTEGER | DEFAULT 0 |
| module_count | INTEGER | DEFAULT 0 |
| memory_ratio | REAL | DEFAULT 0.0 |
| control_ratio | REAL | DEFAULT 0.0 |
| compute_ratio | REAL | DEFAULT 0.0 |
| top_module | TEXT | DEFAULT '' |
| pdk | TEXT | DEFAULT 'sky130A' |
| clock_period_ns | REAL | DEFAULT 0.0 |
| expected_cell_count | INTEGER | DEFAULT 0 |
| classification | TEXT | DEFAULT '' |
| created_at | TEXT | DEFAULT datetime('now') |
| updated_at | TEXT | DEFAULT datetime('now') |

### 3.18 `telemetry_execution_records` (auto-init, warehouse)

| Column | Type | Constraints |
|--------|------|-------------|
| id | TEXT | PRIMARY KEY |
| failure | TEXT | |
| root_cause | TEXT | |
| resolution | TEXT | |
| trust_score | REAL | |
| telemetry_summary | TEXT | |
| outcome | TEXT | |
| created_at | TEXT | |

### 3.19 `telemetry_recommendation_records` (auto-init, warehouse)

| Column | Type | Constraints |
|--------|------|-------------|
| id | TEXT | PRIMARY KEY |
| recommendation_id | TEXT | |
| run_id | TEXT | |
| failure_type | TEXT | |
| recommendation | TEXT | |
| trust_level | REAL | |
| accepted | INTEGER | |
| rejected | INTEGER | |
| outcome | TEXT | |
| timestamp | TEXT | |

### 3.20 `upload_queue` (separate DB: `~/.gli-flow/upload_queue.db`)

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| destination | TEXT | NOT NULL |
| payload | TEXT | NOT NULL |
| status | TEXT | NOT NULL DEFAULT 'pending' |
| created_at | TEXT | NOT NULL |
| next_retry_at | TEXT | |
| retry_count | INTEGER | DEFAULT 0 |
| error_message | TEXT | |
| run_id | TEXT | |

**Indexes:** `idx_uq_status`, `idx_uq_next_retry`, `idx_uq_run_id`

### 3.21 Cloud Ingestion Tables (separate `IngestionDatabase`)

See `cloud_ingestion/database.py` for:

| Table | Type | PK |
|-------|------|----|
| `telemetry_events` | AUTOINCREMENT | id |
| `failure_atlas_events` | AUTOINCREMENT | id |
| `upload_audit` | AUTOINCREMENT | id |
| `consent_records` | AUTOINCREMENT | id |

---

## 4. Data Ownership Mapping

### 4.1 Component → Table → Operation Matrix

| Component | runs | failure_atlas_entries | resolution_patterns | schema_version | Other |
|-----------|------|----------------------|---------------------|----------------|-------|
| **CLI** (main.py) | R, D | R, D | — | — | telemetry_audit_log: R |
| **FlowOrchestrator** | R, W | R, W | — | — | — |
| **DatabaseManager** | R, W | — | — | — | — |
| **FailureAtlasRepository** | — | R, W, D | — | — | execution_intelligence: R, W |
| **ResolutionRepository** | — | R (via subquery) | R, W | — | resolution_feedback: R, W |
| **Backend API** | R | R | R | — | feedback_records: R, W; user_journey: R, W; resolution_tracking: R, W; audit_log: R |
| **TelemetryWarehouse** | — | — | — | — | telemetry_execution_records: W; telemetry_recommendation: W |
| **UploadQueue** | — | — | — | — | upload_queue: R, W, D |
| **DesignIntel** | — | R | — | — | design_features: R, W; design_profiles: R, W |
| **DataProgram** | R | R | — | — | — |
| **SyntheticEngine** | — | R | — | — | — |
| **MigrationEngine** | W (schema) | W (schema) | W (schema) | R, W | All tables: schema validation |
| **CommunityIntel** | — | — | — | — | telemetry_audit_log: R, W; community_telemetry: R, W; community_unknown: R, W; community_escalations: R, W |

**Legend:** R=Read, W=Write, D=Delete

---

## 5. PostgreSQL Compatibility Audit

### 5.1 SQLite-Specific Features Found

| # | Issue | File(s) | Line(s) | Impact | Migration Strategy |
|---|-------|---------|---------|--------|-------------------|
| 1 | **AUTOINCREMENT** (6 tables) | `upload_queue.py:14`, `audit.py:10`, `telemetry.py:8`, `dataset.py:8`, `cloud_ingestion/database.py:12,27,44,58`, `migrations.py:265,279` | Multiple | HIGH — PostgreSQL uses `SERIAL` or `IDENTITY` | Replace with `SERIAL PRIMARY KEY` or `GENERATED ALWAYS AS IDENTITY` |
| 2 | **INSERT OR REPLACE** | `failure_atlas/repository.py:116`, `design_intel/feature_extractor.py:187`, `profile_engine.py:175` | 116, 187, 175 | HIGH — PostgreSQL uses `ON CONFLICT ... DO UPDATE SET` (UPSERT) | Rewrite as `INSERT ... ON CONFLICT (pk) DO UPDATE SET ...` |
| 3 | **INSERT OR IGNORE** | `migrations.py:521,534,598,615` | 521, 534, 598, 615 | MEDIUM | Replace with `INSERT ... ON CONFLICT DO NOTHING` |
| 4 | **PRAGMA journal_mode=WAL** | `sqlite.py:18`, `migrations.py:558`, `repository.py:40`, `cloud_ingestion/database.py:93` | 18, 558, 40, 93 | CRITICAL — PostgreSQL has no PRAGMA | Remove — PostgreSQL handles concurrency natively |
| 5 | **PRAGMA synchronous=NORMAL** | `cloud_ingestion/database.py:94` | 94 | LOW | Remove |
| 6 | **PRAGMA table_info()** | `migrations.py:633` | 633 | MEDIUM — schema validation | Replace with `SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s` |
| 7 | **sqlite_master** | `migrations.py:509`, `cli/main.py:314` | 509, 314 | MEDIUM | Replace with `SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'` |
| 8 | **rowid usage** | `migrations.py:199–200` | 199-200 | HIGH — dedup migration uses `rowid` | Rewrite dedup logic using primary key or explicit uniqueness |
| 9 | **`lastrowid` usage** | `cloud_ingestion/database.py:185`, `upload_queue.py:60` | 185, 60 | MEDIUM — PostgreSQL uses `RETURNING` clause | Replace with `INSERT ... RETURNING id` |
| 10 | **JSON storage as TEXT** | All tables (JSON stored in TEXT columns) | Various | LOW — PostgreSQL has native `JSONB` | Migrate columns to `JSONB` for type safety and indexing |
| 11 | **Timestamp assumptions** | All tables use TEXT with `datetime('now')` defaults | Various | MEDIUM — PostgreSQL has native `TIMESTAMPTZ` | Migrate to `TIMESTAMPTZ` with `NOW()` or `CURRENT_TIMESTAMP` defaults |
| 12 | **Boolean stored as INTEGER** | `fix_applied`, `consent_given`, `drc_is_clean`, `regression_detected`, `is_important`, etc. | Various | LOW — PostgreSQL has native `BOOLEAN` | Migrate 0/1 INTEGER columns to `BOOLEAN` |
| 13 | **`LIKE` for search** | `failure_atlas/repository.py:189`, `resolution_intelligence/repository.py:111` | 189, 111 | LOW — supported in PostgreSQL | Keep as-is or migrate to `ILIKE` or `pg_trgm` |
| 14 | **`json_extract()` function** | `failure_atlas/repository.py:346-347` | 346-347 | MEDIUM — SQLite extension | Replace with PostgreSQL `jsonb_extract_path()` or `->`/`->>` operators |
| 15 | **`date()` function** | `failure_atlas/repository.py:361` | 361 | LOW | Replace with PostgreSQL `DATE()` or `::date` cast |
| 16 | **`COALESCE` with `datetime('now')`** | `resolution_intelligence/repository.py:60` | 60 | LOW | Replace with `COALESCE(?, NOW())` |
| 17 | **`check_same_thread=False`** | `cloud_ingestion/database.py:91` | 91 | LOW — PostgreSQL handles threading natively | Remove parameter |
| 18 | **`sqlite3.Row` row factory** | `repository.py:38`, `server.py:49`, `cloud_ingestion/database.py:92`, `upload_queue.py:45`, `warehouse.py:25` | 38, 49, 92, 45, 25 | MEDIUM — dict-like row access | Replace with `psycopg2.extras.RealDictCursor` or SQLAlchemy |
| 19 | **Multiple SQL statements per execute** | `migrations.py:586` (split by `;`) | 586 | LOW | Use separate executes or `psycopg2.extras.execute_values` |
| 20 | **`CREATE TABLE IF NOT EXISTS`** | Everywhere (52 occurrences) | Multiple | LOW — PostgreSQL supports `IF NOT EXISTS` | Keep as-is |

### 5.2 SQLite-Specific Features NOT Used (no issue)

- `ATTACH DATABASE` — not used
- `VIRTUAL TABLE` (FTS, etc.) — not used
- `RAISE(ROLLBACK)` triggers — not used
- `AUTOINCREMENT` on TEXT PKs — not used (UUIDs used instead)
- `SELECT ... WITHOUT ROWID` — not used

---

## 6. Risk Assessment

### 6.1 Risk Classification

| Risk | Count | Items |
|------|-------|-------|
| **CRITICAL** | 1 | PRAGMA usage (WAL) — must be removed |
| **HIGH** | 4 | AUTOINCREMENT → SERIAL, INSERT OR REPLACE → UPSERT, rowid usage, INSERT OR IGNORE |
| **MEDIUM** | 8 | sqlite_master queries, PRAGMA table_info, json_extract, sqlite3.Row, timestamp types, lastrowid → RETURNING, LIKE search patterns, boolean→BOOLEAN |
| **LOW** | 7 | PRAGMA synchronous=NORMAL, JSON storage format, check_same_thread, COALESCE date defaults, DATE() function, compound statements, CREATE IF NOT EXISTS |

### 6.2 Critical Risks Detail

**CRITICAL: PRAGMA journal_mode=WAL**
- 4 files use `PRAGMA journal_mode=WAL` immediately after connection
- PostgreSQL has WAL built-in and always enabled
- These PRAGMA calls will raise `psycopg2.errors.SyntaxError`
- **Fix:** Conditionally execute (only for SQLite) or remove in PostgreSQL provider

### 6.3 Migration Complexity by Table

| Table | Complexity | Reason |
|-------|-----------|--------|
| `schema_version` | LOW | Simple 4-column table |
| `runs` | HIGH | 44 columns, most queries use positional indexing |
| `failure_atlas_entries` | HIGH | 45 columns, UNIQUE index on 3 columns, DELETE with rowid |
| `resolution_patterns` | MEDIUM | 22 columns, triggers use upsert |
| `community_telemetry` | MEDIUM | AUTOINCREMENT → SERIAL |
| `upload_queue` | MEDIUM | AUTOINCREMENT + lastrowid |
| `cloud_ingestion.*` | MEDIUM | 4 tables with AUTOINCREMENT, separate DB |
| `telemetry_audit_log` | MEDIUM | AUTOINCREMENT |
| `design_profiles` | LOW | Simple PK, INSERT OR REPLACE |
| `design_features` | LOW | Simple PK, INSERT OR REPLACE |
| `telemetry_execution_records` | LOW | Simple inserts |

### 6.4 Overall Assessment

**Total files requiring changes:** ~45 Python files import sqlite3
**Total distinct tables:** 21 (across 3 database files)
**Total critical/high issues:** 5
**Total medium issues:** 8
**Total low issues:** 7

**Verdict:** Migration is feasible but requires careful abstraction layer design. The codebase has no ORM, making every raw SQL call a potential breakage point. The recommended approach is a DatabaseProvider interface with SQLiteProvider (existing) and PostgresProvider implementations, rather than a big-bang rewrite.
