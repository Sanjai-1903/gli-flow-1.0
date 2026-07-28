from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import random
import multiprocessing
import time

from gli_flow.synthetic.golden_designs import GoldenDesign
from gli_flow.synthetic.failure_injector import FailureInjector, InjectionConfig, InjectionType


@dataclass
class SyntheticRunResult:
    design_name: str
    injection_config: Optional[InjectionConfig] = None
    runtime_sec: float = 0.0
    memory_mb: float = 0.0
    status: str = "SUCCESS"
    root_cause: Optional[str] = None
    telemetry_summary: Dict[str, Any] = field(default_factory=dict)
    resolution_candidate: Optional[str] = None
    run_seed: Optional[int] = None
    qor: Optional[float] = None
    fingerprint: Optional[str] = None


@dataclass
class CampaignResult:
    campaign_id: str
    design_name: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    results: List[SyntheticRunResult] = field(default_factory=list)
    average_runtime: float = 0.0
    average_memory: float = 0.0
    success_rate: float = 0.0
    dataset_yield: int = 0


INJECTION_FAILURE_MAP: Dict[InjectionType, Dict[str, Any]] = {
    InjectionType.CLOCK_PERIOD_SWEEP: {
        "failure_type": "Timing",
        "root_cause": "Clock period too aggressive",
        "resolution": "Relax clock period",
    },
    InjectionType.UTILIZATION_SWEEP: {
        "failure_type": "Congestion",
        "root_cause": "High utilization causing routing congestion",
        "resolution": "Reduce utilization or add more routing layers",
    },
    InjectionType.FLOORPLAN_SHRINK: {
        "failure_type": "Congestion",
        "root_cause": "Floorplan too small for cell area",
        "resolution": "Expand floorplan dimensions",
    },
    InjectionType.MACRO_CONGESTION: {
        "failure_type": "Congestion",
        "root_cause": "Macro placement causing routing blockage",
        "resolution": "Add halo around macros or spread macros",
    },
    InjectionType.PDN_STRESS: {
        "failure_type": "Power",
        "root_cause": "PDN insufficient for power draw",
        "resolution": "Widen power straps or add more VIA layers",
    },
    InjectionType.ROUTING_CONGESTION: {
        "failure_type": "Routing",
        "root_cause": "Routing congestion beyond capacity",
        "resolution": "Adjust floorplan aspect ratio or reduce cell density",
    },
    InjectionType.TIMING_CONSTRAINT_ERRORS: {
        "failure_type": "Timing",
        "root_cause": "Incorrect timing constraints",
        "resolution": "Fix timing constraints",
    },
    InjectionType.MISSING_CONSTRAINTS: {
        "failure_type": "Timing",
        "root_cause": "Missing timing constraints",
        "resolution": "Add missing constraints (create_clock, set_input_delay, etc.)",
    },
    InjectionType.DRC_VIOLATIONS: {
        "failure_type": "DRC",
        "root_cause": "DRC violations from cell overhang or spacing",
        "resolution": "Fix spacing/width violations or relax DRC rules",
    },
    InjectionType.LVS_MISMATCHES: {
        "failure_type": "LVS",
        "root_cause": "LVS net mismatch between schematic and layout",
        "resolution": "Check extracted netlist against reference",
    },
    InjectionType.TOOL_CONFIGURATION_ERRORS: {
        "failure_type": "Tool Failures",
        "root_cause": "Tool configuration error",
        "resolution": "Fix tool configuration file",
    },
    InjectionType.SKEW_INJECTION: {
        "failure_type": "CTS",
        "root_cause": "Clock skew outside limits",
        "resolution": "Rebalance clock tree or add skew groups",
    },
    InjectionType.UNCERTAINTY_CHANGES: {
        "failure_type": "Timing",
        "root_cause": "Timing uncertainty too high",
        "resolution": "Reduce clock uncertainty margin",
    },
    InjectionType.FALSE_PATH_ERRORS: {
        "failure_type": "Timing",
        "root_cause": "False path incorrectly specified",
        "resolution": "Correct false path constraints",
    },
    InjectionType.MULTICYCLE_ERRORS: {
        "failure_type": "Timing",
        "root_cause": "Multicycle path constraints missing",
        "resolution": "Add multicycle path constraints",
    },
    InjectionType.DENSITY_STRESS: {
        "failure_type": "Routing",
        "root_cause": "Cell density too high for routability",
        "resolution": "Reduce density or increase aspect ratio",
    },
    InjectionType.MACRO_CLUSTERING: {
        "failure_type": "Routing",
        "root_cause": "Macro clustering causing routing congestion",
        "resolution": "Distribute macros more evenly",
    },
    InjectionType.CHANNEL_COLLAPSE: {
        "failure_type": "Routing",
        "root_cause": "Routing channel collapsed due to blockage",
        "resolution": "Adjust macro placement to free channels",
    },
    InjectionType.PDN_STARVATION: {
        "failure_type": "Power",
        "root_cause": "PDN starvation in high-density region",
        "resolution": "Add local power grid connections",
    },
    InjectionType.IR_DROP_SCENARIOS: {
        "failure_type": "IR Drop",
        "root_cause": "Excessive IR drop in power grid",
        "resolution": "Widen power rails or add more VDD/VSS pairs",
    },
    InjectionType.EXCESSIVE_SWITCHING: {
        "failure_type": "Power",
        "root_cause": "Switching activity too high causing dynamic IR drop",
        "resolution": "Add decoupling capacitors or reduce toggle rate",
    },
    InjectionType.EXTRACTION_FAILURES: {
        "failure_type": "Extraction",
        "root_cause": "Parasitic extraction failure",
        "resolution": "Fix extraction configuration or reduce net count",
    },
    InjectionType.MISSING_DEVICES: {
        "failure_type": "LVS",
        "root_cause": "Missing devices in extracted netlist",
        "resolution": "Check extraction deck and device recognition",
    },
    InjectionType.NET_DISCONNECTS: {
        "failure_type": "LVS",
        "root_cause": "Net disconnects in extracted netlist",
        "resolution": "Check routing connections and via placement",
    },
    InjectionType.CORRUPTED_CONFIGS: {
        "failure_type": "Tool Failures",
        "root_cause": "Corrupted configuration file",
        "resolution": "Restore configuration from backup",
    },
    InjectionType.MISSING_FILES: {
        "failure_type": "Tool Failures",
        "root_cause": "Required input file missing",
        "resolution": "Restore missing file from source control",
    },
    InjectionType.VERSION_MISMATCHES: {
        "failure_type": "Tool Failures",
        "root_cause": "Tool version mismatch with PDK requirement",
        "resolution": "Align tool versions with PDK requirements",
    },
}


