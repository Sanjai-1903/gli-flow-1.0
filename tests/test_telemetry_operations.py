import json
import os
import tempfile
import unittest
from datetime import datetime


class TestTelemetryExporter(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self._init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def _init_db(self):
        conn = __import__("sqlite3").connect(self.db_path)
        cur = conn.cursor()
        cur.executescript("""
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
            INSERT INTO community_telemetry (event, failure_type, tool, details, created_at) VALUES
                ('escalation_created', 'TIMING_VIOLATION', 'openroad', '{"severity":"HIGH"}', '2026-06-15T10:00:00Z'),
                ('failure_atlas_miss', 'DRC_VIOLATION', 'openroad', '{"severity":"MEDIUM"}', '2026-06-15T11:00:00Z');
            INSERT INTO community_unknown_dataset (tool, failure_type, signature, frequency, last_seen) VALUES
                ('openroad', 'TIMING_VIOLATION', 'wns:-0.05', 3, '2026-06-15T10:00:00Z'),
                ('yosys', 'SYNTAX_ERROR', 'parse:line42', 1, '2026-06-14T10:00:00Z');
            INSERT INTO community_escalations (id, failure_type, tool, status, consent_given, created_at) VALUES
                ('esc_001', 'TIMING_VIOLATION', 'openroad', 'open', 1, '2026-06-15T10:00:00Z');
            INSERT INTO resolution_patterns (id, failure_fingerprint, failure_type, resolution, confidence) VALUES
                ('pat_001', 'timing:wns:-0.05', 'TIMING_VIOLATION', 'Reduce clock frequency', 0.85);
        """)
        conn.commit()
        conn.close()

    def _patch_db_path(self, cls):
        original = cls.__init__
        def patched_init(self, db_path=None):
            original(self, self.db_path if not db_path else db_path)
        cls.db_path = self.db_path
        return cls

    def test_export_to_json(self):
        from failure_atlas.community_intelligence.export import TelemetryExporter
        exporter = TelemetryExporter(self.db_path)
        result = exporter.export_to_json()
        data = json.loads(result)
        self.assertIn("export_metadata", data)
        self.assertIn("telemetry_events", data)
        self.assertIn("failure_atlas_entries", data)
        self.assertIn("escalations", data)
        self.assertIn("resolution_patterns", data)
        meta = data["export_metadata"]
        self.assertEqual(meta["record_count"]["telemetry_events"], 2)
        self.assertEqual(meta["record_count"]["failure_atlas_entries"], 2)
        self.assertEqual(meta["record_count"]["escalations"], 1)
        self.assertEqual(meta["record_count"]["resolution_patterns"], 1)

    def test_export_privacy_validated(self):
        from failure_atlas.community_intelligence.export import TelemetryExporter
        exporter = TelemetryExporter(self.db_path)
        data = json.loads(exporter.export_to_json())
        self.assertTrue(data["export_metadata"]["privacy_validated"])

    def test_export_csv(self):
        from failure_atlas.community_intelligence.export import TelemetryExporter
        exporter = TelemetryExporter(self.db_path)
        outputs = exporter.export_to_csv()
        self.assertIn("telemetry_events", outputs)
        self.assertIn("failure_atlas_entries", outputs)
        self.assertIn("escalations", outputs)
        self.assertIn("resolution_patterns", outputs)
        self.assertGreater(len(outputs["telemetry_events"]), 0)
        self.assertIn("event", outputs["telemetry_events"])

    def test_export_empty_db(self):
        conn = __import__("sqlite3").connect(self.db_path)
        for table in ["community_telemetry", "community_unknown_dataset",
                       "community_escalations", "resolution_patterns"]:
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
        conn.close()

        from failure_atlas.community_intelligence.export import TelemetryExporter
        exporter = TelemetryExporter(self.db_path)
        data = json.loads(exporter.export_to_json())
        meta = data["export_metadata"]
        self.assertEqual(meta["record_count"]["telemetry_events"], 0)
        self.assertEqual(meta["record_count"]["failure_atlas_entries"], 0)

    def test_export_filter_by_run_id(self):
        from failure_atlas.community_intelligence.export import TelemetryExporter
        exporter = TelemetryExporter(self.db_path)
        data = json.loads(exporter.export_to_json(run_id="nonexistent"))
        self.assertIsNotNone(data["export_metadata"])

    def test_export_filter_by_date(self):
        from failure_atlas.community_intelligence.export import TelemetryExporter
        exporter = TelemetryExporter(self.db_path)
        data = json.loads(exporter.export_to_json(from_date="2026-06-15", to_date="2026-06-15"))
        self.assertGreater(data["export_metadata"]["record_count"]["telemetry_events"], 0)

    def test_dataset_snapshot(self):
        from failure_atlas.community_intelligence.snapshot import DatasetSnapshot
        snap = DatasetSnapshot(self.db_path)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp = f.name
        try:
            result = snap.create(output_path=tmp)
            self.assertIn("snapshot_metadata", result)
            self.assertIn("failure_atlas_data", result)
            self.assertIn("resolution_data", result)
            meta = result["snapshot_metadata"]
            self.assertEqual(meta["type"], "dataset_snapshot")
            self.assertTrue(meta["privacy_validated"])
            self.assertTrue(os.path.exists(tmp))
        finally:
            os.unlink(tmp)


class TestPrivacyValidator(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)

    def tearDown(self):
        os.unlink(self.db_path)

    def test_sanitize_excluded_fields(self):
        from failure_atlas.community_intelligence.export import PrivacyValidator
        validator = PrivacyValidator(self.db_path)
        d = {"rtl": "module counter; endmodule", "safe_field": "hello"}
        result = validator.sanitize_dict(d)
        self.assertEqual(result["rtl"], "[BLOCKED]")
        self.assertEqual(result["safe_field"], "hello")

    def test_sanitize_nested_dict(self):
        from failure_atlas.community_intelligence.export import PrivacyValidator
        validator = PrivacyValidator(self.db_path)
        d = {"meta": {"rtl": "verilog code", "name": "test"}}
        result = validator.sanitize_dict(d)
        self.assertEqual(result["meta"]["rtl"], "[BLOCKED]")
        self.assertEqual(result["meta"]["name"], "test")

    def test_sanitize_path_redaction(self):
        from failure_atlas.community_intelligence.export import PrivacyValidator
        validator = PrivacyValidator(self.db_path)
        d = {"path": "/home/user/design/src/top.sdc"}
        result = validator.sanitize_dict(d)
        self.assertNotIn("/home/user", str(result["path"]))
        self.assertIn("[PATH REDACTED]", str(result["path"]))

    def test_sanitize_instance_redaction(self):
        from failure_atlas.community_intelligence.export import PrivacyValidator
        validator = PrivacyValidator(self.db_path)
        d = {"instance": "TOP.U_DSP.u_mult"}
        result = validator.sanitize_dict(d)
        self.assertNotIn("U_DSP", str(result["instance"]))

    def test_generate_report_clean(self):
        from failure_atlas.community_intelligence.export import PrivacyValidator
        validator = PrivacyValidator(self.db_path)
        report = validator.generate_report({"safe": "data"})
        self.assertTrue(report["valid"])
        self.assertEqual(report["issue_count"], 0)

    def test_generate_report_issues(self):
        from failure_atlas.community_intelligence.export import PrivacyValidator
        validator = PrivacyValidator(self.db_path)
        report = validator.generate_report({"rtl": "bad", "gds": "worse"})
        self.assertFalse(report["valid"])
        self.assertGreaterEqual(report["issue_count"], 2)

    def test_blocked_extensions(self):
        from failure_atlas.community_intelligence.export import PrivacyValidator
        validator = PrivacyValidator(self.db_path)
        d = {"file": "design.v", "gds_file": "output.gds"}
        result = validator.sanitize_dict(d)
        self.assertEqual(result["file"], "[BLOCKED FILE]")
        self.assertEqual(result["gds_file"], "[BLOCKED FILE]")


class TestTelemetryAuditLog(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)

    def tearDown(self):
        os.unlink(self.db_path)

    def test_record_and_retrieve(self):
        from failure_atlas.community_intelligence.audit import TelemetryAuditLog
        audit = TelemetryAuditLog(self.db_path)
        audit.record("event_created", "test_event", "success")
        audit.record("event_sanitized", "test_event", "success")
        audit.record("event_rejected", "bad_event", "rejected", reason="Blocked field")
        logs = audit.get_logs()
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[0]["event_type"], "event_rejected")
        self.assertEqual(logs[2]["event_type"], "event_created")

    def test_get_stats(self):
        from failure_atlas.community_intelligence.audit import TelemetryAuditLog
        audit = TelemetryAuditLog(self.db_path)
        audit.record("event_created", "a", "success")
        audit.record("event_rejected", "b", "rejected")
        stats = audit.get_stats()
        self.assertEqual(stats["total_entries"], 2)
        self.assertEqual(stats["total_rejected"], 1)

    def test_filter_by_event_type(self):
        from failure_atlas.community_intelligence.audit import TelemetryAuditLog
        audit = TelemetryAuditLog(self.db_path)
        audit.record("event_created", "a", "success")
        audit.record("event_sanitized", "b", "success")
        logs = audit.get_logs(event_type="event_created")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["event_type"], "event_created")


