import sqlite3
from typing import Dict, Any

class RunTrustEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def compute_run_trust_score(self, run_id: str) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            entries = conn.execute(
                "SELECT detection_classification FROM failure_atlas_entries WHERE run_id = ?",
                (run_id,)
            ).fetchall()
            
            total = len(entries)
            if total == 0:
                return {"verified_count": 0, "heuristic_count": 0, "unverified_count": 0, "trust_ratio": 0.0}
            
            verified = sum(1 for e in entries if e["detection_classification"] == "VERIFIED")
            heuristic = sum(1 for e in entries if e["detection_classification"] == "HEURISTIC")
            unverified = sum(1 for e in entries if e["detection_classification"] == "UNVERIFIED")
            
            trust_ratio = verified / total
            
            return {
                "verified_count": verified,
                "heuristic_count": heuristic,
                "unverified_count": unverified,
                "trust_ratio": round(trust_ratio, 4)
            }
