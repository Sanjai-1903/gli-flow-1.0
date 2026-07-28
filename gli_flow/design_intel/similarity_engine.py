import json
import math
import sqlite3
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
from gli_flow.database.migrations import _get_db_path
from gli_flow.design_intel.profile_engine import DesignProfileEngine, DesignProfile
from gli_flow.design_intel.feature_extractor import DesignFeatureExtractor, DesignFeatureRecord
from gli_flow.design_intel.design_classifier import DesignClassifier, DesignClass

log = logging.getLogger(__name__)


@dataclass
class DesignSimilarityResult:
    design_name: str
    similarity_score: float
    shared_class: bool
    cell_ratio: float
    depth_ratio: float


class DesignSimilarityEngine:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or _get_db_path()
        self._profile_engine = DesignProfileEngine(self._db_path)
        self._feature_extractor = DesignFeatureExtractor(self._db_path)
        self._classifier = DesignClassifier(self._db_path)
        self._profiles: Dict[str, DesignProfile] = {}
        self._features: Dict[str, DesignFeatureRecord] = {}
        self._classes: Dict[str, str] = {}

    def _load_all(self):
        for p in self._profile_engine.list_profiles():
            self._profiles[p.design_name] = p
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM design_features").fetchall()
            for r in rows:
                feat = DesignFeatureRecord(
                    design_name=r["design_name"],
                    fanout_histogram=json.loads(r["fanout_histogram"]),
                    logic_depth=r["logic_depth"] or 0,
                    register_density=r["register_density"] or 0.0,
                    memory_density=r["memory_density"] or 0.0,
                    dsp_density=r["dsp_density"] or 0.0,
                    combinational_depth=r["combinational_depth"] or 0,
                    sequential_depth=r["sequential_depth"] or 0,
                )
                self._features[feat.design_name] = feat
            cls_rows = conn.execute(
                "SELECT design_name, classification FROM design_profiles WHERE classification != ''"
            ).fetchall()
            for r in cls_rows:
                self._classes[r["design_name"]] = r["classification"]

    def find_similar(
        self, design_name: str, top_n: int = 5
    ) -> List[DesignSimilarityResult]:
        self._load_all()

        query_profile = self._profiles.get(design_name)
        query_features = self._features.get(design_name)
        query_class = self._classes.get(design_name)

        if not query_profile and not query_features:
            return []

        scores: List[Tuple[str, float]] = []
        for name, profile in self._profiles.items():
            if name == design_name:
                continue

            score = 0.0
            components = 0

            if query_class and self._classes.get(name) == query_class:
                score += 30.0
                components += 1

            if query_profile and profile:
                delta_cells = abs(
                    query_profile.expected_cell_count - profile.expected_cell_count
                )
                max_cells = max(
                    query_profile.expected_cell_count, profile.expected_cell_count, 1
                )
                cell_score = (1 - delta_cells / max_cells) * 25
                score += max(0, cell_score)
                components += 1

                delta_mem = abs(
                    query_profile.memory_ratio - profile.memory_ratio
                )
                score += max(0, (1 - delta_mem * 3)) * 10
                components += 1

                delta_ctrl = abs(
                    query_profile.control_ratio - profile.control_ratio
                )
                score += max(0, (1 - delta_ctrl * 3)) * 10
                components += 1

            feat = self._features.get(name)
            if query_features and feat:
                delta_depth = abs(query_features.logic_depth - feat.logic_depth)
                max_depth = max(query_features.logic_depth, feat.logic_depth, 1)
                score += max(0, (1 - delta_depth / max_depth)) * 15
                components += 1

                delta_reg = abs(
                    query_features.register_density - feat.register_density
                )
                score += max(0, (1 - delta_reg * 3)) * 10
                components += 1

            if components > 0:
                avg_score = score / components if components > 0 else 0
                scores.append((name, round(avg_score, 4)))

        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for name, sim in scores[:top_n]:
            p = self._profiles.get(name)
            f = self._features.get(name)
            cell_ratio = (
                min(query_profile.expected_cell_count, p.expected_cell_count)
                / max(query_profile.expected_cell_count, p.expected_cell_count, 1)
                if query_profile and p
                else 0.0
            )
            depth_ratio = (
                min(query_features.logic_depth, f.logic_depth)
                / max(query_features.logic_depth, f.logic_depth, 1)
                if query_features and f
                else 0.0
            )
            results.append(
                DesignSimilarityResult(
                    design_name=name,
                    similarity_score=sim,
                    shared_class=query_class is not None
                    and self._classes.get(name) == query_class,
                    cell_ratio=round(cell_ratio, 4),
                    depth_ratio=round(depth_ratio, 4),
                )
            )

        return results

    def find_similar_by_class(self, design_class: DesignClass) -> List[str]:
        self._load_all()
        return [
            name
            for name, cls in self._classes.items()
            if cls == design_class.value
        ]

    def similarity_matrix(self) -> Dict[str, Dict[str, float]]:
        self._load_all()
        matrix = {}
        for name in self._profiles:
            similars = self.find_similar(name, top_n=10)
            matrix[name] = {s.design_name: s.similarity_score for s in similars}
        return matrix
