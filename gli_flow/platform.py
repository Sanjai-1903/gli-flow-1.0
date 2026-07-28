import os
import platform
import shutil
import sys
from pathlib import Path


def get_platform():
    system = platform.system().lower()
    if system == "linux":
        return "linux"
    elif system == "darwin":
        return "macos"
    elif system == "windows":
        if "microsoft" in platform.uname().release.lower():
            return "wsl2"
        return "windows"
    return system


def get_default_pdk_root() -> str:
    return str(Path.home() / ".gli-flow" / "pdk")


def get_tool_path(name: str) -> str:
    from gli_flow.core.tool_discovery import (
        find_openroad_binary, find_yosys_binary, find_klayout_binary,
        find_magic_binary, find_netgen_binary,
    )
    tool_map = {
        "openroad": find_openroad_binary,
        "yosys": find_yosys_binary,
        "klayout": find_klayout_binary,
        "magic": find_magic_binary,
        "netgen": find_netgen_binary,
    }
    finder = tool_map.get(name)
    if finder:
        tb = finder()
        if tb:
            return tb.path
    path = shutil.which(name)
    if path:
        return path
    return ""


def check_environment():
    result = {
        "platform": get_platform(),
        "python": sys.version,
        "pdk_root": os.environ.get("PDK_ROOT", get_default_pdk_root()),
        "orfs_root": os.environ.get("ORFS_ROOT", ""),
        "tools": {},
        "issues": [],
    }
    for tool in ("openroad", "yosys", "klayout", "magic", "netgen"):
        path = get_tool_path(tool)
        result["tools"][tool] = path
        if not path:
            result["issues"].append(f"{tool} not found in PATH")
    if not result["pdk_root"] or not Path(result["pdk_root"]).is_dir():
        result["issues"].append(f"PDK_ROOT directory not found: {result['pdk_root']}")
    return result


def to_native_path(path_str: str) -> str:
    path = Path(path_str)
    plat = get_platform()
    if plat == "wsl2" and path_str.startswith("/mnt/"):
        parts = path_str.split("/")
        drive = parts[2].upper()
        rest = "/".join(parts[3:])
        sep = "\\"
        backslash_path = rest.replace("/", sep)
        return drive + ":" + sep + backslash_path
    return str(path.resolve())