class CampaignRunner:
    def __init__(self, failure_injector: FailureInjector):
        self.failure_injector = failure_injector

    def _run_single_variation(
        self,
        design: GoldenDesign,
        injection_types: Optional[List[InjectionType]],
        base_seed: Optional[int],
        variation_index: int,
    ) -> SyntheticRunResult:
        run_seed = base_seed + variation_index if base_seed is not None else random.randint(0, 100000)
        random.seed(run_seed)

        injection_config: Optional[InjectionConfig] = None
        if injection_types:
            chosen_type = random.choice(injection_types)
            params = {"variation_id": variation_index, "severity": random.uniform(0.3, 0.9)}
            injection_config = InjectionConfig(
                injection_type=chosen_type,
                parameters=params,
                seed=run_seed,
                description=f"Var {variation_index} of {chosen_type.name}",
            )

        base = design.base_metrics
        if injection_config:
            injection_result = self.failure_injector.inject(design.name, injection_config)
        else:
            injection_result = {}

        wns = injection_result.get("setup_wns_ns", base.get("setup_wns_ns", 0))
        tns = injection_result.get("setup_tns_ns", base.get("setup_tns_ns", 0))
        drc_v = injection_result.get("drc_total_violations", base.get("drc_total_violations", 0))
        lvs_status = injection_result.get("lvs_status", base.get("lvs_status", "PASS"))

        if drc_v > 0 and drc_v != base.get("drc_total_violations", 0):
            status = "FAILURE"
            root_cause = f"DRC violations: {drc_v}"
            resolution = "Fix DRC spacing/width violations"
        elif lvs_status in ("FAIL", "FAILED", "ERROR"):
            status = "FAILURE"
            root_cause = "LVS mismatch detected"
            resolution = "Check netlist extraction"
        elif wns < -0.5 and wns != base.get("setup_wns_ns", 0):
            status = "FAILURE"
            root_cause = "Timing violation (WNS too negative)"
            resolution = "Optimize critical path or relax clock"
        elif injection_config and injection_config.injection_type in (
            InjectionType.MISSING_FILES,
            InjectionType.CORRUPTED_CONFIGS,
            InjectionType.VERSION_MISMATCHES,
        ):
            status = "FAILURE"
            info = INJECTION_FAILURE_MAP.get(injection_config.injection_type, {})
            root_cause = info.get("root_cause", "Tool failure")
            resolution = info.get("resolution", "Fix tool setup")
        else:
            noise = random.uniform(-0.02, 0.05)
            if wns + noise < -0.3:
                status = "FAILURE"
                root_cause = "Marginal timing failure"
                resolution = "Optimize timing"
            else:
                status = "SUCCESS"
                root_cause = None
                resolution = None

        sim_runtime = base.get("runtime_sec", 100) * (1 + random.uniform(-0.1, 0.3) if status == "FAILURE" else random.uniform(-0.1, 0.1))
        sim_qor = design.expected_qor * (1 + random.uniform(-0.1, 0.01) if status == "FAILURE" else random.uniform(-0.02, 0.05))
        sim_memory = random.uniform(100.0, 500.0)

        return SyntheticRunResult(
            design_name=design.name,
            injection_config=injection_config,
            runtime_sec=sim_runtime,
            memory_mb=sim_memory,
            status=status,
            root_cause=root_cause,
            telemetry_summary={
                "wns": wns,
                "tns": tns,
                "utilization": base.get("utilization", 0),
                "drc_violations": drc_v,
                "lvs_status": lvs_status,
                "area": 1000 + random.randint(-100, 100),
                "power": 50 + random.randint(-5, 5),
            },
            resolution_candidate=resolution,
            run_seed=run_seed,
            qor=sim_qor,
            fingerprint=design.fingerprint,
        )

    def run_campaign(
        self,
        design: GoldenDesign,
        num_variations: int,
        injection_types: Optional[List[InjectionType]] = None,
        base_seed: Optional[int] = None,
        num_workers: int = 1,
    ) -> CampaignResult:
        campaign_id = f"{design.name}_campaign_{random.randint(1000, 9999)}"
        print(f"Campaign '{campaign_id}' for '{design.name}' ({num_variations} vars, {num_workers} workers)")

        result = CampaignResult(
            campaign_id=campaign_id,
            design_name=design.name,
            total_runs=num_variations,
            successful_runs=0,
            failed_runs=0,
        )

        all_results: List[SyntheticRunResult] = []
        if num_workers > 1:
            args = [(design, injection_types, base_seed, i) for i in range(num_variations)]
            with multiprocessing.Pool(num_workers) as pool:
                all_results = pool.starmap(self._run_single_variation, args)
        else:
            for i in range(num_variations):
                all_results.append(self._run_single_variation(design, injection_types, base_seed, i))

        total_runtime = 0.0
        total_memory = 0.0
        yielded = 0

        for r in all_results:
            result.results.append(r)
            total_runtime += r.runtime_sec
            total_memory += r.memory_mb
            if r.status == "SUCCESS":
                result.successful_runs += 1
            else:
                result.failed_runs += 1
                yielded += 1

        n = num_variations or 1
        result.average_runtime = total_runtime / n
        result.average_memory = total_memory / n
        result.success_rate = result.successful_runs / n
        result.dataset_yield = yielded

        print(f"  Done: {result.successful_runs}/{result.total_runs} OK, {result.failed_runs} FAIL, yield={yielded}")
        return result
