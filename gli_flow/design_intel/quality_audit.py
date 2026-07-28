import json
import sqlite3
import logging
from typing import Dict, Any, List, Optional
from gli_flow.database.migrations import _get_db_path

log = logging.getLogger(__name__)


class DatasetQualityAudit:
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

    def audit_failure_atlas(self) -> Dict[str, Any]:
        with self._conn() as conn:
            total = conn.execute(f"SELECT COUNT(*) FROM failure_atlas_entries WHERE detection_classification IN ({self.placeholders})", self.classifications).fetchone()[0]
            with_design = conn.execute(
                f"SELECT COUNT(*) FROM failure_atlas_entries WHERE design_name IS NOT NULL AND design_name != '' AND detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()[0]
            with_type = conn.execute(f"SELECT COUNT(*) FROM failure_atlas_entries WHERE failure_type IS NOT NULL AND failure_type != '' AND detection_classification IN ({self.placeholders})", self.classifications).fetchone()[0]
            with_severity = conn.execute(f"SELECT COUNT(*) FROM failure_atlas_entries WHERE severity IS NOT NULL AND severity != '' AND detection_classification IN ({self.placeholders})", self.classifications).fetchone()[0]
            with_signature = conn.execute(f"SELECT COUNT(*) FROM failure_atlas_entries WHERE signature IS NOT NULL AND signature != '' AND detection_classification IN ({self.placeholders})", self.classifications).fetchone()[0]
            distinct_designs = conn.execute(
                f"SELECT COUNT(DISTINCT design_name) FROM failure_atlas_entries WHERE design_name IS NOT NULL AND design_name != '' AND detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()[0]

        return {
            "table": "failure_atlas_entries",
            "total_records": total,
            "with_design_name": with_design,
            "design_name_pct": round(with_design / total * 100, 1) if total > 0 else 0,
            "with_failure_type": with_type,
            "failure_type_pct": round(with_type / total * 100, 1) if total > 0 else 0,
            "with_severity": with_severity,
            "with_signature": with_signature,
            "distinct_designs": distinct_designs,
        }

    def audit_runs(self) -> Dict[str, Any]:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            with_design = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE design_name IS NOT NULL AND design_name != ''"
            ).fetchone()[0]
            with_cells = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE cell_count IS NOT NULL"
            ).fetchone()[0]
            with_wns = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE wns IS NOT NULL"
            ).fetchone()[0]
            distinct_designs = conn.execute(
                "SELECT COUNT(DISTINCT design_name) FROM runs WHERE design_name IS NOT NULL AND design_name != ''"
            ).fetchone()[0]

        return {
            "table": "runs",
            "total_records": total,
            "with_design_name": with_design,
            "design_name_pct": round(with_design / total * 100, 1) if total > 0 else 0,
            "with_cell_count": with_cells,
            "with_wns": with_wns,
            "distinct_designs": distinct_designs,
        }

    def audit_design_profiles(self) -> Dict[str, Any]:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM design_profiles").fetchone()[0]
            with_type = conn.execute(
                "SELECT COUNT(*) FROM design_profiles WHERE design_type != 'unknown'"
            ).fetchone()[0]
            with_classification = conn.execute(
                "SELECT COUNT(*) FROM design_profiles WHERE classification != ''"
            ).fetchone()[0]
            with_cells = conn.execute(
                "SELECT COUNT(*) FROM design_profiles WHERE expected_cell_count > 0"
            ).fetchone()[0]

        return {
            "table": "design_profiles",
            "total_records": total,
            "with_design_type": with_type,
            "with_classification": with_classification,
            "with_cell_count": with_cells,
        }

    def audit_features(self) -> Dict[str, Any]:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM design_features").fetchone()[0]
            with_histogram = conn.execute(
                "SELECT COUNT(*) FROM design_features WHERE fanout_histogram != '[0,0,0,0,0,0,0,0,0,0]'"
            ).fetchone()[0]
            with_depth = conn.execute(
                "SELECT COUNT(*) FROM design_features WHERE logic_depth > 0"
            ).fetchone()[0]

        return {
            "table": "design_features",
            "total_records": total,
            "with_fanout_histogram": with_histogram,
            "with_logic_depth": with_depth,
        }

    def audit_execution_records(self) -> Dict[str, Any]:
        with self._conn() as conn:
            intel_count = conn.execute("SELECT COUNT(*) FROM execution_intelligence").fetchone()[0]
            tele_count = conn.execute("SELECT COUNT(*) FROM telemetry_execution_records").fetchone()[0]

        return {
            "execution_intelligence_count": intel_count,
            "telemetry_execution_count": tele_count,
        }

    def full_audit(self) -> Dict[str, Any]:
        return {
            "failure_atlas": self.audit_failure_atlas(),
            "runs": self.audit_runs(),
            "design_profiles": self.audit_design_profiles(),
            "design_features": self.audit_features(),
            "execution_records": self.audit_execution_records(),
        }

    def check_every_record_has_design_identity(self) -> bool:
        with self._conn() as conn:
            missing = conn.execute(
                f"SELECT COUNT(*) FROM failure_atlas_entries WHERE (design_name IS NULL OR design_name = '') AND detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()[0]
            runs_missing = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE design_name IS NULL OR design_name = ''"
            ).fetchone()[0]
        return missing == 0 and runs_missing == 0

    def check_every_record_has_feature_vector(self) -> bool:
        with self._conn() as conn:
            profiles = conn.execute("SELECT COUNT(*) FROM design_profiles").fetchone()[0]
            features = conn.execute("SELECT COUNT(*) FROM design_features").fetchone()[0]
        return profiles > 0 and features > 0
