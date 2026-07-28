import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import PROResult
from gli_flow.telemetry.parser import TelemetryParser


def test_pro_result_dataclass():
    r = PROResult(buffer_count=120, slack_improvement_ns=0.35, wire_length_change_pct=-2.5,
                  setup_violations_fixed=15, hold_violations_fixed=3)
    assert r.buffer_count == 120
    assert r.slack_improvement_ns == 0.35


def test_pro_result_empty():
    r = PROResult(buffer_count=0, slack_improvement_ns=0.0, wire_length_change_pct=0.0,
                  setup_violations_fixed=0, hold_violations_fixed=0)
    assert r.buffer_count == 0


def test_parse_pro_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "pro_log.txt"
        report.write_text("Inserted 85 buffers\nSlack improvement: 0.28\nSetup violations fixed: 12\nHold violations fixed: 2\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_pro_report(str(report))
        assert metrics["pro_buffer_count"] == 85
        assert metrics["pro_slack_improvement_ns"] == 0.28
        assert metrics["pro_setup_fixed"] == 12
        assert metrics["pro_hold_fixed"] == 2


def test_parse_pro_report_empty():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "pro_log.txt"
        report.write_text("No timing violations to fix\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_pro_report(str(report))
        assert metrics["pro_buffer_count"] == 0


def test_parse_pro_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_pro_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["pro_status"] == "NOT_RUN"
        assert metrics["pro_slack_improvement_ns"] is None
