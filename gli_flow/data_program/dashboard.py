import json
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from gli_flow.database.migrations import _get_db_path
from gli_flow.data_program.growth_tracker import AtlasGrowthTracker, ExecutionTracker

log = logging.getLogger(__name__)


class DatasetDashboard:
    def __init__(self, db_path: Optional[str] = None, include_heuristic: bool = False, include_unverified: bool = False):
        self._db_path = db_path or _get_db_path()
        self._atlas = AtlasGrowthTracker(self._db_path, include_heuristic=include_heuristic, include_unverified=include_unverified)
        self._exec = ExecutionTracker(self._db_path)
        self.classifications = ["VERIFIED"]
        if include_heuristic:
            self.classifications.append("HEURISTIC")
        if include_unverified:
            self.classifications.append("UNVERIFIED")
        self.placeholders = ",".join("?" for _ in self.classifications)

    def _conn(self):
        return sqlite3.connect(self._db_path)

    def atlas_metrics(self) -> Dict[str, Any]:
        return self._atlas.summary()

    def execution_metrics(self) -> Dict[str, Any]:
        return self._exec.summary()

    def resolution_quality_metrics(self) -> Dict[str, Any]:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM resolution_patterns").fetchone()[0]
            trusted = conn.execute(
                "SELECT COUNT(*) FROM resolution_patterns WHERE trust_level = 'HIGH'"
            ).fetchone()[0]
            reviewed = conn.execute(
                "SELECT COUNT(*) FROM resolution_patterns WHERE engineer_confirmations > 0"
            ).fetchone()[0]
            avg_trust = conn.execute(
                "SELECT AVG(trust_score) FROM resolution_patterns WHERE trust_score IS NOT NULL"
            ).fetchone()[0] or 0.0
            avg_success = conn.execute(
                "SELECT AVG(CAST(success_count AS REAL) / NULLIF(success_count + failure_count, 0)) FROM resolution_patterns WHERE success_count + failure_count > 0"
            ).fetchone()[0] or 0.0
            tracked = conn.execute(
                "SELECT COUNT(DISTINCT failure_type) FROM resolution_patterns"
            ).fetchone()[0] or 0
            return {
                "total_patterns": total,
                "high_trust_patterns": trusted,
                "reviewed_patterns": reviewed,
                "avg_trust_score": round(avg_trust, 4),
                "avg_success_rate": round(avg_success, 4),
                "tracked_failure_types": tracked,
            }

    def trust_metrics(self) -> Dict[str, Any]:
        with self._conn() as conn:
            with_trust = conn.execute(
                f"SELECT COUNT(*) FROM failure_atlas_entries WHERE confidence IS NOT NULL AND detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()[0]
            avg_conf = conn.execute(
                f"SELECT AVG(confidence) FROM failure_atlas_entries WHERE confidence IS NOT NULL AND detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()[0] or 0.0
            resolved = conn.execute(
                f"SELECT COUNT(*) FROM failure_atlas_entries WHERE fix_applied = 1 AND detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()[0]
            return {
                "entries_with_trust": with_trust,
                "avg_confidence": round(avg_conf, 4),
                "resolved_entries": resolved,
            }

    def prediction_coverage_metrics(self) -> Dict[str, Any]:
        with self._conn() as conn:
            total_runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0] or 0
            with_predictions = conn.execute(
                f"SELECT COUNT(DISTINCT run_id) FROM failure_atlas_entries WHERE detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()[0] or 0
            drc_entries = conn.execute(
                f"SELECT COUNT(*) FROM failure_atlas_entries WHERE failure_type LIKE '%DRC%' AND detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()[0] or 0
            timing_entries = conn.execute(
                f"SELECT COUNT(*) FROM failure_atlas_entries WHERE failure_type LIKE '%Tim%' AND detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()[0] or 0
            lvs_entries = conn.execute(
                f"SELECT COUNT(*) FROM failure_atlas_entries WHERE failure_type LIKE '%LVS%' AND detection_classification IN ({self.placeholders})",
                self.classifications
            ).fetchone()[0] or 0
            return {
                "total_runs": total_runs,
                "runs_with_entries": with_predictions,
                "prediction_coverage_percent": round(
                    (with_predictions / total_runs * 100) if total_runs > 0 else 0, 1
                ),
                "drc_entry_count": drc_entries,
                "timing_entry_count": timing_entries,
                "lvs_entry_count": lvs_entries,
            }

    def full_dashboard(self) -> Dict[str, Any]:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "atlas": self.atlas_metrics(),
            "execution_records": self.execution_metrics(),
            "resolutions": self.resolution_quality_metrics(),
            "trust": self.trust_metrics(),
            "prediction_coverage": self.prediction_coverage_metrics(),
        }

    def render_markdown(self) -> str:
        d = self.full_dashboard()
        lines = []
        lines.append("## Dataset Scale Dashboard")
        lines.append("")
        lines.append(f"**Generated**: {d['generated_at']}")
        lines.append("")
        lines.append("### Atlas Growth")
        lines.append("")
        lines.append(f"| Metric | Value | Target | % |")
        lines.append(f"|---|---|---|---|")
        a = d["atlas"]
        lines.append(f"| Signatures | {a['current_signatures']} | {a['target_signatures']} | {a['coverage_percent']}% |")
        lines.append(f"| Entries | {a['current_entries']} | -- | -- |")
        lines.append(f"| Growth Rate | {a['growth_rate_per_day']}/day | -- | -- |")
        lines.append(f"| Failure Types | {len(a['distinct_failure_types'])} | -- | -- |")
        lines.append(f"| Designs | {len(a['distinct_designs'])} | -- | -- |")
        lines.append("")
        lines.append("### Execution Records")
        lines.append("")
        lines.append(f"| Metric | Value | Target | % |")
        lines.append(f"|---|---|---|---|")
        e = d["execution_records"]
        lines.append(f"| Intelligence Records | {e['execution_intelligence_records']} | -- | -- |")
        lines.append(f"| Telemetry Records | {e['telemetry_execution_records']} | -- | -- |")
        lines.append(f"| Resolution Patterns | {e['resolution_patterns']} | -- | -- |")
        lines.append(f"| Total | {e['total_intelligence_records']} | {e['target_records']} | {round(e['total_intelligence_records']/max(e['target_records'],1)*100,1)}% |")
        lines.append(f"| Total Runs | {e['run_count']} | -- | -- |")
        lines.append("")
        lines.append("### Resolution Quality")
        lines.append("")
        rq = d["resolutions"]
        lines.append(f"| Metric | Value |")
        lines.append(f"|---|---|")
        lines.append(f"| Total Patterns | {rq['total_patterns']} |")
        lines.append(f"| High Trust | {rq['high_trust_patterns']} |")
        lines.append(f"| Reviewed | {rq['reviewed_patterns']} |")
        lines.append(f"| Avg Trust Score | {rq['avg_trust_score']} |")
        lines.append(f"| Avg Success Rate | {rq['avg_success_rate']} |")
        lines.append(f"| Tracked Failure Types | {rq['tracked_failure_types']} |")
        lines.append("")
        lines.append("### Trust Distribution")
        lines.append("")
        t = d["trust"]
        lines.append(f"| Metric | Value |")
        lines.append(f"|---|---|")
        lines.append(f"| Entries With Trust Score | {t['entries_with_trust']} |")
        lines.append(f"| Avg Confidence | {t['avg_confidence']} |")
        lines.append(f"| Resolved Entries | {t['resolved_entries']} |")
        lines.append("")
        lines.append("### Prediction Coverage")
        lines.append("")
        pc = d["prediction_coverage"]
        lines.append(f"| Metric | Value |")
        lines.append(f"|---|---|")
        lines.append(f"| Total Runs | {pc['total_runs']} |")
        lines.append(f"| Runs with Atlas Entries | {pc['runs_with_entries']} |")
        lines.append(f"| Prediction Coverage | {pc['prediction_coverage_percent']}% |")
        lines.append(f"| DRC Entries | {pc['drc_entry_count']} |")
        lines.append(f"| Timing Entries | {pc['timing_entry_count']} |")
        lines.append(f"| LVS Entries | {pc['lvs_entry_count']} |")
        return "\n".join(lines)
