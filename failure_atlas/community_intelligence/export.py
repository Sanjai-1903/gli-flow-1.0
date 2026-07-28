import csv
import hashlib
import io
import json
import os
import re
import sqlite3
from datetime import datetime
from typing import Optional


EXCLUDED_FIELDS = {
    "rtl", "netlist", "gds", "def", "lef", "source", "customer_ip",
    "project_files", "license", "credential", "password", "secret",
    "private_key", "design_files", "bitstream",
}
EXCLUDED_EXTENSIONS = {
    ".v", ".sv", ".vh", ".svh", ".gds", ".oas", ".sp", ".cdl",
    ".def", ".lef", ".lib", ".db", ".bit", ".bin",
}
PATH_PATTERN = re.compile(r"(/[\w./-]+)+")
INSTANCE_PATTERN = re.compile(r"\b([A-Z][\w/]+(?:\.[A-Z][\w/]+)+)\b")


class PrivacyValidator:
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

    @staticmethod
    def _is_excluded_field(key: str) -> bool:
        key_lower = key.lower()
        return key_lower in EXCLUDED_FIELDS

    def sanitize_value(self, key: str, value: any) -> any:
        if value is None:
            return None
        if self._is_excluded_field(key):
            return "[BLOCKED]"
        if isinstance(value, str):
            ext = os.path.splitext(value)[1].lower()
            if ext in EXCLUDED_EXTENSIONS:
                return "[BLOCKED FILE]"
            value = PATH_PATTERN.sub("[PATH REDACTED]", value)
            value = INSTANCE_PATTERN.sub("[INSTANCE REDACTED]", value)
        return value

    def sanitize_dict(self, d: dict) -> dict:
        out = {}
        for k, v in d.items():
            if self._is_excluded_field(k):
                out[k] = "[BLOCKED]"
            elif k.lower() == "details" and isinstance(v, str):
                try:
                    # Attempt to parse and sanitize nested details
                    details_dict = json.loads(v)
                    out[k] = self.sanitize_dict(details_dict)
                except Exception:
                    out[k] = self.sanitize_value(k, v)
            elif isinstance(v, dict):
                out[k] = self.sanitize_dict(v)
            elif isinstance(v, list):
                out[k] = [self.sanitize_dict(i) if isinstance(i, dict) else self.sanitize_value(k, i) for i in v]
            else:
                out[k] = self.sanitize_value(k, v)
        return out

    def validate_dict(self, d: dict, path: str = "") -> list[str]:
        issues = []
        for k, v in d.items():
            if self._is_excluded_field(k):
                issues.append(f"{path}.{k}: excluded field present")
            if isinstance(v, str):
                ext = os.path.splitext(v)[1].lower()
                if ext in EXCLUDED_EXTENSIONS:
                    issues.append(f"{path}.{k}: excluded file extension {ext}")
                if PATH_PATTERN.fullmatch(v):
                    issues.append(f"{path}.{k}: exposed file path")
            elif isinstance(v, dict):
                issues.extend(self.validate_dict(v, f"{path}.{k}"))
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        issues.extend(self.validate_dict(item, f"{path}.{k}[{i}]"))
        return issues

    def generate_report(self, data: dict) -> dict:
        issues = self.validate_dict(data)
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "issue_count": len(issues),
            "validated_at": datetime.utcnow().isoformat(),
        }


