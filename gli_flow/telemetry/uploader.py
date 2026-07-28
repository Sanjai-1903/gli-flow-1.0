import json
import logging
import os
import subprocess
import sys
from typing import Optional

import httpx

from gli_flow.telemetry.settings import get_telemetry_settings, TelemetryMode
from gli_flow.telemetry.upload_queue import UploadQueue
from gli_flow.telemetry.retry_engine import RetryEngine
from failure_atlas.community_intelligence.export import TelemetryExporter
from failure_atlas.community_intelligence.audit import TelemetryAuditLog

logger = logging.getLogger(__name__)

DEFAULT_SERVER_URL = os.environ.get("GLI_SERVER_URL", "http://localhost:8100")
DEFAULT_API_KEY = os.environ.get("GLI_API_KEY", "")


class TelemetryUploader:
    def __init__(self, db_path: Optional[str] = None,
                 server_url: str = "", api_key: str = ""):
        self.db_path = db_path
        self.settings = get_telemetry_settings()
        self.exporter = TelemetryExporter(db_path)
        self.audit = TelemetryAuditLog(db_path)
        self.queue = UploadQueue()
        self.retry = RetryEngine(self.queue)
        self.server_url = (server_url or DEFAULT_SERVER_URL).rstrip("/")
        self.api_key = api_key or DEFAULT_API_KEY

    def should_upload(self) -> bool:
        if self.settings.mode == TelemetryMode.LOCAL or self.settings.mode == TelemetryMode.DISABLED:
            return False
        if not self.settings.consent_given:
            return False
        return True

    def _do_http_upload(self, payload: dict):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                f"{self.server_url}/api/v1/telemetry",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()

    def upload_run_telemetry(self, run_id: str):
        if not self.should_upload():
            logger.info(
                "Skipping telemetry upload for run %s (mode=%s, consent=%s)",
                run_id, self.settings.mode, self.settings.consent_given,
            )
            return

        logger.info("Preparing telemetry upload for run %s", run_id)

        try:
            payload_json = self.exporter.export_to_json(run_id=run_id)
            payload = json.loads(payload_json)

            if not payload.get("telemetry_events") and not payload.get("failure_atlas_entries"):
                logger.info("No telemetry data found for run %s", run_id)
                return

            if self.settings.mode == TelemetryMode.ATLAS:
                payload["telemetry_events"] = [
                    e for e in payload.get("telemetry_events", [])
                    if e.get("event") in ["unknown_failure_detected", "failure_atlas_miss"]
                ]
                if "escalations" in payload:
                    for esc in payload["escalations"]:
                        if "details" in esc:
                            esc["details"] = {
                                k: v for k, v in esc["details"].items()
                                if k in ["tool", "stage", "failure_type"]
                            }

            payload.pop("resolution_patterns", None)
            payload.pop("export_metadata", None)
            for entry in payload.get("failure_atlas_entries", []):
                entry["run_id"] = run_id
                entry.setdefault("tool", "")
                entry.setdefault("stage", "")
                entry.setdefault("failure_type", "UNKNOWN")
                entry.setdefault("frequency", 1)
            payload["run_id"] = run_id
            payload["source_version"] = "1.0"

            event_count = len(payload.get("telemetry_events", []))
            failure_count = len(payload.get("failure_atlas_entries", []))

            try:
                self._do_http_upload(payload)
                self.audit.record(
                    TelemetryAuditLog.EVENT_UPLOADED,
                    f"run_{run_id}",
                    "success",
                    payload={
                        "mode": self.settings.mode,
                        "event_count": event_count,
                        "failure_count": failure_count,
                    },
                )
                logger.info(
                    "Uploaded run=%s events=%d failures=%d",
                    run_id, event_count, failure_count,
                )
            except Exception as e:
                logger.warning("Upload failed for run=%s, queueing for retry: %s", run_id, e)
                self.queue.enqueue("telemetry", payload, run_id=run_id, status="pending")
                self.audit.record(
                    TelemetryAuditLog.EVENT_UPLOADED,
                    f"run_{run_id}",
                    "failed",
                    payload={"error": str(e), "queued": True},
                )

        except Exception as e:
            logger.error("Telemetry export failed for run %s: %s", run_id, e)
            self.audit.record(
                TelemetryAuditLog.EVENT_UPLOADED,
                f"run_{run_id}",
                "failed",
                payload={"error": str(e)},
            )

    def process_upload_queue(self, batch_size: int = 10) -> dict:
        def upload_fn(payload):
            self._do_http_upload(payload)
        return self.retry.process_queue(upload_fn, batch_size)

    def trigger_background_upload(self, run_id: str):
        if not self.should_upload():
            return

        try:
            cmd = [sys.executable, "-m", "gli_flow.cli.main", "telemetry", "upload-internal", run_id]
            if self.db_path:
                cmd.extend(["--db-path", self.db_path])
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception as e:
            logger.warning("Failed to trigger background telemetry upload: %s", e)

    def get_queue_stats(self) -> dict:
        return self.queue.get_queue_stats()


def auto_upload_run(run_id: str, db_path: Optional[str] = None):
    uploader = TelemetryUploader(db_path)
    uploader.trigger_background_upload(run_id)
