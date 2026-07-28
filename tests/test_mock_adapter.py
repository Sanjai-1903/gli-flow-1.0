import tempfile
from pathlib import Path

from gli_flow.testing.mock_adapter import MockEDAAdapter


def test_mock_adapter_init():
    a = MockEDAAdapter()
    assert a.platform == "mock"
    assert a.validate_environment() == []


def test_mock_adapter_generate_config():
    with tempfile.TemporaryDirectory() as tmp:
        manifest = {"design_name": "test", "pdk": "sky130"}
        result = MockEDAAdapter().generate_config(manifest, tmp)
        assert result["success"]
        assert Path(result["config_path"]).exists()


def test_mock_adapter_run():
    with tempfile.TemporaryDirectory() as tmp:
        a = MockEDAAdapter()
        result = a.run("config.json", "/tmp/design", tmp)
        assert result["success"]
        assert result["returncode"] == 0
        assert result["duration"] == 42.0
        assert (Path(tmp) / "reports" / "metrics.csv").exists()
        assert (Path(tmp) / "results" / "6_final.gds").exists()


def test_mock_adapter_run_corner():
    with tempfile.TemporaryDirectory() as tmp:
        a = MockEDAAdapter()
        result = a.run_corner("config.json", "/tmp/design", tmp, None)
        assert result["success"]
        assert result["wns"] == 0.05


def test_mock_adapter_stage_methods_return_dataclasses():
    a = MockEDAAdapter()
    with tempfile.TemporaryDirectory() as tmp:
        assert a.run_hierarchical_partitioning(tmp, "test", None).total_blocks >= 1
        assert a.run_block_synthesis(tmp, "test", None).total_cells >= 1
        assert a.run_clock_gating(tmp, "test", None).total_registers > 0
        assert a.run_scan_insertion(tmp, "test", None).scan_coverage_pct > 0
        assert a.run_formal(tmp, "test", None).is_equivalent
        assert a.run_pro(tmp, "test", None).buffer_count > 0
        assert a.run_antenna_check(tmp, "test", None).is_clean
        assert a.run_decap(tmp, "test", None).total_decap_cells > 0
        assert a.run_power_analysis(tmp, "test", None).total_power_mw > 0
        assert a.run_em_check(tmp, "test", None).is_clean
        assert a.run_density_check(tmp, "test", None).density_pct > 0
        assert a.run_yield_enhancement(tmp, "test", None).redundant_vias > 0
        assert a.run_top_floorplanning(tmp, "test", None).die_width_um > 0
        assert a.run_atpg(tmp, "test", None).fault_coverage_pct > 0
        assert a.run_si_analysis(tmp, "test", None).is_clean
        assert a.run_timing_signoff(tmp, "test", None).setup_satisfied
        assert a.run_d2d_interface_check(tmp, "test", None).is_clean


def test_mock_adapter_run_fill():
    with tempfile.TemporaryDirectory() as tmp:
        a = MockEDAAdapter()
        path = a.run_fill(tmp, "test", None)
        assert path is not None
        assert Path(path).exists()


def test_mock_adapter_drc_lvs():
    with tempfile.TemporaryDirectory() as tmp:
        a = MockEDAAdapter()
        drc = a.run_drc(tmp, "test", "fake.gds", None)
        assert drc.is_clean
        lvs = a.run_lvs(tmp, "test", "fake.gds", "fake.v", None)
        assert lvs.is_clean
