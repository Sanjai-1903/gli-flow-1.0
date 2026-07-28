"""Tests for the GLI-FLOW installer — validates tool detection, version parsing,
install report output, and failure paths."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from gli_flow.installer.tool_detector import (
    detect_tool,
    DetectionResult,
    Confidence,
    parse_version,
    meets_min_version,
)
from gli_flow.installer.validation import (
    InstallReport,
    ValidationResult,
    doctor_report,
    TOOL_MIN_VERSIONS,
)
from gli_flow.installer.system import (
    is_wsl,
    check_command,
    check_python_version,
)
from gli_flow.installer.yosys import install_linux as yosys_install
from gli_flow.installer.openroad import install_linux as openroad_install
from gli_flow.installer.klayout import install_linux as klayout_install
from gli_flow.installer.sv2v import install_linux as sv2v_install


# ─── Tool Detection Tests ─────────────────────────────────────────────


class FakeSystemInfo:
    def __init__(self, is_macos=False, arch="amd64", version="22.04"):
        self.is_macos = is_macos
        self.arch = arch
        self.version = version


def test_detect_tool_missing():
    result = detect_tool("nonexistent_tool_xyz")
    assert result.exists is False
    assert result.confidence == Confidence.UNKNOWN


def test_detect_tool_python():
    result = detect_tool("python3")
    assert result.exists is True
    assert result.version is not None


def test_check_command():
    assert check_command("python3") is not None
    assert check_command("nonexistent_tool_xyz") is None


# ─── Version Parsing Tests ─────────────────────────────────────────────


class TestParseVersion:
    def test_simple(self):
        assert parse_version("0.27") == (0, 27)

    def test_triple(self):
        assert parse_version("3.14.4") == (3, 14, 4)

    def test_with_prefix(self):
        assert parse_version("Yosys 0.33 (git sha1 abc123)") == (0, 33)

    def test_no_digits(self):
        assert parse_version("not a version") == (0,)


class TestMeetsMinVersion:
    def test_satisfied(self):
        assert meets_min_version("3.11.0", "3.9") is True

    def test_unsatisfied(self):
        assert meets_min_version("0.25", "0.27") is False

    def test_equal(self):
        assert meets_min_version("0.27", "0.27") is True

    def test_none_version(self):
        assert meets_min_version(None, "0.27") is False


# ─── Install Report Tests ──────────────────────────────────────────────


class TestInstallReport:
    def test_empty_report_is_ready(self):
        report = InstallReport()
        report.validations.append(ValidationResult(tool="python3", installed=True, version="3.11", ok=True))
        assert report.success is True

    def test_failed_makes_not_ready(self):
        report = InstallReport()
        report.failed.append("yosys")
        assert report.success is False

    def test_action_required_not_in_failed(self):
        report = InstallReport()
        report.action_required.append(("yosys", "not installed", "install it"))
        text = report.summary_text()
        assert "ACTION REQUIRED" in text
        assert "yosys" in text

    def test_summary_text_includes_pass(self):
        report = InstallReport()
        report.validations.append(ValidationResult(tool="yosys", installed=True, version="0.33", ok=True))
        text = report.summary_text()
        assert "PASS" in text
        assert "READY" in text

    def test_summary_text_includes_fail(self):
        report = InstallReport()
        report.failed.append("magic")
        report.validations.append(ValidationResult(tool="magic", installed=False, ok=False))
        text = report.summary_text()
        assert "FAIL" in text
        assert "NOT READY" in text

    def test_summary_text_includes_action_required(self):
        report = InstallReport()
        report.failed.append("yosys")
        report.action_required.append(("yosys", "not installed", "Install OSS CAD Suite"))
        text = report.summary_text()
        assert "ACTION REQUIRED" in text


# ─── Doctor Report Tests ──────────────────────────────────────────────


class TestDoctorReport:
    def test_all_pass(self):
        vals = [
            ValidationResult(tool="yosys", installed=True, version="0.33", ok=True),
            ValidationResult(tool="git", installed=True, version="2.40", ok=True),
        ]
        text = doctor_report(vals)
        assert "READY" in text

    def test_some_fail(self):
        vals = [
            ValidationResult(tool="yosys", installed=True, version="0.33", ok=True),
            ValidationResult(tool="magic", installed=False, ok=False),
        ]
        text = doctor_report(vals)
        assert "NOT READY" in text
        assert "magic" in text


# ─── WSL Detection Tests ──────────────────────────────────────────────


class TestIsWsl:
    def test_not_wsl(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert is_wsl() is False

    def test_is_wsl(self):
        with patch("builtins.open", MagicMock()) as mock:
            mock.return_value.__enter__.return_value.read.return_value = "Linux version 5.10.102.1-microsoft-standard-WSL2"
            assert is_wsl() is True

    def test_not_wsl_content(self):
        with patch("builtins.open", MagicMock()) as mock:
            mock.return_value.__enter__.return_value.read.return_value = "Linux version 6.2.0-34-generic (buildd@ubuntu)"
            assert is_wsl() is False


# ─── Installer Tool Logic Tests ───────────────────────────────────────


class TestYosysInstaller:
    def test_already_installed(self):
        info = FakeSystemInfo()
        with patch("gli_flow.installer.yosys.detect_tool") as mock_detect:
            mock_detect.return_value = DetectionResult(
                tool="yosys", exists=True, version="Yosys 0.33",
                path="/usr/bin/yosys", confidence=Confidence.HIGH,
            )
            ok, msg = yosys_install(info)
            assert ok is True
            assert "already installed" in msg

    def test_apt_fails_no_yosys(self):
        info = FakeSystemInfo()
        with patch("gli_flow.installer.yosys.detect_tool") as mock_detect:
            mock_detect.return_value = DetectionResult(tool="yosys", exists=False)
            with patch("gli_flow.installer.yosys.shutil.which", return_value="/usr/bin/apt-get"):
                with patch("gli_flow.installer.yosys.run_sudo", return_value=False):
                    ok, msg = yosys_install(info)
                    assert ok is False
                    assert "OSS CAD Suite" in msg or "apt" in msg


class TestOpenroadInstaller:
    def test_already_installed(self):
        info = FakeSystemInfo()
        with patch("gli_flow.installer.openroad.detect_tool") as mock_detect:
            mock_detect.return_value = DetectionResult(
                tool="openroad", exists=True, version="OpenROAD 2.0",
                path="/usr/bin/openroad", confidence=Confidence.HIGH,
            )
            ok, msg = openroad_install(info)
            assert ok is True
            assert "already installed" in msg


class TestKlayoutInstaller:
    def test_already_installed(self):
        info = FakeSystemInfo()
        with patch("gli_flow.installer.klayout.detect_tool") as mock_detect:
            mock_detect.return_value = DetectionResult(
                tool="klayout", exists=True, version="KLayout 0.28",
                path="/usr/bin/klayout", confidence=Confidence.HIGH,
            )
            ok, msg = klayout_install(info)
            assert ok is True
            assert "already installed" in msg

    def test_apt_fails(self):
        info = FakeSystemInfo()
        with patch("gli_flow.installer.klayout.detect_tool") as mock_detect:
            mock_detect.return_value = DetectionResult(tool="klayout", exists=False)
            with patch("gli_flow.installer.klayout.check_command", return_value="/usr/bin/apt-get"):
                with patch("gli_flow.installer.klayout.run_sudo", return_value=False):
                    ok, msg = klayout_install(info)
                    assert ok is False
                    assert "KLayout" in msg or "apt" in msg


class TestSv2vInstaller:
    def test_already_installed(self):
        info = FakeSystemInfo()
        with patch("gli_flow.installer.sv2v.detect_tool") as mock_detect:
            mock_detect.return_value = DetectionResult(
                tool="sv2v", exists=True, version="sv2v v0.0.13",
                path="/usr/bin/sv2v", confidence=Confidence.HIGH,
            )
            ok, msg = sv2v_install(info)
            assert ok is True
            assert "already installed" in msg


# ─── Tool Min Versions Tests ──────────────────────────────────────────


class TestToolMinVersions:
    def test_all_tools_have_min_version(self):
        for tool in ["yosys", "openroad", "klayout", "magic", "netgen", "sv2v"]:
            assert tool in TOOL_MIN_VERSIONS, f"{tool} missing from TOOL_MIN_VERSIONS"


# ─── Python Version Test ──────────────────────────────────────────────


def test_python_version():
    ok, ver = check_python_version()
    assert ok is True
    parts = ver.split(".")
    assert len(parts) >= 2
    assert int(parts[0]) >= 3 and int(parts[1]) >= 9
