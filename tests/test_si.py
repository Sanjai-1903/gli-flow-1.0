import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import CrosstalkViolation, SIResult
from gli_flow.telemetry.parser import TelemetryParser


def test_crosstalk_violation_dataclass():
    v = CrosstalkViolation(net_name="data_bus", delta_delay_ns=0.12, aggressor_count=3, victim_net="data_bus")
    assert v.delta_delay_ns == 0.12
    assert v.aggressor_count == 3


def test_si_result_clean():
    r = SIResult(total_crosstalk_violations=0, violations=[], max_delta_delay_ns=0.03,
                 total_aggressors=0, is_clean=True)
    assert r.is_clean
    assert r.max_delta_delay_ns == 0.03


def test_si_result_violations():
    v = CrosstalkViolation(net_name="clk", delta_delay_ns=0.15, aggressor_count=5, victim_net="clk")
    r = SIResult(total_crosstalk_violations=1, violations=[v], max_delta_delay_ns=0.15,
                 total_aggressors=5, is_clean=False)
    assert not r.is_clean
    assert r.violations[0].net_name == "clk"


def test_parse_si_report_clean():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "si_report.txt"
        report.write_text("Crosstalk violations: 0\nMax delta delay: 0.030\nTotal aggressors: 0\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_si_report(str(report))
        assert metrics["si_crosstalk_violations"] == 0
        assert metrics["si_is_clean"] is True


def test_parse_si_report_violations():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "si_report.txt"
        report.write_text("Crosstalk violations: 2\nMax delta delay: 0.15\nTotal aggressors: 8\nCrosstalk violation on data_bus delta 0.12 aggressors 3\nCrosstalk violation on clk delta 0.15 aggressors 5\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_si_report(str(report))
        assert metrics["si_crosstalk_violations"] >= 2
        assert metrics["si_max_delta_delay_ns"] >= 0.15


def test_parse_si_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_si_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["si_status"] == "NOT_RUN"
        assert metrics["si_is_clean"] is False
