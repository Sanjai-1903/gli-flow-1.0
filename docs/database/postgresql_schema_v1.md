# PostgreSQL Schema Design v1

**Generated:** 2026-06-23
**Source:** Evidence-based mapping from SQLite tables documented in `docs/audit/postgresql_migration_readiness_v1.md`

---

## Mapping Rules

1. Every SQLite table maps to a PostgreSQL table
2. `TEXT` with JSON content → `JSONB` where semantically JSON
3. `INTEGER` booleans (0/1) → `BOOLEAN`
4. `TEXT` timestamps with `datetime('now')` → `TIMESTAMPTZ` with `NOW()`
5. `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY` (or `BIGSERIAL`)
6. `TEXT PRIMARY KEY` (UUIDs) → `UUID PRIMARY KEY` with `gen_random_uuid()`
7. Indexes, unique constraints, foreign keys preserved
8. No tables invented — only those found in audit

---

## 1. `schema_version` — Migration tracking

```sql
CREATE TABLE IF NOT EXISTS schema_version (
    source      TEXT        NOT NULL,
    version     INTEGER     NOT NULL,
    applied_at  TIMESTAMPTZ DEFAULT NOW(),
    description TEXT,
    PRIMARY KEY (source, version)
);
```

---

## 2. `runs` — Primary run records

```sql
CREATE TABLE IF NOT EXISTS runs (
    run_id                          TEXT        PRIMARY KEY,
    design_name                     TEXT        NOT NULL,
    status                          TEXT        DEFAULT 'PENDING',
    current_stage                   TEXT        DEFAULT 'INITIALIZING',
    progress                        INTEGER     DEFAULT 0,
    wns                             DOUBLE PRECISION,
    tns                             DOUBLE PRECISION,
    hold_wns                        DOUBLE PRECISION,
    hold_tns                        DOUBLE PRECISION,
    utilization                     DOUBLE PRECISION,
    runtime_sec                     DOUBLE PRECISION,
    cell_count                      INTEGER,
    qor_score                       DOUBLE PRECISION,
    timestamp                       TIMESTAMPTZ DEFAULT NOW(),
    run_dir                         TEXT,
    regression                      INTEGER     DEFAULT 0,
    drc_violations                  INTEGER,
    drc_magic_violations            INTEGER,
    drc_klayout_violations          INTEGER,
    drc_is_clean                    BOOLEAN     DEFAULT FALSE,
    lvs_result                      TEXT,
    lvs_is_clean                    BOOLEAN     DEFAULT FALSE,
    setup_wns_ns                    DOUBLE PRECISION,
    hold_whs_ns                     DOUBLE PRECISION,
    signoff_setup_pass              BOOLEAN     DEFAULT FALSE,
    signoff_hold_pass               BOOLEAN     DEFAULT FALSE,
    signoff_gate_json               JSONB,
    tapeout_ready                   BOOLEAN     DEFAULT FALSE,
    created_at                      TIMESTAMPTZ,
    updated_at                      TIMESTAMPTZ,
    tags                            JSONB,
    is_important                    BOOLEAN     DEFAULT FALSE,
    important_marked_at             TIMESTAMPTZ,
    important_source                TEXT,
    implementation_status           TEXT        DEFAULT 'NOT_STARTED',
    signoff_status                  TEXT        DEFAULT 'NOT_RUN',
    implementation_score            DOUBLE PRECISION,
    signoff_score                   DOUBLE PRECISION,
    root_cause_summary              TEXT,
    llm_investigation_available     BOOLEAN     DEFAULT FALSE,
    llm_investigation_status        TEXT,
    llm_investigation_summary       TEXT,
    llm_investigation_timestamp     TIMESTAMPTZ,
    llm_investigation_failed_attempts JSONB     DEFAULT '{"attempts":[]}'
);
```

---

## 3. `failure_atlas_entries` — Failure records

