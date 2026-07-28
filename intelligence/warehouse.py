import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

from intelligence.intelligence_records import ExecutionIntelligenceRecord
from intelligence.recommendation_outcome_record import RecommendationOutcomeRecord
from gli_flow.database.migrations import _get_db_path


@dataclass
class TelemetryWarehouse:
    execution_records: List[ExecutionIntelligenceRecord] = field(default_factory=list)
    recommendation_records: List[RecommendationOutcomeRecord] = field(default_factory=list)

    def __post_init__(self):
        self._db_path = _get_db_path()
        self._init_tables()

    def _get_conn(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        conn = self._get_conn()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_execution_records (
                    id TEXT PRIMARY KEY,
                    failure TEXT,
                    root_cause TEXT,
                    resolution TEXT,
                    trust_score REAL,
                    telemetry_summary TEXT,
                    outcome TEXT,
                    created_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_recommendation_records (
                    id TEXT PRIMARY KEY,
                    recommendation_id TEXT,
                    run_id TEXT,
                    failure_type TEXT,
                    recommendation TEXT,
                    trust_level REAL,
                    accepted INTEGER,
                    rejected INTEGER,
                    outcome TEXT,
                    timestamp TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_telemetry_exec_failure
                ON telemetry_execution_records(failure)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_telemetry_rec_failure
                ON telemetry_recommendation_records(failure_type)
            """)
            conn.commit()
        finally:
            conn.close()

    def store_execution(self, record: ExecutionIntelligenceRecord):
        self.execution_records.append(record)
        conn = self._get_conn()
        try:
            conn.execute(
                """
                INSERT INTO telemetry_execution_records
                (id, failure, root_cause, resolution, trust_score, telemetry_summary, outcome, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    record.failure,
                    record.root_cause,
                    record.resolution,
                    record.trust_score,
                    json.dumps(record.telemetry_summary),
                    record.outcome,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def store_recommendation(self, record: RecommendationOutcomeRecord):
        self.recommendation_records.append(record)
        conn = self._get_conn()
        try:
            conn.execute(
                """
                INSERT INTO telemetry_recommendation_records
                (id, recommendation_id, run_id, failure_type, recommendation, trust_level,
                 accepted, rejected, outcome, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    record.recommendation_id,
                    record.run_id,
                    record.failure_type,
                    record.recommendation,
                    record.trust_level,
                    1 if record.accepted else 0,
                    1 if record.rejected else 0,
                    record.outcome,
                    record.timestamp.isoformat() if hasattr(record.timestamp, 'isoformat') else str(record.timestamp),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def get_execution_records_by_failure(self, failure_type: str) -> List[ExecutionIntelligenceRecord]:
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "SELECT * FROM telemetry_execution_records WHERE failure = ? ORDER BY created_at DESC",
                (failure_type,),
            )
            rows = cursor.fetchall()
            return [
                ExecutionIntelligenceRecord(
                    failure=row["failure"],
                    root_cause=row["root_cause"],
                    resolution=row["resolution"],
                    trust_score=row["trust_score"],
                    telemetry_summary=json.loads(row["telemetry_summary"]) if row["telemetry_summary"] else {},
                    outcome=row["outcome"],
                )
                for row in rows
            ]
        finally:
            conn.close()

    def get_successful_recommendations(self, failure_type: str) -> List[RecommendationOutcomeRecord]:
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "SELECT * FROM telemetry_recommendation_records WHERE failure_type = ? AND outcome = 'SUCCESS' ORDER BY timestamp DESC",
                (failure_type,),
            )
            rows = cursor.fetchall()
            return [
                RecommendationOutcomeRecord(
                    recommendation_id=row["recommendation_id"],
                    run_id=row["run_id"],
                    failure_type=row["failure_type"],
                    recommendation=row["recommendation"],
                    trust_level=row["trust_level"],
                    accepted=bool(row["accepted"]),
                    rejected=bool(row["rejected"]),
                    outcome=row["outcome"],
                    timestamp=row["timestamp"],
                )
                for row in rows
            ]
        finally:
            conn.close()

    def get_all_failures(self) -> List[str]:
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "SELECT DISTINCT failure FROM telemetry_execution_records ORDER BY failure"
            )
            return [row["failure"] for row in cursor.fetchall()]
        finally:
            conn.close()

    def count_records(self) -> int:
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT COUNT(*) as cnt FROM telemetry_execution_records")
            return cursor.fetchone()["cnt"]
        finally:
            conn.close()
