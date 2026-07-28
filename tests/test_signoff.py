import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import TimingSignoffResult
from gli_flow.telemetry.parser import TelemetryParser


def test_timing_signoff_result_dataclass():
    r = TimingSignoffResult(total_endpoints=1000, setup_wns_ns=0.05, setup_tns_ns=0.0,
                            hold_wns_ns=0.02, hold_tns_ns=0.0, max_ocv_derating=1.1,
                            setup_satisfied=True)
    assert r.setup_wns_ns == 0.05
    assert r.setup_satisfied
    assert r.total_endpoints == 1000


def test_timing_signoff_result_violation():
    r = TimingSignoffResult(total_endpoints=1000, setup_wns_ns=-0.12, setup_tns_ns=-2.5,
                            hold_wns_ns=0.01, hold_tns_ns=0.0, max_ocv_derating=1.15,
                            setup_satisfied=False)
    assert not r.setup_satisfied
    assert r.setup_wns_ns == -0.12
    assert r.setup_tns_ns == -2.5


def test_parse_signoff_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "signoff_setup.rpt"
        report.write_text("wns 0.05\ntns 0.00\nEndpoints: 1000\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_signoff_report(str(report))
        assert metrics["signoff_setup_wns_ns"] == 0.05
        assert metrics["signoff_setup_satisfied"] is True


def test_parse_signoff_report_negative():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "signoff_setup.rpt"
        report.write_text("wns -0.12\ntns -2.50\nEndpoints: 1000\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_signoff_report(str(report))
        assert metrics["signoff_setup_wns_ns"] == -0.12
        assert metrics["signoff_setup_tns_ns"] == -2.50
        assert metrics["signoff_setup_satisfied"] is False


def test_parse_signoff_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_signoff_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["signoff_setup_satisfied"] is False
        assert metrics["signoff_setup_wns_ns"] is None