```sql
CREATE TABLE IF NOT EXISTS failure_atlas_entries (
    id                       UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id                   TEXT        NOT NULL,
    failure_id               TEXT,
    failure_type             TEXT        NOT NULL,
    severity                 TEXT        NOT NULL,
    title                    TEXT,
    description              TEXT,
    recommended_fix          JSONB,
    confidence               DOUBLE PRECISION DEFAULT 0.8,
    signature                TEXT,
    domain                   TEXT,
    category                 TEXT,
    evidence                 JSONB,
    detected_at              TIMESTAMPTZ DEFAULT NOW(),
    created_at               TIMESTAMPTZ DEFAULT NOW(),
    parent_run_id            TEXT,
    fix_applied              BOOLEAN     DEFAULT FALSE,
    fix_type                 TEXT,
    fix_description          TEXT,
    fix_run_id               TEXT,
    before_metrics           JSONB,
    after_metrics            JSONB,
    resolution_confidence    TEXT,
    entry_level              TEXT        DEFAULT 'FAILURE',
    failure_hash             TEXT,
    tool_name                TEXT,
    tool_version             TEXT,
    tool_stage               TEXT,
    first_seen               TIMESTAMPTZ,
    last_seen                TIMESTAMPTZ,
    occurrence_count         INTEGER     DEFAULT 1,
    environment_fingerprint  TEXT,
    resolution_attempts      INTEGER     DEFAULT 0,
    resolution_success_rate  DOUBLE PRECISION DEFAULT 0.0,
    regression_detected      BOOLEAN     DEFAULT FALSE,
    artifact_snapshot        JSONB,
    execution_snapshot       JSONB,
    timing_snapshot          JSONB,
    utilization_snapshot     JSONB,
    congestion_snapshot      JSONB,
    runtime_snapshot         JSONB,
    detection_classification TEXT        DEFAULT 'UNVERIFIED',
    design_name              TEXT        DEFAULT ''
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_fae_run_type_sig
    ON failure_atlas_entries(run_id, failure_type, signature)
    WHERE signature IS NOT NULL;
```

Notes:
- UUID PK replaces TEXT UUID
- UNIQUE index is conditional (only when signature is not null) to match SQLite behavior
- All JSON-holding TEXT columns → JSONB

---

## 4. `ai_investigation_feedback`

```sql
CREATE TABLE IF NOT EXISTS ai_investigation_feedback (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id  TEXT        NOT NULL,
    feedback_type     TEXT        NOT NULL,
    resolved          BOOLEAN     DEFAULT FALSE,
    comment           TEXT        DEFAULT '',
    created_at        TIMESTAMPTZ NOT NULL,
    run_id            TEXT        DEFAULT '',
    failure_type      TEXT        DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_ai_feedback_investigation ON ai_investigation_feedback(investigation_id);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_failure ON ai_investigation_feedback(failure_type);
```

---

## 5. `ai_resolution_capture`

```sql
CREATE TABLE IF NOT EXISTS ai_resolution_capture (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id  TEXT        NOT NULL,
    failure_type      TEXT        NOT NULL,
    tool              TEXT        NOT NULL,
    stage             TEXT        DEFAULT '',
    fix_description   TEXT        NOT NULL,
    resolution_outcome TEXT       DEFAULT '',
    design_name       TEXT        DEFAULT '',
    pdk               TEXT        DEFAULT '',
    metrics_before    JSONB       DEFAULT '{}',
    metrics_after     JSONB       DEFAULT '{}',
    created_at        TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ai_resolution_failure ON ai_resolution_capture(failure_type);
CREATE INDEX IF NOT EXISTS idx_ai_resolution_investigation ON ai_resolution_capture(investigation_id);
```

---

## 6. `community_escalations`

```sql
CREATE TABLE IF NOT EXISTS community_escalations (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id                  TEXT        DEFAULT '',
    failure_type            TEXT        NOT NULL,
    tool                    TEXT        DEFAULT '',
    stage                   TEXT        DEFAULT '',
    status                  TEXT        NOT NULL DEFAULT 'open',
    consent_given           BOOLEAN     DEFAULT FALSE,
    consent_timestamp       TEXT        DEFAULT '',
    bharatcode_submission_id TEXT       DEFAULT '',
    bharatcode_status       TEXT        DEFAULT '',
    ai_summary              TEXT        DEFAULT '',
    user_notes              TEXT        DEFAULT '',
    engineer_response       JSONB       DEFAULT '{}',
    atlas_id_created        TEXT        DEFAULT '',
    created_at              TIMESTAMPTZ NOT NULL,
    sent_at                 TIMESTAMPTZ,
    resolved_at             TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_esc_failure_type ON community_escalations(failure_type);
CREATE INDEX IF NOT EXISTS idx_esc_status ON community_escalations(status);
CREATE INDEX IF NOT EXISTS idx_esc_created ON community_escalations(created_at);
```

