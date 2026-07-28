"""Week 4: QoR redesign — implementation, signoff, and tapeout sub-scores."""

from gli_flow.analytics.qor_score import (
    calculate_qor_score,
    calculate_implementation_score,
    calculate_signoff_score,
)


def test_implementation_score_high_with_good_util():
    score = calculate_implementation_score(utilization=30.0, cell_count=5000)
    assert score > 0.5


def test_implementation_score_low_with_bad_util():
    score = calculate_implementation_score(utilization=95.0, cell_count=50000)
    assert score < 0.5


def test_implementation_score_none():
    score = calculate_implementation_score(utilization=None, cell_count=None)
    assert score == 0.0


def test_signoff_score_high_with_clean_metrics():
    score = calculate_signoff_score(wns=0.5, tns=0.0, drc_clean=True, lvs_clean=True)
    assert score > 0.8


def test_signoff_score_penalized_by_drc():
    clean = calculate_signoff_score(wns=0.5, tns=0.0, drc_clean=True, lvs_clean=True)
    dirty = calculate_signoff_score(wns=0.5, tns=0.0, drc_clean=False, lvs_clean=True)
    assert dirty < clean


def test_signoff_score_penalized_by_lvs():
    clean = calculate_signoff_score(wns=0.5, tns=0.0, drc_clean=True, lvs_clean=True)
    dirty = calculate_signoff_score(wns=0.5, tns=0.0, drc_clean=True, lvs_clean=False)
    assert dirty < clean


def test_signoff_score_zero_on_hold_violation():
    score = calculate_signoff_score(wns=0.5, tns=0.0, drc_clean=True, lvs_clean=True, hold_wns=-0.1)
    assert score == 0.0


def test_signoff_score_none_timing():
    score = calculate_signoff_score(wns=None, tns=None, drc_clean=True, lvs_clean=True)
    assert score == 0.0


def test_qor_result_has_implementation_score():
    result = calculate_qor_score(wns=0.5, tns=0.0, utilization=30.0, cell_count=5000)
    assert "implementation_score" in result
    assert "signoff_score" in result


def test_qor_result_subscores_reasonable():
    result = calculate_qor_score(wns=0.0, tns=0.0, utilization=50.0, cell_count=10000)
    impl = result["implementation_score"]
    signoff = result["signoff_score"]
    overall = result["score"]
    assert 0.0 <= impl <= 1.0
    assert 0.0 <= signoff <= 1.0
    assert 0.0 <= overall <= 1.0
