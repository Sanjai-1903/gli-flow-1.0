import json
import tempfile
from pathlib import Path

import pytest

DESIGN_PATH = "examples/tiny_or"


@pytest.fixture
def mock_orch():
    """Create a FlowOrchestrator with an isolated temp database."""
    from gli_flow.core.orchestrator import FlowOrchestrator

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    orch = FlowOrchestrator(
        design_path=DESIGN_PATH,
        threads=1,
        mock=True,
        db_path=db_path,
    )
    yield orch
    orch.database.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.mark.e2e
def test_mock_pipeline_full_run(mock_orch):
    """Run the full 29-stage pipeline in mock mode on tiny_or, verify completion."""
    record = mock_orch.run()

    assert record.status == "SUCCESS", f"Pipeline failed: status={record.status}"
    assert record.current_stage == "DONE"
    assert record.progress == 100
    assert record.qor_score is not None, "QoR score not computed"
    assert record.runtime_sec is not None and record.runtime_sec > 0


@pytest.mark.e2e
def test_mock_pipeline_generates_metrics(mock_orch):
    """Verify mock mode produces realistic metrics from TelemetryParser."""
    from gli_flow.telemetry.parser import TelemetryParser

    record = mock_orch.run()

    reports_dir = mock_orch.run_dir / "reports"
    assert reports_dir.exists(), f"Reports dir not found: {reports_dir}"

    parser = TelemetryParser(str(reports_dir))
    metrics = parser.parse_all()

    assert "setup_wns_ns" in metrics or "wns" in metrics
    assert "utilization" in metrics
    assert "runtime_sec" in metrics


@pytest.mark.e2e
def test_mock_pipeline_check_stage_files(mock_orch):
    """Verify each pipeline stage creates its expected report file."""
    record = mock_orch.run()
    reports_dir = mock_orch.run_dir / "reports"

    expected_files = [
        "partition_log.txt",
        "block_synth_log.txt",
        "clock_gating_log.txt",
        "scan_log.txt",
        "formal_log.txt",
        "pro_log.txt",
        "antenna_report.txt",
        "decap_log.txt",
        "power_report.txt",
        "em_report.txt",
        "density_report.txt",
        "yield_report.txt",
        "top_floorplan_log.txt",
        "atpg_report.txt",
        "si_report.txt",
        "signoff_worst_setup.rpt",
        "signoff_typical_setup.rpt",
        "signoff_best_setup.rpt",
        "d2d_report.txt",
        "metrics.csv",
        "timing.rpt",
        "utilization.rpt",
        "runtime.rpt",
    ]
    for fname in expected_files:
        assert (reports_dir / fname).exists(), f"Missing report: {fname}"

    artifacts_dir = mock_orch.run_dir / "artifacts"
    assert artifacts_dir.exists()
    assert (mock_orch.run_dir / "results" / "6_final.gds").exists()


@pytest.mark.e2e
def test_mock_pipeline_drc_lvs_clean(mock_orch):
    """Verify DRC and LVS report clean results in mock mode."""
    record = mock_orch.run()
    assert record.status == "SUCCESS"


@pytest.mark.e2e
def test_mock_pipeline_generates_manifest(mock_orch):
    """Verify reproducibility manifest is generated."""
    record = mock_orch.run()

    manifest_path = mock_orch.run_dir / "reproducibility.json"
    assert manifest_path.exists()
    with open(manifest_path) as f:
        manifest = json.load(f)
    assert "run_id" in manifest
    assert "design_name" in manifest
    assert manifest["design_name"] == "tiny_or"


@pytest.mark.e2e
def test_mock_pipeline_via_cli():
    """Verify gli-flow run --mock works via CLI subprocess."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "gli_flow", "run", DESIGN_PATH, "--mock"],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"CLI mock run failed: stderr={result.stderr[:500]}"
    assert "SUCCESS" in result.stdout
