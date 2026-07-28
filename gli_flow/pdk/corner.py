from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CornerType(Enum):
    WORST = "worst"
    TYPICAL = "typical"
    BEST = "best"
    CUSTOM = "custom"


class ProcessCorner(Enum):
    SLOW = "slow"
    TYPICAL = "typical"
    FAST = "fast"


@dataclass
class PVTCorner:
    name: str
    corner_type: CornerType = CornerType.CUSTOM
    process: ProcessCorner = ProcessCorner.TYPICAL
    voltage: float = 1.8
    temperature: float = 25.0
    voltage_unit: str = "V"
    temperature_unit: str = "C"

    @property
    def is_worst(self) -> bool:
        return self.corner_type == CornerType.WORST

    @property
    def is_typical(self) -> bool:
        return self.corner_type == CornerType.TYPICAL

    @property
    def is_best(self) -> bool:
        return self.corner_type == CornerType.BEST

    def lib_suffix(self) -> str:
        mapping = {
            CornerType.WORST: "ss",
            CornerType.TYPICAL: "tt",
            CornerType.BEST: "ff",
            CornerType.CUSTOM: self.name,
        }
        return mapping.get(self.corner_type, self.name)

    def orfs_corner_name(self) -> str:
        return f"{self.lib_suffix()}_{self.voltage}V_{self.temperature}C"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.corner_type.value,
            "process": self.process.value,
            "voltage": self.voltage,
            "temperature": self.temperature,
        }

    @classmethod
    def worst(cls) -> PVTCorner:
        return cls(
            name="worst",
            corner_type=CornerType.WORST,
            process=ProcessCorner.SLOW,
            voltage=1.62,
            temperature=125,
        )

    @classmethod
    def typical(cls) -> PVTCorner:
        return cls(
            name="typical",
            corner_type=CornerType.TYPICAL,
            process=ProcessCorner.TYPICAL,
            voltage=1.80,
            temperature=25,
        )

    @classmethod
    def best(cls) -> PVTCorner:
        return cls(
            name="best",
            corner_type=CornerType.BEST,
            process=ProcessCorner.FAST,
            voltage=1.98,
            temperature=-40,
        )

    @classmethod
    def from_dict(cls, d: dict) -> PVTCorner:
        corner_type = CornerType(d.get("type", "custom"))
        process = ProcessCorner(d.get("process", "typical"))
        return cls(
            name=d.get("name", "custom"),
            corner_type=corner_type,
            process=process,
            voltage=d.get("voltage", 1.8),
            temperature=d.get("temperature", 25),
        )


DEFAULT_CORNERS = {
    "sky130": [PVTCorner.worst(), PVTCorner.typical(), PVTCorner.best()],
    "gf180mcu": [PVTCorner.worst(), PVTCorner.typical(), PVTCorner.best()],
}
