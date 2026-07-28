# Telemetry Schema Review

> Review of community_telemetry, community_unknown_dataset, resolution_patterns, failure_atlas
> Generated: 2026-06-15

---

## 1. community_telemetry

### Current Schema (Migration 29)
```sql
CREATE TABLE community_telemetry (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event           TEXT NOT NULL,        -- Event type string
    escalation_id   TEXT DEFAULT '',       -- FK to community_escalations
    failure_type    TEXT DEFAULT '',
    tool            TEXT DEFAULT '',
    atlas_id        TEXT DEFAULT '',       -- FK to failure_atlas_entries
    details         TEXT DEFAULT '{}',     -- JSON blob
    created_at      TEXT NOT NULL
);
```

### Issues Found

| Issue | Severity | Description |
|-------|----------|-------------|
| Missing index on `created_at` | LOW | No index on timestamp column — range queries use table scan |
| `details` is untyped JSON | MEDIUM | No schema enforcement; callers can add arbitrary keys |
| No `run_id` column | LOW | Cannot trace events back to a run without joining through escalation_id |
| No `gli_version` column | MEDIUM | Cannot determine which GLI version generated the event |
| `event` is TEXT but should be constrained | MEDIUM | Events are validated in Python but DB allows any string |
| No source IP/user tracking | SAFE (by design) | Privacy-by-design: no user tracking columns |

### Recommended Changes
```sql
-- Add: run_id TEXT DEFAULT '' (for direct run association)
-- Add: gli_version TEXT DEFAULT '' (for version tracking)
-- Add: event_source TEXT DEFAULT '' (dashboard, cli, automated)
-- Change: details TEXT CHECK (json_valid(details)) for SQLite 3.38+
-- Add: INDEX idx_ct_created ON community_telemetry(created_at)
-- Add: INDEX idx_ct_type ON community_telemetry(failure_type)
```

---

## 2. community_unknown_dataset

### Current Schema (Migration 30)
```sql
CREATE TABLE community_unknown_dataset (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    tool                TEXT NOT NULL,
    failure_type        TEXT NOT NULL,
    signature           TEXT DEFAULT '',
    frequency           INTEGER DEFAULT 1,
    ai_helpfulness      TEXT DEFAULT 'unknown',
    resolution_outcome  TEXT DEFAULT '',
    consent_given       INTEGER DEFAULT 0,
    escalation_id       TEXT DEFAULT '',
    last_seen           TEXT NOT NULL
);
```

### Issues Found

| Issue | Severity | Description |
|-------|----------|-------------|
| No unique constraint on (tool, failure_type, signature) | **HIGH** | Same failure can have multiple rows — dedup logic is Python-only |
| No first_seen column | MEDIUM | Cannot determine when a failure first appeared |
| No severity column | LOW | Severity is not tracked in the dataset |
| No confidence column | LOW | Confidence is not tracked |
| No stage column | LOW | Cannot filter by flow stage |
| consent_given is INTEGER but used as boolean | LOW | Should use SQLite boolean convention |
| last_seen is TEXT but always an ISO timestamp | LOW | Should use datetime type or add a CHECK |

### Recommended Changes
```sql
-- Add: UNIQUE(tool, failure_type, signature) -- prevents duplicates at DB level
-- Add: first_seen TEXT DEFAULT (datetime('now')) -- tracks first occurrence
-- Add: stage TEXT DEFAULT '' -- flow stage
-- Add: severity TEXT DEFAULT 'MEDIUM' -- LOW/MEDIUM/HIGH/TAPEOUT_BLOCKING
-- Add: confidence REAL DEFAULT 0.0 -- how confident we are it's a real failure
-- Add: resolution_attempts INTEGER DEFAULT 0 -- count of attempts
-- Change: consent_given INTEGER DEFAULT 0 -- keep as is, boolean INTEGER is fine
```

---

## 3. resolution_patterns

### Current Schema (Migrations 31, 33)
```sql
CREATE TABLE resolution_patterns (
    id                      TEXT PRIMARY KEY,
    failure_fingerprint     TEXT NOT NULL,
    failure_type            TEXT NOT NULL,
    root_cause              TEXT,
    resolution              TEXT NOT NULL,
    resolution_type         TEXT,
    success_count           INTEGER DEFAULT 0,
    failure_count           INTEGER DEFAULT 0,
    confidence              REAL DEFAULT 0.0,
    first_seen              TEXT,
    last_seen               TEXT,
    created_at              TEXT DEFAULT (datetime('now')),
    updated_at              TEXT DEFAULT (datetime('now')),
    unique_runs             INTEGER DEFAULT 0,
    unique_designs          INTEGER DEFAULT 0,
    engineer_confirmations  INTEGER DEFAULT 0,
    contradictory_reports   INTEGER DEFAULT 0,
    trust_score             REAL DEFAULT 0.0,
    trust_level             TEXT DEFAULT 'LOW',
    trust_reason            TEXT DEFAULT '',
    tracked_run_ids         TEXT DEFAULT '[]',
    tracked_design_names    TEXT DEFAULT '[]'
);
```

