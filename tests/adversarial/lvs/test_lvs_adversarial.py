import pytest
from pathlib import Path


class MockResult:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class TestLvsAdversarial:
    """Adversarial tests: no input may produce CLEAN/PASS without evidence."""

    BANNER = "Netgen 1.5.133 compiled on ...\nWarning: ...\n"

    @pytest.fixture
    def parser(self):
        from gli_flow.backends.openroad_adapter import OpenRoadAdapter
        return OpenRoadAdapter(pdk_root="/tmp")

    def test_sigabrt_crash(self, parser, tmp_path):
        """Netgen SIGABRT (rc=-6) must produce ERROR, never PASS."""
        result = MockResult(returncode=-6, stdout=self.BANNER, stderr="abort")
        report = tmp_path / "lvs_report.txt"
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR", f"SIGABRT expected ERROR, got {lvs.status}"
        assert not lvs.is_clean
        assert not lvs.comparison_completed

    def test_segfault_crash(self, parser, tmp_path):
        """Netgen segfault (rc=-11) must produce ERROR, never PASS."""
        result = MockResult(returncode=-11, stdout="", stderr="")
        report = tmp_path / "lvs_report.txt"
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR"
        assert not lvs.is_clean

    def test_timeout(self, parser, tmp_path):
        """Timeout must produce ERROR, never PASS."""
        result = MockResult(returncode=-2, stdout="", stderr="timed out")
        report = tmp_path / "lvs_report.txt"
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR"
        assert not lvs.is_clean

    def test_missing_report_no_stdout(self, parser, tmp_path):
        """No report and no stdout evidence → ERROR."""
        result = MockResult(returncode=0, stdout="", stderr="")
        report = tmp_path / "lvs_report.txt"
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR"
        assert not lvs.is_clean

    def test_empty_report(self, parser, tmp_path):
        """Empty report with only banner stdout → ERROR."""
        result = MockResult(returncode=0, stdout=self.BANNER, stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR"
        assert not lvs.is_clean

    def test_corrupt_report_garbage(self, parser, tmp_path):
        """Garbage report content → ERROR."""
        result = MockResult(returncode=0, stdout=self.BANNER, stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("\x00\x01\x02garbage\xff\xfe")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR"
        assert not lvs.is_clean

    def test_corrupt_report_no_numbers(self, parser, tmp_path):
        """Report with text but no device/net numbers → ERROR."""
        result = MockResult(returncode=0, stdout=self.BANNER, stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("Some text\nbut no device counts\n")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "ERROR"
        assert not lvs.is_clean

    def test_mismatch_report(self, parser, tmp_path):
        """Mismatch evidence → FAIL."""
        result = MockResult(returncode=0, stdout=(
            self.BANNER +
            "Circuit 1 contains 10 devices, Circuit 2 contains 8 devices\n"
            "Circuit 1 contains 15 nets, Circuit 2 contains 20 nets\n"
        ), stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("Unmatched devices: 2\nUnmatched nets: 5\n")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "FAIL"
        assert not lvs.is_clean
        assert lvs.comparison_completed

    def test_valid_pass(self, parser, tmp_path):
        """Valid match → PASS."""
        result = MockResult(returncode=0, stdout=(
            self.BANNER +
            "Circuit 1 contains 10 devices, Circuit 2 contains 10 devices\n"
            "Circuit 1 contains 15 nets, Circuit 2 contains 15 nets\n"
            "Netlists match\n"
        ), stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("Netlists match\nUnmatched devices: 0\nUnmatched nets: 0\n")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "PASS"
        assert lvs.is_clean
        assert lvs.comparison_completed
        assert lvs.report_exists
        assert lvs.report_size > 0

    def test_netlists_match_from_stdout_with_report(self, parser, tmp_path):
        """'Netlists match' in stdout with report → PASS."""
        result = MockResult(returncode=0, stdout=(
            self.BANNER +
            "Circuit 1 contains 10 devices, Circuit 2 contains 10 devices\n"
            "Netlists match\n"
        ), stderr="")
        report = tmp_path / "lvs_report.txt"
        report.write_text("Netlists match\nUnmatched devices: 0\nUnmatched nets: 0\n")
        lvs = parser._parse_lvs_report(str(report), result, 0.1)
        assert lvs.status == "PASS"
        assert lvs.comparison_completed
