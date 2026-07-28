import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import ClockGatingResult
from gli_flow.telemetry.parser import TelemetryParser


def test_clock_gating_result_dataclass():
    r = ClockGatingResult(total_registers=1000, gated_registers=650, power_savings_pct=65.0, clock_gates_inserted=42)
    assert r.power_savings_pct == 65.0
    assert r.clock_gates_inserted == 42


def test_clock_gating_result_empty():
    r = ClockGatingResult(total_registers=1000, gated_registers=0, power_savings_pct=0.0, clock_gates_inserted=0)
    assert r.gated_registers == 0


def test_parse_clock_gating_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "clock_gating_log.txt"
        report.write_text("Total registers: 1000\nGated registers: 650\nClock gate cells: 42\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_clock_gating_report(str(report))
        assert metrics["cg_total_registers"] == 1000
        assert metrics["cg_gated_registers"] == 650
        assert metrics["cg_power_savings_pct"] == 65.0


def test_parse_clock_gating_report_empty():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "clock_gating_log.txt"
        report.write_text("No registers found\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_clock_gating_report(str(report))
        assert metrics["cg_total_registers"] == 0


def test_parse_clock_gating_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_clock_gating_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["cg_status"] == "NOT_RUN"
        assert metrics["cg_power_savings_pct"] is None
