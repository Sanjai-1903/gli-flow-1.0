import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

log = logging.getLogger(__name__)

from gli_flow.database.factory import create_provider
from gli_flow.database.migrations import _get_db_path
from failure_atlas.intelligence_model import ExecutionIntelligenceRecord


REQUIRED_FIELDS = [
    "id", "run_id", "failure_id", "failure_type", "severity",
    "title", "description", "recommended_fix", "confidence",
    "signature", "detected_at", "domain", "category",
]

RESOLUTION_FIELDS = [
    "fix_applied", "fix_type", "fix_description", "fix_run_id",
    "before_metrics", "after_metrics", "resolution_confidence",
]


class FailureAtlasRepository:

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = _get_db_path()
        supabase_token = os.environ.get("SUPABASE_API_TOKEN")
        supabase_ref = os.environ.get("SUPABASE_PROJECT_REF")
        if supabase_token and supabase_ref:
            self._provider = create_provider()
        else:
            self._provider = create_provider(db_path=self.db_path)

    def close(self):
        if self._provider:
            self._provider.close()

    @staticmethod
    def classify_entry_level(severity: str) -> str:
        severity = (severity or "").upper()
        if severity == "INFO":
            return "INFO"
        if severity in {"LOW", "MEDIUM", "WARNING"}:
            return "WARNING"
        return "FAILURE"

    @staticmethod
    def _decode_row(row: Dict[str, Any]) -> Dict[str, Any]:
        for key in ("recommended_fix", "evidence", "before_metrics", "after_metrics"):
            val = row.get(key)
            if isinstance(val, str) and val:
                try:
                    row[key] = json.loads(val)
                except json.JSONDecodeError:
                    pass
        if isinstance(row.get("fix_applied"), int):
            row["fix_applied"] = bool(row["fix_applied"])
        return row

    def _raw_execute(self, sql: str, params=None):
        self._provider.execute(sql, params)
        return self._provider

    def _fetchone(self, sql: str, params=None) -> Optional[Dict[str, Any]]:
        row = self._provider.fetchone(sql, params)
        if row is None:
            return None
        return self._decode_row(row)

    def _fetchall(self, sql: str, params=None) -> List[Dict[str, Any]]:
        rows = self._provider.fetchall(sql, params)
        return [self._decode_row(row) for row in rows]

    def _execute(self, sql: str, params=None):
        self._provider.execute(sql, params)

    def insert_entry_if_not_exists(self, entry: Dict[str, Any]) -> str:
        """Insert only if no entry with same (run_id, failure_type, signature) exists.
        Returns the id of the existing or new entry."""
        existing = self._fetchone(
            "SELECT id FROM failure_atlas_entries WHERE run_id = ? AND failure_type = ? AND signature = ?",
            (entry.get("run_id", ""), entry.get("failure_type", ""), entry.get("signature", "")),
        )
        if existing:
            return existing["id"]
        return self.insert_entry(entry)

    def insert_entry(self, entry: Dict[str, Any]) -> str:
        entry.setdefault("id", str(uuid.uuid4()))
        entry.setdefault("failure_id", entry["id"])
        entry.setdefault("detected_at", datetime.now(timezone.utc).isoformat())
        entry.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        entry.setdefault("confidence", 0.8)
        entry.setdefault("entry_level", self.classify_entry_level(entry.get("severity", "MEDIUM")))

        cols = [
            "id", "run_id", "failure_id", "failure_type", "severity",
            "title", "description", "recommended_fix", "confidence",
            "signature", "domain", "category", "evidence",
            "detected_at", "created_at", "parent_run_id",
            "fix_applied", "fix_type", "fix_description", "fix_run_id",
            "before_metrics", "after_metrics", "resolution_confidence",
            "entry_level", "design_name", "detection_classification",
        ]
        placeholders = ", ".join("?" for _ in cols)
        update_set = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != "id")
        sql = (
            f"INSERT INTO failure_atlas_entries ({', '.join(cols)}) "
            f"VALUES ({placeholders}) "
            f"ON CONFLICT (id) DO UPDATE SET {update_set}"
        )
        self._execute(
            sql,
            (
                entry["id"],
                entry.get("run_id", ""),
                entry.get("failure_id", entry["id"]),
                entry.get("failure_type", "UNKNOWN"),
                entry.get("severity", "MEDIUM"),
                entry.get("title", ""),
                entry.get("description", ""),
                json.dumps(entry.get("recommended_fix", "")),
                entry.get("confidence", 0.8),
                entry.get("signature", ""),
                entry.get("domain", ""),
                entry.get("category", ""),
                json.dumps(entry.get("evidence", {})),
                entry.get("detected_at"),
                entry.get("created_at"),
                entry.get("parent_run_id"),
                bool(entry.get("fix_applied")),
                entry.get("fix_type", ""),
                entry.get("fix_description", ""),
                entry.get("fix_run_id", ""),
                json.dumps(entry.get("before_metrics", {})),
                json.dumps(entry.get("after_metrics", {})),
                entry.get("resolution_confidence", ""),
                entry.get("entry_level", "FAILURE"),
                entry.get("design_name", ""),
                entry.get("detection_classification", ""),
            ),
        )
        return entry["id"]

    def get_entries_for_run(self, run_id: str) -> List[Dict[str, Any]]:
        return self._fetchall(
            "SELECT * FROM failure_atlas_entries WHERE run_id = ? ORDER BY detected_at DESC",
            (run_id,),
        )

    def get_failures_for_run(self, run_id: str) -> List[Dict[str, Any]]:
        return self.get_entries_for_run(run_id)

    def search_entries(self, failure_type: Optional[str] = None, severity: Optional[str] = None,
                       domain: Optional[str] = None, limit: int = 50, offset: int = 0,
                       search: Optional[str] = None, entry_level: Optional[str] = None,
                       design_name: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM failure_atlas_entries WHERE 1=1"
        params = []
        if failure_type:
            query += " AND failure_type = ?"
            params.append(failure_type)
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        if entry_level:
            query += " AND entry_level = ?"
            params.append(entry_level)
        if design_name:
            query += " AND design_name = ?"
            params.append(design_name)
        if search:
            query += " AND (title LIKE ? OR description LIKE ? OR failure_type LIKE ? OR design_name LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])
        query += " ORDER BY detected_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        return self._fetchall(query, params)

    def get_all_failures(self, limit: int = 50, offset: int = 0,
                         severity: Optional[str] = None,
                         failure_type: Optional[str] = None,
                         search: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.search_entries(
            failure_type=failure_type,
            severity=severity,
            limit=limit,
            offset=offset,
            search=search,
        )

    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        return self._fetchone(
            "SELECT * FROM failure_atlas_entries WHERE id = ?",
            (entry_id,),
        )

    def get_failure_by_id(self, failure_id: str) -> Optional[Dict[str, Any]]:
        row = self.get_entry(failure_id)
        if row:
            return row
        return self._fetchone(
            "SELECT * FROM failure_atlas_entries WHERE failure_id = ?",
            (failure_id,),
        )

    def count_entries(self, failure_type: Optional[str] = None) -> int:
        query = "SELECT COUNT(*) FROM failure_atlas_entries WHERE 1=1"
        params = []
        if failure_type:
            query += " AND failure_type = ?"
            params.append(failure_type)
        return self._provider.fetchval(query, params) or 0

    def get_failure_count(self, severity: Optional[str] = None,
                          failure_type: Optional[str] = None) -> int:
        query = "SELECT COUNT(*) FROM failure_atlas_entries WHERE 1=1"
        params = []
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        if failure_type:
            query += " AND failure_type = ?"
            params.append(failure_type)
        return self._provider.fetchval(query, params) or 0

    def update_resolution(self, entry_id: str = None, resolution: Dict[str, Any] = None,
                          *legacy_args, failure_id: str = None, fix_type: str = "", fix_description: str = "",
                          fix_run_id: str = "", before_metrics: Dict[str, Any] = None,
                          after_metrics: Dict[str, Any] = None):
        if entry_id is None:
            entry_id = failure_id
        if resolution is None:
            resolution = {
                "fix_applied": True,
                "fix_type": fix_type,
                "fix_description": fix_description,
                "fix_run_id": fix_run_id,
                "before_metrics": before_metrics or {},
                "after_metrics": after_metrics or {},
            }
        elif isinstance(resolution, str):
            if legacy_args:
                fix_description = legacy_args[0]
            if len(legacy_args) > 1:
                fix_run_id = legacy_args[1]
            resolution = {
                "fix_applied": True,
                "fix_type": resolution,
                "fix_description": fix_description,
                "fix_run_id": fix_run_id,
                "before_metrics": before_metrics or {},
                "after_metrics": after_metrics or {},
            }
        before = resolution.get("before_metrics") or {}
        after = resolution.get("after_metrics") or {}
        if not resolution.get("resolution_confidence"):
            confidence = "MEDIUM"
            if before and after:
                before_wns = before.get("wns", 0.0)
                after_wns = after.get("wns", 0.0)
                confidence = "HIGH" if after_wns > before_wns else "LOW"
            resolution["resolution_confidence"] = confidence
        self._execute(
            """
            UPDATE failure_atlas_entries SET
                fix_applied = ?,
                fix_type = ?,
                fix_description = ?,
                fix_run_id = ?,
                before_metrics = ?,
                after_metrics = ?,
                resolution_confidence = ?
            WHERE id = ?
            """,
            (
                bool(resolution.get("fix_applied")),
                resolution.get("fix_type", ""),
                resolution.get("fix_description", ""),
                resolution.get("fix_run_id", ""),
                json.dumps(resolution.get("before_metrics", {})),
                json.dumps(resolution.get("after_metrics", {})),
                resolution.get("resolution_confidence", ""),
                entry_id,
            ),
        )
        return True

    def get_analytics_summary(self) -> Dict[str, Any]:
        total = self.get_failure_count()
        fixed = self._fetchone("SELECT COUNT(*) as cnt FROM failure_atlas_entries WHERE fix_applied = 1")["cnt"]
        return {
            "total_failures": total,
            "fixed_count": fixed,
            "unfixed_count": total - fixed,
            "success_rate": round(fixed / total * 100, 1) if total else 0,
        }

    def get_common_failures(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._fetchall(
            """
            SELECT failure_type, COUNT(*) as count
            FROM failure_atlas_entries
            GROUP BY failure_type
            ORDER BY count DESC
            LIMIT ?
            """,
            (limit,),
        )

    def get_fix_effectiveness(self, min_samples: int = 3) -> List[Dict[str, Any]]:
        return self._fetchall(
            """
            SELECT failure_type, fix_type, COUNT(*) as sample_size,
                   ROUND(CAST(SUM(fix_applied) AS FLOAT) / COUNT(*) * 100, 1) as success_rate
            FROM failure_atlas_entries
            WHERE fix_type IS NOT NULL AND fix_type != ''
            GROUP BY failure_type, fix_type
            HAVING sample_size >= ?
            ORDER BY sample_size DESC
            """,
            (min_samples,),
        )

    def get_qor_improvements(self) -> List[Dict[str, Any]]:
        return self._fetchall(
            """
            SELECT fix_type, COUNT(*) as sample_size,
                   COALESCE(AVG(json_extract(after_metrics, '$.wns') - json_extract(before_metrics, '$.wns')), 0) as avg_wns_improvement,
                   COALESCE(AVG(json_extract(after_metrics, '$.tns') - json_extract(before_metrics, '$.tns')), 0) as avg_tns_improvement
            FROM failure_atlas_entries
            WHERE fix_type IS NOT NULL AND fix_type != ''
            GROUP BY fix_type
            ORDER BY avg_wns_improvement DESC
            """
        )

    def get_failure_trends(self) -> Dict[str, Any]:
        return {
            "failure_distribution": self._fetchall(
                "SELECT failure_type, COUNT(*) as count FROM failure_atlas_entries GROUP BY failure_type ORDER BY count DESC"
            ),
            "daily_counts": self._fetchall(
                "SELECT DATE(detected_at) as date, COUNT(*) as count FROM failure_atlas_entries GROUP BY DATE(detected_at) ORDER BY date DESC"
            ),
        }

    def get_mttr_by_type(self) -> List[Dict[str, Any]]:
        return self._fetchall(
            """
            SELECT failure_type, COUNT(*) as sample_size,
                   ROUND(CAST(SUM(CASE WHEN fix_applied = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as resolution_rate
            FROM failure_atlas_entries
            GROUP BY failure_type
            ORDER BY sample_size DESC
            """
        )

    def similar_failures(self, failure_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self._fetchall(
            """
            SELECT failure_type, fix_type, COUNT(*) as sample_size,
                   ROUND(CAST(SUM(fix_applied) AS FLOAT) / COUNT(*) * 100, 1) as success_rate
            FROM failure_atlas_entries
            WHERE failure_type = ?
            GROUP BY failure_type, fix_type
            ORDER BY sample_size DESC
            LIMIT ?
            """,
            (failure_type, limit),
        )

    def get_regression_events(self) -> List[Dict[str, Any]]:
        return self._fetchall(
            """
            SELECT f1.*
            FROM failure_atlas_entries f1
            WHERE f1.detected_at = (
                SELECT MIN(f2.detected_at)
                FROM failure_atlas_entries f2
                WHERE f2.failure_type = f1.failure_type
            )
            ORDER BY f1.detected_at DESC
            """
        )

    def delete_failure_level_entries_for_run(self, run_id: str) -> int:
        self._provider.execute(
            "DELETE FROM failure_atlas_entries WHERE run_id = ? AND entry_level = 'FAILURE'",
            (run_id,),
        )
        return self._provider.rowcount

    def get_statistics(self) -> Dict[str, Any]:
        try:
            total = self._fetchone("SELECT COUNT(*) as cnt FROM failure_atlas_entries")["cnt"]
            fixed = self._fetchone("SELECT COUNT(*) as cnt FROM failure_atlas_entries WHERE fix_applied = 1")["cnt"]
            return {"total_entries": total, "fixed_entries": fixed, "fix_rate": round(fixed / total * 100, 1) if total else 0.0}
        except Exception as e:
            log.error(f"Failed to get failure atlas statistics: {e}")
            return {"total_entries": -1, "fixed_entries": -1, "fix_rate": -1.0, "error": str(e)}

    def get_top_failures(self, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            return self._fetchall(
                """
                SELECT failure_type, severity, COUNT(*) as occurrences,
                       ROUND(CAST(COUNT(*) AS FLOAT) / (SELECT COUNT(*) FROM failure_atlas_entries) * 100, 1) as percentage
                FROM failure_atlas_entries
                GROUP BY failure_type, severity
                ORDER BY occurrences DESC LIMIT ?
                """,
                (limit,),
            )
        except Exception as e:
            log.warning(f"Failed to get top failures: {e}")
            return []

    def get_domain_summary(self) -> List[Dict[str, Any]]:
        try:
            return self._fetchall(
                """
                SELECT domain, COUNT(*) as occurrences,
                       ROUND(CAST(COUNT(*) AS FLOAT) / (SELECT COUNT(*) FROM failure_atlas_entries) * 100, 1) as percentage
                FROM failure_atlas_entries
                GROUP BY domain ORDER BY occurrences DESC
                """,
            )
        except Exception as e:
            log.warning(f"Failed to get domain summary: {e}")
            return []

    def get_resolution_rate_by_type(self) -> List[Dict[str, Any]]:
        try:
            return self._fetchall(
                """
                SELECT failure_type,
                       COUNT(*) as total,
                       SUM(CASE WHEN fix_applied = 1 THEN 1 ELSE 0 END) as fixed,
                       ROUND(CAST(SUM(CASE WHEN fix_applied = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as fix_rate
                FROM failure_atlas_entries
                GROUP BY failure_type ORDER BY total DESC
                """,
            )
        except Exception as e:
            log.warning(f"Failed to get resolution rate: {e}")
            return []

    def get_severity_distribution(self) -> List[Dict[str, Any]]:
        try:
            return self._fetchall(
                """
                SELECT severity, COUNT(*) as occurrences,
                       ROUND(CAST(COUNT(*) AS FLOAT) / (SELECT COUNT(*) FROM failure_atlas_entries) * 100, 1) as percentage
                FROM failure_atlas_entries
                GROUP BY severity ORDER BY occurrences DESC
                """,
            )
        except Exception as e:
            log.warning(f"Failed to get severity distribution: {e}")
            return []

    def get_related_entries(self, entry_id: str) -> List[Dict[str, Any]]:
        entry = self.get_entry(entry_id)
        if not entry:
            return []
        try:
            return self._fetchall(
                """
                SELECT * FROM failure_atlas_entries
                WHERE (failure_type = ? OR domain = ?) AND id != ?
                ORDER BY detected_at DESC LIMIT 5
                """,
                (entry.get("failure_type", ""), entry.get("domain", ""), entry_id),
            )
        except Exception:
            return []

    def insert_intelligence_record(self, record: ExecutionIntelligenceRecord) -> str:
        record_id = str(uuid.uuid4())
        self._execute(
            """
            INSERT INTO execution_intelligence (
                id, event_type, tool, stage, severity, fingerprint,
                timestamp, failure_context, root_cause_analysis, resolution,
                trust_score, outcome
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                record.event_type,
                record.tool,
                record.stage,
                record.severity,
                record.fingerprint,
                record.timestamp,
                json.dumps(record.failure_context),
                json.dumps(record.root_cause_analysis),
                json.dumps(record.resolution),
                record.trust_score,
                record.outcome,
            ),
        )
        return record_id

    def get_intelligence_records(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        return self._fetchall(
            "SELECT * FROM execution_intelligence ORDER BY timestamp DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )

