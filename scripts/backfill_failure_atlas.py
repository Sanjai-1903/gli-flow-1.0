import os, sys, json, uuid, time, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from failure_atlas.repository import FailureAtlasRepository
from gli_flow.database.sqlite import DatabaseManager

db = DatabaseManager()
runs = db.get_recent_runs(limit=10000)
failed_runs = [r for r in runs if r["status"] == "FAILED"]

repo = FailureAtlasRepository()

# get existing run_ids from the failure_atlas_entries table
cursor = repo.connection.cursor()
cursor.execute("SELECT DISTINCT run_id FROM failure_atlas_entries")
existing_run_ids = {row[0] for row in cursor.fetchall()}

count = 0
for r in failed_runs:
    if r["run_id"] in existing_run_ids:
        continue
    entry = {
        "run_id": r["run_id"],
        "failure_id": str(uuid.uuid4()),
        "failure_type": "PIPELINE_FAILURE",
        "severity": "HIGH",
        "title": f"Pipeline failed at stage {r['current_stage'] or 'UNKNOWN'}",
        "description": f"Run {r['run_id']} failed at stage {r['current_stage'] or 'UNKNOWN'} with progress {r['progress']}%",
        "confidence": 0.9,
        "signature": f"pipeline_failure_{r['current_stage'] or 'UNKNOWN'}",
        "domain": "PIPELINE",
        "category": "PIPELINE_FAILURE",
        "evidence": json.dumps({"stage": r["current_stage"], "progress": r["progress"]}),
        "detected_at": r["timestamp"] or time.strftime('%Y-%m-%dT%H:%M:%S'),
    }
    repo.insert_entry(entry)
    count += 1

repo.close()
db.close()
print(f"Backfilled {count} failure atlas entries for previously failed runs")