class TelemetryExporter:
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            from gli_flow.database.migrations import _get_db_path
            self.db_path = _get_db_path()
        self.validator = PrivacyValidator(db_path)

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def export_telemetry(self, run_id: Optional[str] = None,
                         from_date: Optional[str] = None,
                         to_date: Optional[str] = None) -> dict:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            telemetry_params: list = []
            telemetry_clauses: list = []
            if from_date:
                if len(from_date) == 10:
                    from_date = from_date + "T00:00:00Z"
                telemetry_clauses.append("created_at >= ?")
                telemetry_params.append(from_date)
            if to_date:
                if len(to_date) == 10:
                    to_date = to_date + "T23:59:59Z"
                telemetry_clauses.append("created_at <= ?")
                telemetry_params.append(to_date)
            telemetry_where = " AND ".join(telemetry_clauses) if telemetry_clauses else "1=1"
            cur.execute(
                f"SELECT * FROM community_telemetry WHERE {telemetry_where} ORDER BY created_at DESC",
                telemetry_params,
            )
            telemetry = [dict(r) for r in cur.fetchall()]

            unknown_params: list = []
            unknown_clauses: list = []
            if from_date:
                fd = from_date + "T00:00:00Z" if len(from_date) == 10 else from_date
                unknown_clauses.append("last_seen >= ?")
                unknown_params.append(fd)
            if to_date:
                td = to_date + "T23:59:59Z" if len(to_date) == 10 else to_date
                unknown_clauses.append("last_seen <= ?")
                unknown_params.append(td)
            unknown_where = " AND ".join(unknown_clauses) if unknown_clauses else "1=1"
            cur.execute(
                f"SELECT * FROM community_unknown_dataset WHERE {unknown_where} ORDER BY frequency DESC",
                unknown_params,
            )
            unknowns = [dict(r) for r in cur.fetchall()]

            esc_params: list = []
            esc_clauses: list = []
            if run_id:
                esc_clauses.append("id = ?")
                esc_params.append(run_id)
            if from_date:
                fd = from_date + "T00:00:00Z" if len(from_date) == 10 else from_date
                esc_clauses.append("created_at >= ?")
                esc_params.append(fd)
            if to_date:
                td = to_date + "T23:59:59Z" if len(to_date) == 10 else to_date
                esc_clauses.append("created_at <= ?")
                esc_params.append(td)
            esc_where = " AND ".join(esc_clauses) if esc_clauses else "1=1"
            cur.execute(
                f"SELECT * FROM community_escalations WHERE {esc_where} ORDER BY created_at DESC",
                esc_params,
            )
            escalations = [dict(r) for r in cur.fetchall()]

            res_params: list = []
            res_clauses: list = []
            if from_date:
                fd = from_date + "T00:00:00Z" if len(from_date) == 10 else from_date
                res_clauses.append("last_seen >= ?")
                res_params.append(fd)
            if to_date:
                td = to_date + "T23:59:59Z" if len(to_date) == 10 else to_date
                res_clauses.append("last_seen <= ?")
                res_params.append(td)
            res_where = " AND ".join(res_clauses) if res_clauses else "1=1"
            cur.execute(
                f"SELECT * FROM resolution_patterns WHERE {res_where} ORDER BY last_seen DESC",
                res_params,
            )
            patterns = [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

        return self._build_export(telemetry, unknowns, escalations, patterns)

    def _sanitize_records(self, records: list[dict]) -> list[dict]:
        return [self.validator.sanitize_dict(r) for r in records]

    def _build_export(self, telemetry: list, unknowns: list,
                      escalations: list, patterns: list) -> dict:
        export = {
            "export_metadata": {
                "version": "1.0",
                "exported_at": datetime.utcnow().isoformat(),
                "record_count": {
                    "telemetry_events": len(telemetry),
                    "failure_atlas_entries": len(unknowns),
                    "escalations": len(escalations),
                    "resolution_patterns": len(patterns),
                },
                "privacy_validated": False,
            },
            "telemetry_events": self._sanitize_records(telemetry),
            "failure_atlas_entries": self._sanitize_records(unknowns),
            "escalations": self._sanitize_records(escalations),
            "resolution_patterns": self._sanitize_records(patterns),
        }
        report = self.validator.generate_report(export)
        export["export_metadata"]["privacy_validated"] = report["valid"]
        export["export_metadata"]["privacy_report"] = report
        return export

    def export_to_json(self, run_id: Optional[str] = None,
                       from_date: Optional[str] = None,
                       to_date: Optional[str] = None) -> str:
        data = self.export_telemetry(run_id, from_date, to_date)
        return json.dumps(data, indent=2, default=str)

    def export_to_csv(self, run_id: Optional[str] = None,
                      from_date: Optional[str] = None,
                      to_date: Optional[str] = None) -> dict[str, str]:
        data = self.export_telemetry(run_id, from_date, to_date)
        outputs = {}
        for section, records in [
            ("telemetry_events", data.get("telemetry_events", [])),
            ("failure_atlas_entries", data.get("failure_atlas_entries", [])),
            ("escalations", data.get("escalations", [])),
            ("resolution_patterns", data.get("resolution_patterns", [])),
        ]:
            if not records:
                outputs[section] = ""
                continue
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
            outputs[section] = buf.getvalue()
        return outputs

    def export_dataset_snapshot(self) -> dict:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM community_unknown_dataset ORDER BY frequency DESC")
            unknowns = [dict(r) for r in cur.fetchall()]
            cur.execute(
                "SELECT * FROM resolution_patterns ORDER BY last_seen DESC",
            )
            patterns = [dict(r) for r in cur.fetchall()]
            cur.execute(
                "SELECT event, COUNT(*) as count FROM community_telemetry GROUP BY event",
            )
            telemetry_summary = [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

        snapshot = {
            "snapshot_metadata": {
                "version": "1.0",
                "created_at": datetime.utcnow().isoformat(),
                "type": "dataset_snapshot",
                "purpose": "AI training preparation",
                "record_count": {
                    "unknown_failures": len(unknowns),
                    "resolution_patterns": len(patterns),
                    "telemetry_summary": len(telemetry_summary),
                },
                "privacy_validated": False,
            },
            "failure_atlas_data": self._sanitize_records(unknowns),
            "resolution_data": self._sanitize_records(patterns),
            "telemetry_metadata": telemetry_summary,
        }
        report = self.validator.generate_report(snapshot)
        snapshot["snapshot_metadata"]["privacy_validated"] = report["valid"]
        snapshot["snapshot_metadata"]["privacy_report"] = report
        return snapshot
