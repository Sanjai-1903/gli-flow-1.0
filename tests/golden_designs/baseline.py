"""
Golden Design Baseline definitions.

Each golden design has a known-good baseline for:
  QoR, runtime, DRC, LVS, timing

Used for regression detection in CI.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DesignBaseline:
    name: str
    rtl_files: list[str]
    top_module: str
    pdk: str = "sky130A"
    expected_qor_min: float = 0.0
    expected_wns_min: float = -10.0
    expected_tns_min: float = -100.0
    expected_util_max: float = 80.0
    expected_max_runtime_s: float = 3600.0
    expected_drc_clean: bool = True
    expected_lvs_clean: bool = True
    expected_setup_pass: bool = True
    expected_hold_pass: bool = True
    tags: list[str] = field(default_factory=list)


GOLDEN_DESIGNS: list[DesignBaseline] = []


def _register(d: DesignBaseline) -> DesignBaseline:
    GOLDEN_DESIGNS.append(d)
    return d


COUNTER = _register(DesignBaseline(
    name="counter",
    rtl_files=["counter.v"],
    top_module="counter",
    pdk="sky130A",
    expected_qor_min=0.5,
    expected_wns_min=0.0,
    expected_tns_min=0.0,
    expected_util_max=30.0,
    expected_max_runtime_s=300.0,
    expected_drc_clean=True,
    expected_lvs_clean=True,
    expected_setup_pass=True,
    expected_hold_pass=True,
    tags=["tiny", "combinatorial"],
))

UART = _register(DesignBaseline(
    name="uart",
    rtl_files=["uart_top.sv", "uart_rx.sv", "uart_tx.sv"],
    top_module="uart_top",
    pdk="sky130A",
    expected_qor_min=0.4,
    expected_wns_min=-1.0,
    expected_tns_min=-10.0,
    expected_util_max=50.0,
    expected_max_runtime_s=600.0,
    expected_drc_clean=True,
    expected_lvs_clean=True,
    expected_setup_pass=True,
    expected_hold_pass=True,
    tags=["medium", "sequential"],
))

GPIO = _register(DesignBaseline(
    name="gpio",
    rtl_files=["gpio.v"],
    top_module="gpio_top",
    pdk="sky130A",
    expected_qor_min=0.4,
    expected_wns_min=0.0,
    expected_tns_min=0.0,
    expected_util_max=40.0,
    expected_max_runtime_s=400.0,
    expected_drc_clean=True,
    expected_lvs_clean=True,
    expected_setup_pass=True,
    expected_hold_pass=True,
    tags=["medium", "io"],
))

FIR = _register(DesignBaseline(
    name="fir",
    rtl_files=["fir.v"],
    top_module="fir_top",
    pdk="sky130A",
    expected_qor_min=0.3,
    expected_wns_min=-2.0,
    expected_tns_min=-50.0,
    expected_util_max=60.0,
    expected_max_runtime_s=900.0,
    expected_drc_clean=True,
    expected_lvs_clean=True,
    expected_setup_pass=True,
    expected_hold_pass=True,
    tags=["medium", "dsp"],
))

PICORV32 = _register(DesignBaseline(
    name="picorv32",
    rtl_files=["picorv32.v"],
    top_module="picorv32",
    pdk="sky130A",
    expected_qor_min=0.1,
    expected_wns_min=-10.0,
    expected_tns_min=-200.0,
    expected_util_max=80.0,
    expected_max_runtime_s=3600.0,
    expected_drc_clean=True,
    expected_lvs_clean=True,
    expected_setup_pass=True,
    expected_hold_pass=True,
    tags=["large", "cpu"],
))


def get_design(name: str) -> Optional[DesignBaseline]:
    for d in GOLDEN_DESIGNS:
        if d.name == name:
            return d
    return None


def compare_baseline(
    design: DesignBaseline,
    actual_qor: float,
    actual_wns: float,
    actual_tns: float,
    actual_util: float,
    actual_runtime: float,
    drc_clean: bool,
    lvs_clean: bool,
) -> list[str]:
    alerts = []
    if actual_qor < design.expected_qor_min:
        alerts.append(f"QoR regression: {actual_qor} < {design.expected_qor_min}")
    if actual_wns < design.expected_wns_min:
        alerts.append(f"WNS regression: {actual_wns} < {design.expected_wns_min}")
    if actual_tns < design.expected_tns_min:
        alerts.append(f"TNS regression: {actual_tns} < {design.expected_tns_min}")
    if actual_util > design.expected_util_max:
        alerts.append(f"Utilization regression: {actual_util}% > {design.expected_util_max}%")
    if actual_runtime > design.expected_max_runtime_s:
        alerts.append(f"Runtime regression: {actual_runtime}s > {design.expected_max_runtime_s}s")
    if design.expected_drc_clean and not drc_clean:
        alerts.append("DRC regression: expected clean, got violations")
    if design.expected_lvs_clean and not lvs_clean:
        alerts.append("LVS regression: expected clean, got violations")
    return alerts
