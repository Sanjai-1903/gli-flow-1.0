import sqlite3
from failure_atlas.run_trust_engine import RunTrustEngine
import os
from pathlib import Path

def run_audit():
    db_path = os.environ.get("GLI_FLOW_DB") or str(Path.home() / ".gli_flow" / "gli_flow.db")
    engine = RunTrustEngine(db_path)
    
    with sqlite3.connect(db_path) as conn:
        runs = conn.execute("SELECT run_id, design_name FROM runs ORDER BY timestamp DESC LIMIT 20").fetchall()
    
    print(f"{'Run ID':<20} | {'Design':<15} | {'Trust Ratio':<12} | {'V/H/U Breakdown'}")
    print("-" * 75)
    
    for run_id, design in runs:
        score = engine.compute_run_trust_score(run_id)
        breakdown = f"{score['verified_count']}/{score['heuristic_count']}/{score['unverified_count']}"
        print(f"{run_id:<20} | {design:<15} | {score['trust_ratio']:<12.2f} | {breakdown}")

if __name__ == "__main__":
    run_audit()
