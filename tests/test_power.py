import tempfile
from pathlib import Path

from gli_flow.telemetry.parser import TelemetryParser
from gli_flow.backends.openroad_adapter import PowerResult


def test_power_result_dataclass():
    pr = PowerResult(total_power_mw=10.5, leakage_mw=0.5, internal_mw=5.0, switching_mw=5.0)
    assert pr.total_power_mw == 10.5
    assert pr.leakage_mw == 0.5
    assert pr.internal_mw == 5.0
    assert pr.switching_mw == 5.0
    assert pr.max_ir_drop_mv is None
    assert pr.ir_violation_count == 0


def test_power_result_with_ir():
    pr = PowerResult(total_power_mw=10.5, leakage_mw=0.5, internal_mw=5.0, switching_mw=5.0,
                     max_ir_drop_mv=85.0, mean_ir_drop_mv=42.0, ir_violation_count=3)
    assert pr.max_ir_drop_mv == 85.0
    assert pr.mean_ir_drop_mv == 42.0
    assert pr.ir_violation_count == 3


def test_parse_power_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_power_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["power_status"] == "NOT_RUN"
        assert metrics["total_power_mw"] is None
        assert metrics["max_ir_drop_mv"] is None


def test_parse_power_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "power_report.txt"
        report.write_text(
            "Group                  Internal  Switching  Leakage    Total\n"
            "Sequential             0.452     0.123      0.008      0.583\n"
            "Combinational          0.891     0.234      0.012      1.137\n"
            "Clock                  0.567     0.089      0.001      0.657\n"
            "Total                  1.910     0.446      0.021      2.377\n"
        )
        p = TelemetryParser(tmp)
        metrics = p.parse_power_report(str(report))
        assert metrics["total_power_mw"] == 2.377
        assert metrics["leakage_mw"] == 0.021
        assert metrics["internal_mw"] == 1.910
        assert metrics["switching_mw"] == 0.446


def test_parse_power_report_malformed():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "power_report.txt"
        report.write_text("garbage data\nno numbers here\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_power_report(str(report))
        assert metrics["total_power_mw"] == 0.0
