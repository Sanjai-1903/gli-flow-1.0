from regression.detector import detect_regression


def test_no_baseline():
    result = detect_regression({"qor_score": 0.9}, baseline_metrics=None)
    assert result["regression_detected"] is False
    assert result["alerts"] == []


def test_no_regression():
    result = detect_regression(
        {"qor_score": 0.9, "wns": 0.0, "tns": 0.0, "utilization": 50},
        baseline_metrics={"qor_score": 0.9, "wns": 0.0, "tns": 0.0, "utilization": 50},
    )
    assert result["regression_detected"] is False


def test_qor_regression():
    result = detect_regression(
        {"qor_score": 0.7, "wns": 0.0, "tns": 0.0, "utilization": 50},
        baseline_metrics={"qor_score": 0.9, "wns": 0.0, "tns": 0.0, "utilization": 50},
    )
    assert result["regression_detected"] is True
    assert any("QoR regression" in a for a in result["alerts"])


def test_wns_degradation():
    result = detect_regression(
        {"qor_score": 0.9, "wns": -0.5, "tns": 0.0, "utilization": 50},
        baseline_metrics={"qor_score": 0.9, "wns": 0.0, "tns": 0.0, "utilization": 50},
    )
    assert result["regression_detected"] is True
    assert any("WNS degraded" in a for a in result["alerts"])


def test_tns_degradation():
    result = detect_regression(
        {"qor_score": 0.9, "wns": 0.0, "tns": -5.0, "utilization": 50},
        baseline_metrics={"qor_score": 0.9, "wns": 0.0, "tns": 0.0, "utilization": 50},
    )
    assert result["regression_detected"] is True
    assert any("TNS degraded" in a for a in result["alerts"])


def test_hold_violation():
    result = detect_regression(
        {"qor_score": 0.9, "wns": 0.0, "tns": 0.0, "utilization": 50, "hold_wns": -0.1},
        baseline_metrics={"qor_score": 0.9, "wns": 0.0, "tns": 0.0, "utilization": 50},
    )
    assert result["regression_detected"] is True
    assert any("Hold violation" in a for a in result["alerts"])


def test_utilization_increase():
    result = detect_regression(
        {"qor_score": 0.9, "wns": 0.0, "tns": 0.0, "utilization": 85},
        baseline_metrics={"qor_score": 0.9, "wns": 0.0, "tns": 0.0, "utilization": 50},
    )
    assert result["regression_detected"] is True
    assert any("Utilization increased" in a for a in result["alerts"])
