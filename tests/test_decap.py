import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import DecapResult
from gli_flow.telemetry.parser import TelemetryParser


def test_decap_result_dataclass():
    r = DecapResult(total_decap_cells=120, decap_area_um2=450.0, decap_capacitance_pf=3.6,
                    target_coverage_pct=20.0, actual_coverage_pct=18.5)
    assert r.total_decap_cells == 120
    assert r.decap_capacitance_pf == 3.6
    assert r.actual_coverage_pct == 18.5


def test_decap_result_empty():
    r = DecapResult(total_decap_cells=0, decap_area_um2=0.0, decap_capacitance_pf=0.0,
                    target_coverage_pct=20.0, actual_coverage_pct=0.0)
    assert r.total_decap_cells == 0


def test_parse_decap_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "decap_log.txt"
        report.write_text("Inserted 85 decap cells\nDecap capacitance: 2.55 pF\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_decap_report(str(report))
        assert metrics["decap_total_cells"] == 85
        assert metrics["decap_capacitance_pf"] == 2.55


def test_parse_decap_report_empty():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "decap_log.txt"
        report.write_text("No decap cells needed\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_decap_report(str(report))
        assert metrics["decap_total_cells"] == 0


def test_parse_decap_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_decap_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["decap_status"] == "NOT_RUN"
        assert metrics["decap_total_cells"] is None
