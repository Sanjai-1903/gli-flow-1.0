from __future__ import annotations

import os
import re

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from gli_flow.pdk.corner import PVTCorner, DEFAULT_CORNERS


def resolve_env_vars(path: str) -> str:
    if not path:
        return path
    def _replace(m):
        var = m.group(1)
        return os.environ.get(var, m.group(0))
    return re.sub(r'\$\{?(\w+)\}?', _replace, path)


@dataclass
class PDK(ABC):
    name: str
    variant: str = ""
    description: str = ""
    version: str = ""
    vendor: str = ""

    orfs_platform: str = ""
    pdk_root_env: str = "PDK_ROOT"
    pdk_install_dir: str = ""
    volare_pdk_name: str = ""

    default_voltage: float = 1.8
    power_net_name: str = "VDD"
    ground_net_name: str = "VSS"
    nominal_voltage: float = 1.8

    track_height: int = 0
    metal_layers: list[str] = field(default_factory=list)
    via_layers: list[str] = field(default_factory=list)

    min_temperature: float = -40
    max_temperature: float = 125
    min_voltage: float = 1.62
    max_voltage: float = 1.98

    corners: list[PVTCorner] = field(default_factory=list)

    magic_tech_file: str = ""
    magic_rcfile: str = ""
    netgen_setup_file: str = ""
    fill_rules_file: str = ""
    liberty_file: str = ""

    def __post_init__(self):
        if not self.corners:
            self.corners = DEFAULT_CORNERS.get(self.name, [
                PVTCorner.worst(), PVTCorner.typical(), PVTCorner.best(),
            ])
        self.magic_tech_file = resolve_env_vars(self.magic_tech_file)
        self.magic_rcfile = resolve_env_vars(self.magic_rcfile)
        self.netgen_setup_file = resolve_env_vars(self.netgen_setup_file)
        self.fill_rules_file = resolve_env_vars(self.fill_rules_file)
        self.liberty_file = resolve_env_vars(self.liberty_file)

    @property
    def platform_dir(self) -> str:
        return self.orfs_platform

    def get_corner(self, name: str) -> Optional[PVTCorner]:
        for c in self.corners:
            if c.name == name:
                return c
        return None

    def worst_corner(self) -> PVTCorner:
        for c in self.corners:
            if c.is_worst:
                return c
        return self.corners[0] if self.corners else PVTCorner.worst()

    def typical_corner(self) -> PVTCorner:
        for c in self.corners:
            if c.is_typical:
                return c
        return self.corners[1] if len(self.corners) > 1 else PVTCorner.typical()

    def lib_dir(self, corner: PVTCorner) -> str:
        return f"{self.pdk_install_dir}/{self.variant}/libs.ref/lib/{self.lib_set(corner)}"

    def lef_dir(self) -> str:
        return f"{self.pdk_install_dir}/{self.variant}/libs.ref/lef"

    @abstractmethod
    def lib_set(self, corner: PVTCorner) -> str:
        ...

    @abstractmethod
    def generate_config_mk(self, design_name: str, corner: PVTCorner) -> str:
        ...

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "variant": self.variant,
            "description": self.description,
            "version": self.version,
            "vendor": self.vendor,
            "orfs_platform": self.orfs_platform,
            "metal_layers": self.metal_layers,
            "via_layers": self.via_layers,
            "corners": [c.to_dict() for c in self.corners],
        }
