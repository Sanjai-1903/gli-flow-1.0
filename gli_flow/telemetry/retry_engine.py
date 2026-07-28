import json
import logging
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Callable

from gli_flow.telemetry.upload_queue import UploadQueue

logger = logging.getLogger(__name__)

BASE_DELAY_SEC = 30
MAX_DELAY_SEC = 3600
MAX_RETRIES = 10


class RetryEngine:
    def __init__(self, queue: Optional[UploadQueue] = None):
        self.queue = queue or UploadQueue()

    @staticmethod
    def get_delay(retry_count: int) -> float:
        base = BASE_DELAY_SEC * (2 ** retry_count)
        delay = min(base, MAX_DELAY_SEC)
        jitter = random.uniform(-0.25, 0.25) * delay
        return max(delay + jitter, 1.0)

    @staticmethod
    def should_retry(retry_count: int) -> bool:
        return retry_count < MAX_RETRIES

    def _get_next_retry_at(self, retry_count: int) -> str:
        delay = self.get_delay(retry_count)
        next_time = datetime.now(timezone.utc) + timedelta(seconds=delay)
        return next_time.isoformat()

    def process_item(self, item: dict, upload_fn: Callable) -> bool:
        try:
            payload = json.loads(item["payload"])
            upload_fn(payload)
            self.queue.mark_completed(item["id"])
            return True
        except Exception as e:
            retry_count = item.get("retry_count", 0)
            if self.should_retry(retry_count):
                next_at = self._get_next_retry_at(retry_count)
                self.queue.mark_failed(item["id"], str(e), next_at)
                logger.warning(
                    "Upload failed for item=%d (retry %d/%d), next at %s: %s",
                    item["id"], retry_count + 1, MAX_RETRIES, next_at, e,
                )
            else:
                self.queue.mark_failed(item["id"], f"Max retries exceeded: {e}")
                logger.error(
                    "Upload failed permanently for item=%d after %d retries: %s",
                    item["id"], retry_count, e,
                )
            return False

    def process_queue(self, upload_fn: Callable, batch_size: int = 10) -> dict:
        results = {"processed": 0, "succeeded": 0, "failed": 0, "errors": []}
        items = self.queue.dequeue(limit=batch_size)
        for item in items:
            success = self.process_item(item, upload_fn)
            results["processed"] += 1
            if success:
                results["succeeded"] += 1
            else:
                results["failed"] += 1
                if item.get("retry_count", 0) >= MAX_RETRIES:
                    results["errors"].append(
                        f"item={item['id']}: max retries exceeded"
                    )
        return results
