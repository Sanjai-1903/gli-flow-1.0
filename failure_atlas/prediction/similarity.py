import math
from typing import List, Dict, Any, Optional
from failure_atlas.repository import FailureAtlasRepository


class ExecutionSimilarityEngine:
    """Finds historical runs similar to the current one based on design + metric similarity.

    Combines:
      - Run-level metric similarity (Euclidean distance on WNS, TNS, utilization, DRC)
      - Design-level similarity (class, cell count, ratios, depth, density)

    When design_name is provided, entries from design-similar designs get a boost.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.repo = FailureAtlasRepository(db_path=db_path)
        self._design_engine = None

    @property
    def design_engine(self):
        if self._design_engine is None:
            from gli_flow.design_intel.similarity_engine import DesignSimilarityEngine
            self._design_engine = DesignSimilarityEngine(self.repo.db_path)
        return self._design_engine

    def _normalize(self, metrics: Dict[str, Any]) -> List[float]:
        return [
            float(metrics.get("wns", 0.0)),
            float(metrics.get("tns", 0.0)),
            float(metrics.get("utilization", 0)),
            float(metrics.get("drc_violations", 0)),
        ]

    def _extract_metrics(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        before = entry.get("before_metrics", {})
        if isinstance(before, str):
            import json
            before = json.loads(before)
        if isinstance(before, dict):
            return {
                "wns": before.get("wns", 0.0),
                "tns": before.get("tns", 0.0),
                "utilization": before.get("utilization", 50),
                "drc_violations": before.get("drc_total", 0),
            }
        return {}

    def _euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

    def find_similar(self, current_metrics: Dict[str, Any], top_n: int = 3,
                     design_name: Optional[str] = None) -> List[Dict[str, Any]]:
        current_vec = self._normalize(current_metrics)
        all_entries = self.repo.get_all_failures(limit=1000)

        if not all_entries:
            return []

        design_sim_map = {}
        if design_name:
            try:
                similar_designs = self.design_engine.find_similar(design_name, top_n=10)
                for sd in similar_designs:
                    design_sim_map[sd.design_name] = sd.similarity_score
            except Exception:
                design_sim_map = {}

        scored = []
        for entry in all_entries:
            hist_metrics = self._extract_metrics(entry)
            hist_vec = self._normalize(hist_metrics)
            distance = self._euclidean_distance(current_vec, hist_vec)
            run_similarity = 1.0 / (1.0 + distance)

            entry_design = entry.get("design_name", "") or ""
            design_boost = 1.0
            if entry_design in design_sim_map:
                design_boost = 1.0 + (design_sim_map[entry_design] / 100.0 * 0.5)
            elif design_name and entry_design == design_name:
                design_boost = 1.5

            similarity = run_similarity * design_boost

            scored.append({
                "run_id": entry.get("run_id", "unknown"),
                "entry_id": entry.get("id", ""),
                "failure_type": entry.get("failure_type", "UNKNOWN"),
                "design_name": entry_design,
                "vec": hist_vec,
                "similarity": round(similarity, 4),
                "run_similarity": round(run_similarity, 4),
                "design_boost": round(design_boost, 4),
                "detected_at": entry.get("detected_at", ""),
            })

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_n]

    def find_similar_by_failure_type(self, failure_type: str, top_n: int = 5) -> List[Dict[str, Any]]:
        entries = self.repo.search_entries(failure_type=failure_type, limit=100)
        scored = []
        for entry in entries:
            scored.append({
                "run_id": entry.get("run_id", "unknown"),
                "entry_id": entry.get("id", ""),
                "failure_type": entry.get("failure_type", "UNKNOWN"),
                "similarity": entry.get("confidence", 0.5),
                "detected_at": entry.get("detected_at", ""),
            })
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_n]
