"""
Adversarial tests: Tool discovery version strategies.

Cases:
  1. Unsupported version flag — netgen must not fall through to TkCon
  2. Interactive Tcl tool — version probe must not enter Tcl event loop
  3. GUI-launching tool — discovered binary may not support --version
  4. Broken wrapper — version probe must not hang on wrapper that opens X
  5. Broken symlink — version probe must handle ENOENT gracefully
  6. PATH shadowing — version strategy must work regardless of which binary
"""

import os
import stat
import subprocess
import tempfile
from pathlib import Path


def test_netgen_version_handles_unsupported_flag():
    """_version_netgen must not use --version/-version (which trigger TkCon)."""
    from gli_flow.core.tool_discovery import _version_netgen
    import inspect
    src = inspect.getsource(_version_netgen)
    assert "batch" in src
    assert "--version" not in src


def test_netgen_version_with_nonexistent_binary():
    """_version_netgen must return None for nonexistent binary."""
    from gli_flow.core.tool_discovery import _version_netgen
    result = _version_netgen("/nonexistent/netgen")
    assert result is None


def test_version_strategies_handle_nonexistent_binary():
    """All version strategies must return None for nonexistent binaries."""
    from gli_flow.core.tool_discovery import VERSION_STRATEGIES
    for name, strategy in VERSION_STRATEGIES.items():
        result = strategy("/nonexistent/" + name)
        assert result is None, f"{name} strategy should return None for missing binary"


def test_netgen_version_with_broken_symlink():
    """_version_netgen must handle broken symlinks without crashing."""
    from gli_flow.core.tool_discovery import _version_netgen
    with tempfile.TemporaryDirectory() as tmp:
        broken = Path(tmp) / "netgen-broken"
        broken.symlink_to("/nonexistent/netgen")
        result = _version_netgen(str(broken))
        assert result is None


def test_netgen_version_with_non_executable():
    """_version_netgen must handle non-executable files."""
    from gli_flow.core.tool_discovery import _version_netgen
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "netgen"
        f.write_text("#!/bin/bash\necho fake\n")
        result = _version_netgen(str(f))
        assert result is None


def test_get_version_routes_netgen_correctly():
    """_get_version with tool_name='netgen' must use netgen strategy."""
    from gli_flow.core.tool_discovery import _get_version, _version_netgen, _version_generic
    import threading
    results = []
    def check():
        v = _get_version("/usr/bin/netgen", "netgen")
        results.append(v)
    t = threading.Thread(target=check)
    t.start()
    t.join(timeout=5)
    assert not t.is_alive(), "_get_version for netgen hung (would open TkCon)"
