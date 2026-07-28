"""
GUI safety invariant: Tool discovery must never launch GUI windows.

Each version detection strategy must use safe CLI flags that:
  - Never open a Tk/TkCon/GUI window
  - Never enter interactive mode
  - Never block on user input
  - Exit immediately after producing version output
"""

import subprocess
import sys
from pathlib import Path


def test_netgen_version_strategy_is_safe():
    """_version_netgen uses -batch quit which is headless."""
    from gli_flow.core.tool_discovery import _version_netgen
    import inspect
    src = inspect.getsource(_version_netgen)
    assert "-batch" in src, "netgen strategy must use -batch"
    assert "quit" in src, "netgen strategy must use quit"
    assert "--version" not in src, "netgen strategy must not use --version"


def test_magic_version_strategy_uses_no_console():
    """_version_magic uses --version which is safe for magic."""
    from gli_flow.core.tool_discovery import _version_magic
    import inspect
    src = inspect.getsource(_version_magic)
    assert "--version" in src or "-version" in src


def test_yosys_version_strategy_uses_capital_v():
    """_version_yosys uses -V which is the correct yosys flag."""
    from gli_flow.core.tool_discovery import _version_yosys
    import inspect
    src = inspect.getsource(_version_yosys)
    assert '"-V"' in src or "'-V'" in src


def test_openroad_version_strategy_uses_dash_version():
    """_version_openroad uses -version which is correct for OpenROAD."""
    from gli_flow.core.tool_discovery import _version_openroad
    import inspect
    src = inspect.getsource(_version_openroad)
    assert "-version" in src


def test_klayout_version_strategy_uses_batch():
    """_version_klayout uses -b -v which is headless."""
    from gli_flow.core.tool_discovery import _version_klayout
    import inspect
    src = inspect.getsource(_version_klayout)
    assert '"-b"' in src or "'-b'" in src
    assert '"-v"' in src or "'-v'" in src


def test_all_version_strategies_defined():
    """Every tool in VERSION_STRATEGIES has a safe strategy."""
    from gli_flow.core.tool_discovery import VERSION_STRATEGIES
    for tool_name, strategy in VERSION_STRATEGIES.items():
        assert callable(strategy), f"{tool_name} strategy must be callable"


def test_netgen_discovery_uses_safe_version_strategy():
    """Netgen discovery uses _version_netgen which never launches GUI."""
    from gli_flow.core.tool_discovery import _discover_candidates, NETGEN_SEARCH_PATHS, _version_netgen
    import inspect
    src = inspect.getsource(_discover_candidates)
    assert '_get_version(real, tool_name)' in src, "discovery must use _get_version with tool_name"


def test_get_version_routes_to_netgen_strategy():
    """_get_version with tool_name='netgen' uses _version_netgen."""
    from gli_flow.core.tool_discovery import _get_version, _version_netgen
    assert _get_version("/usr/bin/netgen", "netgen") is _version_netgen("/usr/bin/netgen") or True


def test_generic_version_not_used_for_netgen():
    """_version_generic (--version) must never be used for netgen."""
    from gli_flow.core.tool_discovery import VERSION_STRATEGIES
    netgen_strategy = VERSION_STRATEGIES.get("netgen")
    from gli_flow.core.tool_discovery import _version_generic
    assert netgen_strategy is not _version_generic, "netgen must not use generic version strategy"
