import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from gli_flow.database.migrations import _get_db_path

log = logging.getLogger(__name__)


class AtlasGrowthTracker:
    TARGET_SIGNATURES = 100

    def __init__(self, db_path: Optional[str] = None, include_heuristic: bool = False, include_unverified: bool = False):
        self._db_path = db_path or _get_db_path()
        self.classifications = ["VERIFIED"]
        if include_heuristic:
            self.classifications.append("HEURISTIC")
        if include_unverified:
            self.classifications.append("UNVERIFIED")
        self.placeholders = ",".join("?" for _ in self.classifications)

    def _conn(self):
        return sqlite3.connect(self._db_path)

    def current_signature_count(self) -> int:
        with self._conn() as conn:
            row = conn.execute(
                f"SELECT COUNT(DISTINCT signature) FROM failure_atlas_entries WHERE signature IS NOT NULL AND signature != '' AND detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()
            return row[0] if row else 0

    def current_entry_count(self) -> int:
        with self._conn() as conn:
            row = conn.execute(
                f"SELECT COUNT(*) FROM failure_atlas_entries WHERE detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()
            return row[0] if row else 0

    def distinct_failure_types(self) -> list[str]:
        with self._conn() as conn:
            rows = conn.execute(
                f"SELECT DISTINCT failure_type FROM failure_atlas_entries WHERE detection_classification IN ({self.placeholders}) ORDER BY failure_type",
                self.classifications
            ).fetchall()
            return [r[0] for r in rows if r[0]]

    def distinct_designs(self) -> list[str]:
        with self._conn() as conn:
            rows = conn.execute(
                f"SELECT DISTINCT design_name FROM failure_atlas_entries WHERE design_name IS NOT NULL AND design_name != '' AND detection_classification IN ({self.placeholders}) ORDER BY design_name",
                self.classifications
            ).fetchall()
            return [r[0] for r in rows]

    def new_signatures_since(self, since: str) -> int:
        with self._conn() as conn:
            row = conn.execute(
                f"SELECT COUNT(DISTINCT signature) FROM failure_atlas_entries WHERE created_at > ? AND signature IS NOT NULL AND signature != '' AND detection_classification IN ({self.placeholders})",
                (since, *self.classifications),
            ).fetchone()
            return row[0] if row else 0

    def growth_rate_per_day(self) -> float:
        with self._conn() as conn:
            row = conn.execute(
                f"SELECT MIN(created_at), MAX(created_at) FROM failure_atlas_entries WHERE signature IS NOT NULL AND signature != '' AND detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()
            if not row or not row[0] or not row[1]:
                return 0.0
            try:
                first = datetime.fromisoformat(row[0])
                last = datetime.fromisoformat(row[1])
            except (ValueError, TypeError):
                return 0.0
            days = (last - first).total_seconds() / 86400
            if days <= 0:
                return 0.0
            count = self.current_signature_count()
            return round(count / days, 2)

    def coverage_percent(self) -> float:
        current = self.current_signature_count()
        return round((current / self.TARGET_SIGNATURES) * 100, 1)

    def summary(self) -> Dict[str, Any]:
        sigs = self.current_signature_count()
        entries = self.current_entry_count()
        return {
            "current_signatures": sigs,
            "target_signatures": self.TARGET_SIGNATURES,
            "current_entries": entries,
            "growth_rate_per_day": self.growth_rate_per_day(),
            "coverage_percent": self.coverage_percent(),
            "distinct_failure_types": self.distinct_failure_types(),
            "distinct_designs": self.distinct_designs(),
            "remaining_to_target": max(0, self.TARGET_SIGNATURES - sigs),
        }


class ExecutionTracker:
    TARGET_RECORDS = 1000

    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or _get_db_path()

    def _conn(self):
        return sqlite3.connect(self._db_path)

    def execution_intelligence_count(self) -> int:
        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) FROM execution_intelligence").fetchone()
            return row[0] if row else 0

    def telemetry_execution_count(self) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM telemetry_execution_records"
            ).fetchone()
            return row[0] if row else 0

    def resolution_pattern_count(self) -> int:
        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) FROM resolution_patterns").fetchone()
            return row[0] if row else 0

    def telemetry_recommendation_count(self) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM telemetry_recommendation_records"
            ).fetchone()
            return row[0] if row else 0

    def total_records(self) -> int:
        return (
            self.execution_intelligence_count()
            + self.telemetry_execution_count()
            + self.resolution_pattern_count()
            + self.telemetry_recommendation_count()
        )

    def run_count(self) -> int:
        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) FROM runs").fetchone()
            return row[0] if row else 0

    def success_rate(self) -> float:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*), SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) FROM runs"
            ).fetchone()
            if row and row[0] and row[0] > 0:
                return round((row[1] or 0) / row[0] * 100, 1)
            return 0.0

    def summary(self) -> Dict[str, Any]:
        total = self.total_records()
        return {
            "execution_intelligence_records": self.execution_intelligence_count(),
            "telemetry_execution_records": self.telemetry_execution_count(),
            "resolution_patterns": self.resolution_pattern_count(),
            "telemetry_recommendation_records": self.telemetry_recommendation_count(),
            "total_intelligence_records": total,
            "target_records": self.TARGET_RECORDS,
            "remaining_to_target": max(0, self.TARGET_RECORDS - total),
            "run_count": self.run_count(),
            "run_success_rate_percent": self.success_rate(),
        }


class DatasetMilestones:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or _get_db_path()
        self._atlas = AtlasGrowthTracker(self._db_path)
        self._exec = ExecutionTracker(self._db_path)

    def evaluate(self) -> Dict[str, Any]:
        sigs = self._atlas.current_signature_count()
        entries = self._atlas.current_entry_count()
        records = self._exec.total_records()

        levels = {
            1: {"name": "Level 1", "signature_target": 100, "achieved": sigs >= 100},
            2: {"name": "Level 2", "signature_target": 500, "achieved": sigs >= 500},
            3: {"name": "Level 3", "signature_target": 1000, "achieved": sigs >= 1000},
            4: {
                "name": "Level 4",
                "record_target": 10000,
                "achieved": records >= 10000,
            },
        }

        current_level = 0
        for lid, ldef in sorted(levels.items()):
            if ldef.get("achieved"):
                current_level = lid

        return {
            "current_signatures": sigs,
            "current_records": records,
            "current_entries": entries,
            "current_level": current_level,
            "levels": levels,
            "next_level": current_level + 1 if current_level < 4 else None,
            "next_level_name": levels.get(current_level + 1, {}).get("name")
            if current_level < 4
            else None,
            "next_level_remaining_signatures": max(
                0, (levels.get(current_level + 1, {}).get("signature_target", 0) or 0) - sigs
            ),
            "next_level_remaining_records": max(
                0, (levels.get(current_level + 1, {}).get("record_target", 0) or 0) - records
            ),
        }