class TestTelemetryReplayEngine(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)
        self.export_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
        self.export_path = self.export_file.name
        self.export_data = {
            "export_metadata": {
                "version": "1.0",
                "exported_at": "2026-06-15T12:00:00Z",
                "record_count": {"telemetry_events": 2, "failure_atlas_entries": 1,
                                "escalations": 1, "resolution_patterns": 1},
                "privacy_validated": True,
            },
            "telemetry_events": [
                {"event": "escalation_created", "failure_type": "TIMING", "tool": "openroad",
                 "details": {"severity": "HIGH"}, "created_at": "2026-06-15T10:00:00Z"},
                {"event": "failure_atlas_miss", "failure_type": "DRC", "tool": "openroad",
                 "details": {}, "created_at": "2026-06-15T11:00:00Z"},
            ],
            "failure_atlas_entries": [
                {"tool": "openroad", "failure_type": "TIMING", "signature": "wns:-0.05",
                 "frequency": 3, "last_seen": "2026-06-15T10:00:00Z"},
            ],
            "escalations": [
                {"id": "esc_001", "failure_type": "TIMING", "status": "open",
                 "created_at": "2026-06-15T10:00:00Z"},
            ],
            "resolution_patterns": [
                {"failure_fingerprint": "timing:wns:-0.05", "resolution": "Reduce clock",
                 "confidence": 0.85, "last_seen": "2026-06-15T10:00:00Z"},
            ],
        }
        json.dump(self.export_data, self.export_file)
        self.export_file.close()

    def tearDown(self):
        os.unlink(self.db_path)
        os.unlink(self.export_path)

    def test_replay_dry_run(self):
        from failure_atlas.community_intelligence.replay import TelemetryReplayEngine
        engine = TelemetryReplayEngine(self.db_path)
        results = engine.replay(self.export_path, dry_run=True)
        self.assertIn("replay_metadata", results)
        self.assertIn("events", results)
        self.assertIn("failures", results)
        self.assertIn("resolutions", results)
        self.assertIn("timeline", results)
        meta = results["replay_metadata"]
        self.assertEqual(meta["total_events"], 5)
        self.assertEqual(meta["successful"], 5)
        self.assertEqual(meta["failed"], 0)
        self.assertEqual(len(results["events"]), 2)
        self.assertEqual(len(results["failures"]), 1)
        self.assertEqual(len(results["resolutions"]), 2)

    def test_replay_invalid_file(self):
        from failure_atlas.community_intelligence.replay import TelemetryReplayEngine
        engine = TelemetryReplayEngine(self.db_path)
        with self.assertRaises(FileNotFoundError):
            engine.replay("/nonexistent/file.json")

    def test_summary_text(self):
        from failure_atlas.community_intelligence.replay import TelemetryReplayEngine
        engine = TelemetryReplayEngine(self.db_path)
        engine.replay(self.export_path, dry_run=True)
        summary = engine.summary_text()
        self.assertIn("Replay Summary", summary)
        self.assertIn("Successful:  5", summary)


