import json
import sqlite3
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from gli_flow.database.migrations import _get_db_path
from gli_flow.synthetic.golden_designs import GOLDEN_DESIGNS

log = logging.getLogger(__name__)

DESIGN_TYPE_MAP = {d.name: d.design_type for d in GOLDEN_DESIGNS}
DESIGN_TAGS = {d.name: d.tags for d in GOLDEN_DESIGNS}
DESIGN_CLOCK = {d.name: d.clock_period_ns for d in GOLDEN_DESIGNS}
DESIGN_CELLS = {d.name: d.expected_cell_count for d in GOLDEN_DESIGNS}
DESIGN_QOR = {d.name: d.expected_qor for d in GOLDEN_DESIGNS}
DESIGN_WNS = {d.name: d.expected_wns for d in GOLDEN_DESIGNS}


@dataclass
class DesignProfile:
    design_name: str
    design_type: str = "unknown"
    rtl_size: int = 0
    module_count: int = 0
    memory_ratio: float = 0.0
    control_ratio: float = 0.0
    compute_ratio: float = 0.0
    top_module: str = ""
    pdk: str = "sky130A"
    clock_period_ns: float = 0.0
    expected_cell_count: int = 0

    def to_row(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_row(row: Dict[str, Any]) -> "DesignProfile":
        return DesignProfile(
            design_name=row.get("design_name", ""),
            design_type=row.get("design_type", "unknown"),
            rtl_size=row.get("rtl_size", 0) or 0,
            module_count=row.get("module_count", 0) or 0,
            memory_ratio=row.get("memory_ratio", 0.0) or 0.0,
            control_ratio=row.get("control_ratio", 0.0) or 0.0,
            compute_ratio=row.get("compute_ratio", 0.0) or 0.0,
            top_module=row.get("top_module", ""),
            pdk=row.get("pdk", "sky130A"),
            clock_period_ns=row.get("clock_period_ns", 0.0) or 0.0,
            expected_cell_count=row.get("expected_cell_count", 0) or 0,
        )


class DesignProfileEngine:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or _get_db_path()
        self._init_tables()

    def _init_tables(self):
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS design_profiles (
                    design_name TEXT PRIMARY KEY,
                    design_type TEXT DEFAULT 'unknown',
                    rtl_size INTEGER DEFAULT 0,
                    module_count INTEGER DEFAULT 0,
                    memory_ratio REAL DEFAULT 0.0,
                    control_ratio REAL DEFAULT 0.0,
                    compute_ratio REAL DEFAULT 0.0,
                    top_module TEXT DEFAULT '',
                    pdk TEXT DEFAULT 'sky130A',
                    clock_period_ns REAL DEFAULT 0.0,
                    expected_cell_count INTEGER DEFAULT 0,
                    classification TEXT DEFAULT '',
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now'))
                )"""
            )

    def _conn(self):
        return sqlite3.connect(self._db_path)

    def infer_design_name(self, run_id: str) -> Optional[str]:
        known = {
            "counter": "counter", "gcd": "gcd", "uart": "uart",
            "fir": "fir", "picorv32": "picorv32", "ibex": "ibex",
            "serv": "serv", "tinyml": "tinyml_accel",
            "sram": "sram_controller", "aes": "aes_cipher",
            "gpio": "gpio", "mini_mac": "mac",
            "systolic": "systolic_array",
        }
        rid_lower = run_id.lower()
        for key, name in known.items():
            if key in rid_lower:
                return name
        return None

    def build_profile_from_golden(self, design_name: str) -> Optional[DesignProfile]:
        design_type = DESIGN_TYPE_MAP.get(design_name, "unknown")
        tags = DESIGN_TAGS.get(design_name, [])
        clock = DESIGN_CLOCK.get(design_name, 0.0)
        cells = DESIGN_CELLS.get(design_name, 0)
        qor = DESIGN_QOR.get(design_name, 0.0)

        has_sram = "sram" in tags
        is_cpu = "cpu" in tags
        is_dsp = "dsp" in tags
        is_ml = "ml" in tags
        is_crypto = "crypto" in tags
        is_memory = "memory" in tags
        is_io = "io" in tags
        is_combinatorial = "combinatorial" in tags
        is_sequential = "sequential" in tags

        if cells == 0:
            return None

        memory_ratio = 0.15 if has_sram else 0.02
        if is_memory:
            memory_ratio = 0.45
        if is_dsp:
            memory_ratio = 0.05

        control_ratio = 0.25
        if is_cpu:
            control_ratio = 0.35
        elif is_combinatorial:
            control_ratio = 0.10
        elif is_dsp or is_ml:
            control_ratio = 0.15

        compute_ratio = max(0.0, 1.0 - memory_ratio - control_ratio)

        return DesignProfile(
            design_name=design_name,
            design_type=design_type,
            rtl_size=cells * 3,
            module_count=max(1, cells // 200),
            memory_ratio=round(memory_ratio, 4),
            control_ratio=round(control_ratio, 4),
            compute_ratio=round(compute_ratio, 4),
            top_module=design_name,
            pdk="sky130A",
            clock_period_ns=clock,
            expected_cell_count=cells,
        )

    def build_profile_from_runs(self, design_name: str) -> Optional[DesignProfile]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT cell_count, utilization, wns, tns, drc_violations, lvs_result, run_dir "
                "FROM runs WHERE design_name = ? AND cell_count IS NOT NULL ORDER BY timestamp DESC LIMIT 5",
                (design_name,),
            ).fetchall()
        if not rows:
            return None

        avg_cells = sum(r[0] for r in rows if r[0]) / max(len([r for r in rows if r[0]]), 1)
        avg_util = sum(r[1] for r in rows if r[1]) / max(len([r for r in rows if r[1]]), 1) if any(r[1] for r in rows) else 0

        return DesignProfile(
            design_name=design_name,
            design_type="medium" if avg_cells > 5000 else "large" if avg_cells > 500 else "tiny",
            rtl_size=int(avg_cells * 3),
            module_count=max(1, int(avg_cells / 200)),
            memory_ratio=0.1,
            control_ratio=0.3,
            compute_ratio=0.6,
            expected_cell_count=int(avg_cells),
        )

    def store_profile(self, profile: DesignProfile):
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO design_profiles
                   (design_name, design_type, rtl_size, module_count,
                    memory_ratio, control_ratio, compute_ratio,
                    top_module, pdk, clock_period_ns, expected_cell_count)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    profile.design_name,
                    profile.design_type,
                    profile.rtl_size,
                    profile.module_count,
                    profile.memory_ratio,
                    profile.control_ratio,
                    profile.compute_ratio,
                    profile.top_module,
                    profile.pdk,
                    profile.clock_period_ns,
                    profile.expected_cell_count,
                ),
            )

    def get_profile(self, design_name: str) -> Optional[DesignProfile]:
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM design_profiles WHERE design_name = ?", (design_name,)
            ).fetchone()
            if row:
                return DesignProfile.from_row(dict(row))
        return None

    def list_profiles(self) -> List[DesignProfile]:
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM design_profiles ORDER BY design_name"
            ).fetchall()
            return [DesignProfile.from_row(dict(r)) for r in rows]

    def discover_design_names(self, include_heuristic: bool = False, include_unverified: bool = False) -> List[str]:
        names = set()
        classifications = ["VERIFIED"]
        if include_heuristic:
            classifications.append("HEURISTIC")
        if include_unverified:
            classifications.append("UNVERIFIED")
        placeholders = ",".join("?" for _ in classifications)

        with self._conn() as conn:
            for row in conn.execute("SELECT DISTINCT design_name FROM runs WHERE design_name IS NOT NULL AND design_name != ''").fetchall():
                names.add(row[0])
            for row in conn.execute(
                f"SELECT run_id FROM failure_atlas_entries WHERE detection_classification IN ({placeholders})",
                classifications
            ).fetchall():
                rid = row[0]
                inferred = self.infer_design_name(rid)
                if inferred:
                    names.add(inferred)
        return sorted(names)

    def generate_all_profiles(self) -> List[DesignProfile]:
        names = self.discover_design_names()
        for name in GOLDEN_DESIGNS:
            names.append(name.name)
        names = sorted(set(names))

        profiles = []
        for name in names:
            profile = self.build_profile_from_golden(name) or self.build_profile_from_runs(name)
            if profile:
                self.store_profile(profile)
                profiles.append(profile)
                log.info("Profile built: %s -> %s (%d cells)", name, profile.design_type, profile.expected_cell_count)
        return profiles
