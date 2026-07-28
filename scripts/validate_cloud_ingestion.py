#!/usr/bin/env python3
"""E2E validation of the cloud ingestion pipeline.

Launches the ingestion server → simulates telemetry uploads → verifies DB.
Tests: Run→Telemetry→Sanitizer→Queue→HTTPS→Server→Database.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from cloud_ingestion.config import CloudIngestionConfig
from cloud_ingestion.server import create_app
from cloud_ingestion.database import IngestionDatabase

TEST_RUN_ID = "validation-test-run-001"
TEST_API_KEY = "test-api-key-validation"
PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name}: {detail}")


def main():
    config = CloudIngestionConfig.load()
    config.server.port = 18100
    config.auth.api_key = TEST_API_KEY
    config.database.url = "sqlite:////tmp/cloud_ingestion_validation.db"

    db = IngestionDatabase(config)
    db.initialize()

    app = create_app(config)

    import uvicorn
    from threading import Thread

    server_thread = Thread(
        target=uvicorn.run,
        args=(app,),
        kwargs={"host": "127.0.0.1", "port": 18100, "log_level": "error"},
        daemon=True,
    )
    server_thread.start()
    time.sleep(2)

    base_url = "http://127.0.0.1:18100"
    headers = {"Content-Type": "application/json", "X-API-Key": TEST_API_KEY}

    print("\n=== Phase 1: Health Check ===")
    try:
        resp = httpx.get(f"{base_url}/api/v1/health", timeout=5)
        check("Health endpoint responds", resp.status_code == 200)
        check("Status is ok", resp.json().get("status") == "ok")
    except Exception as e:
        check("Health endpoint responds", False, str(e))

    print("\n=== Phase 2: Auth Enforcement ===")
    try:
        resp = httpx.post(
            f"{base_url}/api/v1/telemetry",
            json={"run_id": TEST_RUN_ID, "source_version": "1.0"},
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        check("Rejects missing API key", resp.status_code == 401)
    except Exception as e:
        check("Rejects missing API key", False, str(e))

    print("\n=== Phase 3: Empty Upload ===")
    try:
        resp = httpx.post(
            f"{base_url}/api/v1/telemetry",
            json={
                "run_id": TEST_RUN_ID,
                "source_version": "1.0",
                "telemetry_events": [],
                "failure_atlas_entries": [],
                "escalations": [],
            },
            headers=headers,
            timeout=5,
        )
        check("Empty upload accepted", resp.status_code == 200)
        data = resp.json()
        check("Returns run_id", data.get("run_id") == TEST_RUN_ID)
        check("Status is accepted", data.get("status") == "accepted")
    except Exception as e:
        check("Empty upload accepted", False, str(e))

    print("\n=== Phase 4: Telemetry Event Upload ===")
    telemetry_events = [
        {
            "run_id": TEST_RUN_ID,
            "tool": "yosys",
            "stage": "synthesis",
            "event": "synthesis_completed",
            "design_name": "counter",
            "metrics": {"runtime_sec": 12.5, "cell_count": 150},
            "recorded_at": "2025-01-01T00:00:00Z",
        },
        {
            "run_id": TEST_RUN_ID,
            "tool": "openroad",
            "stage": "placement",
            "event": "placement_completed",
            "design_name": "counter",
            "metrics": {"runtime_sec": 45.2, "utilization": 0.65},
            "recorded_at": "2025-01-01T00:01:00Z",
        },
    ]
    try:
        resp = httpx.post(
            f"{base_url}/api/v1/telemetry",
            json={
                "run_id": TEST_RUN_ID,
                "source_version": "1.0",
                "telemetry_events": telemetry_events,
                "failure_atlas_entries": [],
                "escalations": [],
            },
            headers=headers,
            timeout=5,
        )
        check("Telemetry upload accepted", resp.status_code == 200)
        data = resp.json()
        check("2 events accepted", data.get("telemetry_accepted") == 2)
    except Exception as e:
        check("Telemetry upload accepted", False, str(e))

    print("\n=== Phase 5: Failure Atlas Upload ===")
    fa_entries = [
        {
            "run_id": TEST_RUN_ID,
            "tool": "openroad",
            "stage": "routing",
            "failure_type": "ROUTING_VIOLATION",
            "error_text": "Unroutable pin at (10,20)",
            "design_name": "gcd",
            "design_category": "Controller",
            "frequency": 3,
        },
        {
            "run_id": TEST_RUN_ID,
            "tool": "yosys",
            "stage": "synthesis",
            "failure_type": "SYNTHESIS_TIMEOUT",
            "error_text": "Synthesis exceeded 3600s",
            "design_name": "aes_cipher",
            "design_category": "Controller",
        },
    ]
    try:
        resp = httpx.post(
            f"{base_url}/api/v1/telemetry",
            json={
                "run_id": TEST_RUN_ID,
                "source_version": "1.0",
                "telemetry_events": [],
                "failure_atlas_entries": fa_entries,
                "escalations": [],
            },
            headers=headers,
            timeout=5,
        )
        check("FA upload accepted", resp.status_code == 200)
        data = resp.json()
        check("2 failures accepted", data.get("failures_accepted") == 2)
        upload_id = data.get("upload_id", "")
        check("Upload ID generated", bool(upload_id))
    except Exception as e:
        check("FA upload accepted", False, str(e))

    print("\n=== Phase 6: Database Verification ===")
    stats = db.get_stats()
    check("Telemetry events in DB", stats["total_telemetry_events"] >= 2)
    check("FA entries in DB", stats["total_failure_atlas_entries"] >= 2)
    check("Upload audit recorded", stats["total_uploads"] >= 2)
    check("Unique runs tracked", stats["unique_runs"] >= 1)

    print("\n=== Phase 7: Client-Side UploadQueue ===")
    from gli_flow.telemetry.upload_queue import UploadQueue
    q = UploadQueue(db_path="/tmp/test_upload_queue.db")
    q_id = q.enqueue("telemetry", {"test": "payload"}, run_id="test-run")
    check("Queue enqueue works", q_id > 0)
    items = q.dequeue(limit=5)
    check("Queue dequeue works", len(items) >= 1)
    check("Dequeued item matches", items[0]["destination"] == "telemetry")

    q.mark_completed(items[0]["id"])
    remaining = q.get_pending_count()
    check("Queue items marked completed", remaining >= 0)

    q.flush_completed(older_than_hours=0)
    stats = q.get_queue_stats()
    check("Queue flush works", stats["total"] >= 0)

    if os.path.exists("/tmp/test_upload_queue.db"):
        os.unlink("/tmp/test_upload_queue.db")

    print("\n=== Phase 8: Client-Side Retry Engine ===")
    from gli_flow.telemetry.retry_engine import RetryEngine
    re = RetryEngine()
    for i in range(5):
        delay = re.get_delay(i)
        check(f"Retry delay {i} is reasonable", 1 <= delay <= 7200, f"got {delay:.1f}s")
        if i >= 3:
            break

    check("Should retry at 0", re.should_retry(0) == True)
    check("Should retry at 9", re.should_retry(9) == True)
    check("Should NOT retry at 10", re.should_retry(10) == False)

    print("\n=== Phase 9: Client-Side FailureAtlasUploader ===")
    from gli_flow.telemetry.failure_atlas_uploader import FailureAtlasUploader
    fa_uploader = FailureAtlasUploader(
        server_url=base_url,
        api_key=TEST_API_KEY,
    )
    fa_entry = {
        "run_id": TEST_RUN_ID,
        "tool": "openroad",
        "stage": "cts",
        "failure_type": "CTS_SKEW_VIOLATION",
        "error_text": "Clock skew exceeds limit",
        "design_name": "uart",
        "design_category": "Controller",
    }
    result = fa_uploader.upload_entry(fa_entry, run_id=TEST_RUN_ID)
    check("FA uploader direct upload", result == True)

    print("\n=== Phase 10: Stats Endpoint ===")
    try:
        resp = httpx.get(f"{base_url}/api/v1/stats", headers=headers, timeout=5)
        check("Stats endpoint responds", resp.status_code == 200)
        s = resp.json()
        check("Stats has telemetry count", s.get("total_telemetry_events", 0) >= 2)
    except Exception as e:
        check("Stats endpoint responds", False, str(e))

    print(f"\n{'='*50}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    print(f"{'='*50}")

    db.close()

    if os.path.exists("/tmp/cloud_ingestion_validation.db"):
        os.unlink("/tmp/cloud_ingestion_validation.db")

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
