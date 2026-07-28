import shutil
import subprocess

from gli_flow.core.subprocess_env import safe_env
from gli_flow.installer.system import check_command, run_sudo, run, get_sv2v_recommendation
from gli_flow.installer.tool_detector import detect_tool


def is_installed() -> bool:
    return check_command("sv2v") is not None


def installed_version() -> str:
    try:
        result = run(["sv2v", "--version"])
        return result.stdout.strip() or result.stderr.strip()
    except Exception:
        return ""


def install_linux(info) -> tuple[bool, str]:
    detection = detect_tool("sv2v")
    if detection.exists and detection.version:
        return (True, f"already installed ({detection.version})")

    ok, msg = _install_via_apt()
    if ok:
        return (True, msg)

    ok, msg = _install_via_cargo()
    if ok:
        return (True, msg)

    return (False, get_sv2v_recommendation())


def _install_via_apt() -> tuple[bool, str]:
    if not shutil.which("apt-get"):
        return (False, "apt-get not available")
    ok = run_sudo(["apt-get", "install", "-y", "sv2v"], "Installing sv2v via apt")
    if ok:
        detection = detect_tool("sv2v")
        if detection.exists:
            return (True, f"installed via apt ({detection.version})")
    return (False, "apt package 'sv2v' not found")


def _install_via_cargo() -> tuple[bool, str]:
    if not shutil.which("cargo"):
        cargo_ok = _install_rust()
        if not cargo_ok:
            return (False, "cargo not available and rust install failed")
    try:
        subprocess.run(
            ["cargo", "install", "sv2v"],
            check=True, capture_output=True, timeout=600, env=safe_env(),
        )
        detection = detect_tool("sv2v")
        if detection.exists:
            return (True, f"installed via cargo ({detection.version})")
        return (False, "cargo install succeeded but sv2v not found on PATH")
    except subprocess.CalledProcessError as e:
        return (False, f"cargo install failed: {e.stderr.decode()[:200] if e.stderr else str(e)}")
    except Exception as e:
        return (False, f"cargo install failed: {e}")


def _install_rust() -> bool:
    print("  [INFO] Installing Rust toolchain...")
    try:
        subprocess.run(
            ["curl", "--proto", "=https", "--tlsv1.2", "-sSf", "https://sh.rustup.rs", "-o", "/tmp/rustup.sh"],
            check=True, capture_output=True, timeout=60, env=safe_env(),
        )
        result = subprocess.run(
            ["sh", "/tmp/rustup.sh", "-y"],
            capture_output=True, timeout=120, env=safe_env(),
        )
        cargo_home = shutil.which("cargo") or str(subprocess.run(
            ["sh", "-c", "echo $HOME/.cargo/bin"], capture_output=True, text=True, timeout=5, env=safe_env(),
        ).stdout.strip())
        if cargo_home and check_command("cargo"):
            return True
        return False
    except Exception:
        return False


def install_darwin() -> bool:
    try:
        subprocess.run(
            ["brew", "install", "sv2v"],
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