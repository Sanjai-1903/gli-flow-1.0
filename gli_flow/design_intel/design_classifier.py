import json
import sqlite3
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional
from gli_flow.database.migrations import _get_db_path
from gli_flow.design_intel.profile_engine import DesignProfile, DesignProfileEngine
from gli_flow.design_intel.feature_extractor import DesignFeatureRecord, DesignFeatureExtractor

log = logging.getLogger(__name__)


class DesignClass(Enum):
    CPU = "CPU"
    CONTROLLER = "Controller"
    DSP = "DSP"
    ACCELERATOR = "Accelerator"
    MEMORY_HEAVY = "Memory-heavy"
    INTERCONNECT = "Interconnect"


CLASSIFICATION_RULES = {
    "CPU": {
        "tags_contain": ["cpu"],
        "min_register_density": 0.20,
        "min_control_ratio": 0.30,
        "description": "General-purpose processor with control-heavy logic",
    },
    "DSP": {
        "tags_contain": ["dsp"],
        "min_logic_depth": 8,
        "min_compute_ratio": 0.60,
        "description": "Digital signal processing with deep datapath",
    },
    "Accelerator": {
        "tags_contain": ["ml"],
        "min_dsp_density": 0.10,
        "min_compute_ratio": 0.50,
        "description": "ML/AI accelerator with dense compute",
    },
    "Memory-heavy": {
        "tags_contain": ["sram", "memory"],
        "min_memory_ratio": 0.15,
        "min_memory_density": 0.10,
        "description": "Design dominated by SRAM/memory macros",
    },
    "Interconnect": {
        "tags_contain": ["io"],
        "min_fanout_high": True,
        "description": "I/O or interconnect-heavy design",
    },
    "Controller": {
        "tags_contain": ["sequential", "combinatorial"],
        "min_register_density": 0.05,
        "description": "FSM or control logic design",
    },
}


class DesignClassifier:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or _get_db_path()
        self._profile_engine = DesignProfileEngine(self._db_path)
        self._feature_extractor = DesignFeatureExtractor(self._db_path)

    def _conn(self):
        return sqlite3.connect(self._db_path)

    def _golden_tags(self, design_name: str) -> List[str]:
        from gli_flow.synthetic.golden_designs import GOLDEN_DESIGNS
        for d in GOLDEN_DESIGNS:
            if d.name == design_name:
                return d.tags
        return []

    def classify(self, design_name: str) -> DesignClass:
        tags = self._golden_tags(design_name)
        profile = self._profile_engine.get_profile(design_name)
        features = self._feature_extractor.get_features(design_name)

        for cls_name in ("CPU", "DSP", "Accelerator", "Memory-heavy", "Interconnect", "Controller"):
            rule = CLASSIFICATION_RULES[cls_name]

            tag_match = any(t in tags for t in rule.get("tags_contain", []))
            if not tag_match:
                continue

            feature_match = True
            if "min_register_density" in rule and features:
                if features.register_density < rule["min_register_density"]:
                    feature_match = False
            if "min_logic_depth" in rule and features:
                if features.logic_depth < rule["min_logic_depth"]:
                    feature_match = False
            if "min_compute_ratio" in rule and profile:
                if profile.compute_ratio < rule["min_compute_ratio"]:
                    feature_match = False
            if "min_dsp_density" in rule and features:
                if features.dsp_density < rule["min_dsp_density"]:
                    feature_match = False
            if "min_memory_ratio" in rule and profile:
                if profile.memory_ratio < rule["min_memory_ratio"]:
                    feature_match = False
            if "min_memory_density" in rule and features:
                if features.memory_density < rule["min_memory_density"]:
                    feature_match = False

            if tag_match and feature_match:
                return DesignClass(cls_name)

        return DesignClass.CONTROLLER

    def classify_all(self) -> Dict[str, DesignClass]:
        with self._conn() as conn:
            names = conn.execute(
                "SELECT design_name FROM design_profiles"
            ).fetchall()
        results = {}
        for (name,) in names:
            cls = self.classify(name)
            results[name] = cls
            self._store_classification(name, cls.value)
        return results

    def _store_classification(self, design_name: str, class_name: str):
        with self._conn() as conn:
            conn.execute(
                "UPDATE design_profiles SET classification = ? WHERE design_name = ?",
                (class_name, design_name),
            )

    def get_classification(self, design_name: str) -> Optional[DesignClass]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT classification FROM design_profiles WHERE design_name = ?",
                (design_name,),
            ).fetchone()
            if row and row[0]:
                return DesignClass(row[0])
        return None

    def summary(self) -> Dict[str, Any]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT classification, COUNT(*) FROM design_profiles WHERE classification != '' GROUP BY classification ORDER BY COUNT(*) DESC"
            ).fetchall()
        distribution = {r[0]: r[1] for r in rows}
        total = sum(distribution.values())
        return {
            "distribution": distribution,
            "total_classified": total,
        }
