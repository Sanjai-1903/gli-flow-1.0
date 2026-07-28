import json
import math
import sqlite3
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from gli_flow.database.migrations import _get_db_path

log = logging.getLogger(__name__)


@dataclass
class DesignFeatureRecord:
    design_name: str
    fanout_histogram: List[int] = field(default_factory=lambda: [0] * 10)
    logic_depth: int = 0
    register_density: float = 0.0
    memory_density: float = 0.0
    dsp_density: float = 0.0
    combinational_depth: int = 0
    sequential_depth: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "design_name": self.design_name,
            "fanout_histogram": json.dumps(self.fanout_histogram),
            "logic_depth": self.logic_depth,
            "register_density": self.register_density,
            "memory_density": self.memory_density,
            "dsp_density": self.dsp_density,
            "combinational_depth": self.combinational_depth,
            "sequential_depth": self.sequential_depth,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DesignFeatureRecord":
        fh = data.get("fanout_histogram", [0] * 10)
        if isinstance(fh, str):
            fh = json.loads(fh)
        return DesignFeatureRecord(
            design_name=data.get("design_name", ""),
            fanout_histogram=fh,
            logic_depth=data.get("logic_depth", 0) or 0,
            register_density=data.get("register_density", 0.0) or 0.0,
            memory_density=data.get("memory_density", 0.0) or 0.0,
            dsp_density=data.get("dsp_density", 0.0) or 0.0,
            combinational_depth=data.get("combinational_depth", 0) or 0,
            sequential_depth=data.get("sequential_depth", 0) or 0,
        )


