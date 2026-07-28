import pytest
from gli_flow.analytics.qor_score import calculate_qor_score


def test_qor_perfect():
    result = calculate_qor_score(
        wns=0.0, tns=0.0, utilization=50, runtime=5, cell_count=1000,
        drc_clean=True, lvs_clean=True, signoff_complete=True,
    )
    assert result["score"] == pytest.approx(0.95, abs=0.01)
    assert result["breakdown"]["timing"] == 1.0
    assert result["breakdown"]["area"] == pytest.approx(0.75, abs=0.01)


def test_qor_wns_penalty():
    result = calculate_qor_score(wns=-0.5, tns=-2.0, utilization=50, runtime=5)
    assert 0.0 < result["score"] < 1.0
    assert result["breakdown"]["timing"] < 1.0


def test_qor_max_penalty():
    result = calculate_qor_score(wns=-5.0, tns=-100, utilization=95, runtime=9999, cell_count=100000)
    assert result["score"] > 0.0  # design quality still contributes
    assert result["breakdown"]["density"] == 0.0


def test_qor_all_none():
    result = calculate_qor_score()
    assert result["score"] == 0.0
    assert result["breakdown"]["timing"] == 0.0


def test_qor_none_vs_violated():
    none_result = calculate_qor_score()
    violated_result = calculate_qor_score(wns=-0.1, tns=-0.5)
    assert none_result["score"] == 0.0
    assert violated_result["score"] > 0.0


def test_qor_density_penalty():
    result = calculate_qor_score(cell_count=50000)
    assert result["breakdown"]["density"] == 0.0