---

## 7. `community_telemetry`

```sql
CREATE TABLE IF NOT EXISTS community_telemetry (
    id             SERIAL      PRIMARY KEY,
    event          TEXT        NOT NULL,
    escalation_id  TEXT        DEFAULT '',
    failure_type   TEXT        DEFAULT '',
    tool           TEXT        DEFAULT '',
    atlas_id       TEXT        DEFAULT '',
    details        JSONB       DEFAULT '{}',
    created_at     TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ct_event ON community_telemetry(event);
CREATE INDEX IF NOT EXISTS idx_ct_esc ON community_telemetry(escalation_id);
```

---

## 8. `community_unknown_dataset`

```sql
CREATE TABLE IF NOT EXISTS community_unknown_dataset (
    id                 SERIAL      PRIMARY KEY,
    tool               TEXT        NOT NULL,
    failure_type       TEXT        NOT NULL,
    signature          TEXT        DEFAULT '',
    frequency          INTEGER     DEFAULT 1,
    ai_helpfulness     TEXT        DEFAULT 'unknown',
    resolution_outcome TEXT        DEFAULT '',
    consent_given      BOOLEAN     DEFAULT FALSE,
    escalation_id      TEXT        DEFAULT '',
    last_seen          TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ud_failure ON community_unknown_dataset(failure_type);
CREATE INDEX IF NOT EXISTS idx_ud_tool ON community_unknown_dataset(tool);
CREATE INDEX IF NOT EXISTS idx_ud_freq ON community_unknown_dataset(frequency DESC);
```

---

## 9. `resolution_patterns`

```sql
CREATE TABLE IF NOT EXISTS resolution_patterns (
    id                     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    failure_fingerprint    TEXT        NOT NULL,
    failure_type           TEXT        NOT NULL,
    root_cause             TEXT,
    resolution             TEXT        NOT NULL,
    resolution_type        TEXT,
    success_count          INTEGER     DEFAULT 0,
    failure_count          INTEGER     DEFAULT 0,
    confidence             DOUBLE PRECISION DEFAULT 0.0,
    first_seen             TIMESTAMPTZ,
    last_seen              TIMESTAMPTZ,
    created_at             TIMESTAMPTZ DEFAULT NOW(),
    updated_at             TIMESTAMPTZ DEFAULT NOW(),
    unique_runs            INTEGER     DEFAULT 0,
    unique_designs         INTEGER     DEFAULT 0,
    engineer_confirmations INTEGER     DEFAULT 0,
    contradictory_reports  INTEGER     DEFAULT 0,
    trust_score            DOUBLE PRECISION DEFAULT 0.0,
    trust_level            TEXT        DEFAULT 'UNVERIFIED',
    trust_reason           TEXT,
    tracked_run_ids        JSONB       DEFAULT '[]',
    tracked_design_names   JSONB       DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_rp_fingerprint ON resolution_patterns(failure_fingerprint);
CREATE INDEX IF NOT EXISTS idx_rp_type ON resolution_patterns(failure_type);
CREATE INDEX IF NOT EXISTS idx_rp_confidence ON resolution_patterns(confidence DESC);
```

---

## 10. `resolution_feedback`

```sql
CREATE TABLE IF NOT EXISTS resolution_feedback (
    id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id     TEXT        NOT NULL,
    run_id         TEXT        NOT NULL,
    feedback_type  TEXT        NOT NULL,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rf_pattern ON resolution_feedback(pattern_id);
CREATE INDEX IF NOT EXISTS idx_rf_run ON resolution_feedback(run_id);
```

---

## 11. `execution_intelligence`