class DesignFeatureExtractor:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or _get_db_path()
        self._init_tables()

    def _init_tables(self):
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS design_features (
                    design_name TEXT PRIMARY KEY,
                    fanout_histogram TEXT DEFAULT '[0,0,0,0,0,0,0,0,0,0]',
                    logic_depth INTEGER DEFAULT 0,
                    register_density REAL DEFAULT 0.0,
                    memory_density REAL DEFAULT 0.0,
                    dsp_density REAL DEFAULT 0.0,
                    combinational_depth INTEGER DEFAULT 0,
                    sequential_depth INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now'))
                )"""
            )

    def _conn(self):
        return sqlite3.connect(self._db_path)

    def _golden_tags(self, design_name: str) -> List[str]:
        from gli_flow.synthetic.golden_designs import GOLDEN_DESIGNS
        for d in GOLDEN_DESIGNS:
            if d.name == design_name:
                return d.tags
        return []

    def _compute_fanout_histogram(self, design_name: str, cell_count: int) -> List[int]:
        tags = self._golden_tags(design_name)
        is_cpu = "cpu" in tags
        is_dsp = "dsp" in tags
        is_ml = "ml" in tags
        is_combinatorial = "combinatorial" in tags
        is_sequential = "sequential" in tags
        is_memory = "memory" in tags
        is_crypto = "crypto" in tags

        scale = max(1, cell_count // 1000)
        if is_cpu:
            return [scale * 5, scale * 8, scale * 12, scale * 10, scale * 7, scale * 4, scale * 2, scale, 0, 0]
        elif is_dsp or is_ml:
            return [scale * 3, scale * 5, scale * 8, scale * 12, scale * 10, scale * 6, scale * 3, scale, scale, 0]
        elif is_combinatorial:
            return [scale * 8, scale * 10, scale * 8, scale * 5, scale * 3, scale, scale, 0, 0, 0]
        elif is_sequential:
            return [scale * 2, scale * 4, scale * 8, scale * 12, scale * 10, scale * 6, scale * 3, scale, scale, scale]
        elif is_memory:
            return [scale * 6, scale * 8, scale * 6, scale * 4, scale * 3, scale * 2, scale, 0, 0, 0]
        elif is_crypto:
            return [scale * 4, scale * 6, scale * 10, scale * 10, scale * 8, scale * 4, scale * 2, scale, 0, 0]
        else:
            return [scale * 4, scale * 6, scale * 8, scale * 8, scale * 6, scale * 4, scale * 2, scale, 0, 0]

    def _compute_register_density(self, design_name: str, cell_count: int) -> float:
        tags = self._golden_tags(design_name)
        if "cpu" in tags:
            return 0.35
        elif "dsp" in tags or "ml" in tags:
            return 0.25
        elif "combinatorial" in tags:
            return 0.08
        elif "sequential" in tags:
            return 0.45
        elif "memory" in tags:
            return 0.10
        elif "crypto" in tags:
            return 0.30
        return 0.20

    def _compute_memory_density(self, design_name: str) -> float:
        tags = self._golden_tags(design_name)
        has_sram = "sram" in tags
        is_memory = "memory" in tags
        if is_memory:
            return 0.50
        elif has_sram:
            return 0.20
        return 0.02

    def _compute_dsp_density(self, design_name: str) -> float:
        tags = self._golden_tags(design_name)
        if "dsp" in tags:
            return 0.15
        elif "ml" in tags:
            return 0.25
        return 0.01

    def _compute_logic_depth(self, design_name: str, cell_count: int) -> int:
        tags = self._golden_tags(design_name)
        if "cpu" in tags:
            return max(5, int(math.log2(max(cell_count, 10)) * 3))
        elif "dsp" in tags or "ml" in tags:
            return max(10, int(math.log2(max(cell_count, 10)) * 5))
        elif "combinatorial" in tags:
            return max(3, int(math.log2(max(cell_count, 10)) * 2))
        elif "sequential" in tags:
            return max(4, int(math.log2(max(cell_count, 10)) * 2))
        elif "memory" in tags:
            return max(2, int(math.log2(max(cell_count, 10)) * 1))
        elif "crypto" in tags:
            return max(8, int(math.log2(max(cell_count, 10)) * 4))
        return max(3, int(math.log2(max(cell_count, 10)) * 2))

    def extract(self, design_name: str, cell_count: int = 0) -> DesignFeatureRecord:
        tags = self._golden_tags(design_name)
        has_sram = "sram" in tags
        is_memory = "memory" in tags

        hist = self._compute_fanout_histogram(design_name, cell_count)
        reg_den = self._compute_register_density(design_name, cell_count)
        mem_den = self._compute_memory_density(design_name)
        dsp_den = self._compute_dsp_density(design_name)
        logic_dep = self._compute_logic_depth(design_name, cell_count)
        comb_dep = max(1, logic_dep // 2)
        seq_dep = logic_dep - comb_dep

        record = DesignFeatureRecord(
            design_name=design_name,
            fanout_histogram=hist,
            logic_depth=logic_dep,
            register_density=reg_den,
            memory_density=mem_den,
            dsp_density=dsp_den,
            combinational_depth=comb_dep,
            sequential_depth=seq_dep,
        )
        return record

    def store(self, record: DesignFeatureRecord):
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO design_features
                   (design_name, fanout_histogram, logic_depth, register_density,
                    memory_density, dsp_density, combinational_depth, sequential_depth)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.design_name,
                    json.dumps(record.fanout_histogram),
                    record.logic_depth,
                    record.register_density,
                    record.memory_density,
                    record.dsp_density,
                    record.combinational_depth,
                    record.sequential_depth,
                ),
            )

    def get_features(self, design_name: str) -> Optional[DesignFeatureRecord]:
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM design_features WHERE design_name = ?", (design_name,)
            ).fetchone()
            if row:
                return DesignFeatureRecord.from_dict(dict(row))
        return None

    def extract_for_all_profiles(self) -> List[DesignFeatureRecord]:
        with self._conn() as conn:
            names = conn.execute(
                "SELECT design_name FROM design_profiles"
            ).fetchall()

        records = []
        for (name,) in names:
            profile_path = None
            with self._conn() as conn2:
                row = conn2.execute(
                    "SELECT expected_cell_count FROM design_profiles WHERE design_name = ?",
                    (name,),
                ).fetchone()
                cells = row[0] if row else 1000

            record = self.extract(name, cells)
            self.store(record)
            records.append(record)
            log.info("Features extracted: %s (depth=%d, reg=%.1f%%)", name, record.logic_depth, record.register_density * 100)
        return records
