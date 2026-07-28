from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional
import json
import sqlite3
from pathlib import Path
from gli_flow.database.migrations import _get_db_path

EXPECTED_FAILURE_TYPES = {
    "Timing", "Routing", "CTS", "DRC", "LVS",
    "Power", "IR Drop", "Antenna", "Extraction", "Tool Failures",
}
EXPECTED_ROOT_CAUSES = {
    "Placement", "CTS", "Routing", "Signoff", "Constraints",
    "Tool Config", "PDK", "Extraction", "Floorplan",
    "Clock Skew", "IR Drop", "Cell Density", "Macro Congestion",
}
EXPECTED_STAGES = {"placement", "cts", "routing", "signoff", "lvs", "extraction"}
EXPECTED_DESIGNS = {
    "counter", "gcd", "uart", "gpio", "fir", "picorv32",
    "ibex", "serv", "opentitan_ibex", "tinyml_accel",
    "sram_controller", "aes_cipher",
}


@dataclass
class FailureCoverageMatrix:
    failure_types: Dict[str, Set[str]] = field(default_factory=lambda: {ft: set() for ft in EXPECTED_FAILURE_TYPES})
    tools: Set[str] = field(default_factory=set)
    stages: Set[str] = field(default_factory=set)
    pdks: Set[str] = field(default_factory=set)
    designs: Set[str] = field(default_factory=set)

    def track_failure(self, failure_type: str, root_cause: str, tool: str, stage: str, pdk: str, design: str):
        if failure_type not in self.failure_types:
            self.failure_types[failure_type] = set()
        self.failure_types[failure_type].add(root_cause)
        self.tools.add(tool)
        self.stages.add(stage)
        self.pdks.add(pdk)
        self.designs.add(design)

    def load_from_db(self, db_path: Optional[str] = None, min_classification: str = "VERIFIED"):
        conn = sqlite3.connect(db_path or _get_db_path())
        classification_filter = {
            "VERIFIED": ("VERIFIED",),
            "HEURISTIC": ("VERIFIED", "HEURISTIC"),
            "UNVERIFIED": ("VERIFIED", "HEURISTIC", "UNVERIFIED"),
        }.get(min_classification, ("VERIFIED", "HEURISTIC"))
        placeholders = ",".join("?" for _ in classification_filter)
        rows = conn.execute(
            f"SELECT failure_type, domain, tool_name, tool_stage, pdk_name, design_name "
            f"FROM failure_atlas_entries "
            f"WHERE detection_classification IN ({placeholders})",
            classification_filter,
        ).fetchall()
        conn.close()
        for ft, domain, tool, stage, pdk, design in rows:
            root_cause = domain or "UNKNOWN"
            self.track_failure(
                ft or "UNKNOWN",
                root_cause,
                tool or "openroad",
                stage or "unknown",
                pdk or "sky130A",
                design or "unknown",
            )

    def get_coverage_gaps(self) -> Dict[str, Any]:
        gaps = {}

        missing_types = EXPECTED_FAILURE_TYPES - set(self.failure_types.keys())
        if missing_types:
            gaps["missing_failure_types"] = sorted(missing_types)

        missing_stages = EXPECTED_STAGES - self.stages
        if missing_stages:
            gaps["missing_stages"] = sorted(missing_stages)

        missing_designs = EXPECTED_DESIGNS - self.designs
        if missing_designs:
            gaps["missing_designs"] = sorted(missing_designs)

        low_coverage_types = {
            ft: len(rcs)
            for ft, rcs in self.failure_types.items()
            if len(rcs) < 2 and ft in self.failure_types
        }
        if low_coverage_types:
            gaps["low_coverage_types"] = low_coverage_types

        gaps["summary"] = {
            "failure_types_covered": len(self.failure_types),
            "expected_failure_types": len(EXPECTED_FAILURE_TYPES),
            "failure_type_coverage_pct": round(
                len(self.failure_types) / len(EXPECTED_FAILURE_TYPES) * 100, 1
            ),
            "designs_covered": len(self.designs),
            "expected_designs": len(EXPECTED_DESIGNS),
            "design_coverage_pct": round(
                len(self.designs) / len(EXPECTED_DESIGNS) * 100, 1
            ),
            "stages_covered": len(self.stages),
            "expected_stages": len(EXPECTED_STAGES),
            "stage_coverage_pct": round(
                len(self.stages) / len(EXPECTED_STAGES) * 100, 1
            ),
            "total_root_causes_tracked": sum(len(rc) for rc in self.failure_types.values()),
        }

        return gaps

    def generate_json(self, output_path: Path):
        matrix_data = {
            "failure_types": {ft: sorted(list(rc)) for ft, rc in self.failure_types.items()},
            "tools": sorted(list(self.tools)),
            "stages": sorted(list(self.stages)),
            "pdks": sorted(list(self.pdks)),
            "designs": sorted(list(self.designs)),
            "coverage_gaps": self.get_coverage_gaps(),
        }
        with open(output_path, "w") as f:
            json.dump(matrix_data, f, indent=4)
