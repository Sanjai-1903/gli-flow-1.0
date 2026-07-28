import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from gli_flow.core.subprocess_env import safe_env
from gli_flow.installer.system import check_command, run


SUPPORTED_PDKS = {"sky130", "gf180mcu"}
DEFAULT_PDK_ROOT = str(Path.home() / ".gli-flow" / "pdk")
DEFAULT_SKY130_COMMIT = "bdc9412b3e468c102d01b7cf6337be06ec6e9c9a"
DEFAULT_GF180_COMMIT = "4c3cb2e0a9e6c7f8d1a2b3c4d5e6f7a8b9c0d1e2"


def volare_installed() -> bool:
    return check_command("volare") is not None


def _pip_install(pip_cmd: str) -> bool:
    for extra_flag in [[], ["--break-system-packages"]]:
        cmd = [pip_cmd, "install"] + extra_flag + ["volare"]
        try:
            print(f"  [INFO] Installing volare via {' '.join(cmd)} ...")
            subprocess.run(cmd, check=True, timeout=120, env=safe_env())
            return True
        except FileNotFoundError:
            return False
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    return False


def _pipx_install() -> bool:
    pipx_path = shutil.which("pipx")
    if not pipx_path:
        return False
    cmd = [pipx_path, "install", "volare"]
    try:
        print(f"  [INFO] Installing volare via {' '.join(cmd)} ...")
        subprocess.run(cmd, check=True, timeout=120, env=safe_env())
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def install_volare() -> bool:
    if _pip_install("pip3"):
        return True
    if _pip_install("pip"):
        return True
    if _pipx_install():
        return True
    print("  [WARN] Could not install volare via pip3, pip, or pipx")
    return False


def pdk_is_installed(pdk: str, pdk_root: str = DEFAULT_PDK_ROOT) -> bool:
    candidates = [pdk]
    if pdk == "sky130":
        candidates += ["sky130A", "sky130B"]
    for cand in candidates:
        pdk_path = Path(pdk_root) / cand
        if pdk_path.exists() and any(pdk_path.iterdir()):
            return True
    return False


def install_sky130(pdk_root: str, commit: str = DEFAULT_SKY130_COMMIT) -> bool:
    for attempt, args in [
        ("auto-detected version", ["volare", "enable", "--pdk", "sky130"]),
        (f"commit {commit}", ["volare", "enable", "--pdk", "sky130", commit]),
    ]:
        print(f"  [INFO] volare enable --pdk sky130 ({attempt}) ...")
        try:
            subprocess.run(args, check=True, timeout=600, env=safe_env(extra={"PDK_ROOT": pdk_root}))
            return True
        except subprocess.CalledProcessError:
            print(f"  [WARN] volare enable failed ({attempt})")
        except subprocess.TimeoutExpired:
            print(f"  [WARN] volare enable timed out ({attempt})")
    return False


def install_gf180mcu(pdk_root: str, commit: str = DEFAULT_GF180_COMMIT) -> bool:
    print(f"  [INFO] volare enable --pdk gf180mcu ...")
    try:
        subprocess.run(
            ["volare", "enable", "--pdk", "gf180mcu", commit],
            check=True, timeout=600, env=safe_env(extra={"PDK_ROOT": pdk_root}),
        )
        return True
    except subprocess.CalledProcessError:
        print(f"  [WARN] volare enable failed for gf180mcu")
        return False
    except subprocess.TimeoutExpired:
        print(f"  [WARN] volare enable timed out for gf180mcu")
        return False


def ensure_pdk_root(pdk_root: str) -> bool:
    path = Path(pdk_root)
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError:
        try:
            subprocess.run(
                ["sudo", "mkdir", "-p", pdk_root],
                check=True, capture_output=True, timeout=30, env=safe_env(),
            )
            subprocess.run(
                ["sudo", "chmod", "a+rwx", pdk_root],
                check=True, capture_output=True, timeout=30, env=safe_env(),
            )
            return True
        except subprocess.CalledProcessError:
            return False


def install_pdk(pdk: str, pdk_root: str = DEFAULT_PDK_ROOT, force: bool = False) -> bool:
    if not force and pdk_is_installed(pdk, pdk_root):
        return True

    if not ensure_pdk_root(pdk_root):
        return False

    if not volare_installed():
        if not install_volare():
            return False

    if pdk == "sky130":
        return install_sky130(pdk_root)
    elif pdk == "gf180mcu":
        return install_gf180mcu(pdk_root)

    return False
