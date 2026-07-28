import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from failure_atlas.community_intelligence import (
    EscalationTelemetry,
    UnknownFailureDataset,
    TelemetryAuditLog,
    TelemetryExporter,
    TelemetryReplayEngine,
    TelemetryHealth
)

class TestTelemetryEndToEnd(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)
        
        # Initialize tables using class initializers
        EscalationTelemetry(self.db_path)
        UnknownFailureDataset(self.db_path)
        TelemetryAuditLog(self.db_path)
        
        # We also need resolution_patterns and community_escalations for health.py
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS community_escalations (
                id TEXT PRIMARY KEY,
                failure_type NOT NULL,
                status TEXT DEFAULT 'open',
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS resolution_patterns (
                id TEXT PRIMARY KEY,
                failure_fingerprint TEXT NOT NULL,
                last_seen TEXT
            );
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_complete_lifecycle(self):
        # 1. Record a Telemetry Event
        # We need to patch EscalationTelemetry to use our test DB
        telemetry = EscalationTelemetry(self.db_path)
        event_details = {"severity": "HIGH", "rtl": "SECRET_CODE"} # rtl should be sanitized
        telemetry.record(
            event="ai_investigation_run",
            failure_type="DRC_VIOLATION",
            tool="magic",
            details=event_details
        )
        
        # 2. Verify it's in the DB and sanitized (Wait, EscalationTelemetry itself doesn't sanitize, the Exporter does)
        conn = sqlite3.connect(self.db_path)
        row = conn.execute("SELECT * FROM community_telemetry").fetchone()
        self.assertIsNotNone(row)
        details = json.loads(row[6])
        self.assertEqual(details["rtl"], "SECRET_CODE") # Still here in internal DB
        conn.close()
        
        # 3. Audit Log should be updated if we use it
        audit = TelemetryAuditLog(self.db_path)
        audit.record(TelemetryAuditLog.EVENT_CREATED, "ai_investigation_run", "success", payload=event_details)
        
        # 4. Export the data
        exporter = TelemetryExporter(self.db_path)
        export_json = exporter.export_to_json()
        export_data = json.loads(export_json)
        
        self.assertEqual(len(export_data["telemetry_events"]), 1)
        # Verify sanitization in export
        exported_details = export_data["telemetry_events"][0]["details"]
        self.assertEqual(exported_details["rtl"], "[BLOCKED]")
        
        # 5. Replay the data into a NEW database
        new_db_fd, new_db_path = tempfile.mkstemp(suffix="_new.db")
        os.close(new_db_fd)
        try:
            # Initialize new DB tables
            EscalationTelemetry(new_db_path)
            UnknownFailureDataset(new_db_path)
            TelemetryAuditLog(new_db_path)

            conn = sqlite3.connect(new_db_path)
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS community_escalations (
                    id TEXT PRIMARY KEY,
                    failure_type NOT NULL,
                    status TEXT DEFAULT 'open',
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS resolution_patterns (
                    id TEXT PRIMARY KEY,
                    failure_fingerprint TEXT NOT NULL,
                    last_seen TEXT
                );
            """)
            conn.commit()
            conn.close()
            
            # Create a temporary export file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(export_data, f)
                export_file_path = f.name
                
            replay_engine = TelemetryReplayEngine(new_db_path)
            replay_results = replay_engine.replay(export_file_path, dry_run=False)
            
            self.assertEqual(replay_results["replay_metadata"]["successful"], 1)
            
            # 6. Verify health metrics in the new DB
            health = TelemetryHealth(new_db_path)
            health_status = health.get_health()
            
            self.assertEqual(health_status["collected_events"], 1)
            self.assertEqual(health_status["overall_status"], "healthy")
            
        finally:
            if os.path.exists(new_db_path):
                os.unlink(new_db_path)
            if 'export_file_path' in locals() and os.path.exists(export_file_path):
                os.unlink(export_file_path)

if __name__ == "__main__":
    unittest.main()
