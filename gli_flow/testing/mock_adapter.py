import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from gli_flow.testing.layout_images import generate_placeholder_images

from gli_flow.backends.openroad_adapter import (
    DRCViolation, DRCResult, LVSResult,
    EMViolation, EMCheckResult, DecapResult,
    ScanChain, ScanResult, ATPGPattern, ATPGResult,
    ClockGatingResult, PROResult,
    CrosstalkViolation, SIResult, YieldResult,
    AntennaViolation, AntennaResult, DensityResult,
    FormalResult, TimingSignoffResult, PowerResult,
    HierarchicalBlock, HierarchicalPartitionResult,
    BlockSynthesisResult, PlacedBlock, TopFloorplanResult,
    D2DInterfaceViolation, D2DInterfaceResult,
)


logger = logging.getLogger(__name__)


class MockEDAAdapter:

    def __init__(self, pdk_root=None, pdk=None, orfs_root=None):
        self.pdk_root = pdk_root or os.environ.get("PDK_ROOT", "/mock/pdk")
        self.pdk = pdk

    def set_pdk(self, pdk) -> None:
        self.pdk = pdk

    @property
    def platform(self) -> str:
        return "mock"

    def validate_environment(self):
        return []

    def generate_config(self, manifest, run_dir, corner=None):
        design_name = manifest.get("design_name", "unnamed")
        design_info = {
            "design_name": design_name,
            "pdk": "mock",
            "platform": "mock",
            "config_mk": str(Path(run_dir) / "config.mk"),
            "design_dir": str(Path(run_dir) / "design"),
            "src_dir": str(Path(run_dir) / "src"),
            "orfs_results_dir": str(Path(run_dir) / "results"),
            "orfs_reports_dir": str(Path(run_dir) / "reports"),
        }
        run_config_path = Path(run_dir) / "config.json"
        run_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(run_config_path, "w") as f:
            json.dump({**manifest, "orfs": design_info}, f, indent=2)
        return {"success": True, "config_path": str(run_config_path), "orfs_info": design_info}

    def _ensure_dirs(self, run_dir):
        Path(run_dir, "reports").mkdir(parents=True, exist_ok=True)
        Path(run_dir, "logs").mkdir(parents=True, exist_ok=True)
        Path(run_dir, "artifacts").mkdir(parents=True, exist_ok=True)
        Path(run_dir, "results").mkdir(parents=True, exist_ok=True)

    def _write_report(self, run_dir, filename, content):
        (Path(run_dir) / "reports" / filename).write_text(content)

    def run_packaging(self, run_dir, design_name, pdk, **kwargs):
        config_path = Path(run_dir) / "config.json"
        return self.run(str(config_path), run_dir, run_dir, **kwargs)

    def run(self, config_path, design_dir, run_dir, timeout=3600, **kwargs):
        self._ensure_dirs(run_dir)
        reports_dir = Path(run_dir) / "reports"
        logs_dir = Path(run_dir) / "logs"
        artifacts_dir = Path(run_dir) / "artifacts"
        results_dir = Path(run_dir) / "results"

        reports_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        results_dir.mkdir(parents=True, exist_ok=True)

        (reports_dir / "metrics.csv").write_text(
            "wns,0.05\ntns,0.00\nutilization,65.0\ncell_count,100\nruntime_sec,42.0\n"
        )
        (reports_dir / "timing.rpt").write_text("wns: 0.05\ntns: 0.00\n")
        (reports_dir / "utilization.rpt").write_text("Core Utilization: 65.0%\nTotal Cells: 100\n")
        (reports_dir / "runtime.rpt").write_text("Total Runtime: 42.0 sec\n")
        (reports_dir / "6_finish.rpt").write_text(
            "wns max 0.05\ntns max 0.00\nclk period_min = 10.00\n"
            "Total Power 0.001\nsetup violation count 0\nhold violation count 0\n"
        )

        (results_dir / "6_final.gds").write_text("fake_gds_data")
        (results_dir / "6_final.def").write_text(
            "UNITS DISTANCE MICRONS 1000\nDIEAREA ( 0 0 ) ( 10000 10000 );\n"
        )
        (results_dir / "1_synth.v").write_text("// mock netlist\n")
        (results_dir / "6_final.sdc").write_text("create_clock -period 10 [get_ports clk]\n")

        (artifacts_dir / "6_final.gds").write_text("fake_gds_data")
        (artifacts_dir / "6_final.def").write_text(
            "UNITS DISTANCE MICRONS 1000\nDIEAREA ( 0 0 ) ( 10000 10000 );\n"
        )
        (artifacts_dir / "1_synth.v").write_text("// mock netlist\n")
        (artifacts_dir / "6_final.sdc").write_text("create_clock -period 10 [get_ports clk]\n")

        generate_placeholder_images(str(reports_dir))

        return {
            "success": True, "returncode": 0,
            "stdout": "Mock run completed", "stderr": "",
            "duration": 42.0,
            "log_file": str(logs_dir / "mock.log"),
            "reports_dir": str(reports_dir),
            "output_dir": str(run_dir),
        }

    def run_corner(self, config_path, design_dir, run_dir, corner, timeout=3600):
        self._ensure_dirs(run_dir)
        return {
            "success": True, "wns": 0.05, "tns": 0.0, "duration": 10.0,
        }

    def run_hierarchical_partitioning(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "partition_log.txt").write_text(
            "Partition: top instances 100\n"
        )
        return HierarchicalPartitionResult(
            total_blocks=1,
            blocks=[HierarchicalBlock(name="top", instance_count=100)],
            runtime_seconds=0.5,
        )

    def run_block_synthesis(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "block_synth_log.txt").write_text(
            "Number of blocks: 1\nNumber of cells: 100\nChip area for top module: 5000.0\n"
        )
        return BlockSynthesisResult(
            total_blocks=1, total_cells=100, total_area_um2=5000.0, estimated_power_mw=0.5,
            runtime_seconds=1.0,
        )

    def run_clock_gating(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "clock_gating_log.txt").write_text(
            "Total registers: 50\nGated registers: 25\nClock gate cells: 5\n"
        )
        return ClockGatingResult(
            total_registers=50, gated_registers=25, power_savings_pct=50.0, clock_gates_inserted=5,
            runtime_seconds=0.3,
        )

    def run_scan_insertion(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "scan_log.txt").write_text(
            "Scan chain: chain_0 length 20 flops 20\nScan coverage: 100.0%\n"
        )
        return ScanResult(
            total_flops=20, scanned_flops=20,
            chains=[ScanChain(chain_id=0, num_flops=20, scan_in_port="SI", scan_out_port="SO", chain_length=20)],
            scan_coverage_pct=100.0, test_clk_period_ns=100.0, was_inserted=True,
            runtime_seconds=0.5,
        )

    def run_formal(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "formal_log.txt").write_text(
            "Formal verification: EQUIVALENT\nCompare points: 100\n"
        )
        return FormalResult(
            total_compare_points=100, unmatched_points=0, failures=0, is_equivalent=True,
            runtime_seconds=2.0,
        )

    def run_pro(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "pro_log.txt").write_text(
            "Inserted 10 buffers\nSlack improvement: 0.12\n"
            "Setup violations fixed: 2\nHold violations fixed: 0\n"
        )
        return PROResult(
            buffer_count=10, slack_improvement_ns=0.12, wire_length_change_pct=-0.5,
            setup_violations_fixed=2, hold_violations_fixed=0,
            runtime_seconds=1.0,
        )

    def run_antenna_check(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "antenna_report.txt").write_text(
            "Antenna violations: 0\n"
        )
        return AntennaResult(total_violations=0, violations=[], max_antenna_ratio=0.0, is_clean=True)

    def run_fill(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        gds_path = str(Path(run_dir) / "fill.gds")
        Path(gds_path).write_text("fake_fill_gds")
        return gds_path

    def run_decap(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "decap_log.txt").write_text(
            "Decap cells: 10\nDecap cap: 0.50 pF\n"
        )
        return DecapResult(
            total_decap_cells=10, decap_area_um2=50.0, decap_capacitance_pf=0.5,
            target_coverage_pct=20.0, actual_coverage_pct=18.0,
            runtime_seconds=0.5,
        )

    def run_power_analysis(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "power_report.txt").write_text(
            "Total Power: 0.50 mW\nIR Drop: 5.0 mV\n"
        )
        return PowerResult(
            total_power_mw=0.5, leakage_mw=0.01, internal_mw=0.3, switching_mw=0.19,
            max_ir_drop_mv=5.0, mean_ir_drop_mv=3.0, ir_violation_count=0,
        )

    def run_em_check(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "em_report.txt").write_text(
            "EM violations: 0\nMax current density: 0.50 mA/um\n"
        )
        return EMCheckResult(
            total_violations=0, violations=[], max_current_density_ma_um=0.5,
            avg_current_density_ma_um=0.3, is_clean=True,
            runtime_seconds=0.5,
        )

    def run_density_check(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "density_report.txt").write_text(
            "Density: 65.0%\nMin density: 45.0%\nMax density: 75.0%\nViolations: 0\n"
        )
        return DensityResult(
            density_pct=65.0, min_density_pct=45.0, max_density_pct=75.0, violations=0,
            runtime_seconds=0.3,
        )

    def run_yield_enhancement(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "yield_report.txt").write_text(
            "Redundant vias: 25\nRepair coverage: 95.0\nTotal spots: 2\nCritical spots: 0\n"
        )
        return YieldResult(
            redundant_vias=25, repair_coverage_pct=95.0, critical_area_reduction_pct=10.0,
            total_spots=2, critical_spots=0,
            runtime_seconds=0.5,
        )

    def run_top_floorplanning(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "top_floorplan_log.txt").write_text(
            "Die area: 1000.0 x 1000.0\nBlock top placed at (0.0 0.0) size (1000.0 1000.0)\n"
        )
        return TopFloorplanResult(
            total_blocks=1,
            blocks=[PlacedBlock(name="top", x=0, y=0, width=1000, height=1000)],
            die_width_um=1000.0, die_height_um=1000.0,
            runtime_seconds=0.5,
        )

    def run_drc(self, run_dir, design_name, gds_file, pdk):
        self._ensure_dirs(run_dir)
        (Path(run_dir) / "drc_raw.txt").write_text("DRC_TOTAL: 0\n")
        return DRCResult(
            total_violations=0, by_rule={}, violations=[], is_clean=True,
            runtime_seconds=0.5,
        )

    def run_lvs(self, run_dir, design_name, gds_file, netlist_file, pdk):
        self._ensure_dirs(run_dir)
        report_path = Path(run_dir) / "reports" / "lvs_report.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("Netlists match\nCircuits match uniquely\nUnmatched devices: 0\nUnmatched nets: 0\n")
        (Path(run_dir) / "lvs_comp.out").write_text("Circuits match uniquely\n")
        from gli_flow.backends.openroad_adapter import LVSStatus
        return LVSResult(
            status=LVSStatus.PASS, unmatched_devices=0, unmatched_nets=0,
            parameter_mismatches=0, short_count=0, open_count=0, is_clean=True,
            runtime_seconds=0.5, return_code=0, report_exists=True,
            report_size=report_path.stat().st_size, comparison_completed=True,
            parser_status="parsed",
        )

    def run_atpg(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "atpg_report.txt").write_text(
            "Total patterns: 10\nDetected faults: 95\nTotal faults: 100\nFault coverage: 95.0%\n"
        )
        return ATPGResult(
            total_patterns=10, detected_faults=95, total_faults=100, fault_coverage_pct=95.0,
            test_time_est_us=100.0, patterns=[], runtime_seconds=0.5,
        )

    def run_si_analysis(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "si_report.txt").write_text(
            "Crosstalk violations: 0\nMax delta delay: 0.030\nTotal aggressors: 0\n"
        )
        return SIResult(
            total_crosstalk_violations=0, violations=[], max_delta_delay_ns=0.03,
            total_aggressors=0, is_clean=True,
            runtime_seconds=0.3,
        )

    def pre_synthesis_checks(self, rtl_files, top_module, run_dir):
        return {
            "has_sv": False,
            "latch_inferred": False,
            "multi_driver": False,
            "missing_modules": [],
            "errors": [],
            "warnings": [],
        }

    def run_klayout_drc(self, run_dir, design_name, gds_file, pdk):
        return DRCResult(
            total_violations=0, by_rule={}, violations=[], is_clean=True,
            runtime_seconds=0.3,
        )

    def merge_drc_results(self, magic_result, klayout_result):
        return DRCResult(
            total_violations=magic_result.total_violations + klayout_result.total_violations,
            by_rule={**magic_result.by_rule, **klayout_result.by_rule},
            violations=magic_result.violations + klayout_result.violations,
            is_clean=magic_result.is_clean and klayout_result.is_clean,
            runtime_seconds=magic_result.runtime_seconds + klayout_result.runtime_seconds,
        )

    def run_post_fill_density_check(self, run_dir, design_name, pdk):
        return DensityResult(
            density_pct=65.0, min_density_pct=45.0, max_density_pct=75.0, violations=0,
            runtime_seconds=0.3,
        )

    def run_timing_signoff(self, run_dir, design_name, pdk, corner_name="typical"):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", f"signoff_{corner_name}_setup.rpt").write_text(
            "WNS: 0.05\nTNS: 0.00\nEndpoints: 50\n"
        )
        return TimingSignoffResult(
            total_endpoints=50, setup_wns_ns=0.05, setup_tns_ns=0.0,
            hold_wns_ns=0.02, hold_tns_ns=0.0, max_ocv_derating=1.1,
            setup_satisfied=True, hold_satisfied=True,
            runtime_seconds=1.0,
        )

    def run_d2d_interface_check(self, run_dir, design_name, pdk):
        self._ensure_dirs(run_dir)
        Path(run_dir, "reports", "d2d_report.txt").write_text(
            "Cross-boundary paths: 10\nInterface violations: 0\n"
        )
        return D2DInterfaceResult(
            total_violations=0, violations=[], max_cross_delay_ns=0.02, is_clean=True,
            runtime_seconds=0.3,
        )
