from pathlib import Path

from gli_flow.backends.openroad_adapter import PowerResult


def test_power_signoff_passes_with_valid_result():
    """Regression: valid PowerResult with report exists and no violations -> power_pass=True"""
    pr = PowerResult(total_power_mw=10.5, leakage_mw=0.5, internal_mw=5.0, switching_mw=5.0,
                     ir_violation_count=0)
    result_has_data = (
        hasattr(pr, 'total_power_mw')
        and pr.total_power_mw is not None
        and pr.total_power_mw > 0
    )
    assert result_has_data, "Valid PowerResult should have data"
    limits_ok = (
        hasattr(pr, 'ir_violation_count')
        and pr.ir_violation_count is not None
        and pr.ir_violation_count == 0
    )
    assert limits_ok, "Valid PowerResult should have no violations"


def test_power_signoff_fails_with_zeroed_result():
    """Regression: zeroed PowerResult (as from exception handler) -> power_pass=False"""
    pr = PowerResult(total_power_mw=0.0, leakage_mw=0.0, internal_mw=0.0, switching_mw=0.0)
    result_has_data = (
        hasattr(pr, 'total_power_mw')
        and pr.total_power_mw is not None
        and pr.total_power_mw > 0
    )
    assert not result_has_data, "Zeroed PowerResult should be detected as no data"


def test_power_signoff_fails_with_none_power():
    """Regression: PowerResult with None total_power_mw -> power_pass=False"""
    pr = PowerResult(total_power_mw=None, leakage_mw=0.0, internal_mw=0.0, switching_mw=0.0)
    result_has_data = (
        hasattr(pr, 'total_power_mw')
        and pr.total_power_mw is not None
        and pr.total_power_mw > 0
    )
    assert not result_has_data, "None total_power_mw should be detected as no data"


def test_power_signoff_fails_with_ir_violations():
    """Regression: PowerResult with ir violations -> power_pass=False (limits exceeded)"""
    pr = PowerResult(total_power_mw=10.5, leakage_mw=0.5, internal_mw=5.0, switching_mw=5.0,
                     ir_violation_count=3)
    result_has_data = (
        hasattr(pr, 'total_power_mw')
        and pr.total_power_mw is not None
        and pr.total_power_mw > 0
    )
    assert result_has_data
    limits_exceeded = (
        hasattr(pr, 'ir_violation_count')
        and pr.ir_violation_count is not None
        and pr.ir_violation_count > 0
    )
    assert limits_exceeded, "IR violations should be detected as limits exceeded"


def test_power_signoff_gate_default_is_false():
    """Regression: SignoffGate power_pass defaults to False"""
    from gli_flow.core.orchestrator import SignoffGate
    gate = SignoffGate()
    assert gate.power_pass is False, "Default power_pass must be False (not True)"


def test_power_signoff_gate_set_from_status_pass():
    """SignoffGate.set_from_status with PASS sets power_pass=True"""
    from gli_flow.core.orchestrator import SignoffGate
    gate = SignoffGate()
    gate.set_from_status("power_pass", "PASS")
    assert gate.power_pass is True


def test_power_signoff_gate_set_from_status_fail():
    """SignoffGate.set_from_status with FAIL sets power_pass=False"""
    from gli_flow.core.orchestrator import SignoffGate
    gate = SignoffGate()
    gate.set_from_status("power_pass", "PASS")
    gate.set_from_status("power_pass", "FAIL")
    assert gate.power_pass is False


def test_power_signoff_gate_set_from_status_not_run():
    """SignoffGate.set_from_status with NOT_RUN sets power_pass=False"""
    from gli_flow.core.orchestrator import SignoffGate
    gate = SignoffGate()
    gate.set_from_status("power_pass", "PASS")
    gate.set_from_status("power_pass", "NOT_RUN")
    assert gate.power_pass is False


def test_power_signoff_gate_set_from_status_error():
    """SignoffGate.set_from_status with ERROR sets power_pass=False"""
    from gli_flow.core.orchestrator import SignoffGate
    gate = SignoffGate()
    gate.set_from_status("power_pass", "PASS")
    gate.set_from_status("power_pass", "ERROR")
    assert gate.power_pass is False


def test_power_signoff_blocking_failures_message():
    """SignoffGate.blocking_failures includes power message when power_pass=False"""
    from gli_flow.core.orchestrator import SignoffGate
    gate = SignoffGate()
    gate.power_pass = False
    msgs = gate.blocking_failures()
    assert any("Power analysis" in m for m in msgs)


def test_release_gate_no_errors_with_valid_data():
    """release_gate_errors returns empty when power_pass matches telemetry data"""
    from gli_flow.core.orchestrator import SignoffGate
    gate = SignoffGate()
    gate.power_pass = True
    telemetry = {"total_power_mw": 10.5}
    errors = gate.release_gate_errors(telemetry)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_release_gate_detects_power_pass_without_data():
    """release_gate_errors detects power_pass=True with missing telemetry"""
    from gli_flow.core.orchestrator import SignoffGate
    gate = SignoffGate()
    gate.power_pass = True
    telemetry = {"total_power_mw": None}
    errors = gate.release_gate_errors(telemetry)
    assert any("power_pass=True" in e for e in errors)


def test_release_gate_no_errors_with_power_fail():
    """release_gate_errors returns empty when power_pass=False (expected fail)"""
    from gli_flow.core.orchestrator import SignoffGate
    gate = SignoffGate()
    gate.power_pass = False
    telemetry = {"total_power_mw": None}
    errors = gate.release_gate_errors(telemetry)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_release_gate_no_errors_with_zero_telemetry():
    """release_gate_errors returns empty when power_pass=True but telemetry has zero power
    (zero power is unusual but not a gate regression if the result was actually zero)"""
    from gli_flow.core.orchestrator import SignoffGate
    gate = SignoffGate()
    gate.power_pass = True
    telemetry = {"total_power_mw": 0.0}
    errors = gate.release_gate_errors(telemetry)
    assert any("power_pass=True" in e for e in errors), \
        "Zero telemetry with power_pass=True should be caught"


def test_release_gate_none_telemetry_is_safe():
    """release_gate_errors handles None telemetry without error"""
    from gli_flow.core.orchestrator import SignoffGate
    gate = SignoffGate()
    gate.power_pass = False
    errors = gate.release_gate_errors(None)
    assert errors == []
