import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    source TEXT NOT NULL,
    version INTEGER NOT NULL,
    applied_at TEXT DEFAULT (datetime('now')),
    description TEXT,
    PRIMARY KEY (source, version)
)
"""


@dataclass
class Migration:
    version: int
    description: str
    sql: str


@dataclass
class MigrationState:
    current_version: int = 0
    pending: list[Migration] = field(default_factory=list)
    applied: list[Migration] = field(default_factory=list)
    error: Optional[str] = None
    ok: bool = True


RUNS_MIGRATIONS = [
    Migration(1, "initial runs table", """
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            design_name TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            current_stage TEXT DEFAULT 'INITIALIZING',
            progress INTEGER DEFAULT 0,
            wns REAL DEFAULT NULL,
            tns REAL DEFAULT NULL,
            hold_wns REAL DEFAULT NULL,
            hold_tns REAL DEFAULT NULL,
            utilization REAL DEFAULT NULL,
            runtime_sec REAL DEFAULT NULL,
            cell_count INTEGER DEFAULT NULL,
            qor_score REAL DEFAULT NULL,
            timestamp TEXT DEFAULT (datetime('now')),
            run_dir TEXT DEFAULT NULL,
            regression INTEGER DEFAULT 0,
            drc_violations INTEGER DEFAULT NULL,
            drc_magic_violations INTEGER DEFAULT NULL,
            drc_klayout_violations INTEGER DEFAULT NULL,
            drc_is_clean INTEGER DEFAULT 0,
            lvs_result TEXT DEFAULT NULL,
            lvs_is_clean INTEGER DEFAULT 0,
            setup_wns_ns REAL DEFAULT NULL,
            hold_whs_ns REAL DEFAULT NULL,
            signoff_setup_pass INTEGER DEFAULT 0,
            signoff_hold_pass INTEGER DEFAULT 0,
            signoff_gate_json TEXT DEFAULT NULL,
            tapeout_ready INTEGER DEFAULT 0
        )
    """),
    Migration(2, "add created_at to runs", """
        ALTER TABLE runs ADD COLUMN created_at TEXT DEFAULT NULL
    """),
    Migration(3, "add updated_at to runs", """
        ALTER TABLE runs ADD COLUMN updated_at TEXT DEFAULT NULL
    """),
    Migration(4, "add tags to runs", """
        ALTER TABLE runs ADD COLUMN tags TEXT DEFAULT NULL
    """),
    Migration(5, "add important columns to runs", """
        ALTER TABLE runs ADD COLUMN is_important INTEGER DEFAULT 0;
        ALTER TABLE runs ADD COLUMN important_marked_at TEXT DEFAULT NULL;
        ALTER TABLE runs ADD COLUMN important_source TEXT DEFAULT NULL
    """),
    Migration(6, "add implementation/signoff status columns", """
        ALTER TABLE runs ADD COLUMN implementation_status TEXT DEFAULT 'NOT_STARTED';
        ALTER TABLE runs ADD COLUMN signoff_status TEXT DEFAULT 'NOT_RUN';
        ALTER TABLE runs ADD COLUMN implementation_score REAL DEFAULT NULL;
        ALTER TABLE runs ADD COLUMN signoff_score REAL DEFAULT NULL;
        ALTER TABLE runs ADD COLUMN root_cause_summary TEXT DEFAULT NULL
    """),
    Migration(7, "add LLM investigation columns", """
        ALTER TABLE runs ADD COLUMN llm_investigation_available INTEGER DEFAULT 0;
        ALTER TABLE runs ADD COLUMN llm_investigation_status TEXT DEFAULT NULL;
        ALTER TABLE runs ADD COLUMN llm_investigation_summary TEXT DEFAULT NULL;
        ALTER TABLE runs ADD COLUMN llm_investigation_timestamp TEXT DEFAULT NULL
    """),
    Migration(8, "add LLM investigation failed attempts column", """
        ALTER TABLE runs ADD COLUMN llm_investigation_failed_attempts TEXT DEFAULT '{"attempts":[]}'
    """),
]

FAILURE_ATLAS_MIGRATIONS = [
    Migration(1, "initial failure_atlas_entries table", """
        CREATE TABLE IF NOT EXISTS failure_atlas_entries (
            id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            failure_id TEXT,
            failure_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT,
            description TEXT,
            recommended_fix TEXT,
            confidence REAL DEFAULT 0.8,
            signature TEXT,
            domain TEXT,
            category TEXT,
            evidence TEXT,
            detected_at TEXT DEFAULT (datetime('now')),
            created_at TEXT DEFAULT (datetime('now')),
            parent_run_id TEXT,
            fix_applied INTEGER DEFAULT 0,
            fix_type TEXT,
            fix_description TEXT,
            fix_run_id TEXT,
            before_metrics TEXT,
            after_metrics TEXT,
            resolution_confidence TEXT
        )
    """),
    Migration(2, "add parent_run_id to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN parent_run_id TEXT DEFAULT NULL
    """),
    Migration(3, "add before_metrics to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN before_metrics TEXT DEFAULT NULL
    """),
    Migration(4, "add after_metrics to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN after_metrics TEXT DEFAULT NULL
    """),
    Migration(5, "add resolution_confidence to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN resolution_confidence TEXT DEFAULT NULL
    """),
    Migration(6, "add created_at to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN created_at TEXT DEFAULT (datetime('now'))
    """),
    Migration(7, "add entry_level to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN entry_level TEXT DEFAULT 'FAILURE'
    """),
    Migration(8, "add failure_hash to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN failure_hash TEXT DEFAULT NULL
    """),
    Migration(9, "add tool_name to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN tool_name TEXT DEFAULT NULL
    """),
    Migration(10, "add tool_version to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN tool_version TEXT DEFAULT NULL
    """),
    Migration(11, "add tool_stage to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN tool_stage TEXT DEFAULT NULL
    """),
    Migration(12, "add first_seen to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN first_seen TEXT DEFAULT NULL
    """),
    Migration(13, "add last_seen to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN last_seen TEXT DEFAULT NULL
    """),
    Migration(14, "add occurrence_count to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN occurrence_count INTEGER DEFAULT 1
    """),
    Migration(15, "add environment_fingerprint to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN environment_fingerprint TEXT DEFAULT NULL
    """),
    Migration(16, "add resolution_attempts to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN resolution_attempts INTEGER DEFAULT 0
    """),
    Migration(17, "add resolution_success_rate to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN resolution_success_rate REAL DEFAULT 0.0
    """),
    Migration(18, "add regression_detected to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN regression_detected INTEGER DEFAULT 0
    """),
    Migration(19, "add artifact_snapshot to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN artifact_snapshot TEXT DEFAULT NULL
    """),
    Migration(20, "add execution_snapshot to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN execution_snapshot TEXT DEFAULT NULL
    """),
    Migration(21, "add timing_snapshot to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN timing_snapshot TEXT DEFAULT NULL
    """),
    Migration(22, "add utilization_snapshot to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN utilization_snapshot TEXT DEFAULT NULL
    """),
    Migration(23, "add congestion_snapshot to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN congestion_snapshot TEXT DEFAULT NULL
    """),
    Migration(24, "add runtime_snapshot to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN runtime_snapshot TEXT DEFAULT NULL
    """),
    Migration(25, "deduplicate cross-tool DRC disagreements and add uniqueness constraint", """
        DELETE FROM failure_atlas_entries
        WHERE rowid NOT IN (
            SELECT MIN(rowid) FROM failure_atlas_entries
            WHERE failure_type = 'CROSS_TOOL_DRC_DISAGREEMENT'
            GROUP BY run_id, failure_type, signature
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_fa_unique_run_type_sig
        ON failure_atlas_entries(run_id, failure_type, signature);
    """),
    Migration(26, "create ai_investigation_feedback table", """
        CREATE TABLE IF NOT EXISTS ai_investigation_feedback (
            id TEXT PRIMARY KEY,
            investigation_id TEXT NOT NULL,
            feedback_type TEXT NOT NULL,
            resolved INTEGER DEFAULT 0,
            comment TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            run_id TEXT DEFAULT '',
            failure_type TEXT DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_ai_feedback_investigation ON ai_investigation_feedback(investigation_id);
        CREATE INDEX IF NOT EXISTS idx_ai_feedback_failure ON ai_investigation_feedback(failure_type);
    """),
    Migration(27, "create ai_resolution_capture table", """
        CREATE TABLE IF NOT EXISTS ai_resolution_capture (
            id TEXT PRIMARY KEY,
            investigation_id TEXT NOT NULL,
            failure_type TEXT NOT NULL,
            tool TEXT NOT NULL,
            stage TEXT DEFAULT '',
            fix_description TEXT NOT NULL,
            resolution_outcome TEXT DEFAULT '',
            design_name TEXT DEFAULT '',
            pdk TEXT DEFAULT '',
            metrics_before TEXT DEFAULT '{}',
            metrics_after TEXT DEFAULT '{}',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_ai_resolution_failure ON ai_resolution_capture(failure_type);
        CREATE INDEX IF NOT EXISTS idx_ai_resolution_investigation ON ai_resolution_capture(investigation_id);
    """),
    Migration(28, "create community_escalations table", """
        CREATE TABLE IF NOT EXISTS community_escalations (
            id TEXT PRIMARY KEY,
            run_id TEXT DEFAULT '',
            failure_type TEXT NOT NULL,
            tool TEXT DEFAULT '',
            stage TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'open',
            consent_given INTEGER DEFAULT 0,
            consent_timestamp TEXT DEFAULT '',
            bharatcode_submission_id TEXT DEFAULT '',
            bharatcode_status TEXT DEFAULT '',
            ai_summary TEXT DEFAULT '',
            user_notes TEXT DEFAULT '',
            engineer_response TEXT DEFAULT '{}',
            atlas_id_created TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            sent_at TEXT DEFAULT '',
            resolved_at TEXT DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_esc_failure_type ON community_escalations(failure_type);
        CREATE INDEX IF NOT EXISTS idx_esc_status ON community_escalations(status);
        CREATE INDEX IF NOT EXISTS idx_esc_created ON community_escalations(created_at);
    """),
    Migration(29, "create community_telemetry table", """
        CREATE TABLE IF NOT EXISTS community_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            escalation_id TEXT DEFAULT '',
            failure_type TEXT DEFAULT '',
            tool TEXT DEFAULT '',
            atlas_id TEXT DEFAULT '',
            details TEXT DEFAULT '{}',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_ct_event ON community_telemetry(event);
        CREATE INDEX IF NOT EXISTS idx_ct_esc ON community_telemetry(escalation_id);
    """),
    Migration(30, "create community_unknown_dataset table", """
        CREATE TABLE IF NOT EXISTS community_unknown_dataset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool TEXT NOT NULL,
            failure_type TEXT NOT NULL,
            signature TEXT DEFAULT '',
            frequency INTEGER DEFAULT 1,
            ai_helpfulness TEXT DEFAULT 'unknown',
            resolution_outcome TEXT DEFAULT '',
            consent_given INTEGER DEFAULT 0,
            escalation_id TEXT DEFAULT '',
            last_seen TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_ud_failure ON community_unknown_dataset(failure_type);
        CREATE INDEX IF NOT EXISTS idx_ud_tool ON community_unknown_dataset(tool);
        CREATE INDEX IF NOT EXISTS idx_ud_freq ON community_unknown_dataset(frequency DESC);
    """),
    Migration(31, "create resolution_patterns table", """
        CREATE TABLE IF NOT EXISTS resolution_patterns (
            id TEXT PRIMARY KEY,
            failure_fingerprint TEXT NOT NULL,
            failure_type TEXT NOT NULL,
            root_cause TEXT,
            resolution TEXT NOT NULL,
            resolution_type TEXT,
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            confidence REAL DEFAULT 0.0,
            first_seen TEXT,
            last_seen TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_rp_fingerprint ON resolution_patterns(failure_fingerprint);
        CREATE INDEX IF NOT EXISTS idx_rp_type ON resolution_patterns(failure_type);
        CREATE INDEX IF NOT EXISTS idx_rp_confidence ON resolution_patterns(confidence DESC);
    """),
    Migration(32, "create resolution_feedback table", """
        CREATE TABLE IF NOT EXISTS resolution_feedback (
            id TEXT PRIMARY KEY,
            pattern_id TEXT NOT NULL,
            run_id TEXT NOT NULL,
            feedback_type TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_rf_pattern ON resolution_feedback(pattern_id);
        CREATE INDEX IF NOT EXISTS idx_rf_run ON resolution_feedback(run_id);
    """),
    Migration(33, "add trust/reputation columns to resolution_patterns", """
        ALTER TABLE resolution_patterns ADD COLUMN unique_runs INTEGER DEFAULT 0;
        ALTER TABLE resolution_patterns ADD COLUMN unique_designs INTEGER DEFAULT 0;
        ALTER TABLE resolution_patterns ADD COLUMN engineer_confirmations INTEGER DEFAULT 0;
        ALTER TABLE resolution_patterns ADD COLUMN contradictory_reports INTEGER DEFAULT 0;
        ALTER TABLE resolution_patterns ADD COLUMN trust_score REAL DEFAULT 0.0;
        ALTER TABLE resolution_patterns ADD COLUMN trust_level TEXT DEFAULT 'UNVERIFIED';
        ALTER TABLE resolution_patterns ADD COLUMN trust_reason TEXT DEFAULT NULL;
        ALTER TABLE resolution_patterns ADD COLUMN tracked_run_ids TEXT DEFAULT '[]';
        ALTER TABLE resolution_patterns ADD COLUMN tracked_design_names TEXT DEFAULT '[]'
    """),
    Migration(34, "create execution_intelligence table", """
        CREATE TABLE IF NOT EXISTS execution_intelligence (
            id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            tool TEXT NOT NULL,
            stage TEXT NOT NULL,
            severity TEXT NOT NULL,
            fingerprint TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            failure_context TEXT NOT NULL DEFAULT '{}',
            root_cause_analysis TEXT NOT NULL DEFAULT '{}',
            resolution TEXT NOT NULL DEFAULT '{}',
            trust_score REAL DEFAULT 0.0,
            outcome TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_ei_fingerprint ON execution_intelligence(fingerprint);
        CREATE INDEX IF NOT EXISTS idx_ei_event_type ON execution_intelligence(event_type);
    """),
    Migration(35, "add detection_classification to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN detection_classification TEXT DEFAULT 'UNVERIFIED'
    """),
    Migration(36, "add design_name to failure_atlas_entries", """
        ALTER TABLE failure_atlas_entries ADD COLUMN design_name TEXT DEFAULT ''
    """),
]


BETA_MIGRATIONS = [
    Migration(1, "create feedback_records table", """
        CREATE TABLE IF NOT EXISTS feedback_records (
            id TEXT PRIMARY KEY,
            feedback_type TEXT NOT NULL,
            title TEXT DEFAULT '',
            description TEXT DEFAULT '',
            gli_version TEXT DEFAULT '',
            os TEXT DEFAULT '',
            tool_versions TEXT DEFAULT '{}',
            recent_run_id TEXT DEFAULT '',
            failure_fingerprint TEXT DEFAULT '',
            telemetry_health_summary TEXT DEFAULT '{}',
            priority_score REAL DEFAULT 0.0,
            priority_level TEXT DEFAULT 'MEDIUM',
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback_records(feedback_type);
        CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback_records(status);
        CREATE INDEX IF NOT EXISTS idx_feedback_priority ON feedback_records(priority_level);
        CREATE INDEX IF NOT EXISTS idx_feedback_created ON feedback_records(created_at);
    """),
    Migration(2, "create user_journey_events table", """
        CREATE TABLE IF NOT EXISTS user_journey_events (
            id TEXT PRIMARY KEY,
            session_id TEXT DEFAULT '',
            stage TEXT NOT NULL,
            event_type TEXT DEFAULT '',
            details TEXT DEFAULT '{}',
            duration_sec REAL DEFAULT 0.0,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_journey_session ON user_journey_events(session_id);
        CREATE INDEX IF NOT EXISTS idx_journey_stage ON user_journey_events(stage);
        CREATE INDEX IF NOT EXISTS idx_journey_created ON user_journey_events(created_at);
    """),
    Migration(3, "create resolution_tracking table", """
        CREATE TABLE IF NOT EXISTS resolution_tracking (
            id TEXT PRIMARY KEY,
            run_id TEXT DEFAULT '',
            failure_fingerprint TEXT DEFAULT '',
            resolution_suggested TEXT DEFAULT '',
            suggested_at TEXT DEFAULT (datetime('now')),
            accepted_at TEXT DEFAULT NULL,
            rejected_at TEXT DEFAULT NULL,
            success_verified INTEGER DEFAULT 0,
            failure_type TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_rt_run ON resolution_tracking(run_id);
        CREATE INDEX IF NOT EXISTS idx_rt_fingerprint ON resolution_tracking(failure_fingerprint);
        CREATE INDEX IF NOT EXISTS idx_rt_success ON resolution_tracking(success_verified);
    """),
]

EXPECTED_COLUMNS = {
    "runs": {
        "run_id", "design_name", "status", "current_stage", "progress",
        "wns", "tns", "hold_wns", "hold_tns", "utilization",
        "runtime_sec", "cell_count", "qor_score", "timestamp", "run_dir",
        "regression", "drc_violations", "drc_magic_violations",
        "drc_klayout_violations", "drc_is_clean", "lvs_result",
        "lvs_is_clean", "setup_wns_ns", "hold_whs_ns",
        "signoff_setup_pass", "signoff_hold_pass", "signoff_gate_json",
        "tapeout_ready", "created_at", "updated_at", "tags",
        "is_important", "important_marked_at", "important_source",
        "implementation_status", "signoff_status",
        "implementation_score", "signoff_score", "root_cause_summary",
        "llm_investigation_available", "llm_investigation_status",
        "llm_investigation_summary", "llm_investigation_timestamp",
        "llm_investigation_failed_attempts"
    },
    "failure_atlas_entries": {
        "id", "run_id", "failure_id", "failure_type", "severity", "title",
        "description", "recommended_fix", "confidence", "signature",
        "domain", "category", "evidence", "detected_at", "created_at",
        "parent_run_id", "fix_applied", "fix_type", "fix_description",
        "fix_run_id", "before_metrics", "after_metrics",
        "resolution_confidence", "entry_level",
        "failure_hash", "tool_name", "tool_version", "tool_stage",
        "first_seen", "last_seen", "occurrence_count",
        "environment_fingerprint", "resolution_attempts",
        "resolution_success_rate", "regression_detected",
        "artifact_snapshot", "execution_snapshot", "timing_snapshot",
        "utilization_snapshot", "congestion_snapshot", "runtime_snapshot",
        "detection_classification", "design_name",
    },
    "resolution_patterns": {
        "id", "failure_fingerprint", "failure_type", "root_cause",
        "resolution", "resolution_type", "success_count", "failure_count",
        "confidence", "first_seen", "last_seen", "created_at", "updated_at",
        "unique_runs", "unique_designs", "engineer_confirmations",
        "contradictory_reports", "trust_score", "trust_level", "trust_reason",
        "tracked_run_ids", "tracked_design_names",
    },
    "resolution_feedback": {
        "id", "pattern_id", "run_id", "feedback_type", "created_at",
    },
    "feedback_records": {
        "id", "feedback_type", "title", "description", "gli_version", "os",
        "tool_versions", "recent_run_id", "failure_fingerprint",
        "telemetry_health_summary", "priority_score", "priority_level",
        "status", "created_at", "updated_at",
    },
    "user_journey_events": {
        "id", "session_id", "stage", "event_type", "details",
        "duration_sec", "created_at",
    },
    "resolution_tracking": {
        "id", "run_id", "failure_fingerprint", "resolution_suggested",
        "suggested_at", "accepted_at", "rejected_at", "success_verified",
        "failure_type", "created_at",
    },
    "execution_intelligence": {
        "id", "event_type", "tool", "stage", "severity", "fingerprint",
        "timestamp", "failure_context", "root_cause_analysis", "resolution",
        "trust_score", "outcome"
    },
}


def _get_db_path() -> str:
    db_path = os.environ.get("GLI_FLOW_DB")
    if db_path:
        return db_path
    db_path = os.environ.get("GLI_FLOW_DB_PATH")
    if db_path:
        return db_path
    db_dir = Path.home() / ".gli_flow"
    try:
        db_dir.mkdir(parents=True, exist_ok=True)
        probe = db_dir / ".write_test"
        probe.write_text("")
        probe.unlink(missing_ok=True)
        return str(db_dir / "gli_flow.db")
    except OSError:
        return str(Path.cwd() / "gli_flow.db")


_SOURCES = {"runs", "failure_atlas", "resolution_intelligence", "beta_operations"}


def _ensure_schema_version_table(conn: sqlite3.Connection):
    old_exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
    ).fetchone()
    has_source = False
    if old_exists:
        try:
            conn.execute("SELECT source FROM schema_version LIMIT 1")
            has_source = True
        except sqlite3.OperationalError:
            pass

    if not has_source and old_exists:
        conn.execute("CREATE TABLE IF NOT EXISTS schema_version_old (version INTEGER PRIMARY KEY, applied_at TEXT, description TEXT)")
        conn.execute("INSERT OR IGNORE INTO schema_version_old SELECT version, applied_at, description FROM schema_version")
        conn.execute("DROP TABLE IF EXISTS schema_version")
        conn.execute(SCHEMA_VERSION_TABLE)
        try:
            rows = conn.execute("SELECT description, version FROM schema_version_old").fetchall()
            for desc, ver in rows:
                if "failure_atlas" in (desc or "").lower():
                    src = "failure_atlas"
                elif "runs" in (desc or "").lower():
                    src = "runs"
                else:
                    src = "migrated"
                conn.execute(
                    "INSERT OR IGNORE INTO schema_version (source, version, description) VALUES (?, ?, ?)",
                    (src, ver, desc),
                )
        except sqlite3.OperationalError:
            pass
        conn.commit()
    elif not old_exists:
        conn.execute(SCHEMA_VERSION_TABLE)
        conn.commit()


def _current_version(conn: sqlite3.Connection, source: str) -> int:
    cursor = conn.execute(
        "SELECT COALESCE(MAX(version), 0) FROM schema_version WHERE source = ?",
        (source,),
    )
    return cursor.fetchone()[0]


class MigrationEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or _get_db_path()
        self.conn = sqlite3.connect(self.db_path)
        try:
            self.conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.OperationalError:
            self.conn.close()
            self.conn = sqlite3.connect(self.db_path)
        _ensure_schema_version_table(self.conn)

    def close(self):
        self.conn.close()

    def state(self, source: str, migrations: list[Migration]) -> MigrationState:
        current = _current_version(self.conn, source)
        state = MigrationState(current_version=current)
        for m in migrations:
            if m.version <= current:
                state.applied.append(m)
            else:
                state.pending.append(m)
        return state

    def migrate(self, source: str, migrations: list[Migration], target: Optional[int] = None) -> MigrationState:
        state = self.state(source, migrations)
        if state.error:
            return state
        for m in state.pending:
            if target is not None and m.version > target:
                break
            try:
                # Handle semicolon-separated statements by splitting them
                for statement in m.sql.split(';'):
                    if statement.strip():
                        self.conn.execute(statement)
                self.conn.execute(
                    "INSERT INTO schema_version (source, version, description) VALUES (?, ?, ?)",
                    (source, m.version, m.description),
                )
                self.conn.commit()
                state.applied.append(m)
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    self.conn.execute(
                        "INSERT OR IGNORE INTO schema_version (source, version, description) VALUES (?, ?, ?)",
                        (source, m.version, m.description),
                    )
                    self.conn.commit()
                    state.applied.append(m)
                    continue
                state.error = f"Migration {m.version} ({m.description}) failed. See logs for details."
                state.ok = False
                return state
        state.pending = [m for m in migrations if m.version > _current_version(self.conn, source)]
        state.current_version = _current_version(self.conn, source)
        return state

    def repair(self, source: str, migrations: list[Migration]) -> MigrationState:
        for m in migrations:
            try:
                self.conn.execute(
                    "INSERT OR IGNORE INTO schema_version (source, version, description) VALUES (?, ?, ?)",
                    (source, m.version, m.description),
                )
            except sqlite3.OperationalError:
                pass
        self.conn.commit()
        return self.state(source, migrations)

    def validate_schema(self, source: str, migrations: list[Migration]) -> bool:
        state = self.state(source, migrations)
        if state.error:
            return False
        return len(state.pending) == 0

    def validate_runtime_schema(self) -> tuple[bool, list[str]]:
        errors = []
        for table, expected in EXPECTED_COLUMNS.items():
            try:
                rows = self.conn.execute(f"PRAGMA table_info({table})").fetchall()
            except sqlite3.OperationalError as e:
                errors.append(f"{table}: {e}")
                continue
            actual = {row[1] for row in rows}
            missing = sorted(expected - actual)
            if missing:
                errors.append(f"{table}: missing columns {', '.join(missing)}")
        return (len(errors) == 0, errors)


RESOLUTION_MIGRATIONS = [
    m for m in FAILURE_ATLAS_MIGRATIONS if m.version >= 31
]

MIGRATION_SOURCES = {
    "runs": RUNS_MIGRATIONS,
    "failure_atlas": FAILURE_ATLAS_MIGRATIONS,
    "resolution_intelligence": RESOLUTION_MIGRATIONS,
    "beta_operations": BETA_MIGRATIONS,
}


def migrate_if_needed(db_path: Optional[str] = None) -> None:
    engine = MigrationEngine(db_path)
    try:
        for source, migrations in MIGRATION_SOURCES.items():
            state = engine.migrate(source, migrations)
            if not state.ok:
                raise RuntimeError(f"Schema migration failed for {source}: {state.error}")
        ok, errors = engine.validate_runtime_schema()
        if not ok:
            raise RuntimeError("Schema validation failed: " + "; ".join(errors))
    finally:
        engine.close()
