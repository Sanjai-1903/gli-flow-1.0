import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from gli_flow.database.migrations import _get_db_path

log = logging.getLogger(__name__)

ALL_FAILURE_CATEGORIES = [
    "Timing",
    "Routing",
    "CTS",
    "DRC",
    "LVS",
    "Power",
    "IR Drop",
    "Antenna",
    "Extraction",
    "Tool Failures",
]

ALL_DESIGNS = [
    "counter",
    "gcd",
    "uart",
    "gpio",
    "fir",
    "picorv32",
    "ibex",
    "serv",
    "opentitan_ibex",
    "tinyml_accel",
    "sram_controller",
    "aes_cipher",
]


class SyntheticCampaignPlanner:
    def __init__(self, db_path: Optional[str] = None, include_heuristic: bool = False, include_unverified: bool = False):
        self._db_path = db_path or _get_db_path()
        self.classifications = ["VERIFIED"]
        if include_heuristic:
            self.classifications.append("HEURISTIC")
        if include_unverified:
            self.classifications.append("UNVERIFIED")
        self.placeholders = ",".join("?" for _ in self.classifications)

    def _conn(self):
        return sqlite3.connect(self._db_path)

    def _coverage_by_failure_type(self) -> Dict[str, int]:
        with self._conn() as conn:
            rows = conn.execute(
                f"SELECT failure_type, COUNT(*) AS cnt FROM failure_atlas_entries WHERE detection_classification IN ({self.placeholders}) GROUP BY failure_type ORDER BY cnt DESC",
                self.classifications
            ).fetchall()
            return {r[0]: r[1] for r in rows}

    def _coverage_by_design(self) -> Dict[str, int]:
        with self._conn() as conn:
            rows = conn.execute(
                f"SELECT design_name, COUNT(*) AS cnt FROM failure_atlas_entries WHERE design_name IS NOT NULL AND design_name != '' AND detection_classification IN ({self.placeholders}) GROUP BY design_name ORDER BY cnt DESC",
                self.classifications
            ).fetchall()
            return {r[0]: r[1] for r in rows}

    def _coverage_by_domain(self) -> Dict[str, int]:
        with self._conn() as conn:
            rows = conn.execute(
                f"SELECT domain, COUNT(*) AS cnt FROM failure_atlas_entries WHERE domain IS NOT NULL AND domain != '' AND detection_classification IN ({self.placeholders}) GROUP BY domain ORDER BY cnt DESC",
                self.classifications
            ).fetchall()
            return {r[0]: r[1] for r in rows}

    def detect_gaps(self) -> Dict[str, Any]:
        fc = self._coverage_by_failure_type()
        dc = self._coverage_by_design()

        missing_categories = [c for c in ALL_FAILURE_CATEGORIES if c not in fc]
        low_coverage_categories = [
            {"category": c, "count": fc[c]}
            for c in ALL_FAILURE_CATEGORIES
            if c in fc and fc[c] < 3
        ]

        missing_designs = [d for d in ALL_DESIGNS if d not in dc]
        low_coverage_designs = [
            {"design": d, "count": dc[d]}
            for d in ALL_DESIGNS
            if d in dc and dc[d] < 5
        ]

        return {
            "missing_categories": missing_categories,
            "low_coverage_categories": low_coverage_categories,
            "missing_designs": missing_designs,
            "low_coverage_designs": low_coverage_designs,
            "covered_categories": [c for c in ALL_FAILURE_CATEGORIES if c in fc],
            "covered_designs": [d for d in ALL_DESIGNS if d in dc],
            "category_coverage_percent": round(
                len([c for c in ALL_FAILURE_CATEGORIES if c in fc])
                / len(ALL_FAILURE_CATEGORIES)
                * 100,
                1,
            ),
            "design_coverage_percent": round(
                len([d for d in ALL_DESIGNS if d in dc])
                / len(ALL_DESIGNS)
                * 100,
                1,
            ),
        }

    def recommend_campaigns(self, gap_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        campaigns = []

        for cat in gap_analysis.get("missing_categories", []):
            campaigns.append(
                {
                    "campaign_name": f"COVER_{cat.upper().replace(' ', '_')}",
                    "focus": f"Generate {cat} failure signatures",
                    "category": cat,
                    "priority": "HIGH" if cat in ("Timing", "DRC", "LVS") else "MEDIUM",
                    "rationale": f"No entries exist for {cat} failure type",
                    "suggested_designs": self._suggest_designs_for_category(cat),
                    "estimated_runs": 25,
                }
            )

        for cat_entry in gap_analysis.get("low_coverage_categories", []):
            cat = cat_entry["category"]
            campaigns.append(
                {
                    "campaign_name": f"EXPAND_{cat.upper().replace(' ', '_')}",
                    "focus": f"Expand {cat} coverage ({cat_entry['count']} current)",
                    "category": cat,
                    "priority": "MEDIUM",
                    "rationale": f"Only {cat_entry['count']} entries for {cat}",
                    "suggested_designs": self._suggest_designs_for_category(cat),
                    "estimated_runs": 15,
                }
            )

        for design in gap_analysis.get("missing_designs", []):
            campaigns.append(
                {
                    "campaign_name": f"DESIGN_{design.upper()}",
                    "focus": f"Generate entries for {design} design",
                    "category": "ALL",
                    "priority": "HIGH",
                    "rationale": f"No entries exist for {design} design",
                    "suggested_designs": [design],
                    "estimated_runs": 30,
                }
            )

        for de in gap_analysis.get("low_coverage_designs", []):
            design = de["design"]
            campaigns.append(
                {
                    "campaign_name": f"BOOST_{design.upper()}",
                    "focus": f"Add more entries for {design} ({de['count']} current)",
                    "category": "ALL",
                    "priority": "LOW",
                    "rationale": f"Only {de['count']} entries for {design}",
                    "suggested_designs": [design],
                    "estimated_runs": 10,
                }
            )

        return sorted(campaigns, key=lambda c: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[c["priority"]])

    def _suggest_designs_for_category(self, category: str) -> List[str]:
        mapping = {
            "Timing": ["fir", "picorv32", "ibex"],
            "Routing": ["uart", "gpio", "counter"],
            "CTS": ["fir", "picorv32", "ibex"],
            "DRC": ["counter", "gcd", "sram_controller"],
            "LVS": ["gcd", "uart", "aes_cipher"],
            "Power": ["ibex", "tinyml_accel", "picorv32"],
            "IR Drop": ["ibex", "picorv32", "tinyml_accel"],
            "Antenna": ["counter", "gcd", "sram_controller"],
            "Extraction": ["aes_cipher", "tinyml_accel", "serv"],
            "Tool Failures": ["serv", "opentitan_ibex", "sram_controller"],
        }
        return mapping.get(category, ALL_DESIGNS[:3])

    def plan(self) -> Dict[str, Any]:
        gaps = self.detect_gaps()
        campaigns = self.recommend_campaigns(gaps)
        total_estimated_runs = sum(c.get("estimated_runs", 0) for c in campaigns)

        return {
            "gaps": gaps,
            "recommended_campaigns": campaigns,
            "total_campaigns": len(campaigns),
            "total_estimated_runs": total_estimated_runs,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def generate_seed_plan(self) -> Dict[str, Any]:
        plan = self.plan()
        seed_runs = []
        for c in plan.get("recommended_campaigns", []):
            for design in c.get("suggested_designs", []):
                seed_runs.append(
                    {
                        "design": design,
                        "category": c["category"],
                        "campaign": c["campaign_name"],
                        "priority": c["priority"],
                        "runs": max(1, c["estimated_runs"] // max(len(c.get("suggested_designs", [])), 1)),
                    }
                )
        plan["seed_execution_plan"] = seed_runs
        plan["total_seed_runs"] = sum(s["runs"] for s in seed_runs)
        return plan