### Issues Found

| Issue | Severity | Description |
|-------|----------|-------------|
| `tracked_run_ids` and `tracked_design_names` are JSON arrays in TEXT columns | MEDIUM | Should be normalized into child tables if this data needs to be queriable |
| No unique constraint on (failure_fingerprint, resolution) | **HIGH** | Same fingerprint + resolution can have multiple rows |
| `first_seen`/`last_seen` are TEXT, not datetime | LOW | Consistent with DB convention |
| `trust_level` is denormalized | LOW | Can be derived from trust_score — but convenient for querying |
| `tracked_run_ids` grows unbounded | MEDIUM | A pattern with 10,000 runs stores a 10,000-element JSON array |
| `root_cause` has no length limit | LOW | Could store arbitrarily large text |

### Recommended Changes
```sql
-- Add: UNIQUE(failure_fingerprint, resolution) -- prevents duplicate patterns
-- Normalize: tracked_run_ids → resolution_run_map table
-- Normalize: tracked_design_names → resolution_design_map table
-- Add: CHECK(trust_level IN ('HIGH', 'MEDIUM', 'LOW'))
-- Consider: MAX length constraints on root_cause, resolution, trust_reason
```

### Normalization Proposal

```sql
CREATE TABLE resolution_run_map (
    pattern_id  TEXT NOT NULL REFERENCES resolution_patterns(id),
    run_id      TEXT NOT NULL,
    first_seen  TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (pattern_id, run_id)
);

CREATE TABLE resolution_design_map (
    pattern_id   TEXT NOT NULL REFERENCES resolution_patterns(id),
    design_name  TEXT NOT NULL,
    first_seen   TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (pattern_id, design_name)
);
```

This allows:
- Counting unique runs/designs without JSON parsing
- Querying which runs/designs contributed to a pattern
- Adding timestamps for when each run/design was first seen
- Efficient indexing on run_id and design_name

---

## 4. failure_atlas_entries

### Current Schema (Migrations 1-24)
```sql
CREATE TABLE failure_atlas_entries (
    id                      TEXT PRIMARY KEY,
    run_id                  TEXT NOT NULL,
    failure_id              TEXT,
    failure_type            TEXT NOT NULL,
    severity                TEXT NOT NULL,
    title                   TEXT,
    description             TEXT,
    recommended_fix         TEXT,
    confidence              REAL DEFAULT 0.8,
    signature               TEXT,
    domain                  TEXT,
    category                TEXT,
    evidence                TEXT,         -- JSON blob
    detected_at             TEXT DEFAULT (datetime('now')),
    created_at              TEXT DEFAULT (datetime('now')),
    parent_run_id           TEXT,
    fix_applied             INTEGER DEFAULT 0,
    fix_type                TEXT,
    fix_description         TEXT,
    fix_run_id              TEXT,
    before_metrics          TEXT,
    after_metrics           TEXT,
    resolution_confidence   TEXT,
    entry_level             TEXT DEFAULT 'FAILURE',
    failure_hash            TEXT,
    tool_name               TEXT,
    tool_version            TEXT,
    tool_stage              TEXT,
    first_seen              TEXT,
    last_seen               TEXT,
    occurrence_count        INTEGER DEFAULT 1,
    environment_fingerprint TEXT,
    resolution_attempts     INTEGER DEFAULT 0,
    resolution_success_rate REAL DEFAULT 0.0,
    regression_detected     INTEGER DEFAULT 0,
    artifact_snapshot       TEXT,
    execution_snapshot      TEXT,
    timing_snapshot         TEXT,
    utilization_snapshot    TEXT,
    congestion_snapshot     TEXT,
    runtime_snapshot        TEXT
);
```

### Issues Found

