from typing import Dict, Any, List, Optional
from failure_atlas.repository import FailureAtlasRepository


class KnowledgeGraphBuilder:
    """Builds a knowledge graph from real warehouse records via FailureAtlasRepository.

    Graph entities: Failures, Runs, Fixes, Root Causes
    Graph relationships: causes, fixed_by, similar_to, related_to
    """

    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)
        self.graph = {"entities": [], "relationships": []}

    def build_from_warehouse(self):
        self.graph = {"entities": [], "relationships": []}
        entries = self.repo.get_all_failures(limit=2000)
        seen_entities = set()
        seen_edges = set()

        for entry in entries:
            failure_id = entry.get("failure_id", "")
            failure_type = entry.get("failure_type", "UNKNOWN")
            run_id = entry.get("run_id", "")
            fix_type = entry.get("fix_type", "")
            root_cause = entry.get("description", "Unknown")[:100]

            if failure_id and failure_id not in seen_entities:
                self.graph["entities"].append({
                    "type": "Failure",
                    "id": failure_id,
                    "failure_type": failure_type,
                    "severity": entry.get("severity", ""),
                    "detected_at": entry.get("detected_at", ""),
                })
                seen_entities.add(failure_id)

            edge_key = (failure_id, run_id, "occurs_in")
            if run_id and edge_key not in seen_edges:
                self.graph["relationships"].append({
                    "from": failure_id,
                    "to": run_id,
                    "type": "occurs_in",
                })
                seen_edges.add(edge_key)

            if root_cause and root_cause != "Unknown":
                rc_id = f"rc_{hash(root_cause)}"
                if rc_id not in seen_entities:
                    self.graph["entities"].append({
                        "type": "RootCause",
                        "id": rc_id,
                        "description": root_cause,
                    })
                    seen_entities.add(rc_id)
                rc_edge = (failure_id, rc_id, "caused_by")
                if rc_edge not in seen_edges:
                    self.graph["relationships"].append({
                        "from": failure_id,
                        "to": rc_id,
                        "type": "caused_by",
                    })
                    seen_edges.add(rc_edge)

            if fix_type:
                fix_id = f"fix_{fix_type.replace(' ', '_')}"
                if fix_id not in seen_entities:
                    self.graph["entities"].append({
                        "type": "Fix",
                        "id": fix_id,
                        "fix_type": fix_type,
                    })
                    seen_entities.add(fix_id)
                fix_edge = (failure_id, fix_id, "resolved_by")
                if fix_edge not in seen_edges:
                    self.graph["relationships"].append({
                        "from": failure_id,
                        "to": fix_id,
                        "type": "resolved_by" if entry.get("fix_applied") else "attempted_by",
                    })
                    seen_edges.add(fix_edge)

        related = self.repo.get_related_entries(entries[0]["id"]) if entries else []
        for r in related:
            rel_id = r.get("failure_id", "")
            if rel_id and rel_id not in seen_entities:
                self.graph["entities"].append({
                    "type": "Failure",
                    "id": rel_id,
                    "failure_type": r.get("failure_type", "UNKNOWN"),
                    "severity": r.get("severity", ""),
                })
                seen_entities.add(rel_id)
            if failure_id and rel_id:
                rel_edge = (failure_id, rel_id, "related_to")
                if rel_edge not in seen_edges:
                    self.graph["relationships"].append({
                        "from": failure_id,
                        "to": rel_id,
                        "type": "related_to",
                    })
                    seen_edges.add(rel_edge)

        return self.graph

    def get_failure_subgraph(self, failure_type: str) -> Dict[str, Any]:
        entries = self.repo.search_entries(failure_type=failure_type, limit=100)
        subgraph = {"entities": [], "relationships": []}
        seen = set()
        for entry in entries:
            fid = entry.get("failure_id", "")
            if fid and fid not in seen:
                subgraph["entities"].append({
                    "type": "Failure",
                    "id": fid,
                    "failure_type": entry.get("failure_type", ""),
                    "severity": entry.get("severity", ""),
                })
                seen.add(fid)
            run_id = entry.get("run_id", "")
            if run_id and run_id not in seen:
                subgraph["entities"].append({"type": "Run", "id": run_id})
                seen.add(run_id)
            if fid and run_id:
                subgraph["relationships"].append({
                    "from": fid, "to": run_id, "type": "occurs_in"
                })
            if entry.get("fix_type"):
                fix_id = f"fix_{entry['fix_type'].replace(' ', '_')}"
                if fix_id not in seen:
                    subgraph["entities"].append({
                        "type": "Fix", "id": fix_id, "fix_type": entry["fix_type"]
                    })
                    seen.add(fix_id)
                subgraph["relationships"].append({
                    "from": fid, "to": fix_id, "type": "resolved_by" if entry.get("fix_applied") else "attempted_by"
                })
        return subgraph
