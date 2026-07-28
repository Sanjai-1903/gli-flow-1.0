import subprocess

from gli_flow.core.subprocess_env import safe_env
from gli_flow.installer.system import check_command, run_sudo, run
from gli_flow.installer.tool_detector import detect_tool


KLAYOUT_MIN_VERSION = "0.28"


def is_installed() -> bool:
    return check_command("klayout") is not None


def installed_version() -> str:
    try:
        result = run(["klayout", "-b", "-v"])
        return result.stdout.strip() or result.stderr.strip()
    except Exception:
        return ""


def install_linux(info) -> tuple[bool, str]:
    detection = detect_tool("klayout")
    if detection.exists and detection.version:
        return (True, f"already installed ({detection.version})")

    ok, msg = _install_via_apt()
    if ok:
        return (True, msg)

    return (False, _get_recommendation())


def _install_via_apt() -> tuple[bool, str]:
    if not check_command("apt-get"):
        return (False, "apt-get not available")
    _ensure_universe()
    ok = run_sudo(["apt-get", "install", "-y", "klayout"], "Installing KLayout via apt")
    if ok:
        detection = detect_tool("klayout")
        if detection.exists:
            return (True, f"installed via apt ({detection.version})")
    return (False, "apt package 'klayout' not found in repository")


def _ensure_universe():
    try:
        result = run(["apt-cache", "policy"])
        if result.returncode == 0 and "universe" not in result.stdout:
            run_sudo(["add-apt-repository", "universe"], "Enabling universe repository")
            run_sudo(["apt-get", "update"], "Updating package lists")
    except Exception:
        pass


def _get_recommendation() -> str:
    parts = [
        "Install KLayout manually:",
        "  Enable universe repository:",
        "    sudo add-apt-repository universe",
        "    sudo apt-get update",
        "    sudo apt-get install klayout",
        "",
        "  Or download from: https://www.klayout.de/build.html",
    ]
    return "\n".join(parts)


def install_darwin() -> bool:
    try:
        subprocess.run(
            ["brew", "install", "klayout"],
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