| Issue | Severity | Description |
|-------|----------|-------------|
| 39 columns — schema bloat | MEDIUM | 39 columns, many sparsely populated or deprecated |
| Snapshot columns are TEXT JSON blobs | MEDIUM | `artifact_snapshot`, `execution_snapshot`, `timing_snapshot`, `utilization_snapshot`, `congestion_snapshot`, `runtime_snapshot` — should be a single `snapshots` JSON column or a child table |
| `before_metrics`/`after_metrics` are TEXT JSON | LOW | Consistent with project convention but untyped |
| `evidence` is untyped TEXT JSON | **HIGH** | No schema enforcement — can contain any data including customer IP |
| `resolution_confidence` is TEXT but holds structured data | MEDIUM | Should be a derived field from resolution patterns |
| No unique constraint on (run_id, failure_type, signature) — partially added in Migration 25 | **PARTIALLY FIXED** | Migration 25 only applies to CROSS_TOOL_DRC_DISAGREEMENT — other types still allow duplicates |
| `first_seen`/`last_seen`/`occurrence_count` are partially redundant with `created_at` | MEDIUM | `first_seen` = min(created_at), `last_seen` = max(created_at) if we had history |
| `domain` and `category` overlap | LOW | Domain is pipeline stage; category could be the same as failure_type |
| No `fingerprint` column | LOW | Would be useful for grouping related failures across runs |

### Recommended Changes
```sql
-- Consolidate snapshot columns into one:
-- ALTER TABLE failure_atlas_entries ADD COLUMN snapshots TEXT DEFAULT '{}';
-- Then deprecate: artifact_snapshot, execution_snapshot, timing_snapshot, utilization_snapshot, congestion_snapshot, runtime_snapshot

-- Add: UNIQUE(run_id, failure_type, signature) for ALL failure types, not just CROSS_TOOL_DRC_DISAGREEMENT
-- Add: fingerprint TEXT DEFAULT '' -- for grouping related failures
-- Add: CHECK(evidence IS NULL OR json_valid(evidence)) -- basic JSON validation

-- Move : resolution_confidence → derived from resolution_patterns join
-- Add: resolution_pattern_id TEXT REFERENCES resolution_patterns(id)
```

---

## 5. CROSS-TABLE ISSUES

### Missing Foreign Key Relationships

| From | To | Status | Issue |
|------|----|--------|-------|
| failure_atlas_entries.run_id | runs.run_id | Not enforced | Run deletion orphans entries |
| resolution_patterns.id | failure_atlas_entries.resolution_pattern_id | Missing | No FK exists |
| resolution_feedback.pattern_id | resolution_patterns.id | Not enforced | Pattern deletion orphans feedback |
| community_telemetry.escalation_id | community_escalations.id | Not enforced | Escalation deletion orphans events |
| community_unknown_dataset.escalation_id | community_escalations.id | Not enforced | Same issue |

### Normalization Issues

| Issue | Tables Affected | Impact |
|-------|----------------|--------|
| JSON arrays for tracking (tracked_run_ids, tracked_design_names) | resolution_patterns | Cannot query at SQL level; Python-level parsing needed |
| Snapshot columns as separate TEXT columns | failure_atlas_entries | 6 near-identical columns; should be 1 JSON column |
| Frequency counter with Python-level UPSERT | community_unknown_dataset | Race condition on concurrent writes; DB-level UNIQUE would help |

### Missing Indexes

| Table | Missing Index | Impact |
|-------|--------------|--------|
| failure_atlas_entries | (failure_type, last_seen) | Common query pattern: "recent failures of type X" |
| community_unknown_dataset | (last_seen) | Queries for recently seen unknown failures |

---

## 6. SUMMARY OF RECOMMENDATIONS

### Critical (Must Fix)
1. **Add UNIQUE(failure_fingerprint, resolution)** to `resolution_patterns`
2. **Add UNIQUE(tool, failure_type, signature)** to `community_unknown_dataset`
3. **Add full UNIQUE(run_id, failure_type, signature)** to `failure_atlas_entries` (beyond just CROSS_TOOL_DRC_DISAGREEMENT)
4. **Normalize `tracked_run_ids`/`tracked_design_names`** into child tables
5. **Add evidence sanitization hook** for failure_atlas_entries

### High Priority
6. Consolidate 6 snapshot columns into 1 JSON column
7. Add FK constraints between related tables
8. Add `first_seen` to `community_unknown_dataset`
9. Add `run_id` and `gli_version` to `community_telemetry`
10. Add CHECK constraints for enum-like columns (event, trust_level, severity)

### Low Priority
11. Consolidate duplicated TelemetryManager/TelemetryParser implementations
12. Add max-length constraints on text fields
13. Add JSON schema validation for JSON columns
