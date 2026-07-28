import sqlite3
from datetime import datetime, timezone
from typing import Optional


class TelemetryHealth:
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            from gli_flow.database.migrations import _get_db_path
            self.db_path = _get_db_path()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_health(self) -> dict:
        conn = self._get_connection()
        try:
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM community_telemetry")
            collected = cur.fetchone()[0]

            cur.execute(
                "SELECT COUNT(*) FROM community_telemetry WHERE created_at >= ?",
                (datetime.now(timezone.utc).isoformat()[:10],),
            )
            today = cur.fetchone()[0]

            cur.execute(
                "SELECT created_at FROM community_telemetry ORDER BY created_at DESC LIMIT 1",
            )
            row = cur.fetchone()
            last_event = row[0] if row else None

            cur.execute("SELECT COUNT(*) FROM community_escalations")
            escalations = cur.fetchone()[0]

            cur.execute(
                "SELECT COUNT(*) FROM community_escalations WHERE status = 'open'",
            )
            open_escalations = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM community_unknown_dataset")
            dataset_entries = cur.fetchone()[0]

            cur.execute(
                "SELECT COUNT(*) FROM community_unknown_dataset WHERE resolution_outcome != ''",
            )
            resolved_unknowns = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM resolution_patterns")
            patterns = cur.fetchone()[0]

            audit_stats = self._get_audit_stats(conn)
        finally:
            conn.close()

        upload_success_rate = self._calculate_upload_rate(audit_stats)
        avg_latency = self._calculate_avg_latency(audit_stats)
        queued = self._estimate_queued(audit_stats)

        health_status = self._determine_overall_health(
            collected, upload_success_rate, queued, audit_stats
        )

        return {
            "collected_events": collected,
            "events_today": today,
            "last_event_time": last_event,
            "sanitized_events": audit_stats.get("sanitized", 0),
            "blocked_fields": audit_stats.get("rejected", 0),
            "upload_success_rate": upload_success_rate,
            "upload_failures": audit_stats.get("upload_failures", 0),
            "queued_events": queued,
            "average_upload_latency_ms": avg_latency,
            "last_upload_time": audit_stats.get("last_upload_time"),
            "last_sanitization_time": audit_stats.get("last_sanitized_time"),
            "total_escalations": escalations,
            "open_escalations": open_escalations,
            "dataset_entries": dataset_entries,
            "resolved_unknowns": resolved_unknowns,
            "resolution_patterns": patterns,
            "overall_status": health_status,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    def _get_audit_stats(self, conn) -> dict:
        stats = {
            "sanitized": 0, "rejected": 0, "uploaded": 0,
            "upload_failures": 0, "created": 0,
            "last_upload_time": None, "last_sanitized_time": None,
        }
        try:
            for row in conn.execute(
                "SELECT event_type, COUNT(*) as cnt FROM telemetry_audit_log WHERE status = 'success' GROUP BY event_type"
            ).fetchall():
                key = row["event_type"]
                if key == "event_sanitized":
                    stats["sanitized"] = row["cnt"]
                elif key == "event_uploaded":
                    stats["uploaded"] = row["cnt"]
                elif key == "event_created":
                    stats["created"] = row["cnt"]

            row = conn.execute(
                "SELECT COUNT(*) FROM telemetry_audit_log WHERE event_type = 'event_uploaded' AND status = 'rejected'"
            ).fetchone()
            stats["upload_failures"] = row[0] if row else 0

            row = conn.execute(
                "SELECT COUNT(*) FROM telemetry_audit_log WHERE status = 'rejected'"
            ).fetchone()
            stats["rejected"] = row[0] if row else 0

            row = conn.execute(
                "SELECT MAX(recorded_at) FROM telemetry_audit_log WHERE event_type = 'event_uploaded' AND status = 'success'"
            ).fetchone()
            stats["last_upload_time"] = row[0] if row and row[0] else None

            row = conn.execute(
                "SELECT MAX(recorded_at) FROM telemetry_audit_log WHERE event_type = 'event_sanitized' AND status = 'success'"
            ).fetchone()
            stats["last_sanitized_time"] = row[0] if row and row[0] else None
        except Exception:
            pass
        return stats

    def _calculate_upload_rate(self, audit_stats: dict) -> float:
        total = audit_stats.get("uploaded", 0) + audit_stats.get("upload_failures", 0)
        if total == 0:
            return 1.0
        return audit_stats.get("uploaded", 0) / total

    def _calculate_avg_latency(self, audit_stats: dict) -> float:
        return 0.0

    def _estimate_queued(self, audit_stats: dict) -> int:
        created = audit_stats.get("created", 0)
        sanitized = audit_stats.get("sanitized", 0)
        uploaded = audit_stats.get("uploaded", 0)
        return max(0, created - sanitized - uploaded)

    def _determine_overall_health(self, collected: int, upload_rate: float,
                                   queued: int, audit_stats: dict) -> str:
        if collected == 0:
            return "inactive"
        if audit_stats.get("upload_failures", 0) > 10:
            return "critical"
        if upload_rate < 0.5:
            return "critical"
        if queued > 100:
            return "warning"
        if upload_rate < 0.9:
            return "warning"
        return "healthy"
