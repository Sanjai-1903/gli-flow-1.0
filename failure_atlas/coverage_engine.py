import sqlite3
import json
from pathlib import Path
import re
import os

def get_db_path():
    return os.environ.get("GLI_FLOW_DB") or str(Path.home() / ".gli_flow" / "gli_flow.db")

def get_coverage_data():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    
    # 1. Parse Telemetry Logs
    viewed = {}
    missing = {}
    
    # Assuming run logs are stored in a consistent directory structure
    runs_dir = Path(__file__).resolve().parent.parent / "outputs" / "runs"
    
    if runs_dir.exists():
        for log_file in runs_dir.rglob("*.log"):
            content = log_file.read_text(errors="ignore")
            for m in re.finditer(r"\[TELEMETRY\] rule_knowledge_viewed: rule_id=([^,]+)", content):
                rid = m.group(1)
                viewed[rid] = viewed.get(rid, 0) + 1
            for m in re.finditer(r"\[TELEMETRY\] signature_missing: rule_id=([^,]+)", content):
                rid = m.group(1)
                missing[rid] = missing.get(rid, 0) + 1
                
    # 2. Database Aggregations
    cursor = conn.cursor()
    
    # Most Common Failures
    cursor.execute("""
        SELECT failure_type, COUNT(*) as count 
        FROM failure_atlas_entries 
        GROUP BY failure_type 
        ORDER BY count DESC LIMIT 10
    """)
    common = [dict(row) for row in cursor.fetchall()]
    
    # Most Resolved
    cursor.execute("""
        SELECT failure_type, COUNT(*) as count 
        FROM failure_atlas_entries 
        WHERE fix_applied = 1 
        GROUP BY failure_type 
        ORDER BY count DESC LIMIT 10
    """)
    resolved = [dict(row) for row in cursor.fetchall()]
    
    # Most Unresolved
    cursor.execute("""
        SELECT failure_type, COUNT(*) as count 
        FROM failure_atlas_entries 
        WHERE fix_applied = 0 
        GROUP BY failure_type 
        ORDER BY count DESC LIMIT 10
    """)
    unresolved = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "most_viewed": [{"rule_id": k, "views": v} for k, v in sorted(viewed.items(), key=lambda item: item[1], reverse=True)[:10]],
        "most_requested_missing": [{"rule_id": k, "requests": v} for k, v in sorted(missing.items(), key=lambda item: item[1], reverse=True)[:10]],
        "common_failures": common,
        "most_resolved": resolved,
        "most_unresolved": unresolved
    }
