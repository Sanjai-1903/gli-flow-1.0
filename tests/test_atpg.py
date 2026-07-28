import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import ATPGPattern, ATPGResult
from gli_flow.telemetry.parser import TelemetryParser


def test_atpg_pattern_dataclass():
    p = ATPGPattern(pattern_id=1, fault_type="stuck-at-0", fault_site="A[3]", detect_status="DETECTED")
    assert p.pattern_id == 1
    assert p.fault_type == "stuck-at-0"


def test_atpg_result_dataclass():
    patterns = [
        ATPGPattern(1, "stuck-at-0", "A[3]", "DETECTED"),
        ATPGPattern(2, "stuck-at-1", "B[5]", "DETECTED"),
    ]
    r = ATPGResult(total_patterns=50, detected_faults=480, total_faults=500,
                   fault_coverage_pct=96.0, test_time_est_us=500.0, patterns=patterns)
    assert r.total_patterns == 50
    assert r.fault_coverage_pct == 96.0
    assert len(r.patterns) == 2


def test_atpg_result_zero_faults():
    r = ATPGResult(total_patterns=0, detected_faults=0, total_faults=0,
                   fault_coverage_pct=0.0, test_time_est_us=0.0, patterns=[])
    assert r.fault_coverage_pct == 0.0


def test_parse_atpg_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "atpg_report.txt"
        report.write_text(
            "Total patterns: 42\n"
            "Detected faults: 380\n"
            "Total faults: 400\n"
        )
        p = TelemetryParser(tmp)
        metrics = p.parse_atpg_report(str(report))
        assert metrics["atpg_total_patterns"] == 42
        assert metrics["atpg_detected_faults"] == 380
        assert metrics["atpg_total_faults"] == 400
        assert metrics["atpg_fault_coverage_pct"] == 95.0


def test_parse_atpg_report_empty():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "atpg_report.txt"
        report.write_text("ATPG not run - no scan chains\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_atpg_report(str(report))
        assert metrics["atpg_total_patterns"] == 0
        assert metrics["atpg_fault_coverage_pct"] == 0.0


def test_parse_atpg_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_atpg_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["atpg_status"] == "NOT_RUN"
        assert metrics["atpg_detected_faults"] is None
