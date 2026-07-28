import json
import logging
import os
from typing import Optional

import httpx

from failure_atlas.community_intelligence.export import PrivacyValidator, TelemetryExporter
from gli_flow.telemetry.settings import get_telemetry_settings, TelemetryMode
from gli_flow.telemetry.upload_queue import UploadQueue
from gli_flow.telemetry.retry_engine import RetryEngine

logger = logging.getLogger(__name__)

DEFAULT_SERVER_URL = os.environ.get("GLI_SERVER_URL", "http://localhost:8100")
DEFAULT_API_KEY = os.environ.get("GLI_API_KEY", "")


class FailureAtlasUploader:
    def __init__(self, server_url: str = "", api_key: str = "",
                 db_path: Optional[str] = None):
        self.server_url = (server_url or DEFAULT_SERVER_URL).rstrip("/")
        self.api_key = api_key or DEFAULT_API_KEY
        self.db_path = db_path
        self.settings = get_telemetry_settings()
        self.validator = PrivacyValidator(db_path)
        self.exporter = TelemetryExporter(db_path)
        self.queue = UploadQueue()
        self.retry = RetryEngine(self.queue)

    def should_upload(self) -> bool:
        if self.settings.mode == TelemetryMode.LOCAL or self.settings.mode == TelemetryMode.DISABLED:
            return False
        if not self.settings.consent_given:
            return False
        return True

    def _build_payload(self, entry: dict) -> dict:
        allowed = {
            "run_id", "tool", "stage", "failure_type", "error_text",
            "design_name", "design_category", "log_excerpt", "frequency",
            "first_seen", "last_seen",
        }
        payload = {k: v for k, v in entry.items() if k in allowed and v is not None}
        payload.setdefault("tool", "")
        payload.setdefault("stage", "")
        payload.setdefault("frequency", 1)
        return payload

    def upload_entry(self, entry: dict, run_id: str = "") -> bool:
        if not self.should_upload():
            return False
        sanitized = self.validator.sanitize_dict(entry)
        payload = self._build_payload(sanitized)

        issues = self.validator.validate_dict(sanitized)
        if issues:
            logger.warning("Privacy validation found %d issues, skipping: %s", len(issues), issues)
            return False

        payload_package = {
            "run_id": run_id,
            "source_version": "1.0",
            "failure_atlas_entries": [payload],
            "telemetry_events": [],
            "escalations": [],
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    f"{self.server_url}/api/v1/telemetry",
                    json=payload_package,
                    headers=headers,
                )
                if resp.status_code == 200:
                    logger.info("Failure entry uploaded (run=%s)", run_id)
                    return True
                else:
                    logger.warning("Upload returned %d: %s", resp.status_code, resp.text)
                    return False
        except httpx.TimeoutException:
            logger.warning("Upload timed out for run=%s", run_id)
            return False
        except httpx.NetworkError as e:
            logger.warning("Network error uploading run=%s: %s", run_id, e)
            return False
        except Exception as e:
            logger.error("Upload failed for run=%s: %s", run_id, e)
            return False

    def upload_entry_queued(self, entry: dict, run_id: str = ""):
        if not self.should_upload():
            return
        sanitized = self.validator.sanitize_dict(entry)
        payload = self._build_payload(sanitized)

        issues = self.validator.validate_dict(sanitized)
        if issues:
            logger.warning("Privacy validation found %d issues, not queueing: %s", len(issues), issues)
            return

        package = {
            "run_id": run_id,
            "source_version": "1.0",
            "failure_atlas_entries": [payload],
            "telemetry_events": [],
            "escalations": [],
        }

        self.queue.enqueue("failure-atlas", package, run_id=run_id)

        def upload_fn(payload):
            self._do_http_upload(payload)

        self.retry.process_item(
            {"id": 0, "payload": json.dumps(package, default=str), "retry_count": 0},
            upload_fn,
        )

    def _do_http_upload(self, payload: dict):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{self.server_url}/api/v1/telemetry",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()

    def process_queue(self, batch_size: int = 10) -> dict:
        def upload_fn(payload):
            self._do_http_upload(payload)
        return self.retry.process_queue(upload_fn, batch_size)
