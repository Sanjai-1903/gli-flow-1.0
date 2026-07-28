"""
Regression test: Magic version selection.

Verifies that tool_discovery.py selects the supported Magic version
(8.3.659) over the known-broken version (8.3.105) when both exist.

This test creates a temporary bin directory with mock magic binaries
and tests the discovery logic.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _create_mock_magic(bindir: Path, version: str, name: str = "magic"):
    """Create a mock magic binary that prints the given version string."""
    path = bindir / name
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"print('Magic {version}')\n"
        "sys.exit(0)\n"
    )
    path.chmod(0o755)
    return str(path)


def _create_mock_magicdnull(bindir: Path, version: str):
    """Create a mock magicdnull binary."""
    path = bindir / "magicdnull"
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"print('Magic {version}')\n"
        "sys.exit(0)\n"
    )
    path.chmod(0o755)
    return str(path)


def _create_bash_mock(bindir: Path, version: str, name: str = "magic"):
    """Create a mock binary using /bin/sh so it works with trimmed PATH."""
    path = bindir / name
    path.write_text(
        "#!/bin/sh\n"
        f'echo "Magic {version}"\n'
        "exit 0\n"
    )
    path.chmod(0o755)
    return str(path)


def test_tool_discovery_finds_magic():
    """find_magic_binary should return a ToolInfo when magic is available."""
    from gli_flow.core.tool_discovery import find_magic_binary

    tb = find_magic_binary()
    if tb:
        assert tb.tool_name == "magic"
        assert tb.path is not None
        assert isinstance(tb.version, tuple)
    else:
        # Acceptable if no magic is installed
        pass


def test_tool_discovery_prefers_659_over_105():
    """find_magic_binary should prefer 8.3.659 when both 8.3.105 and 8.3.659 exist."""
    from gli_flow.core.tool_discovery import find_magic_binary

    with tempfile.TemporaryDirectory() as tmp:
        old_home = os.environ.get("HOME", "")
        os.environ["HOME"] = str(Path(tmp))
        try:
            # Create old version at a system path (binary name via PATH)
            system_bindir = Path(tmp) / "usr" / "bin"
            system_bindir.mkdir(parents=True)
            _create_mock_magic(system_bindir, "8.3.105", name="magic")

            # Create new version at the user-local path (matches MAGIC_SEARCH_PATHS)
            user_bindir = Path(tmp) / ".local" / "bin"
            user_bindir.mkdir(parents=True)
            _create_mock_magic(user_bindir, "8.3.659", name="magic")

            # Put system path on PATH
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = str(system_bindir) + ":" + old_path

            tb = find_magic_binary()
            assert tb is not None, "Should find a magic binary"

            # The new version (8.3.659) at the user path should be preferred
            assert tb.version >= (8, 3, 659), (
                f"Expected version >= 8.3.659, got {tb.version_str} at {tb.path}"
            )
        finally:
            os.environ["HOME"] = old_home


def test_magicdnull_prefers_659_over_105():
    """find_magicdnull_binary should prefer user-installed (8.3.659) over system (8.3.105)."""
    from gli_flow.core.tool_discovery import find_magicdnull_binary

    with tempfile.TemporaryDirectory() as tmp:
        old_path = os.environ.get("PATH", "")
        user_libdir = Path(tmp) / ".local" / "lib" / "magic" / "tcl"
        user_libdir.mkdir(parents=True)
        system_libdir = Path(tmp) / "usr" / "lib" / "x86_64-linux-gnu" / "magic" / "tcl"
        system_libdir.mkdir(parents=True)

        old_home = os.environ.get("HOME", "")
        os.environ["HOME"] = str(Path(tmp))
        try:
            # Create old system version
            old_magicdnull = system_libdir / "magicdnull"
            old_magicdnull.write_text(
                "#!/usr/bin/env python3\nimport sys\nprint('Magic 8.3 revision 105')\nsys.exit(0)\n"
            )
            old_magicdnull.chmod(0o755)

            # Create new user-installed version
            new_magicdnull = user_libdir / "magicdnull"
            new_magicdnull.write_text(
                "#!/usr/bin/env python3\nimport sys\nprint('Magic 8.3 revision 659')\nsys.exit(0)\n"
            )
            new_magicdnull.chmod(0o755)

            tb = find_magicdnull_binary()
            assert tb is not None, "Should find a magicdnull binary"
            # Should prefer user-installed 8.3.659
            assert tb.version >= (8, 3, 659), (
                f"Expected version >= 8.3.659, got {tb.version_str} at {tb.path}"
            )
        finally:
            os.environ["PATH"] = old_path
            os.environ["HOME"] = old_home


def test_tool_discovery_historical_risk():
    """is_historical_risk_version should identify 8.3.105 as historically risky."""
    from gli_flow.core.tool_discovery import is_historical_risk_version

    assert is_historical_risk_version("magic", (8, 3, 105)) is True
    assert is_historical_risk_version("magic", (8, 3, 659)) is False
    assert is_historical_risk_version("magic", (8, 3, 106)) is False
    assert is_historical_risk_version("yosys", (0, 40)) is False


def test_tool_discovery_is_broken_version_disabled():
    """is_broken_version should return False for all versions."""
    from gli_flow.core.tool_discovery import is_broken_version

    assert is_broken_version("magic", (8, 3, 105)) is False
    assert is_broken_version("magic", (8, 3, 659)) is False


def test_get_version_risk_warning():
    """get_version_risk_warning returns warning for historical risk versions."""
    from gli_flow.core.tool_discovery import get_version_risk_warning

    warn = get_version_risk_warning("magic", (8, 3, 105))
    assert warn is not None
    assert "historical risk" in warn
    assert get_version_risk_warning("magic", (8, 3, 659)) is None


def test_tool_discovery_semver_parsing():
    """_parse_semver should handle various version strings."""
    from gli_flow.core.tool_discovery import _parse_semver

    assert _parse_semver("8.3.105") == (8, 3, 105)
    assert _parse_semver("8.3.659") == (8, 3, 659)
    assert _parse_semver("1.2.3.4") == (1, 2, 3, 4)
    assert _parse_semver("v2.0-17598-ga008522d8") == (2, 0, 17598)
    assert _parse_semver("Yosys 0.40 (git sha1 ...)") == (0, 40)
    assert _parse_semver("") == (0,)
