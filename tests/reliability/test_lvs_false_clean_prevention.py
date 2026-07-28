import pytest
import subprocess
from pathlib import Path


class MockResult:
    """Simulates subprocess.CompletedProcess for testing _parse_lvs_report."""
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class TestLvsFalseCleanPrevention:
    """Verify that no condition can classify unknown state as CLEAN/PASS."""

    @pytest.fixture
    def parser(self):
        from gli_flow.backends.openroad_adapter import OpenRoadAdapter
        return OpenRoadAdapter(pdk_root="/tmp")

    def test_netgen_crash_returns_error(self, parser, tmp_path):
        """SIGABRT / non-zero exit must produce ERROR, never PASS."""
        result = MockResult(returncode=-6, stdout="Netgen banner\n", stderr="crash")
        report = tmp_path / "lvs_report.txt"
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR", f"crash should be ERROR, got {lvs.status}"
        assert not lvs.is_clean
        assert not lvs.comparison_completed
        assert "crashed" in lvs.parser_status.lower()

    def test_missing_report_returns_error(self, parser, tmp_path):
        """No report file with no stdout evidence must produce ERROR."""
        result = MockResult(returncode=0, stdout="Netgen banner\n", stderr="")
        report = tmp_path / "lvs_report.txt"
        assert not report.exists()
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR", f"missing report no evidence should be ERROR, got {lvs.status}"
        assert not lvs.is_clean
        assert not lvs.comparison_completed

    def test_empty_report_returns_error(self, parser, tmp_path):
        """Empty report file must produce ERROR."""
        result = MockResult(returncode=0, stdout="Netgen banner\n", stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR", f"empty report should be ERROR, got {lvs.status}"
        assert not lvs.is_clean

    def test_corrupt_report_returns_error(self, parser, tmp_path):
        """Report with garbage content (no device counts) must produce ERROR."""
        result = MockResult(returncode=0, stdout="Netgen banner\n", stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("garbage data\nnot a valid report\n")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR", f"corrupt report should be ERROR, got {lvs.status}"
        assert not lvs.is_clean

    def test_mismatch_report_returns_fail(self, parser, tmp_path):
        """Report showing mismatches must produce FAIL."""
        result = MockResult(returncode=0, stdout=(
            "Netgen banner\n"
            "Circuit 1 contains 10 devices, Circuit 2 contains 8 devices\n"
            "Circuit 1 contains 15 nets, Circuit 2 contains 12 nets\n"
        ), stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text(
            "Unmatched devices: 2\nUnmatched nets: 3\n"
        )
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "FAIL", f"mismatch should be FAIL, got {lvs.status}"
        assert not lvs.is_clean
        assert lvs.comparison_completed

    def test_valid_pass_returns_pass(self, parser, tmp_path):
        """Valid match evidence must produce PASS."""
        result = MockResult(returncode=0, stdout=(
            "Netgen banner\n"
            "Circuit 1 contains 10 devices, Circuit 2 contains 10 devices\n"
            "Circuit 1 contains 15 nets, Circuit 2 contains 15 nets\n"
            "Netlists match\n"
        ), stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("Netlists match\nUnmatched devices: 0\nUnmatched nets: 0\n")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "PASS", f"valid match should be PASS, got {lvs.status}"
        assert lvs.is_clean
        assert lvs.comparison_completed
        assert lvs.report_exists
        assert lvs.report_size > 0

    def test_default_values_never_produce_pass(self, parser, tmp_path):
        """All-zero default values must never produce PASS."""
        cases = [
            ("no output", MockResult(0, "", ""), tmp_path / "a.txt"),
            ("banner only", MockResult(0, "Netgen 1.5\n", ""), tmp_path / "b.txt"),
            ("warning only", MockResult(0, "Warning: test\n", ""), tmp_path / "c.txt"),
            ("reading only", MockResult(0, "Reading netlist file /x.spice\n", ""), tmp_path / "d.txt"),
        ]
        for name, mock_result, report in cases:
            lvs = parser._parse_lvs_report(str(report), mock_result, 0.1)
            assert lvs.status != "PASS", f"case '{name}' must not produce PASS, got {lvs.status}"
            assert not lvs.is_clean, f"case '{name}' must not be clean"
