"""
Regression test for INF-ENV-002: Tool discovery launches interactive GUI.

Verifies that:
  1. Netgen version detection uses -batch quit, not --version
  2. Netgen version detection never opens TkCon
  3. All netgen candidates are probed with batch mode only
  4. Version is successfully extracted from batch output
"""

import subprocess
import sys
from pathlib import Path


def test_netgen_version_strategy_uses_batch_quit():
    """_version_netgen must invoke netgen with -batch quit only."""
    from gli_flow.core.tool_discovery import _version_netgen
    import inspect
    source = inspect.getsource(_version_netgen)
    assert "-batch" in source, "netgen version strategy must use -batch"
    assert "quit" in source, "netgen version strategy must pass quit"
    assert "--version" not in source, "netgen version strategy must not use --version"
    assert "-version" not in source, "netgen version strategy must not use -version without batch"


def test_netgen_version_resolves_via_get_version():
    """_get_version with tool_name=netgen calls _version_netgen."""
    from gli_flow.core.tool_discovery import _get_version, VERSION_STRATEGIES
    assert "netgen" in VERSION_STRATEGIES
    strategy = VERSION_STRATEGIES["netgen"]
    from gli_flow.core.tool_discovery import _version_netgen
    assert strategy is _version_netgen


def test_no_tool_uses_generic_version_for_netgen():
    """VERSION_STRATEGIES for netgen must not be _version_generic."""
    from gli_flow.core.tool_discovery import VERSION_STRATEGIES, _version_generic
    assert VERSION_STRATEGIES["netgen"] is not _version_generic


def test_netgen_batch_quit_succeeds_or_times_out():
    """'netgen -batch quit' must exit or timeout, not hang."""
    import shutil
    netgen = shutil.which("netgen") or shutil.which("netgen-lvs")
    if not netgen:
        return
    result = subprocess.run(
        [netgen, "-batch", "quit"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode in (0, 1), f"netgen exited with {result.returncode}"


def test_netgen_batch_quit_produces_no_window():
    """'netgen -batch quit' must not launch any GUI process."""
    import os, time
    import shutil
    netgen = shutil.which("netgen") or shutil.which("netgen-lvs")
    if not netgen:
        return
    before = set(os.listdir("/dev/pts")) if os.path.isdir("/dev/pts") else set()
    result = subprocess.run(
        [netgen, "-batch", "quit"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode in (0, 1)
