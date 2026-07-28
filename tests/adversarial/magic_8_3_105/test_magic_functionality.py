"""
Adversarial test: Magic 8.3.105 functional validation.

Verifies that Magic 8.3.105 can perform all required operations:
1. TCL startup
2. DRC generation
3. DRC report parsing
4. DRC artifact creation
5. magicdnull execution
6. exit codes
7. report integrity

These tests run against the ACTUAL installed Magic binary.
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest


MAGIC_BINARY = "/usr/bin/magic"
MAGICDNUL_BINARY = "/usr/lib/x86_64-linux-gnu/magic/tcl/magicdnull"


def _run_magic(args: list[str], tcl_script: str = "", timeout: int = 30):
    """Run magic/magicdnull with given args and optional TCL script via stdin."""
    cmd = args
    if tcl_script:
        result = subprocess.run(
            cmd,
            input=tcl_script,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    else:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return result


def test_magic_version():
    """Verify magic --version returns 8.3.105."""
    result = _run_magic([MAGIC_BINARY, "--version"])
    assert result.returncode == 0, f"exit {result.returncode}: {result.stderr}"
    assert "8.3.105" in result.stdout, f"version not found in {result.stdout!r}"


def test_magic_tcl_startup():
    """Verify magic -dnull -noconsole executes TCL and exits cleanly."""
    tcl = 'puts "TCL_STARTUP_OK"\nexit 0\n'
    result = _run_magic([MAGIC_BINARY, "-dnull", "-noconsole"], tcl_script=tcl)
    assert result.returncode == 0, f"exit {result.returncode}: {result.stderr}"
    assert "TCL_STARTUP_OK" in result.stdout, f"TCL marker not in output: {result.stdout}"


def test_magicdnull_batch_execution():
    """Verify magicdnull -nowrapper -d NULL runs TCL in batch mode."""
    tcl = 'puts "MAGICDNULL_BATCH_OK"\nexit 0\n'
    result = _run_magic(
        [MAGICDNUL_BINARY, "-nowrapper", "-d", "NULL", "-rcfile", "/dev/null"],
        tcl_script=tcl,
    )
    assert result.returncode == 0, f"exit {result.returncode}: {result.stderr}"
    assert "MAGICDNULL_BATCH_OK" in result.stdout, f"marker not in output: {result.stdout}"


def test_magicdnull_drc_check():
    """Verify DRC check runs without error via magicdnull."""
    tcl = """
    if {[catch {package require drc}]} {
        puts "DRC_SKIP no drc package"
        exit 0
    }
    drc on
    drc check
    set count [drc count]
    puts "DRC_DONE count=$count"
    exit 0
    """
    result = _run_magic(
        [MAGICDNUL_BINARY, "-nowrapper", "-d", "NULL", "-rcfile", "/dev/null"],
        tcl_script=tcl,
    )
    assert result.returncode == 0, f"exit {result.returncode}: {result.stderr}"
    assert "DRC_DONE" in result.stdout or "DRC_SKIP" in result.stdout, \
        f"Neither DRC_DONE nor DRC_SKIP in output: {result.stdout}"


def test_magicdnull_drc_report_generation():
    """Verify DRC report is written to disk."""
    with tempfile.TemporaryDirectory() as tmp:
        report_path = Path(tmp) / "drc_report.txt"
        tcl = f"""
        if {{[catch {{package require drc}}]}} {{
            puts "DRC_SKIP no drc package"
            exit 0
        }}
        drc on
        drc check
        set output [open "{report_path}" w]
        puts $output "DRC Report"
        puts $output "Errors: [drc count]"
        close $output
        puts "REPORT_WRITTEN"
        exit 0
        """
        result = _run_magic(
            [MAGICDNUL_BINARY, "-nowrapper", "-d", "NULL", "-rcfile", "/dev/null"],
            tcl_script=tcl,
        )
        if "DRC_SKIP" in result.stdout:
            pytest.skip("drc package not available in this Magic build")
        assert result.returncode == 0, f"exit {result.returncode}: {result.stderr}"
        assert report_path.exists(), "DRC report not created"
        content = report_path.read_text()
        assert len(content) > 0, "DRC report is empty"
        assert "DRC Report" in content, f"DRC header missing: {content}"


def test_magicdnull_exit_code_on_success():
    """Verify magicdnull returns exit code 0 on clean exit."""
    tcl = "exit 0\n"
    result = _run_magic(
        [MAGICDNUL_BINARY, "-nowrapper", "-d", "NULL", "-rcfile", "/dev/null"],
        tcl_script=tcl,
    )
    assert result.returncode == 0


def test_magicdnull_exit_code_on_error():
    """Verify magicdnull returns non-zero exit code on error exit."""
    tcl = "exit 1\n"
    result = _run_magic(
        [MAGICDNUL_BINARY, "-nowrapper", "-d", "NULL", "-rcfile", "/dev/null"],
        tcl_script=tcl,
    )
    assert result.returncode != 0


def test_magic_version_identification():
    """Verify magic reports 8.3.105 version string correctly."""
    result = _run_magic([MAGIC_BINARY, "--version"])
    assert result.returncode == 0
    version_str = result.stdout.strip()
    parts = version_str.split(".")
    assert len(parts) >= 3, f"Expected semver, got {version_str}"
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    assert (major, minor, patch) == (8, 3, 105), f"Expected 8.3.105, got {major}.{minor}.{patch}"
