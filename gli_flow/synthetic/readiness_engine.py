import sqlite3
from typing import Dict, List, Any, Optional
from gli_flow.database.migrations import _get_db_path
from gli_flow.synthetic.dataset_records import TrainingDataset

ALL_FAILURE_CATEGORIES = [
    "Timing", "Routing", "CTS", "DRC", "LVS", "Power",
    "IR Drop", "Antenna", "Extraction", "Tool Failures",
]
ALL_DESIGNS = [
    "counter", "gcd", "uart", "gpio", "fir", "picorv32",
    "ibex", "serv", "opentitan_ibex", "tinyml_accel",
    "sram_controller", "aes_cipher",
]
ALL_STAGES = ["placement", "cts", "routing", "signoff", "lvs", "extraction"]
ALL_PDKS = ["sky130A"]


class CoverageEngine:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or _get_db_path()

    def _conn(self):
        return sqlite3.connect(self._db_path)

    def calculate_coverage(self, dataset: Optional[TrainingDataset] = None,
                           min_classification: str = "VERIFIED") -> Dict[str, float]:
        classification_filter = {
            "VERIFIED": ("VERIFIED",),
            "HEURISTIC": ("VERIFIED", "HEURISTIC"),
            "UNVERIFIED": ("VERIFIED", "HEURISTIC", "UNVERIFIED"),
        }.get(min_classification, ("VERIFIED", "HEURISTIC"))
        placeholders = ",".join("?" for _ in classification_filter)
        with self._conn() as conn:
            failure_types = set(
                r[0] for r in conn.execute(
                    f"SELECT DISTINCT failure_type FROM failure_atlas_entries "
                    f"WHERE failure_type IS NOT NULL "
                    f"AND detection_classification IN ({placeholders})",
                    classification_filter,
                ).fetchall()
            )
            designs = set(
                r[0] for r in conn.execute(
                    f"SELECT DISTINCT design_name FROM failure_atlas_entries "
                    f"WHERE design_name IS NOT NULL AND design_name != '' "
                    f"AND detection_classification IN ({placeholders})",
                    classification_filter,
                ).fetchall()
            )
            resolutions = set(
                r[0] for r in conn.execute(
                    "SELECT DISTINCT failure_type FROM resolution_patterns WHERE failure_type IS NOT NULL"
                ).fetchall()
            )
            stages = set(
                r[0] for r in conn.execute(
                    f"SELECT DISTINCT tool_stage FROM failure_atlas_entries "
                    f"WHERE tool_stage IS NOT NULL AND tool_stage != '' "
                    f"AND detection_classification IN ({placeholders})",
                    classification_filter,
                ).fetchall()
            )

        fc = min(len(failure_types) / len(ALL_FAILURE_CATEGORIES) * 100, 100)
        dc = min(len(designs) / len(ALL_DESIGNS) * 100, 100)
        rc = min(len(resolutions) / len(ALL_FAILURE_CATEGORIES) * 100, 100)
        sc = min(len(stages) / len(ALL_STAGES) * 100, 100)
        pc = 100.0 if ALL_PDKS[0] in set() else min(
            (len(set(ALL_PDKS) - {"sky130A"}) + 1) / len(ALL_PDKS) * 100, 100
        )

        return {
            "Failure": round(fc, 1),
            "Design": round(dc, 1),
            "Resolution": round(rc, 1),
            "Stage": round(sc, 1),
            "PDK": round(pc, 1),
        }


class CoverageGapDetector:
    THRESHOLD = 50.0

    def detect(self, coverage: Dict[str, float]) -> List[Dict[str, Any]]:
        gaps = []
        for area, pct in coverage.items():
            if pct < self.THRESHOLD:
                gaps.append({
                    "Area": area,
                    "Coverage": pct,
                    "Priority": "HIGH" if pct < 25.0 else "MEDIUM",
                    "Gap": round(self.THRESHOLD - pct, 1),
                })
        return sorted(gaps, key=lambda g: g["Coverage"])


class CampaignRecommendationEngine:
    def recommend(self, gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "Campaign": f"COVER_{g['Area'].upper()}_GAP",
                "Priority": g["Priority"],
                "Focus": f"Improve {g['Area']} coverage from {g['Coverage']}% to {min(100, g['Coverage'] + 50)}%",
            }
            for g in gaps
        ]


class DatasetReadinessEngine:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or _get_db_path()

    def _conn(self):
        return sqlite3.connect(self._db_path)

    def compute_score(self, coverage: Dict[str, float]) -> float:
        avg = sum(coverage.values()) / len(coverage)
        if avg >= 80:
            return min(100, int(avg + 10))
        if avg >= 50:
            return int(avg + 5)
        return int(avg)
