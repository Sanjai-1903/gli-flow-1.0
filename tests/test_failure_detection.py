"""Week 3: Failure Atlas — detection pattern tests for orphaned signatures."""

from failure_atlas.detector import detect_failures
from failure_atlas.taxonomy import (
    FailureDomain, FailureCategory, FailureSeverity,
)
from failure_atlas.recommend_fixes import main as recommend_fixes_main


def _make_metrics(**overrides):
    base = {
        "setup_wns_ns": 0.5,
        "setup_tns_ns": 0.0,
        "hold_whs_ns": 0.1,
        "overflow_h": 0.01,
        "overflow_v": 0.01,
        "drc_total_violations": 0,
        "drc_is_clean": True,
        "lvs_status": "PASS",
        "lvs_result": "PASS",
    }
    base.update(overrides)
    return base


def test_no_detections_with_clean_metrics():
    entries = detect_failures("test_run", _make_metrics())
    assert len(entries) == 0


def test_ir_drop_detected():
    entries = detect_failures("test_run", _make_metrics(power_ir_drop_pct=12.5))
    assert any(e.level1_domain == FailureDomain.POWER and "IR drop" in e.level3_signature for e in entries)


def test_ir_drop_below_threshold_not_detected():
    entries = detect_failures("test_run", _make_metrics(power_ir_drop_pct=5.0))
    assert not any(e.level1_domain == FailureDomain.POWER for e in entries)


def test_clock_skew_detected():
    entries = detect_failures("test_run", _make_metrics(clock_skew_ns=0.75))
    assert any(
        e.level1_domain == FailureDomain.TIMING and e.level2_category == FailureCategory.CLOCK_SKEW
        for e in entries
    )


def test_max_transition_detected():
    entries = detect_failures("test_run", _make_metrics(max_transition_ns=1.2))
    assert any(e.level2_category == FailureCategory.MAX_TRANSITION for e in entries)


def test_max_capacitance_detected():
    entries = detect_failures("test_run", _make_metrics(max_capacitance_pf=0.45))
    assert any(e.level2_category == FailureCategory.MAX_CAPACITANCE for e in entries)


def test_power_false_pass_detected():
    entries = detect_failures("test_run", _make_metrics(
        power_pass=True,
        power_total_mw=None,
        power_static_mw=None,
        power_dynamic_mw=None,
        power_ir_drop_pct=None,
    ))
    assert any(
        e.level1_domain == FailureDomain.POWER and "false pass" in e.level3_signature.lower()
        for e in entries
    )


def test_power_valid_pass_not_detected():
    entries = detect_failures("test_run", _make_metrics(
        power_pass=True,
        power_total_mw=5.0,
        power_static_mw=2.0,
        power_dynamic_mw=3.0,
        power_ir_drop_pct=3.0,
    ))
    assert not any(
        e.level1_domain == FailureDomain.POWER and "false pass" in e.level3_signature.lower()
        for e in entries
    )


def test_combined_detections():
    entries = detect_failures("test_run", _make_metrics(
        setup_wns_ns=-0.6,
        hold_whs_ns=-0.1,
        drc_total_violations=5,
        power_ir_drop_pct=14.0,
        clock_skew_ns=0.9,
    ))
    domains = {e.level1_domain for e in entries}
    assert FailureDomain.TIMING in domains
    assert FailureDomain.DRC in domains
    assert FailureDomain.POWER in domains


def test_recommend_fixes_main_no_crash():
    """recommend_fixes_main() should not crash when files are missing."""
    import sys
    from io import StringIO
    old_out = sys.stdout
    sys.stdout = StringIO()
    try:
        recommend_fixes_main()
    finally:
        sys.stdout = old_out
