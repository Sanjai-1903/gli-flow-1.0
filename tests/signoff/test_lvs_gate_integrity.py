import pytest


class TestLvsGateIntegrity:
    """Signoff gate must only approve verified LVS results."""

    def test_lvs_pass_requires_comparison_completed(self):
        """lvs_pass must be False when comparison was not completed."""
        from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus

        result = LVSResult(
            status=LVSStatus.ERROR,
            comparison_completed=False,
            report_exists=False,
        )
        assert not result.comparison_completed
        assert result.status != LVSStatus.PASS

    def test_lvs_pass_requires_report_exists(self):
        """lvs_pass must be False when no report file exists."""
        from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus

        result = LVSResult(
            status=LVSStatus.PASS,
            comparison_completed=True,
            report_exists=False,
        )
        assert not result.report_exists
        assert result.status == LVSStatus.PASS

    def test_error_status_not_clean(self):
        """ERROR status must never be is_clean."""
        from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus

        result = LVSResult(
            status=LVSStatus.ERROR,
            return_code=-6,
            comparison_completed=False,
            report_exists=False,
        )
        assert not result.is_clean

    def test_not_run_status_not_clean(self):
        """NOT_RUN status must never be is_clean."""
        from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus

        result = LVSResult(status=LVSStatus.NOT_RUN)
        assert not result.is_clean

    def test_pass_requires_all_conditions(self):
        """PASS must require: rc==0, report exists, comparison completed, match evidence."""
        from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus

        valid = LVSResult(
            status=LVSStatus.PASS,
            return_code=0,
            report_exists=True,
            report_size=100,
            comparison_completed=True,
            is_clean=True,
        )
        assert valid.status == LVSStatus.PASS
        assert valid.return_code == 0
        assert valid.report_exists
        assert valid.report_size > 0
        assert valid.comparison_completed
        assert valid.is_clean

    def test_fail_status_produces_is_clean_false(self):
        """FAIL status must produce is_clean=False."""
        from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus

        result = LVSResult(
            status=LVSStatus.FAIL,
            unmatched_devices=5,
            unmatched_nets=3,
            comparison_completed=True,
            report_exists=True,
        )
        assert not result.is_clean
        assert result.unmatched_devices > 0

    def test_signoff_gate_rejects_error(self):
        """SignoffGate must not approve ERROR status."""
        from gli_flow.core.orchestrator import SignoffGate
        gate = SignoffGate()
        assert not gate.lvs_pass
        assert "LVS" in " ".join(gate.blocking_failures())
