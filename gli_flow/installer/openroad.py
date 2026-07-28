import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

from gli_flow.core.subprocess_env import safe_env
from gli_flow.installer.system import check_command, run_sudo, run, get_openroad_recommendation
from gli_flow.installer.tool_detector import detect_tool


OPENROAD_MIN_VERSION = "2.0"
RELEASES_API = "https://api.github.com/repos/Precision-Innovations/OpenROAD/releases?per_page=10"
SUPPORTED_UBUNTU_VERSIONS = ["20.04", "22.04", "24.04"]


def _fix_missing_libraries() -> bool:
    openroad_path = check_command("openroad")
    if not openroad_path:
        return False
    try:
        result = subprocess.run([openroad_path, "-version"], capture_output=True, timeout=10, env=safe_env())
        if result.returncode == 0:
            return True
    except Exception:
        pass
    try:
        ldd = subprocess.run(["ldd", openroad_path], capture_output=True, text=True, timeout=10, env=safe_env())
        if ldd.returncode != 0:
            return False
        fixed = False
        for line in ldd.stdout.split("\n"):
            if "not found" not in line:
                continue
            m = re.search(r"(\S+)\s+=>\s+not found", line)
            if not m:
                continue
            libname = m.group(1)
            stem = re.sub(r"[-]\d[\d.]*\.so", "", libname)
            if not stem:
                stem = libname.split("-")[0] if "-" in libname else libname
            find_cmd = ["find", "/usr/lib", "/usr/local/lib", "-name", f"{stem}*so*" if "*" not in stem else stem]
            find_proc = subprocess.run(find_cmd, capture_output=True, text=True, timeout=10, env=safe_env())
            candidates = [ln.strip() for ln in find_proc.stdout.strip().split("\n") if ln.strip()]
            if not candidates:
                continue
            found = candidates[0]
            if os.path.islink(found):
                found = os.path.realpath(found)
            target_dir = os.path.dirname(found)
            symlink = os.path.join(target_dir, libname)
            if os.path.exists(symlink):
                continue
            subprocess.run(["sudo", "ln", "-sf", found, symlink], timeout=10, env=safe_env())
            print(f"  [INFO] Symlinked {found} -> {symlink}")
            fixed = True
        return fixed
    except Exception:
        return False


def _fetch_deb_urls():
    try:
        req = urllib.request.Request(RELEASES_API, headers={"Accept": "application/json", "User-Agent": "gli-flow"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            releases = json.loads(resp.read())
        deb_map = {}
        for rel in releases:
            for asset in rel.get("assets", []):
                name = asset["name"]
                if "ubuntu" in name and name.endswith(".deb"):
                    for uv in SUPPORTED_UBUNTU_VERSIONS:
                        if f"ubuntu-{uv}" in name or f"ubuntu{uv}" in name:
                            if uv not in deb_map:
                                deb_map[uv] = asset["browser_download_url"]
        return deb_map
    except Exception:
        return {}


def is_installed() -> Optional[str]:
    return check_command("openroad")


def installed_version() -> Optional[str]:
    path = is_installed()
    if not path:
        return None
    try:
        result = run(["openroad", "-version"])
        return result.stdout.strip() or result.stderr.strip()
    except Exception:
        return None


def install_linux(info) -> tuple[bool, str]:
    detection = detect_tool("openroad")
    if detection.exists and detection.version:
        return (True, f"already installed ({detection.version})")

    if detection.exists and detection.version is None:
        print("  [INFO] OpenROAD binary found but fails to launch. Attempting library fix ...")
        if _fix_missing_libraries():
            detection = detect_tool("openroad")
            if detection.version:
                return (True, f"libraries fixed ({detection.version})")
        print("  [WARN] Could not resolve missing libraries automatically.")

    ok, msg = _install_via_apt()
    if ok:
        return (True, msg)

    ok, msg = _install_via_deb(info)
    if ok:
        return (True, msg)

    return (False, get_openroad_recommendation())


def _install_via_apt() -> tuple[bool, str]:
    if not shutil.which("apt-get"):
        return (False, "apt-get not available")
    ok = run_sudo(["apt-get", "install", "-y", "openroad"], "Installing OpenROAD via apt")
    if ok:
        detection = detect_tool("openroad")
        if detection.exists:
            return (True, f"installed via apt ({detection.version})")
    return (False, "apt package 'openroad' not found in repository")


def _install_via_deb(info) -> tuple[bool, str]:
    deb_map = _fetch_deb_urls()
    if not deb_map:
        return (False, "no OpenROAD .deb releases found on GitHub")
    ubuntu_ver = info.version
    candidates = []
    if ubuntu_ver in deb_map:
        candidates.append(ubuntu_ver)
    for preferred in ["24.04", "22.04", "20.04"]:
        if preferred in deb_map and preferred not in candidates:
            candidates.append(preferred)
    for uv in candidates:
        url = deb_map[uv]
        if _install_deb(url):
            detection = detect_tool("openroad")
            if detection.exists:
                return (True, f"installed via .deb ({detection.version})")
        return (False, f".deb for Ubuntu {uv} installed but openroad not found")
    return (False, "no compatible .deb found for this system")


def _download_deb(url: str, dest: str) -> bool:
    if shutil.which("wget"):
        try:
            result = run(["wget", "-q", url, "-O", dest])
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            pass
    if shutil.which("curl"):
        try:
            result = run(["curl", "-fsSL", "-o", dest, url])
            return result.returncode == 0
        except FileNotFoundError:
            pass
    return False


def _install_deb(url: str) -> bool:
    tmp = tempfile.mktemp(suffix=".deb")
    try:
        print("  [INFO] Downloading OpenROAD .deb ...")
        if not _download_deb(url, tmp):
            print("  [WARN] Download failed")
            return False
        _remove_conflicting_packages()
        ok = run_sudo(
            ["dpkg", "--force-overwrite", "-i", tmp],
            "Installing OpenROAD .deb",
        )
        run_sudo(["apt-get", "install", "-y", "-f"], "Fixing dependencies")
        if not ok:
            ok = run_sudo(
                ["dpkg", "--force-overwrite", "-i", tmp],
                "Retrying OpenROAD install",
            )
            run_sudo(["apt-get", "install", "-y", "-f"], "Fixing dependencies")
        return ok
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _remove_conflicting_packages():
    conflicts = ["opensta"]
    for pkg in conflicts:
        run_sudo(
            ["dpkg", "--remove", "--force-depends", pkg],
            f"Removing conflicting package {pkg}",
        )


def install_darwin() -> bool:
    try:
        subprocess.run(
            ["brew", "install", "openroad"],
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