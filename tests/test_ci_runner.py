import tempfile
from pathlib import Path

from gli_flow.ci.config import CIConfig
from gli_flow.ci.reporter import CIReport, generate_junit_xml, generate_markdown_report
from gli_flow.ci.runner import CIRunner


def test_ci_config_defaults():
    c = CIConfig(design_path="/tmp/design")
    assert c.design_path == "/tmp/design"
    assert c.junit_output is None
    assert c.qor_score_min is None


def test_ci_config_with_thresholds():
    c = CIConfig(design_path="/tmp/design", qor_score_min=50.0, wns_max=-0.1, junit_output="report.xml")
    assert c.qor_score_min == 50.0
    assert c.wns_max == -0.1
    assert c.junit_output == "report.xml"


def test_ci_report_dataclass():
    r = CIReport(
        success=True, run_id="ci_123_test", design_name="test",
        metrics={"qor_score": 85.0, "wns": 0.05},
        baseline_metrics={"qor_score": 80.0, "wns": 0.0},
        regressions=[], duration=120.5,
    )
    assert r.success
    assert r.design_name == "test"
    assert r.metrics["qor_score"] == 85.0


def test_ci_report_with_regressions():
    r = CIReport(
        success=False, run_id="ci_456_test", design_name="test",
        metrics={"qor_score": 45.0, "wns": -0.5},
        baseline_metrics={"qor_score": 80.0, "wns": 0.0},
        regressions=["QoR score regressed 45.0 vs baseline 80.0"],
        duration=60.0, error="Run failed",
    )
    assert not r.success
    assert len(r.regressions) == 1


def test_generate_junit_xml_clean():
    r = CIReport(
        success=True, run_id="run_1", design_name="counter",
        metrics={"qor_score": 90.0}, baseline_metrics=None,
        regressions=[], duration=10.5,
    )
    xml = generate_junit_xml(r)
    assert 'tests="1"' in xml
    assert 'failures="0"' in xml
    assert "run_1" in xml


def test_generate_junit_xml_failure():
    r = CIReport(
        success=False, run_id="run_2", design_name="counter",
        metrics={"qor_score": 30.0}, baseline_metrics={"qor_score": 80.0},
        regressions=["QoR score regressed"], duration=5.0,
        error="Run failed",
    )
    xml = generate_junit_xml(r)
    assert 'failures="1"' in xml
    assert "QoR score regressed" in xml
    assert "Run failed" in xml


def test_generate_markdown_report_clean():
    r = CIReport(
        success=True, run_id="run_1", design_name="counter",
        metrics={"qor_score": 90.0, "wns": 0.05},
        baseline_metrics=None, regressions=[], duration=10.5,
    )
    md = generate_markdown_report(r)
    assert "CI Report: counter" in md
    assert "✅ PASS" in md
    assert "90.0" in md


def test_generate_markdown_report_failure():
    r = CIReport(
        success=False, run_id="run_2", design_name="counter",
        metrics={"qor_score": 30.0},
        baseline_metrics={"qor_score": 80.0, "wns": 0.0},
        regressions=["QoR score regressed"], duration=5.0,
        error="Run failed",
    )
    md = generate_markdown_report(r)
    assert "❌ FAIL" in md
    assert "QoR score regressed" in md
    assert "Run failed" in md


def test_ci_runner_instantiate():
    c = CIConfig(design_path="/nonexistent/design")
    runner = CIRunner(c)
    assert runner.config.design_path == "/nonexistent/design"
