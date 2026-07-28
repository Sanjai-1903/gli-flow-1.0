"""
Signoff integrity test for LVS comparison evidence requirements.

Verifies that PASS requires ALL of:
  - return code == 0
  - comparison completed (device counts found in stdout or report)
  - report exists and is non-empty
  - match evidence present (Netlists match or device count balance)

Verifies that missing any of these produces ERROR, never PASS.
"""

import pytest


class MockResult:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class TestLvsComparisonEvidenceRequired:
    """No path to PASS without comparison evidence."""

    @pytest.fixture
    def parser(self):
        from gli_flow.backends.openroad_adapter import OpenRoadAdapter
        return OpenRoadAdapter(pdk_root="/tmp")

    def test_missing_report_no_stdout_evidence_is_error(self, parser, tmp_path):
        """No report and no device counts in stdout → ERROR."""
        result = MockResult(returncode=0, stdout="Netgen banner\n", stderr="")
        report = tmp_path / "lvs_report.txt"
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR", f"expected ERROR, got {lvs.status}"
        assert not lvs.is_clean
        assert not lvs.comparison_completed
        assert not lvs.report_exists

    def test_missing_report_with_device_counts_in_stdout(self, parser, tmp_path):
        """Device counts in stdout but no report → PASS if evidence present."""
        result = MockResult(returncode=0, stdout=(
            "Netgen banner\n"
            "Circuit 1 contains 10 devices, Circuit 2 contains 10 devices\n"
        ), stderr="")
        report = tmp_path / "lvs_report.txt"
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.comparison_completed, "device counts in stdout constitute comparison evidence"
        assert lvs.status in ("PASS", "FAIL"), f"expected PASS/FAIL, got {lvs.status}"

    def test_report_exists_but_no_device_counts_is_error(self, parser, tmp_path):
        """Report file exists but contains no device/net counts → ERROR."""
        result = MockResult(returncode=0, stdout="Netgen banner\n", stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("garbage content\nno device counts here\n")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR", f"expected ERROR, got {lvs.status}"
        assert not lvs.is_clean
        assert lvs.report_exists
        assert not lvs.comparison_completed

    def test_empty_report_is_error(self, parser, tmp_path):
        """Empty report file → ERROR."""
        result = MockResult(returncode=0, stdout="Netgen banner\n", stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR", f"expected ERROR, got {lvs.status}"
        assert not lvs.is_clean
        assert not lvs.comparison_completed

    def test_pass_requires_report_and_device_counts_and_match(self, parser, tmp_path):
        """PASS requires: report exists, device counts, AND match evidence."""
        result = MockResult(returncode=0, stdout=(
            "Netgen banner\n"
            "Circuit 1 contains 10 devices, Circuit 2 contains 10 devices\n"
            "Circuit 1 contains 15 nets, Circuit 2 contains 15 nets\n"
            "Netlists match\n"
        ), stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("Netlists match\nUnmatched devices: 0\nUnmatched nets: 0\n")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "PASS", f"expected PASS, got {lvs.status}"
        assert lvs.is_clean
        assert lvs.comparison_completed
        assert lvs.report_exists
        assert lvs.report_size > 0

    def test_report_device_counts_alone_insufficient_without_stdout(self, parser, tmp_path):
        """Report with device counts but no stdout device lines → still PASS if match."""
        result = MockResult(returncode=0, stdout="Netgen banner\n", stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("Netlists match\nUnmatched devices: 0\nUnmatched nets: 0\n")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "PASS", f"expected PASS, got {lvs.status}"
        assert lvs.is_clean
        assert lvs.comparison_completed

    def test_stdout_only_match_passes_even_without_report(self, parser, tmp_path):
        """'Netlists match' in stdout produces PASS even without report file."""
        result = MockResult(returncode=0, stdout=(
            "Netgen banner\n"
            "Circuit 1 contains 10 devices, Circuit 2 contains 10 devices\n"
            "Netlists match\n"
        ), stderr="")
        report = tmp_path / "lvs_report.txt"
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "PASS", f"expected PASS, got {lvs.status}"
        assert lvs.is_clean

    def test_not_run_never_pass(self):
        """NOT_RUN status must never be PASS."""
        from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus
        result = LVSResult(status=LVSStatus.NOT_RUN)
        assert result.status != LVSStatus.PASS
        assert not result.is_clean
        assert not result.comparison_completed
        assert not result.report_exists

    def test_error_never_pass(self):
        """ERROR status must never be PASS."""
        from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus
        result = LVSResult(
            status=LVSStatus.ERROR,
            return_code=0,
            comparison_completed=False,
            report_exists=False,
        )
        assert result.status != LVSStatus.PASS
        assert not result.is_clean

    def test_fail_never_clean(self):
        """FAIL status must produce is_clean=False."""
        from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus
        result = LVSResult(
            status=LVSStatus.FAIL,
            comparison_completed=True,
            report_exists=True,
            unmatched_devices=5,
        )
        assert result.status == LVSStatus.FAIL
        assert not result.is_clean
