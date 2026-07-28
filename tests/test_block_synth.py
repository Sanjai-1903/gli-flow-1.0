import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import BlockSynthesisResult
from gli_flow.telemetry.parser import TelemetryParser


def test_block_synthesis_result_dataclass():
    r = BlockSynthesisResult(total_blocks=2, total_cells=15000, total_area_um2=120000.0, estimated_power_mw=45.0)
    assert r.total_blocks == 2
    assert r.total_cells == 15000


def test_block_synthesis_result_empty():
    r = BlockSynthesisResult(total_blocks=0, total_cells=0, total_area_um2=0.0, estimated_power_mw=0.0)
    assert r.total_area_um2 == 0.0


def test_parse_block_synthesis_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "block_synth_log.txt"
        log.write_text("Number of blocks: 2\nNumber of cells: 15000\nChip area for top module: 120000.0\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_block_synthesis_report(str(log))
        assert metrics["bs_total_blocks"] == 2
        assert metrics["bs_total_cells"] == 15000
        assert metrics["bs_total_area_um2"] == 120000.0


def test_parse_block_synthesis_report_empty():
    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "block_synth_log.txt"
        log.write_text("Synthesis completed\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_block_synthesis_report(str(log))
        assert metrics["bs_total_cells"] == 0


def test_parse_block_synthesis_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_block_synthesis_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["bs_total_area_um2"] == 0.0
