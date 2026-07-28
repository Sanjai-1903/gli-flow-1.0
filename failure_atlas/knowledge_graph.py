from typing import List, Dict, Any
from failure_atlas.repository import FailureAtlasRepository

class KnowledgeGraphBuilder:
    """Builds a knowledge graph from failure atlas entries."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)
        
    def build_snapshot(self) -> Dict[str, Any]:
        entries = self.repo.get_all_failures(limit=1000)
        
        nodes = {}
        edges = []
        
        for entry in entries:
            # Add nodes
            nodes[entry["failure_id"]] = {"type": "Failure", "data": entry}
            
            # Add relationships (edges)
            if entry.get("fix_applied"):
                edges.append({
                    "from": entry["failure_id"],
                    "to": entry.get("fix_run_id"),
                    "type": "fixed_by"
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
