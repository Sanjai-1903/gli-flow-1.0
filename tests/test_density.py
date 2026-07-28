import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import DensityResult
from gli_flow.telemetry.parser import TelemetryParser


def test_density_result_dataclass():
    r = DensityResult(density_pct=55.0, min_density_pct=30.0, max_density_pct=70.0, violations=0)
    assert r.density_pct == 55.0
    assert r.violations == 0


def test_density_result_violations():
    r = DensityResult(density_pct=25.0, min_density_pct=30.0, max_density_pct=70.0, violations=3)
    assert r.violations == 3
    assert r.density_pct < r.min_density_pct


def test_parse_density_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "density_report.txt"
        report.write_text("Density: 62.5\nMin density: 30.0\nMax density: 70.0\nViolations: 0\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_density_report(str(report))
        assert metrics["density_pct"] == 62.5
        assert metrics["density_min_pct"] == 30.0
        assert metrics["density_violations"] == 0


def test_parse_density_report_violations():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "density_report.txt"
        report.write_text("Density: 28.0\nMin density: 30.0\nMax density: 70.0\nViolations: 2\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_density_report(str(report))
        assert metrics["density_violations"] == 2
        assert metrics["density_pct"] == 28.0


def test_parse_density_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_density_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["density_status"] == "NOT_RUN"
        assert metrics["density_violations"] is None
