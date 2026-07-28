import os
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

from gli_flow.core.subprocess_env import safe_env
from gli_flow.installer.system import check_command, run_sudo, run, get_yosys_recommendation
from gli_flow.installer.tool_detector import detect_tool


YOSYS_MIN_VERSION = "0.27"


def is_installed() -> bool:
    return check_command("yosys") is not None


def installed_version() -> str:
    try:
        result = run(["yosys", "-V"])
        return result.stdout.strip() or result.stderr.strip()
    except Exception:
        return ""


def install_linux(info) -> tuple[bool, str]:
    detection = detect_tool("yosys")
    if detection.exists and detection.version:
        return (True, f"already installed ({detection.version})")

    ok, msg = _install_via_apt()
    if ok:
        return (True, msg)

    ok, msg = _install_via_oss_cad_suite(info)
    if ok:
        return (True, msg)

    return (False, get_yosys_recommendation())


def _install_via_apt() -> tuple[bool, str]:
    if not shutil.which("apt-get"):
        return (False, "apt-get not available")
    ok = run_sudo(["apt-get", "install", "-y", "yosys"], "Installing yosys via apt")
    if ok:
        detection = detect_tool("yosys")
        if detection.exists:
            return (True, f"installed via apt ({detection.version})")
    return (False, "apt package 'yosys' not found in repository")


def _install_via_oss_cad_suite(info) -> tuple[bool, str]:
    if info.arch not in ("amd64", "x86_64"):
        return (False, f"OSS CAD Suite not available for {info.arch}")
    if not shutil.which("wget") and not shutil.which("curl"):
        return (False, "wget or curl required for OSS CAD Suite download")
    target = Path.home() / ".gli-flow" / "tools"
    target.mkdir(parents=True, exist_ok=True)
    url = "https://github.com/YosysHQ/oss-cad-suite-build/releases/latest/download/oss-cad-suite-linux-x86_64.tgz"
    tarball = target / "oss-cad-suite-linux-x86_64.tgz"
    try:
        print("  [INFO] Downloading OSS CAD Suite (this may take a few minutes)...")
        if shutil.which("wget"):
            subprocess.run(
                ["wget", "-q", url, "-O", str(tarball)],
                check=True, timeout=300, env=safe_env(),
            )
        else:
            subprocess.run(
                ["curl", "-fsSL", "-o", str(tarball), url],
                check=True, timeout=300, env=safe_env(),
            )
        extract_dir = target / "oss-cad-suite"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        print("  [INFO] Extracting OSS CAD Suite...")
        with tarfile.open(str(tarball), "r:gz") as tf:
            tf.extractall(path=str(target))
        bin_dir = extract_dir / "bin"
        if bin_dir.exists():
            os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")
            link_target = Path.home() / ".local" / "bin"
            link_target.mkdir(parents=True, exist_ok=True)
            for tool in ("yosys", "yosys-abc", "sby", "sbycore"):
                src = bin_dir / tool
                if src.exists():
                    link = link_target / tool
                    if link.exists() or link.is_symlink():
                        link.unlink()
                    link.symlink_to(src)
        tarball.unlink()
        detection = detect_tool("yosys")
        if detection.exists:
            return (True, f"installed via OSS CAD Suite ({detection.version})")
        return (False, "OSS CAD Suite extracted but yosys not found in PATH")
    except Exception as e:
        return (False, f"OSS CAD Suite install failed: {e}")


def install_darwin() -> bool:
    try:
        subprocess.run(
            ["brew", "install", "yosys"],
            check=True, capture_output=True, timeout=600, env=safe_env(),
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install(info) -> tuple[bool, str]:
    if info.is_macos:
        ok = install_darwin()
        return (ok, "installed via brew" if ok else "brew install failed")
    return install_linux(info)