import sqlite3
import uuid
from pathlib import Path
from datetime import datetime

DB_PATH = str(Path.home() / ".gli_flow" / "gli_flow.db")

def inject():
    conn = sqlite3.connect(DB_PATH)
    run_id = "run_1781605284_5d70499f_picorv32"
    
    failures = [
        {
            "id": str(uuid.uuid4()),
            "run_id": run_id,
            "failure_type": "TIMING_VIOLATION",
            "severity": "CRITICAL",
            "title": "Setup timing violation in CTS",
            "description": "Metastability risk detected due to negative slack.",
            "tool_name": "OpenROAD",
            "tool_stage": "CTS"
        },
        {
            "id": str(uuid.uuid4()),
            "run_id": run_id,
            "failure_type": "DRC_VIOLATION",
            "severity": "ERROR",
            "title": "Metal1 spacing violation",
            "description": "Minimum spacing requirement not met on M1 layer.",
            "tool_name": "Magic",
            "tool_stage": "DRC"
        }
    ]
    
    for f in failures:
        conn.execute("""
            INSERT INTO failure_atlas_entries 
            (id, run_id, failure_type, severity, title, description, tool_name, tool_stage, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (f["id"], f["run_id"], f["failure_type"], f["severity"], f["title"], f["description"], f["tool_name"], f["tool_stage"], datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    print("Injected 2 test failures into failure_atlas_entries")

if __name__ == "__main__":
    inject()
