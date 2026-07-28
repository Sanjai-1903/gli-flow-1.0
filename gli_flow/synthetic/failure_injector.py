import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from gli_flow.synthetic.golden_designs import GoldenDesign, GOLDEN_DESIGNS


class InjectionType(Enum):
    CLOCK_PERIOD_SWEEP = auto()
    UTILIZATION_SWEEP = auto()
    FLOORPLAN_SHRINK = auto()
    MACRO_CONGESTION = auto()
    PDN_STRESS = auto()
    ROUTING_CONGESTION = auto()
    TIMING_CONSTRAINT_ERRORS = auto()
    MISSING_CONSTRAINTS = auto()
    DRC_VIOLATIONS = auto()
    LVS_MISMATCHES = auto()
    TOOL_CONFIGURATION_ERRORS = auto()
    SKEW_INJECTION = auto()
    UNCERTAINTY_CHANGES = auto()
    FALSE_PATH_ERRORS = auto()
    MULTICYCLE_ERRORS = auto()
    DENSITY_STRESS = auto()
    MACRO_CLUSTERING = auto()
    CHANNEL_COLLAPSE = auto()
    PDN_STARVATION = auto()
    IR_DROP_SCENARIOS = auto()
    EXCESSIVE_SWITCHING = auto()
    EXTRACTION_FAILURES = auto()
    MISSING_DEVICES = auto()
    NET_DISCONNECTS = auto()
    CORRUPTED_CONFIGS = auto()
    MISSING_FILES = auto()
    VERSION_MISMATCHES = auto()


INJECTION_TYPES = list(InjectionType)


@dataclass
class InjectionConfig:
    injection_type: InjectionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    seed: Optional[int] = None