```sql
CREATE TABLE IF NOT EXISTS execution_intelligence (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type          TEXT        NOT NULL,
    tool                TEXT        NOT NULL,
    stage               TEXT        NOT NULL,
    severity            TEXT        NOT NULL,
    fingerprint         TEXT        NOT NULL,
    timestamp           TIMESTAMPTZ NOT NULL,
    failure_context     JSONB       NOT NULL DEFAULT '{}',
    root_cause_analysis JSONB       NOT NULL DEFAULT '{}',
    resolution          JSONB       NOT NULL DEFAULT '{}',
    trust_score         DOUBLE PRECISION DEFAULT 0.0,
    outcome             TEXT        NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ei_fingerprint ON execution_intelligence(fingerprint);
CREATE INDEX IF NOT EXISTS idx_ei_event_type ON execution_intelligence(event_type);
```

---

## 12. `feedback_records` — Beta operations

```sql
CREATE TABLE IF NOT EXISTS feedback_records (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_type           TEXT        NOT NULL,
    title                   TEXT        DEFAULT '',
    description             TEXT        DEFAULT '',
    gli_version             TEXT        DEFAULT '',
    os                      TEXT        DEFAULT '',
    tool_versions           JSONB       DEFAULT '{}',
    recent_run_id           TEXT        DEFAULT '',
    failure_fingerprint     TEXT        DEFAULT '',
    telemetry_health_summary JSONB      DEFAULT '{}',
    priority_score          DOUBLE PRECISION DEFAULT 0.0,
    priority_level          TEXT        DEFAULT 'MEDIUM',
    status                  TEXT        DEFAULT 'open',
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback_records(feedback_type);
CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback_records(status);
CREATE INDEX IF NOT EXISTS idx_feedback_priority ON feedback_records(priority_level);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON feedback_records(created_at);
```

---

## 13. `user_journey_events` — Beta operations

```sql
CREATE TABLE IF NOT EXISTS user_journey_events (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  TEXT        DEFAULT '',
    stage       TEXT        NOT NULL,
    event_type  TEXT        DEFAULT '',
    details     JSONB       DEFAULT '{}',
    duration_sec DOUBLE PRECISION DEFAULT 0.0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_journey_session ON user_journey_events(session_id);
CREATE INDEX IF NOT EXISTS idx_journey_stage ON user_journey_events(stage);
CREATE INDEX IF NOT EXISTS idx_journey_created ON user_journey_events(created_at);
```

---

## 14. `resolution_tracking` — Beta operations

```sql
CREATE TABLE IF NOT EXISTS resolution_tracking (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              TEXT        DEFAULT '',
    failure_fingerprint TEXT        DEFAULT '',
    resolution_suggested TEXT       DEFAULT '',
    suggested_at        TIMESTAMPTZ DEFAULT NOW(),
    accepted_at         TIMESTAMPTZ,
    rejected_at         TIMESTAMPTZ,
    success_verified    BOOLEAN     DEFAULT FALSE,
    failure_type        TEXT        DEFAULT '',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rt_run ON resolution_tracking(run_id);
CREATE INDEX IF NOT EXISTS idx_rt_fingerprint ON resolution_tracking(failure_fingerprint);
CREATE INDEX IF NOT EXISTS idx_rt_success ON resolution_tracking(success_verified);
```

---

## 15. `telemetry_audit_log` — Community intelligence (auto-init)

```sql
CREATE TABLE IF NOT EXISTS telemetry_audit_log (
    id           SERIAL      PRIMARY KEY,
    event_type   TEXT        NOT NULL,
    event_name   TEXT        DEFAULT '',
    status       TEXT        NOT NULL,
    reason       TEXT        DEFAULT '',
    payload_hash TEXT        DEFAULT '',
    recorded_at  TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tal_event_type ON telemetry_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_tal_status ON telemetry_audit_log(status);
CREATE INDEX IF NOT EXISTS idx_tal_recorded ON telemetry_audit_log(recorded_at);
```

---

## 16. `design_features` — Design intelligence (auto-init)

