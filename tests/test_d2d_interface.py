import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import D2DInterfaceViolation, D2DInterfaceResult
from gli_flow.telemetry.parser import TelemetryParser


def test_d2d_interface_violation_dataclass():
    v = D2DInterfaceViolation(net_name="d2d_bus", delay_ns=0.15, source_die="die0", dest_die="die1")
    assert v.delay_ns == 0.15
    assert v.source_die == "die0"


def test_d2d_interface_result_clean():
    r = D2DInterfaceResult(total_violations=0, violations=[], max_cross_delay_ns=0.03, is_clean=True)
    assert r.is_clean
    assert r.max_cross_delay_ns == 0.03


def test_d2d_interface_result_violations():
    v = D2DInterfaceViolation("d2d_bus", 0.15, "die0", "die1")
    r = D2DInterfaceResult(total_violations=1, violations=[v], max_cross_delay_ns=0.15, is_clean=False)
    assert not r.is_clean
    assert r.violations[0].net_name == "d2d_bus"


def test_parse_d2d_interface_report_clean():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "d2d_report.txt"
        report.write_text("Cross-boundary paths: 50\nInterface violations: 0\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_d2d_interface_report(str(report))
        assert metrics["d2d_cross_boundary_paths"] == 50
        assert metrics["d2d_is_clean"] is True


def test_parse_d2d_interface_report_violations():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "d2d_report.txt"
        report.write_text("Cross-boundary paths: 50\nInterface violations: 1\nInterface violation on d2d_bus delay 0.15 source die0 dest die1\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_d2d_interface_report(str(report))
        assert metrics["d2d_total_violations"] >= 1
        assert metrics["d2d_is_clean"] is False


def test_parse_d2d_interface_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_d2d_interface_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["d2d_is_clean"] is True
