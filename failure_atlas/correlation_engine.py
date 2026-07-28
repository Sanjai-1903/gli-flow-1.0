import sqlite3
from pathlib import Path
import os
from typing import List, Dict, Any, Optional
from failure_atlas.repository import FailureAtlasRepository
from failure_atlas.intelligence_model import ExecutionIntelligenceRecord

def get_db_path():
    return os.environ.get("GLI_FLOW_DB") or os.environ.get("GLI_FLOW_DB_PATH") or str(Path.home() / ".gli_flow" / "gli_flow.db")

def get_correlation_data(failure_type: str):
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        
        # Statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN fix_applied = 1 THEN 1 ELSE 0 END) as resolved,
                MIN(detected_at) as first_seen,
                MAX(detected_at) as last_seen
            FROM failure_atlas_entries 
            WHERE failure_type = ?
        """, (failure_type,))
        stats = cursor.fetchone()
        
        # Affected Designs
        cursor.execute("""
            SELECT run_id, COUNT(*) as occurrences
            FROM failure_atlas_entries 
            WHERE failure_type = ?
            GROUP BY run_id
            ORDER BY occurrences DESC
        """, (failure_type,))
        designs = [dict(row) for row in cursor.fetchall()]
        
        # Recent Occurrences
        cursor.execute("""
            SELECT run_id, detected_at as timestamp, severity
            FROM failure_atlas_entries 
            WHERE failure_type = ?
            ORDER BY detected_at DESC LIMIT 10
        """, (failure_type,))
        recent = []
        for row in cursor.fetchall():
            recent.append({
                "run_id": row["run_id"],
                "design_name": "",
                "timestamp": row["timestamp"],
                "status": row["severity"],
                "is_important": row["severity"] == "TAPEOUT_BLOCKING"
            })
            
        # Resolution Lineage
        cursor.execute("""
            SELECT run_id, fix_type, fix_description, detected_at as timestamp
            FROM failure_atlas_entries 
            WHERE failure_type = ? AND fix_applied = 1
            ORDER BY detected_at DESC
        """, (failure_type,))
        lineage = []
        for row in cursor.fetchall():
            lineage.append({
                "run_id": row["run_id"],
                "fix_type": row["fix_type"],
                "fix_description": row["fix_description"],
                "outcome": "Resolved",
                "timestamp": row["timestamp"]
            })
            
        # Resolution Effectiveness
        is_drc_type = failure_type in ("DRC", "DRC_SPACING", "DRC_WIDTH", "DRC_ENCLOSURE", "DRC_ANTENNA", "DRC_DENSITY")
        success_condition = (
            "(json_extract(after_metrics, '$.drc_total') = 0 OR json_extract(after_metrics, '$.is_clean') = 1)"
            if is_drc_type else
            "(json_extract(after_metrics, '$.is_clean') = 1 OR json_extract(after_metrics, '$.setup_satisfied') = 1)"
        )
        cursor.execute(f"""
            SELECT 
                fix_type,
                COUNT(*) as attempts,
                SUM(CASE WHEN fix_applied = 1 AND {success_condition}
                    THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN severity = 'TAPEOUT_BLOCKING' THEN 1 ELSE 0 END) as important_run_count
            FROM failure_atlas_entries 
            WHERE failure_type = ? AND fix_type IS NOT NULL AND fix_type != ''
            GROUP BY fix_type
            ORDER BY successful DESC
        """, (failure_type,))
        
        effectiveness = []
        for row in cursor.fetchall():
            effectiveness.append({
                "fix_type": row["fix_type"],
                "attempts": row["attempts"],
                "success_rate": round((row["successful"] / row["attempts"]) * 100, 1),
                "important_runs": row["important_run_count"]
            })
            
        return {
            "failure_type": failure_type,
            "statistics": {
                "total_occurrences": stats["total"] or 0,
                "resolved_count": stats["resolved"] or 0,
                "unresolved_count": (stats["total"] or 0) - (stats["resolved"] or 0),
                "first_seen": stats["first_seen"] or "",
                "last_seen": stats["last_seen"] or ""
            },
            "affected_designs": designs,
            "recent_occurrences": recent,
            "resolution_lineage": lineage,
            "resolution_effectiveness": effectiveness,
            "telemetry": {
                "knowledge_views": len(effectiveness),
                "signature_missing_events": len([r for r in recent if not r.get("is_important")])
            }
        }
    finally:
        conn.close()

class CorrelationEngine:
    """Analyzes failure patterns to establish relationships between failures, root causes, and resolutions."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)
        
    def correlate(self, failure_id: str) -> Dict[str, Any]:
        failure = self.repo.get_failure_by_id(failure_id)
        if not failure:
            return {}
            
        # Correlate failure with other events in the same run
        related = self.repo.get_entries_for_run(failure['run_id'])
        
        # Build a correlation chain: Failure -> Root Cause -> Resolution
        return {
            "failure": failure,
            "related_events": related,
            "root_cause": self._find_root_cause(failure),
            "resolution": self._find_resolution(failure)
        }
        
    def _find_root_cause(self, failure: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Logic to extract root cause from evidence
        evidence = failure.get("evidence", {})
        if isinstance(evidence, dict) and "root_cause" in evidence:
            return evidence["root_cause"]
        return None
        
    def _find_resolution(self, failure: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if failure.get("fix_applied"):
            return {
                "fix_type": failure.get("fix_type"),
                "fix_description": failure.get("fix_description")
            }
        return None