```sql
CREATE TABLE IF NOT EXISTS design_features (
    design_name        TEXT        PRIMARY KEY,
    fanout_histogram   JSONB       DEFAULT '[0,0,0,0,0,0,0,0,0,0]',
    logic_depth        INTEGER     DEFAULT 0,
    register_density   DOUBLE PRECISION DEFAULT 0.0,
    memory_density     DOUBLE PRECISION DEFAULT 0.0,
    dsp_density        DOUBLE PRECISION DEFAULT 0.0,
    combinational_depth INTEGER    DEFAULT 0,
    sequential_depth   INTEGER     DEFAULT 0,
    created_at         TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 17. `design_profiles` — Design intelligence (auto-init)

```sql
CREATE TABLE IF NOT EXISTS design_profiles (
    design_name        TEXT        PRIMARY KEY,
    design_type        TEXT        DEFAULT 'unknown',
    rtl_size           INTEGER     DEFAULT 0,
    module_count       INTEGER     DEFAULT 0,
    memory_ratio       DOUBLE PRECISION DEFAULT 0.0,
    control_ratio      DOUBLE PRECISION DEFAULT 0.0,
    compute_ratio      DOUBLE PRECISION DEFAULT 0.0,
    top_module         TEXT        DEFAULT '',
    pdk                TEXT        DEFAULT 'sky130A',
    clock_period_ns    DOUBLE PRECISION DEFAULT 0.0,
    expected_cell_count INTEGER    DEFAULT 0,
    classification     TEXT        DEFAULT '',
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 18. `telemetry_execution_records` — Intelligence warehouse (auto-init)

```sql
CREATE TABLE IF NOT EXISTS telemetry_execution_records (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    failure           TEXT,
    root_cause        TEXT,
    resolution        TEXT,
    trust_score       DOUBLE PRECISION,
    telemetry_summary JSONB,
    outcome           TEXT,
    created_at        TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_telemetry_exec_failure ON telemetry_execution_records(failure);
```

---

## 19. `telemetry_recommendation_records` — Intelligence warehouse (auto-init)

```sql
CREATE TABLE IF NOT EXISTS telemetry_recommendation_records (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id TEXT,
    run_id            TEXT,
    failure_type      TEXT,
    recommendation    TEXT,
    trust_level       DOUBLE PRECISION,
    accepted          BOOLEAN,
    rejected          BOOLEAN,
    outcome           TEXT,
    timestamp         TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_telemetry_rec_failure ON telemetry_recommendation_records(failure_type);
```

---

## 20. `upload_queue` — Separate database (kept separate for Railway)

```sql
CREATE TABLE IF NOT EXISTS upload_queue (
    id             SERIAL      PRIMARY KEY,
    destination    TEXT        NOT NULL,
    payload        JSONB       NOT NULL,
    status         TEXT        NOT NULL DEFAULT 'pending',
    created_at     TIMESTAMPTZ NOT NULL,
    next_retry_at  TIMESTAMPTZ,
    retry_count    INTEGER     DEFAULT 0,
    error_message  TEXT,
    run_id         TEXT
);

CREATE INDEX IF NOT EXISTS idx_uq_status ON upload_queue(status);
CREATE INDEX IF NOT EXISTS idx_uq_next_retry ON upload_queue(next_retry_at);
CREATE INDEX IF NOT EXISTS idx_uq_run_id ON upload_queue(run_id);
```

---

## 21. Cloud Ingestion Tables (Supabase Cloud, separate schema)

These tables are currently in a separate SQLite database (`cloud_ingestion`). For Supabase migration, they can remain in the same PostgreSQL database under a separate schema (e.g., `ingestion`).

```sql
CREATE SCHEMA IF NOT EXISTS ingestion;

CREATE TABLE IF NOT EXISTS ingestion.telemetry_events (
    id              SERIAL      PRIMARY KEY,
    run_id          TEXT        NOT NULL,
    tool            TEXT        NOT NULL,
    stage           TEXT        NOT NULL,
    event           TEXT        NOT NULL,
    design_name     TEXT,
    metrics         JSONB       DEFAULT '{}',
    details         JSONB,
    recorded_at     TIMESTAMPTZ NOT NULL,
    ingested_at     TIMESTAMPTZ NOT NULL,
    source_ip       TEXT,
    upload_batch_id TEXT
);

CREATE TABLE IF NOT EXISTS ingestion.failure_atlas_events (
    id              SERIAL      PRIMARY KEY,
    run_id          TEXT        NOT NULL,
    tool            TEXT        NOT NULL,
    stage           TEXT        NOT NULL,
    failure_type    TEXT        NOT NULL,
    error_text      TEXT,
    design_name     TEXT,
    design_category TEXT,
    log_excerpt     TEXT,
    frequency       INTEGER     DEFAULT 1,
    first_seen      TIMESTAMPTZ,
    last_seen       TIMESTAMPTZ,
    ingested_at     TIMESTAMPTZ NOT NULL,
    upload_batch_id TEXT
);

CREATE TABLE IF NOT EXISTS ingestion.upload_audit (
    id               SERIAL      PRIMARY KEY,
    run_id           TEXT        NOT NULL,
    batch_id         TEXT        NOT NULL,
    telemetry_count  INTEGER     DEFAULT 0,
    failures_count   INTEGER     DEFAULT 0,
    escalations_count INTEGER    DEFAULT 0,
    source_version   TEXT,
    client_ip        TEXT,
    status           TEXT        NOT NULL DEFAULT 'accepted',
    error_message    TEXT,
    ingested_at      TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS ingestion.consent_records (
    id               SERIAL      PRIMARY KEY,
    run_id           TEXT        NOT NULL,
    consent_given    BOOLEAN     NOT NULL DEFAULT FALSE,
    consent_timestamp TEXT,
    recorded_at      TIMESTAMPTZ NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_te_run_id ON ingestion.telemetry_events(run_id);
CREATE INDEX IF NOT EXISTS idx_te_event ON ingestion.telemetry_events(event);
CREATE INDEX IF NOT EXISTS idx_te_recorded ON ingestion.telemetry_events(recorded_at);
CREATE INDEX IF NOT EXISTS idx_fae_run_id ON ingestion.failure_atlas_events(run_id);
CREATE INDEX IF NOT EXISTS idx_fae_failure_type ON ingestion.failure_atlas_events(failure_type);
CREATE INDEX IF NOT EXISTS idx_fae_design_name ON ingestion.failure_atlas_events(design_name);
CREATE INDEX IF NOT EXISTS idx_ua_run_id ON ingestion.upload_audit(run_id);
CREATE INDEX IF NOT EXISTS idx_ua_status ON ingestion.upload_audit(status);
CREATE INDEX IF NOT EXISTS idx_cr_run_id ON ingestion.consent_records(run_id);
```

---

## Schema Summary

| # | Table | Schema | PK Type | Has FK | Has JSONB |
|---|-------|--------|---------|--------|-----------|
| 1 | schema_version | public | TEXT+INT | No | No |
| 2 | runs | public | TEXT | No | Yes (5 cols) |
| 3 | failure_atlas_entries | public | UUID | No | Yes (14 cols) |
| 4 | ai_investigation_feedback | public | UUID | No | No |
| 5 | ai_resolution_capture | public | UUID | No | Yes (2 cols) |
| 6 | community_escalations | public | UUID | No | Yes (1 col) |
| 7 | community_telemetry | public | SERIAL | No | Yes (1 col) |
| 8 | community_unknown_dataset | public | SERIAL | No | No |
| 9 | resolution_patterns | public | UUID | No | Yes (2 cols) |
| 10 | resolution_feedback | public | UUID | No | No |
| 11 | execution_intelligence | public | UUID | No | Yes (3 cols) |
| 12 | feedback_records | public | UUID | No | Yes (2 cols) |
| 13 | user_journey_events | public | UUID | No | Yes (1 col) |
| 14 | resolution_tracking | public | UUID | No | No |
| 15 | telemetry_audit_log | public | SERIAL | No | No |
| 16 | design_features | public | TEXT | No | Yes (1 col) |
| 17 | design_profiles | public | TEXT | No | No |
| 18 | telemetry_execution_records | public | UUID | No | Yes (1 col) |
| 19 | telemetry_recommendation_records | public | UUID | No | No |
| 20 | upload_queue | public | SERIAL | No | Yes (1 col) |
| 21 | telemetry_events | ingestion | SERIAL | No | Yes (1 col) |
| 22 | failure_atlas_events | ingestion | SERIAL | No | No |
| 23 | upload_audit | ingestion | SERIAL | No | No |
| 24 | consent_records | ingestion | SERIAL | No | No |

**Total tables: 24** (21 existing + 0 invented; 3 cloud ingestion tables moved to separate schema)

**Total JSONB columns:** ~34 across all tables
**Total UUID PKs:** 13
**Total SERIAL PKs:** 7
**Total TEXT PKs:** 4
