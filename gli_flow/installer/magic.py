import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from gli_flow.core.subprocess_env import safe_env
from gli_flow.installer.tool_detector import detect_magic, meets_min_version, _find_on_path
from gli_flow.installer.system import check_command, run_sudo, run, apt_package_exists


MAGIC_MIN_VERSION = "8.3.411"
MAGIC_APT_PACKAGE = "magic"
MAGIC_REPO = "https://github.com/RTimothyEdwards/magic.git"


def is_installed() -> bool:
    d = detect_magic()
    return d.exists


def installed_version() -> str:
    d = detect_magic()
    return d.version or ""


def install_linux(info) -> tuple[bool, str]:
    d = detect_magic()
    if d.exists and d.confidence.value in ("HIGH", "MEDIUM") and meets_min_version(d.version, MAGIC_MIN_VERSION):
        return (True, f"already installed ({d.version})")

    if d.exists and not meets_min_version(d.version, MAGIC_MIN_VERSION):
        print(f"  [WARN] Magic {d.version} may be too old for sky130 PDK (need >= {MAGIC_MIN_VERSION})")

    if apt_package_exists(MAGIC_APT_PACKAGE):
        if run_sudo(["apt-get", "install", "-y", MAGIC_APT_PACKAGE]):
            d2 = detect_magic()
            if d2.exists and meets_min_version(d2.version, MAGIC_MIN_VERSION):
                return (True, f"installed via apt ({d2.version})")
            if d2.exists:
                print(f"  [INFO] Built Magic {d2.version} still below recommended {MAGIC_MIN_VERSION}")
                return (True, f"installed via apt ({d2.version})")
        return (False, "apt install failed")

    print(f"  [INFO] Building Magic VLSI from source ...")
    ok = _build_from_source()
    if ok:
        return (True, "built from source")
    return (False, "magic build from source failed")


def _build_from_source() -> bool:
    build = Path(tempfile.mkdtemp(prefix="magic-build-"))
    src = build / "magic"
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", MAGIC_REPO, str(src)],
            check=True, capture_output=True, timeout=120, env=safe_env(),
        )
        log = subprocess.run(
            ["./configure", "--prefix=/usr/local"],
            capture_output=True, timeout=120, cwd=str(src), env=safe_env(),
        )
        if log.returncode != 0:
            print(f"  [WARN] magic configure failed: {log.stderr.decode()[:300]}")
            return False
        log = subprocess.run(
            ["make", f"-j{os.cpu_count() or 1}"],
            capture_output=True, timeout=600, cwd=str(src), env=safe_env(),
        )
        if log.returncode != 0:
            print(f"  [WARN] magic make failed: {log.stderr.decode()[:300]}")
            return False
        log = subprocess.run(
            ["sudo", "make", "install"],
            capture_output=True, timeout=120, cwd=str(src), env=safe_env(),
        )
        if log.returncode != 0:
            print(f"  [WARN] magic make install failed: {log.stderr.decode()[:300]}")
            return False
        d = detect_magic()
        if d.exists:
            print(f"  [INFO] Installed Magic {d.version} [{d.confidence.value}]")
            return True
        print("  [WARN] magic built but not found on PATH")
        print("  [INFO] Ensure /usr/local/bin is in your PATH")
        return False
    except Exception as e:
        print(f"  [WARN] magic build failed: {e}")
        return False
    finally:
        shutil.rmtree(str(build), ignore_errors=True)


def install_darwin() -> tuple[bool, str]:
    try:
        subprocess.run(
            ["brew", "install", "magic-vlsi"],
            check=True, capture_output=True, timeout=600, env=safe_env(),
        )
        return (True, "installed via brew")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  [INFO] Building Magic from source on macOS ...")
        ok = _build_from_source()
        if ok:
            return (True, "built from source on macOS")
        return (False, "magic installation failed on macOS")


def install(info) -> tuple[bool, str]:
    if info.is_macos:
        return install_darwin()
    return install_linux(info)