class TestTelemetryHealth(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)
        self._init_db()

    def tearDown(self):
        os.unlink(self.db_path)

    def _init_db(self):
        conn = __import__("sqlite3").connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS community_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL, escalation_id TEXT DEFAULT '',
                failure_type TEXT DEFAULT '', tool TEXT DEFAULT '',
                atlas_id TEXT DEFAULT '', details TEXT DEFAULT '{}',
                created_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS community_escalations (
                id TEXT PRIMARY KEY, run_id TEXT DEFAULT '',
                failure_type TEXT NOT NULL, tool TEXT DEFAULT '',
                stage TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'open',
                consent_given INTEGER DEFAULT 0, consent_timestamp TEXT DEFAULT '',
                bharatcode_submission_id TEXT DEFAULT '',
                bharatcode_status TEXT DEFAULT '', ai_summary TEXT DEFAULT '',
                user_notes TEXT DEFAULT '', engineer_response TEXT DEFAULT '{}',
                atlas_id_created TEXT DEFAULT '', created_at TEXT NOT NULL,
                sent_at TEXT DEFAULT '', resolved_at TEXT DEFAULT ''
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS community_unknown_dataset (
                id INTEGER PRIMARY KEY AUTOINCREMENT, tool TEXT NOT NULL,
                failure_type TEXT NOT NULL, signature TEXT DEFAULT '',
                frequency INTEGER DEFAULT 1, ai_helpfulness TEXT DEFAULT 'unknown',
                resolution_outcome TEXT DEFAULT '', consent_given INTEGER DEFAULT 0,
                escalation_id TEXT DEFAULT '', last_seen TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resolution_patterns (
                id TEXT PRIMARY KEY, failure_fingerprint TEXT NOT NULL,
                failure_type TEXT NOT NULL, root_cause TEXT,
                resolution TEXT NOT NULL, resolution_type TEXT,
                success_count INTEGER DEFAULT 0, failure_count INTEGER DEFAULT 0,
                confidence REAL DEFAULT 0.0, first_seen TEXT, last_seen TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        cur.execute("""
            INSERT INTO community_telemetry (event, created_at) VALUES
                ('test_event', '2026-06-15T10:00:00Z')
        """)
        conn.commit()
        conn.close()

    def test_get_health(self):
        from failure_atlas.community_intelligence.health import TelemetryHealth
        health = TelemetryHealth(self.db_path)
        status = health.get_health()
        self.assertIn("collected_events", status)
        self.assertIn("overall_status", status)
        self.assertIn("last_event_time", status)
        self.assertEqual(status["collected_events"], 1)
        self.assertEqual(status["last_event_time"], "2026-06-15T10:00:00Z")


class TestTelemetryExportAPI(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)
        self._init_db()

    def _init_db(self):
        conn = __import__("sqlite3").connect(self.db_path)
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS community_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
                escalation_id TEXT DEFAULT '', failure_type TEXT DEFAULT '',
                tool TEXT DEFAULT '', atlas_id TEXT DEFAULT '',
                details TEXT DEFAULT '{}', created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS community_unknown_dataset (
                id INTEGER PRIMARY KEY AUTOINCREMENT, tool TEXT NOT NULL,
                failure_type TEXT NOT NULL, signature TEXT DEFAULT '',
                frequency INTEGER DEFAULT 1, ai_helpfulness TEXT DEFAULT 'unknown',
                resolution_outcome TEXT DEFAULT '', consent_given INTEGER DEFAULT 0,
                escalation_id TEXT DEFAULT '', last_seen TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS community_escalations (
                id TEXT PRIMARY KEY, run_id TEXT DEFAULT '',
                failure_type TEXT NOT NULL, tool TEXT DEFAULT '',
                stage TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'open',
                consent_given INTEGER DEFAULT 0, consent_timestamp TEXT DEFAULT '',
                bharatcode_submission_id TEXT DEFAULT '', bharatcode_status TEXT DEFAULT '',
                ai_summary TEXT DEFAULT '', user_notes TEXT DEFAULT '',
                engineer_response TEXT DEFAULT '{}', atlas_id_created TEXT DEFAULT '',
                created_at TEXT NOT NULL, sent_at TEXT DEFAULT '', resolved_at TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS resolution_patterns (
                id TEXT PRIMARY KEY, failure_fingerprint TEXT NOT NULL,
                failure_type TEXT NOT NULL, root_cause TEXT,
                resolution TEXT NOT NULL, resolution_type TEXT,
                success_count INTEGER DEFAULT 0, failure_count INTEGER DEFAULT 0,
                confidence REAL DEFAULT 0.0, first_seen TEXT, last_seen TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        os.unlink(self.db_path)

    def test_privacy_validate_endpoint(self):
        from failure_atlas.community_intelligence.export import TelemetryExporter
        exporter = TelemetryExporter(self.db_path)
        data = exporter.export_telemetry()
        report = data.get("export_metadata", {}).get("privacy_report", {})
        self.assertIn("valid", report)
        self.assertIn("issues", report)

    def test_export_no_sensitive_data(self):
        from failure_atlas.community_intelligence.export import TelemetryExporter
        exporter = TelemetryExporter(self.db_path)
        data = json.loads(exporter.export_to_json())
        raw = json.dumps(data).lower()
        blocked = ["rtl", "netlist", "gds", "def", "lef", "bitstream"]
        for term in blocked:
            self.assertNotIn(f'"{term}"', raw,
                             msg=f"Sensitive field '{term}' leaked into export")


if __name__ == "__main__":
    unittest.main()
