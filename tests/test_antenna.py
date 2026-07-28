import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import AntennaViolation, AntennaResult
from gli_flow.telemetry.parser import TelemetryParser


def test_antenna_violation_dataclass():
    v = AntennaViolation(net_name="VDD", ratio=4.5, limit=3.0, layer="metal2")
    assert v.net_name == "VDD"
    assert v.ratio == 4.5


def test_antenna_result_clean():
    r = AntennaResult(total_violations=0, violations=[], max_antenna_ratio=0.5, is_clean=True)
    assert r.is_clean
    assert r.max_antenna_ratio == 0.5


def test_antenna_result_violations():
    v = AntennaViolation(net_name="clk_net", ratio=5.2, limit=3.0, layer="metal3")
    r = AntennaResult(total_violations=1, violations=[v], max_antenna_ratio=5.2, is_clean=False)
    assert not r.is_clean
    assert r.violations[0].net_name == "clk_net"


def test_parse_antenna_report_clean():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "antenna_report.txt"
        report.write_text("Antenna check passed: 0 violations\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_antenna_report(str(report))
        assert metrics["antenna_total_violations"] == 0
        assert metrics["antenna_is_clean"] is True


def test_parse_antenna_report_violations():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "antenna_report.txt"
        report.write_text("Antenna violation on net clk ratio 5.2\nAntenna violation on net rst ratio 3.8\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_antenna_report(str(report))
        assert metrics["antenna_total_violations"] >= 2
        assert metrics["antenna_max_ratio"] >= 5.2
        assert metrics["antenna_is_clean"] is False


def test_parse_antenna_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_antenna_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["antenna_status"] == "NOT_RUN"
        assert metrics["antenna_total_violations"] is None