class FailureInjector:
    def inject(self, design_name: str, config: InjectionConfig) -> Dict[str, Any]:
        design = self._find_design(design_name)
        if not design:
            return {"result": "design_not_found"}

        base = dict(design.base_metrics)
        severity = config.parameters.get("severity", 0.5)

        if config.injection_type == InjectionType.CLOCK_PERIOD_SWEEP:
            return self._apply_clock_period_sweep(base, severity, config)
        elif config.injection_type == InjectionType.UTILIZATION_SWEEP:
            return self._apply_utilization_sweep(base, severity, config)
        elif config.injection_type == InjectionType.FLOORPLAN_SHRINK:
            return self._apply_floorplan_shrink(base, severity, config)
        elif config.injection_type == InjectionType.MACRO_CONGESTION:
            return self._apply_macro_congestion(base, severity, config)
        elif config.injection_type == InjectionType.PDN_STRESS:
            return self._apply_pdn_stress(base, severity, config)
        elif config.injection_type == InjectionType.ROUTING_CONGESTION:
            return self._apply_routing_congestion(base, severity, config)
        elif config.injection_type == InjectionType.TIMING_CONSTRAINT_ERRORS:
            return self._apply_timing_constraint_errors(base, severity, config)
        elif config.injection_type == InjectionType.MISSING_CONSTRAINTS:
            return self._apply_missing_constraints(base, severity, config)
        elif config.injection_type == InjectionType.DRC_VIOLATIONS:
            return self._apply_drc_violations(base, severity, config)
        elif config.injection_type == InjectionType.LVS_MISMATCHES:
            return self._apply_lvs_mismatches(base, severity, config)
        elif config.injection_type == InjectionType.TOOL_CONFIGURATION_ERRORS:
            return self._apply_tool_configuration_errors(base, severity, config)
        elif config.injection_type == InjectionType.SKEW_INJECTION:
            return self._apply_skew_injection(base, severity, config)
        elif config.injection_type == InjectionType.UNCERTAINTY_CHANGES:
            return self._apply_uncertainty_changes(base, severity, config)
        elif config.injection_type == InjectionType.FALSE_PATH_ERRORS:
            return self._apply_false_path_errors(base, severity, config)
        elif config.injection_type == InjectionType.MULTICYCLE_ERRORS:
            return self._apply_multicycle_errors(base, severity, config)
        elif config.injection_type == InjectionType.DENSITY_STRESS:
            return self._apply_density_stress(base, severity, config)
        elif config.injection_type == InjectionType.MACRO_CLUSTERING:
            return self._apply_macro_clustering(base, severity, config)
        elif config.injection_type == InjectionType.CHANNEL_COLLAPSE:
            return self._apply_channel_collapse(base, severity, config)
        elif config.injection_type == InjectionType.PDN_STARVATION:
            return self._apply_pdn_starvation(base, severity, config)
        elif config.injection_type == InjectionType.IR_DROP_SCENARIOS:
            return self._apply_ir_drop_scenarios(base, severity, config)
        elif config.injection_type == InjectionType.EXCESSIVE_SWITCHING:
            return self._apply_excessive_switching(base, severity, config)
        elif config.injection_type == InjectionType.EXTRACTION_FAILURES:
            return self._apply_extraction_failures(base, severity, config)
        elif config.injection_type == InjectionType.MISSING_DEVICES:
            return self._apply_missing_devices(base, severity, config)
        elif config.injection_type == InjectionType.NET_DISCONNECTS:
            return self._apply_net_disconnects(base, severity, config)
        elif config.injection_type == InjectionType.CORRUPTED_CONFIGS:
            return self._apply_corrupted_configs(base, severity, config)
        elif config.injection_type == InjectionType.MISSING_FILES:
            return self._apply_missing_files(base, severity, config)
        elif config.injection_type == InjectionType.VERSION_MISMATCHES:
            return self._apply_version_mismatches(base, severity, config)
        else:
            raise ValueError(f"Unknown injection type: {config.injection_type}")

    def _find_design(self, name: str) -> Optional[GoldenDesign]:
        for d in GOLDEN_DESIGNS:
            if d.name == name:
                return d
        return None

    def _apply_clock_period_sweep(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        factor = 1.0 - severity * 0.4
        orig_wns = base.get("setup_wns_ns", 0)
        orig_tns = base.get("setup_tns_ns", 0)
        cell_count = base.get("cell_count", 100)
        new_wns = orig_wns * factor - severity * 0.1
        new_tns = orig_tns * factor - severity * 0.1 * (cell_count / 50)
        return {
            "setup_wns_ns": new_wns,
            "setup_tns_ns": new_tns,
            "hold_whs_ns": base.get("hold_whs_ns", 0),
            "hold_ths_ns": base.get("hold_ths_ns", 0),
            "drc_total_violations": base.get("drc_total_violations", 0),
            "drc_is_clean": base.get("drc_is_clean", True),
            "lvs_status": base.get("lvs_status", "PASS"),
            "lvs_return_code": base.get("lvs_return_code", 0),
            "result": "clock_period_sweep_applied",
        }

    def _apply_utilization_sweep(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        util_increase = severity * 0.3
        new_util = min(base.get("utilization", 50) * (1 + util_increase), 95)
        overflow_factor = severity * 0.15
        return {
            "utilization": new_util,
            "overflow_h": min(base.get("overflow_h", 0) + overflow_factor, 0.3),
            "overflow_v": min(base.get("overflow_v", 0) + overflow_factor, 0.3),
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.1 * (new_util / 50),
            "setup_tns_ns": base.get("setup_tns_ns", 0) - severity * 1.0 * (new_util / 50),
            "drc_total_violations": base.get("drc_total_violations", 0),
            "drc_is_clean": base.get("drc_is_clean", True),
            "lvs_status": base.get("lvs_status", "PASS"),
            "result": "utilization_sweep_applied",
        }

    def _apply_floorplan_shrink(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        density_factor = severity * 0.5
        new_util = min(base.get("utilization", 50) * (1 + density_factor), 95)
        overflow = min(density_factor * 0.2, 0.25)
        return {
            "utilization": new_util,
            "overflow_h": min(base.get("overflow_h", 0) + overflow, 0.25),
            "overflow_v": min(base.get("overflow_v", 0) + overflow, 0.25),
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.05,
            "drc_total_violations": int(severity * 5),
            "drc_is_clean": False,
            "result": "floorplan_shrink_applied",
        }

    def _apply_macro_congestion(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        congest = severity * 0.25
        return {
            "overflow_h": min(base.get("overflow_h", 0) + congest, 0.3),
            "overflow_v": min(base.get("overflow_v", 0) + congest, 0.3),
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.05,
            "setup_tns_ns": base.get("setup_tns_ns", 0) - severity * 0.5,
            "drc_total_violations": int(severity * 2),
            "result": "macro_congestion_applied",
        }

    def _apply_pdn_stress(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "power_ir_drop_pct": min(base.get("power_ir_drop_pct", 3) * (1 + severity * 2), 25),
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.1,
            "result": "pdn_stress_applied",
        }

    def _apply_routing_congestion(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        congest = severity * 0.2 + 0.05
        return {
            "overflow_h": min(base.get("overflow_h", 0) + congest, 0.35),
            "overflow_v": min(base.get("overflow_v", 0) + congest, 0.35),
            "drc_total_violations": int(severity * 3),
            "drc_is_clean": False if severity > 0.5 else base.get("drc_is_clean", True),
            "result": "routing_congestion_applied",
        }

    def _apply_timing_constraint_errors(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.3,
            "setup_tns_ns": base.get("setup_tns_ns", 0) - severity * 5.0,
            "hold_whs_ns": base.get("hold_whs_ns", 0) - severity * 0.1,
            "result": "timing_errors_injected",
        }

    def _apply_missing_constraints(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.5,
            "setup_tns_ns": base.get("setup_tns_ns", 0) - severity * 10.0,
            "result": "missing_constraints_injected",
        }

    def _apply_drc_violations(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        violations = max(1, int(severity * 20 + random.uniform(-2, 5)))
        return {
            "drc_total_violations": violations,
            "drc_is_clean": False,
            "result": "drc_violations_injected",
        }

    def _apply_lvs_mismatches(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "lvs_status": "FAIL",
            "lvs_return_code": 1,
            "result": "lvs_mismatches_injected",
        }

    def _apply_tool_configuration_errors(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "implementation_status": "FAILED",
            "result": "tool_config_errors_injected",
        }

    def _apply_skew_injection(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "clock_skew_ns": base.get("clock_skew_ns", 0.1) * (1 + severity * 5),
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.15,
            "setup_tns_ns": base.get("setup_tns_ns", 0) - severity * 2.0,
            "result": "skew_injected",
        }

    def _apply_uncertainty_changes(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.2,
            "setup_tns_ns": base.get("setup_tns_ns", 0) - severity * 3.0,
            "result": "uncertainty_changed",
        }

    def _apply_false_path_errors(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.25,
            "hold_whs_ns": base.get("hold_whs_ns", 0) - severity * 0.05,
            "result": "false_path_errors_injected",
        }

    def _apply_multicycle_errors(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.1,
            "hold_whs_ns": base.get("hold_whs_ns", 0) + severity * 0.1,
            "result": "multicycle_errors_injected",
        }

    def _apply_density_stress(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        new_util = min(base.get("utilization", 50) * (1 + severity * 0.3), 95)
        return {
            "utilization": new_util,
            "overflow_h": min(base.get("overflow_h", 0) + severity * 0.2, 0.3),
            "overflow_v": min(base.get("overflow_v", 0) + severity * 0.2, 0.3),
            "drc_total_violations": int(severity * 3),
            "result": "density_stress_applied",
        }

    def _apply_macro_clustering(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        congest = severity * 0.3
        return {
            "overflow_h": min(congest, 0.35),
            "overflow_v": min(congest, 0.35),
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.08,
            "result": "macro_clustering_applied",
        }

    def _apply_channel_collapse(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        congest = severity * 0.4
        return {
            "overflow_h": min(congest, 0.4),
            "overflow_v": min(congest, 0.4),
            "drc_total_violations": int(severity * 5),
            "result": "channel_collapse_applied",
        }

    def _apply_pdn_starvation(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "power_ir_drop_pct": min(base.get("power_ir_drop_pct", 3) * (1 + severity * 3), 30),
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.15,
            "result": "pdn_starvation_injected",
        }

    def _apply_ir_drop_scenarios(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "power_ir_drop_pct": min(base.get("power_ir_drop_pct", 3) * (1 + severity * 4), 35),
            "setup_wns_ns": base.get("setup_wns_ns", 0) - severity * 0.2,
            "result": "ir_drop_scenarios_injected",
        }

    def _apply_excessive_switching(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "power_ir_drop_pct": min(base.get("power_ir_drop_pct", 3) * (1 + severity * 2), 25),
            "result": "excessive_switching_injected",
        }

    def _apply_extraction_failures(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "lvs_status": "ERROR",
            "lvs_return_code": 2,
            "result": "extraction_failures_injected",
        }

    def _apply_missing_devices(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "lvs_status": "FAIL",
            "lvs_return_code": 1,
            "result": "missing_devices_injected",
        }

    def _apply_net_disconnects(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "lvs_status": "FAIL",
            "lvs_return_code": 1,
            "result": "net_disconnects_injected",
        }

    def _apply_corrupted_configs(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "implementation_status": "FAILED",
            "result": "corrupted_configs_injected",
        }

    def _apply_missing_files(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "implementation_status": "FAILED",
            "result": "missing_files_injected",
        }

    def _apply_version_mismatches(self, base: Dict, severity: float, config: InjectionConfig) -> Dict[str, Any]:
        return {
            "implementation_status": "FAILED",
            "result": "version_mismatches_injected",
        }
