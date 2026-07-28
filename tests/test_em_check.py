import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import EMViolation, EMCheckResult
from gli_flow.telemetry.parser import TelemetryParser


def test_em_violation_dataclass():
    v = EMViolation(net_name="VDD", layer="metal4", current_density_ma_um=1.5, limit_ma_um=1.0, wire_width_um=0.5)
    assert v.net_name == "VDD"
    assert v.current_density_ma_um == 1.5
    assert v.limit_ma_um == 1.0
    assert not v.description


def test_em_check_result_clean():
    r = EMCheckResult(total_violations=0, violations=[], max_current_density_ma_um=0.3,
                      avg_current_density_ma_um=0.15, is_clean=True)
    assert r.is_clean
    assert r.total_violations == 0


def test_em_check_result_violations():
    v = EMViolation(net_name="VDD", layer="metal2", current_density_ma_um=2.1, limit_ma_um=1.0, wire_width_um=0.3)
    r = EMCheckResult(total_violations=1, violations=[v], max_current_density_ma_um=2.1,
                      avg_current_density_ma_um=2.1, is_clean=False)
    assert not r.is_clean
    assert r.max_current_density_ma_um == 2.1


def test_parse_em_report_clean():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "em_report.txt"
        report.write_text("EM check passed: 0 violations\nMax current density: 0.250\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_em_report(str(report))
        assert metrics["em_total_violations"] == 0
        assert metrics["em_max_current_density_ma_um"] == 0.25
        assert metrics["em_is_clean"] is True


def test_parse_em_report_violations():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "em_report.txt"
        report.write_text(
            "EM Violation on VDD layer metal2 1.50 (limit 1.00)\n"
            "EM violation on VSS layer metal3 1.80 (limit 1.00)\n"
        )
        p = TelemetryParser(tmp)
        metrics = p.parse_em_report(str(report))
        assert metrics["em_total_violations"] == 2
        assert metrics["em_max_current_density_ma_um"] >= 1.8
        assert metrics["em_is_clean"] is False


def test_parse_em_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_em_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["em_status"] == "NOT_RUN"
        assert metrics["em_total_violations"] is None
        assert metrics["em_is_clean"] is False
