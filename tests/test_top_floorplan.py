import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import PlacedBlock, TopFloorplanResult
from gli_flow.telemetry.parser import TelemetryParser


def test_placed_block_dataclass():
    b = PlacedBlock(name="cpu_core", x=0.0, y=0.0, width=300.0, height=200.0)
    assert b.width == 300.0
    assert b.height == 200.0


def test_top_floorplan_result_dataclass():
    blocks = [PlacedBlock("cpu", 0, 0, 300, 200), PlacedBlock("mem", 400, 0, 250, 200)]
    r = TopFloorplanResult(total_blocks=2, blocks=blocks, die_width_um=1000.0, die_height_um=800.0)
    assert r.die_width_um == 1000.0
    assert len(r.blocks) == 2


def test_top_floorplan_result_empty():
    r = TopFloorplanResult(total_blocks=0, blocks=[], die_width_um=0.0, die_height_um=0.0)
    assert r.total_blocks == 0


def test_parse_top_floorplan_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "top_floorplan_log.txt"
        log.write_text("Die area: 1000.0 x 800.0\nBlock cpu_core placed at (0.0 0.0) size (300.0 200.0)\nBlock mem_subsystem placed at (400.0 0.0) size (250.0 200.0)\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_top_floorplan_report(str(log))
        assert metrics["tf_die_width_um"] == 1000.0
        assert metrics["tf_die_height_um"] == 800.0
        assert metrics["tf_total_blocks"] == 2


def test_parse_top_floorplan_report_empty():
    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "top_floorplan_log.txt"
        log.write_text("No blocks placed\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_top_floorplan_report(str(log))
        assert metrics["tf_total_blocks"] == 0


def test_parse_top_floorplan_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_top_floorplan_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["tf_die_width_um"] == 0.0
