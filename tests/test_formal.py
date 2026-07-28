import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import FormalResult
from gli_flow.telemetry.parser import TelemetryParser


def test_formal_result_dataclass():
    r = FormalResult(total_compare_points=5000, unmatched_points=0, failures=0, is_equivalent=True)
    assert r.is_equivalent
    assert r.total_compare_points == 5000


def test_formal_result_not_equivalent():
    r = FormalResult(total_compare_points=5000, unmatched_points=10, failures=3, is_equivalent=False)
    assert not r.is_equivalent
    assert r.failures == 3


def test_parse_formal_report_equivalent():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "formal_log.txt"
        report.write_text("Compare points: 5000\nEquivalent: 1\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_formal_report(str(report))
        assert metrics["formal_compare_points"] == 5000
        assert metrics["formal_is_equivalent"] is True


def test_parse_formal_report_not_equivalent():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "formal_log.txt"
        report.write_text("Compare points: 5000\nNot equivalent: 3 Mismatches\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_formal_report(str(report))
        assert not metrics["formal_is_equivalent"]
        assert metrics["formal_failures"] > 0


def test_parse_formal_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_formal_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["formal_status"] == "NOT_RUN"
        assert metrics["formal_is_equivalent"] is False
