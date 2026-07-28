import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def get_latest_run_dir():
    from gli_flow.database.migrations import _get_db_path
    db_path = Path(_get_db_path())
    if not db_path.exists():
        return None
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT run_id, run_dir FROM runs ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    run_dir = row[1]
    if run_dir:
        return run_dir
    import glob
    runs = sorted(glob.glob(f"outputs/runs/{row[0]}"))
    return runs[0] if runs else None


@pytest.mark.integration
def test_counter_sky130_full_pipeline():
    """Full RTL-to-GDS pipeline on counter example using mock mode."""
    result = subprocess.run(
        [sys.executable, "-m", "gli_flow", "run", "examples/counter", "--mock"],
        capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, f"Pipeline failed: stderr={result.stderr[:500]}, stdout={result.stdout[:500]}"
    run_dir = get_latest_run_dir()
    assert run_dir is not None, "No run directory found"
    run_path = Path(run_dir)
    results_dir = run_path / "results"
    assert results_dir.is_dir(), f"Results dir not found: {results_dir}"
    gds_path = results_dir / "6_final.gds"
    assert gds_path.exists(), f"GDS not produced: {gds_path}"
    def_path = results_dir / "6_final.def"
    assert def_path.exists(), f"DEF not produced: {def_path}"
    telemetry_path = run_path / "telemetry" / "metrics.json"
    assert telemetry_path.exists(), f"Telemetry not found: {telemetry_path}"
    with open(telemetry_path) as f:
        telemetry = json.load(f)
    metrics = telemetry.get("metrics", {})
    assert metrics.get("wns") is not None, "Missing WNS in telemetry"


@pytest.mark.integration
def test_stages_contain_phase2_stages():
    from gli_flow.core.orchestrator import STAGES
    required = ["FILL", "POWER", "DRC", "LVS", "SCAN_INSERTION", "DECAP", "EM_CHECK", "ATPG"]
    for stage in required:
        assert stage in STAGES, f"{stage} missing from STAGES"
    assert len(STAGES) == 29


@pytest.mark.integration
def test_drc_result_dataclass():
    from gli_flow.backends.openroad_adapter import DRCResult, DRCViolation
    v = DRCViolation(rule_name="test_rule", layer="metal1", x1=0, y1=0, x2=10, y2=10)
    r = DRCResult(total_violations=1, by_rule={"test_rule": 1}, violations=[v], is_clean=False)
    assert r.total_violations == 1
    assert not r.is_clean


@pytest.mark.integration
def test_lvs_result_dataclass():
    from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus
    r = LVSResult(status=LVSStatus.PASS, unmatched_devices=0, unmatched_nets=0,
                  parameter_mismatches=0, short_count=0, open_count=0, is_clean=True)
    assert r.is_clean
    assert r.result == LVSStatus.PASS


@pytest.mark.integration
def test_power_result_dataclass():
    from gli_flow.backends.openroad_adapter import PowerResult
    r = PowerResult(total_power_mw=5.0, leakage_mw=0.1, internal_mw=3.0, switching_mw=1.9)
    assert r.total_power_mw == 5.0


@pytest.mark.integration
def test_em_check_result_dataclass():
    from gli_flow.backends.openroad_adapter import EMCheckResult, EMViolation
    v = EMViolation(net_name="VDD", layer="metal2", current_density_ma_um=1.5, limit_ma_um=1.0, wire_width_um=0.3)
    r = EMCheckResult(total_violations=1, violations=[v], max_current_density_ma_um=1.5,
                      avg_current_density_ma_um=1.5, is_clean=False)
    assert not r.is_clean
    assert r.violations[0].net_name == "VDD"


@pytest.mark.integration
def test_decap_result_dataclass():
    from gli_flow.backends.openroad_adapter import DecapResult
    r = DecapResult(total_decap_cells=50, decap_area_um2=200.0, decap_capacitance_pf=1.5,
                    target_coverage_pct=20.0, actual_coverage_pct=15.0)
    assert r.total_decap_cells == 50


@pytest.mark.integration
def test_scan_result_dataclass():
    from gli_flow.backends.openroad_adapter import ScanResult, ScanChain
    c = ScanChain(chain_id=0, num_flops=64, scan_in_port="SE", scan_out_port="SO", chain_length=64)
    r = ScanResult(total_flops=64, scanned_flops=64, chains=[c],
                   scan_coverage_pct=100.0, test_clk_period_ns=100.0, was_inserted=True)
    assert r.scan_coverage_pct == 100.0


@pytest.mark.integration
def test_atpg_result_dataclass():
    from gli_flow.backends.openroad_adapter import ATPGResult, ATPGPattern
    p = ATPGPattern(pattern_id=1, fault_type="stuck-at-0", fault_site="A[3]", detect_status="DETECTED")
    r = ATPGResult(total_patterns=10, detected_faults=95, total_faults=100,
                   fault_coverage_pct=95.0, test_time_est_us=100.0, patterns=[p])
    assert r.fault_coverage_pct == 95.0


@pytest.mark.integration
def test_formal_result_dataclass():
    from gli_flow.backends.openroad_adapter import FormalResult
    r = FormalResult(total_compare_points=5000, unmatched_points=0, failures=0, is_equivalent=True)
    assert r.is_equivalent
    assert r.total_compare_points == 5000


@pytest.mark.integration
def test_antenna_result_dataclass():
    from gli_flow.backends.openroad_adapter import AntennaViolation, AntennaResult
    v = AntennaViolation(net_name="clk", ratio=4.5, limit=3.0, layer="metal2")
    r = AntennaResult(total_violations=1, violations=[v], max_antenna_ratio=4.5, is_clean=False)
    assert not r.is_clean
    assert r.violations[0].ratio == 4.5


@pytest.mark.integration
def test_density_result_dataclass():
    from gli_flow.backends.openroad_adapter import DensityResult
    r = DensityResult(density_pct=55.0, min_density_pct=30.0, max_density_pct=70.0, violations=0)
    assert r.density_pct == 55.0


@pytest.mark.integration
def test_timing_signoff_result_dataclass():
    from gli_flow.backends.openroad_adapter import TimingSignoffResult
    r = TimingSignoffResult(total_endpoints=1000, setup_wns_ns=0.05, setup_tns_ns=0.0,
                            hold_wns_ns=0.02, hold_tns_ns=0.0, max_ocv_derating=1.1,
                            setup_satisfied=True)
    assert r.setup_satisfied
    assert r.max_ocv_derating == 1.1


@pytest.mark.integration
def test_clock_gating_result_dataclass():
    from gli_flow.backends.openroad_adapter import ClockGatingResult
    r = ClockGatingResult(total_registers=1000, gated_registers=650, power_savings_pct=65.0, clock_gates_inserted=42)
    assert r.power_savings_pct == 65.0


@pytest.mark.integration
def test_pro_result_dataclass():
    from gli_flow.backends.openroad_adapter import PROResult
    r = PROResult(buffer_count=120, slack_improvement_ns=0.35, wire_length_change_pct=-2.5,
                  setup_violations_fixed=15, hold_violations_fixed=3)
    assert r.buffer_count == 120


@pytest.mark.integration
def test_si_result_dataclass():
    from gli_flow.backends.openroad_adapter import CrosstalkViolation, SIResult
    v = CrosstalkViolation(net_name="clk", delta_delay_ns=0.15, aggressor_count=5, victim_net="clk")
    r = SIResult(total_crosstalk_violations=1, violations=[v], max_delta_delay_ns=0.15,
                 total_aggressors=5, is_clean=False)
    assert not r.is_clean


@pytest.mark.integration
def test_yield_result_dataclass():
    from gli_flow.backends.openroad_adapter import YieldResult
    r = YieldResult(redundant_vias=450, repair_coverage_pct=92.5, critical_area_reduction_pct=15.0,
                    total_spots=8, critical_spots=2)
    assert r.redundant_vias == 450


@pytest.mark.integration
def test_hierarchical_partition_result_dataclass():
    from gli_flow.backends.openroad_adapter import HierarchicalBlock, HierarchicalPartitionResult
    b = HierarchicalBlock(name="cpu_core", instance_count=5000)
    r = HierarchicalPartitionResult(total_blocks=1, blocks=[b])
    assert r.total_blocks == 1


@pytest.mark.integration
def test_block_synthesis_result_dataclass():
    from gli_flow.backends.openroad_adapter import BlockSynthesisResult
    r = BlockSynthesisResult(total_blocks=2, total_cells=15000, total_area_um2=120000.0, estimated_power_mw=45.0)
    assert r.total_blocks == 2


@pytest.mark.integration
def test_top_floorplan_result_dataclass():
    from gli_flow.backends.openroad_adapter import PlacedBlock, TopFloorplanResult
    b = PlacedBlock(name="cpu", x=0, y=0, width=300, height=200)
    r = TopFloorplanResult(total_blocks=1, blocks=[b], die_width_um=1000.0, die_height_um=800.0)
    assert r.die_width_um == 1000.0


@pytest.mark.integration
def test_d2d_interface_result_dataclass():
    from gli_flow.backends.openroad_adapter import D2DInterfaceViolation, D2DInterfaceResult
    v = D2DInterfaceViolation(net_name="d2d_bus", delay_ns=0.15, source_die="die0", dest_die="die1")
    r = D2DInterfaceResult(total_violations=1, violations=[v], max_cross_delay_ns=0.15, is_clean=False)
    assert not r.is_clean
