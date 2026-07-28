import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from gli_flow.core.subprocess_env import safe_env
from gli_flow.installer.tool_detector import detect_netgen, detect_netgenexec, detect_netgen_lib_dir, meets_min_version, _find_on_path
from gli_flow.installer.system import check_command, run_sudo, run, apt_package_exists


NETGEN_MIN_VERSION = "1.5"
NETGEN_APT_PACKAGE = "netgen-lvs"
NETGEN_REPO = "https://github.com/RTimothyEdwards/netgen.git"


def is_installed() -> bool:
    return detect_netgen().exists or detect_netgenexec() is not None


def installed_version() -> str:
    return detect_netgen().version or ""


def install_linux(info) -> tuple[bool, str]:
    d = detect_netgen()
    has_netgenexec = detect_netgenexec() is not None
    has_lib = detect_netgen_lib_dir() is not None

    if d.exists and d.confidence.value in ("HIGH", "MEDIUM") and meets_min_version(d.version, NETGEN_MIN_VERSION):
        if has_netgenexec or has_lib:
            return (True, f"already installed ({d.version})")
        print(f"  [WARN] netgen binary found but netgenexec/tclnetgen.so missing")
        print(f"  [INFO] Rebuilding from source to ensure complete installation ...")

    if apt_package_exists(NETGEN_APT_PACKAGE):
        if run_sudo(["apt-get", "install", "-y", NETGEN_APT_PACKAGE]):
            d2 = detect_netgen()
            has_exec = detect_netgenexec() is not None
            has_lib2 = detect_netgen_lib_dir() is not None
            if d2.exists and (has_exec or has_lib2):
                return (True, f"installed via apt ({d2.version})")
            print("  [WARN] apt netgen-lvs installed but netgenexec/tclnetgen.so still missing. Building from source ...")
        else:
            print("  [WARN] apt install failed, building from source ...")
    else:
        print("  [INFO] Building netgen-lvs from source ...")

    ok = _build_from_source()
    if ok:
        return (True, "built from source")
    return (False, "netgen installation failed")


def _build_from_source() -> bool:
    build = Path(tempfile.mkdtemp(prefix="netgen-build-"))
    src = build / "netgen"
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", NETGEN_REPO, str(src)],
            check=True, capture_output=True, timeout=120, env=safe_env(),
        )
        log = subprocess.run(
            ["./configure", "--prefix=/usr/local"],
            capture_output=True, timeout=120, cwd=str(src), env=safe_env(),
        )
        if log.returncode != 0:
            print(f"  [WARN] netgen configure failed: {log.stderr.decode()[:300]}")
            return False
        log = subprocess.run(
            ["make", f"-j{os.cpu_count() or 1}"],
            capture_output=True, timeout=600, cwd=str(src), env=safe_env(),
        )
        if log.returncode != 0:
            print(f"  [WARN] netgen make failed: {log.stderr.decode()[:300]}")
            return False
        log = subprocess.run(
            ["sudo", "make", "install"],
            capture_output=True, timeout=120, cwd=str(src), env=safe_env(),
        )
        if log.returncode != 0:
            print(f"  [WARN] netgen make install failed: {log.stderr.decode()[:300]}")
            return False
        has_exec = detect_netgenexec() is not None
        has_lib = detect_netgen_lib_dir() is not None
        if has_exec or has_lib:
            d = detect_netgen()
            print(f"  [INFO] Installed netgen {d.version or '?'} [{d.confidence.value}]")
            return True
        for p in ["/usr/local/bin/netgenexec", "/usr/local/bin/netgen"]:
            if os.path.exists(p):
                return True
        print("  [WARN] netgen-lvs built but netgenexec not found on PATH")
        print("  [INFO] Ensure /usr/local/bin is in your PATH")
        return False
    except Exception as e:
        print(f"  [WARN] netgen-lvs build failed: {e}")
        return False
    finally:
        shutil.rmtree(str(build), ignore_errors=True)


def install_darwin() -> tuple[bool, str]:
    try:
        subprocess.run(
            ["brew", "install", "netgen-lvs"],
            check=True, capture_output=True, timeout=600, env=safe_env(),
        )
        return (True, "installed via brew")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  [INFO] Building netgen-lvs from source on macOS ...")
        ok = _build_from_source()
        if ok:
            return (True, "built from source on macOS")
        return (False, "netgen installation failed on macOS")


def install(info) -> tuple[bool, str]:
    if info.is_macos:
        return install_darwin()
    return install_linux(info)
