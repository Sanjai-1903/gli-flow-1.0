import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import YieldResult
from gli_flow.telemetry.parser import TelemetryParser


def test_yield_result_dataclass():
    r = YieldResult(redundant_vias=450, repair_coverage_pct=92.5, critical_area_reduction_pct=15.0,
                    total_spots=8, critical_spots=2)
    assert r.redundant_vias == 450
    assert r.repair_coverage_pct == 92.5


def test_yield_result_empty():
    r = YieldResult(redundant_vias=0, repair_coverage_pct=0.0, critical_area_reduction_pct=0.0,
                    total_spots=0, critical_spots=0)
    assert r.critical_spots == 0


def test_parse_yield_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "yield_report.txt"
        report.write_text("Redundant vias: 450\nRepair coverage: 92.5\nCritical spots: 2\nTotal spots: 8\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_yield_report(str(report))
        assert metrics["yield_redundant_vias"] == 450
        assert metrics["yield_repair_coverage_pct"] == 92.5
        assert metrics["yield_critical_spots"] == 2


def test_parse_yield_report_empty():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "yield_report.txt"
        report.write_text("Yield enhancement skipped\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_yield_report(str(report))
        assert metrics["yield_redundant_vias"] == 0


def test_parse_yield_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_yield_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["yield_status"] == "NOT_RUN"
        assert metrics["yield_repair_coverage_pct"] is None
