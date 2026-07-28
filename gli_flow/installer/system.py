import os
import platform
import re
import subprocess
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from gli_flow.core.subprocess_env import safe_env

APT_PACKAGE_CACHE: dict[str, bool] = {}


def apt_package_exists(package: str) -> bool:
    if package in APT_PACKAGE_CACHE:
        return APT_PACKAGE_CACHE[package]
    try:
        result = subprocess.run(
            ["apt-cache", "show", package],
            capture_output=True, text=True, timeout=30, env=safe_env(),
        )
        exists = result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        exists = True
    APT_PACKAGE_CACHE[package] = exists
    return exists


SUPPORTED_PLATFORMS = {
    "ubuntu": {"22.04", "24.04"},
    "debian": {"11", "12"},
    "darwin": set(),
}


@dataclass
class SystemInfo:
    distro: str
    version: str
    arch: str
    is_macos: bool = False
    is_linux: bool = True
    package_manager: str = "apt"
    has_sudo: bool = False
    errors: list[str] = field(default_factory=list)


def detect_platform() -> SystemInfo:
    arch_map = {"x86_64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
    raw_arch = platform.machine()
    arch = arch_map.get(raw_arch, raw_arch)
    system = platform.system()

    if system == "Darwin":
        return SystemInfo(
            distro="macos",
            version=platform.mac_ver()[0] or "unknown",
            arch=arch,
            is_macos=True,
            is_linux=False,
            package_manager="brew",
            has_sudo=False,
        )

    info = SystemInfo(distro="unknown", version="", arch=arch)

    try:
        import distro
        info.distro = distro.id().lower()
        info.version = distro.version() or ""
    except (ImportError, Exception):
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        info.distro = line.split("=", 1)[1].strip().strip('"')
                    elif line.startswith("VERSION_ID="):
                        info.version = line.split("=", 1)[1].strip().strip('"')
        except FileNotFoundError:
            info.errors.append("Cannot detect Linux distribution")

    try:
        result = subprocess.run(
            ["sudo", "-n", "true"], capture_output=True, timeout=5, env=safe_env(),
        )
        info.has_sudo = result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        info.has_sudo = os.geteuid() == 0

    return info


def check_command(name: str) -> Optional[str]:
    path = shutil.which(name)
    if path:
        return path
    extra_paths = [
        "/usr/local/bin",
        str(Path.home() / ".local" / "bin"),
        str(Path.home() / ".gli-flow" / "tools" / "bin"),
    ]
    for extra in extra_paths:
        candidate = Path(extra) / name
        if candidate.is_file() and os.access(str(candidate), os.X_OK):
            return str(candidate)
    return None


def check_tool_version(name: str, min_version: Optional[str] = None) -> Optional[str]:
    path = check_command(name)
    if not path:
        return None

    for flag in ["--version", "-version", "-v"]:
        try:
            result = subprocess.run(
                [name, flag], capture_output=True, text=True, timeout=10, env=safe_env(),
            )
            ver = (result.stdout or "").strip()
            if not ver:
                ver = (result.stderr or "").strip()
            if ver and not any(kw in ver.lower() for kw in ["error", "unknown option", "usage"]):
                return ver.split("\n")[0].strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    return None


def run_sudo(cmd: list[str], description: str = "") -> bool:
    if os.geteuid() == 0:
        full_cmd = cmd
    else:
        full_cmd = ["sudo"] + cmd
    try:
        subprocess.run(full_cmd, check=True, timeout=300, env=safe_env())
        return True
    except subprocess.CalledProcessError:
        return False


def run(cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=safe_env())


def check_python_version() -> tuple[bool, str]:
    v = platform.python_version_tuple()
    major, minor = int(v[0]), int(v[1])
    ok = major >= 3 and minor >= 9
    return ok, f"{major}.{minor}.{v[2]}"


APT_DEPS = [
    "git",
    "curl",
    "wget",
    "ca-certificates",
    "build-essential",
    "cmake",
    "python3",
    "python3-pip",
    "python3-venv",
    "pipx",
    "tcl",
    "tcl-dev",
    "tk-dev",
    "libffi-dev",
    "libssl-dev",
    "libgomp1",
    "libtcl8.6",
    "tcl-tclreadline",
    "netgen-lvs",
    "cargo",
]

APT_MAGIC_PACKAGE = "magic"

BREW_DEPS = [
    "git",
    "cmake",
    "python@3.11",
    "tcl-tk",
    "libffi",
    "openssl",
]


def is_wsl() -> bool:
    if not sys.platform.startswith("linux"):
        return False
    try:
        with open("/proc/version") as f:
            return "microsoft" in f.read().lower() or "wsl" in f.read().lower()
    except FileNotFoundError:
        return False


@dataclass
class ToolDetection:
    name: str
    exists: bool = False
    executable: Optional[str] = None
    version: Optional[str] = None
    launches: bool = False
    error: Optional[str] = None
    remediation: Optional[str] = None


def detect_tool(tool_name: str, version_flags: Optional[list[str]] = None) -> ToolDetection:
    result = ToolDetection(name=tool_name)
    exe = check_command(tool_name)
    if not exe:
        result.exists = False
        result.error = f"'{tool_name}' not found on PATH"
        return result
    result.exists = True
    result.executable = exe
    flags = version_flags or [tool_name, "--version"]
    try:
        proc = subprocess.run(
            flags,
            capture_output=True, text=True, timeout=10, env=safe_env(),
        )
        result.launches = proc.returncode == 0
        ver = (proc.stdout or proc.stderr or "").strip()
        if ver:
            result.version = ver.split("\n")[0]
        if ver and proc.returncode != 0:
            result.error = ver.split("\n")[0]
    except FileNotFoundError:
        result.error = f"'{tool_name}' executable not found despite which()"
    except subprocess.TimeoutExpired:
        result.error = f"'{tool_name}' failed to respond within 10s"
    except OSError as e:
        result.error = f"'{tool_name}' launch failed — the binary may be corrupted or incompatible"
    return result


def get_yosys_recommendation() -> str:
    parts = [
        "Install OSS CAD Suite (recommended):",
        "  wget https://github.com/YosysHQ/oss-cad-suite-build/releases/latest/download/oss-cad-suite-linux-x86_64.tgz",
        "  tar -xzf oss-cad-suite-linux-x86_64.tgz",
        "  export PATH=\"$PWD/oss-cad-suite/bin:$PATH\"",
        "  echo 'export PATH=\"$PWD/oss-cad-suite/bin:$PATH\"' >> ~/.bashrc",
        "",
        "Or install via apt (if available):",
        "  sudo apt-get install yosys",
        "",
        "Reference: https://github.com/YosysHQ/oss-cad-suite-build",
    ]
    return "\n".join(parts)


def get_openroad_recommendation() -> str:
    parts = [
        "Install OpenROAD manually:",
        "",
        "  Option 1 — Binary download:",
        "    https://github.com/The-OpenROAD-Project/OpenROAD/releases",
        "",
        "  Option 2 — Build from source:",
        "    git clone --recursive https://github.com/The-OpenROAD-Project/OpenROAD.git",
        "    cd OpenROAD && mkdir build && cd build",
        "    cmake .. -DCMAKE_BUILD_TYPE=RELEASE",
        "    make -j$(nproc) && sudo make install",
        "",
        "  Option 3 — OSS CAD Suite (includes yosys + openroad):",
        "    https://github.com/YosysHQ/oss-cad-suite-build",
    ]
    return "\n".join(parts)


def get_sv2v_recommendation() -> str:
    parts = [
        "Install sv2v via cargo:",
        "  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
        "  source $HOME/.cargo/env",
        "  cargo install sv2v",
        "",
        "Or via apt (if available):",
        "  sudo apt-get install sv2v",
        "",
        "Reference: https://github.com/zachjs/sv2v",
    ]
    return "\n".join(parts)
