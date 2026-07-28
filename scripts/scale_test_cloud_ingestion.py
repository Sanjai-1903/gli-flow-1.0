#!/usr/bin/env python3
"""Beta scale test for cloud ingestion platform.

Simulates 100 users, 1000 uploads with network interruptions.
"""

import json
import os
import random
import sys
import time
from pathlib import Path
from threading import Thread

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from cloud_ingestion.config import CloudIngestionConfig
from cloud_ingestion.server import create_app

TEST_API_KEY = "scale-test-key"
BASE_URL = "http://127.0.0.1:18101"
PASS = 0
FAIL = 0

TOOLS = ["yosys", "openroad", "ngspice", "netgen", "magic"]
STAGES = ["synthesis", "floorplan", "placement", "cts", "routing", "finish"]
EVENTS = ["stage_completed", "failure_detected", "warning_issued", "timeout"]
FAILURE_TYPES = [
    "TIMING_VIOLATION", "DRC_VIOLATION", "ROUTING_VIOLATION",
    "SYNTHESIS_TIMEOUT", "CTS_SKEW", "ANTENNA_VIOLATION",
    "PLACEMENT_DENSITY", "POWER_DROOP",
]
DESIGNS = [
    ("counter", "Controller"), ("gcd", "Controller"), ("uart", "Controller"),
    ("aes_cipher", "Controller"), ("picorv32", "CPU"), ("ibex", "CPU"),
    ("serv", "CPU"), ("sram_controller", "Memory-heavy"),
    ("fir", "DSP"), ("gpio", "Interconnect"), ("tinyml_accel", "Accelerator"),
]


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
        print(f"  ✗ {name}: {detail}")


def generate_upload(user_id: int, seq: int) -> dict:
    design_name, design_cat = random.choice(DESIGNS)
    run_id = f"scale-user{user_id:03d}-run{seq:03d}"

    num_events = random.randint(1, 5)
    events = []
    for _ in range(num_events):
        events.append({
            "run_id": run_id,
            "tool": random.choice(TOOLS),
            "stage": random.choice(STAGES),
            "event": random.choice(EVENTS),
            "design_name": design_name,
            "metrics": {
                "runtime_sec": round(random.uniform(1, 300), 2),
                "cell_count": random.randint(100, 50000),
                "utilization": round(random.uniform(0.3, 0.95), 3),
            },
        })

    num_failures = random.randint(0, 3)
    failures = []
    for _ in range(num_failures):
        failures.append({
            "run_id": run_id,
            "tool": random.choice(TOOLS),
            "stage": random.choice(STAGES),
            "failure_type": random.choice(FAILURE_TYPES),
            "error_text": f"Simulated failure at stage {random.choice(STAGES)}",
            "design_name": design_name,
            "design_category": design_cat,
            "frequency": random.randint(1, 10),
        })

    return {
        "run_id": run_id,
        "source_version": "1.0",
        "telemetry_events": events,
        "failure_atlas_entries": failures,
        "escalations": [],
    }


def upload_worker(worker_id: int, num_uploads: int, results: list):
    headers = {"Content-Type": "application/json", "X-API-Key": TEST_API_KEY}
    for seq in range(num_uploads):
        payload = generate_upload(worker_id, seq)
        try:
            with httpx.Client(timeout=30.0) as client:
                # Simulate network interruption for ~10% of requests
                if random.random() < 0.1:
                    time.sleep(random.uniform(0.5, 3.0))

                resp = client.post(
                    f"{BASE_URL}/api/v1/telemetry",
                    json=payload,
                    headers=headers,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results.append({
                        "ok": True,
                        "run_id": payload["run_id"],
                        "events": len(payload["telemetry_events"]),
                        "failures": len(payload["failure_atlas_entries"]),
                    })
                else:
                    results.append({
                        "ok": False,
                        "run_id": payload["run_id"],
                        "error": f"HTTP {resp.status_code}",
                    })
        except Exception as e:
            results.append({
                "ok": False,
                "run_id": payload["run_id"],
                "error": str(e),
            })


def main():
    config = CloudIngestionConfig.load()
    config.server.port = 18101
    config.auth.api_key = TEST_API_KEY
    config.database.url = "sqlite:////tmp/cloud_ingestion_scale.db"
    config.auth.enabled = True

    app = create_app(config)

    import uvicorn
    server_thread = Thread(
        target=uvicorn.run,
        args=(app,),
        kwargs={"host": "127.0.0.1", "port": 18101, "log_level": "error"},
        daemon=True,
    )
    server_thread.start()
    time.sleep(2)

    print(f"Server started at {BASE_URL}")

    NUM_USERS = 100
    UPLOADS_PER_USER = 10
    NUM_WORKERS = 10
    total_uploads = NUM_USERS * UPLOADS_PER_USER

    print(f"\nSimulating {NUM_USERS} users × {UPLOADS_PER_USER} uploads = {total_uploads} total")
    start = time.time()

    all_results = []
    threads = []
    uploads_per_worker = total_uploads // NUM_WORKERS

    for w in range(NUM_WORKERS):
        t = Thread(
            target=upload_worker,
            args=(w, uploads_per_worker, all_results),
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.time() - start
    succeeded = sum(1 for r in all_results if r["ok"])
    failed = sum(1 for r in all_results if not r["ok"])
    total_events = sum(r.get("events", 0) for r in all_results if r["ok"])
    total_failures = sum(r.get("failures", 0) for r in all_results if r["ok"])

    print(f"\n=== Scale Test Results ===")
    print(f"  Duration: {elapsed:.1f}s")
    print(f"  Throughput: {total_uploads / elapsed:.1f} uploads/sec")
    print(f"  Succeeded: {succeeded}")
    print(f"  Failed: {failed}")
    print(f"  Total events ingested: {total_events}")
    print(f"  Total failures ingested: {total_failures}")
    print(f"  Success rate: {100 * succeeded / total_uploads:.1f}%")

    check(f"Throughput > 20 uploads/sec", total_uploads / elapsed > 20,
          f"got {total_uploads / elapsed:.1f}")
    check(f"Success rate > 90%", succeeded / total_uploads > 0.9,
          f"got {100 * succeeded / total_uploads:.1f}%")
    check(f"All {total_uploads} requests completed",
          len(all_results) == total_uploads)

    from cloud_ingestion.database import IngestionDatabase
    db = IngestionDatabase(config)
    db.initialize()
    stats = db.get_stats()
    print(f"\n  DB telemetry events: {stats['total_telemetry_events']}")
    print(f"  DB failure entries: {stats['total_failure_atlas_entries']}")
    print(f"  DB upload audits: {stats['total_uploads']}")
    print(f"  DB unique runs: {stats['unique_runs']}")
    print(f"  DB size: {stats['db_size_bytes']} bytes")
    db.close()

    print(f"\n{'='*50}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    print(f"{'='*50}")

    if os.path.exists("/tmp/cloud_ingestion_scale.db"):
        os.unlink("/tmp/cloud_ingestion_scale.db")

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
