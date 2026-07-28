import os
import re
import signal
import subprocess

from gli_flow.core.subprocess_env import safe_env

_OOM_PATTERNS = [
    re.compile(r"Killed", re.IGNORECASE),
    re.compile(r"Out of memory", re.IGNORECASE),
    re.compile(r"cannot allocate memory", re.IGNORECASE),
    re.compile(r"allocate.*fail", re.IGNORECASE),
    re.compile(r"mmap.*failed", re.IGNORECASE),
    re.compile(r"std::bad_alloc", re.IGNORECASE),
    re.compile(r"memory exhausted", re.IGNORECASE),
]

_SIGNAL_MAP = {
    -1: ("SIGHUP", 1),
    -2: ("SIGINT", 2),
    -3: ("SIGQUIT", 3),
    -6: ("SIGABRT", 6),
    -9: ("SIGKILL", 9),
    -11: ("SIGSEGV", 11),
    -15: ("SIGTERM", 15),
}


def sanitized_env(extra_env=None):
    return safe_env(extra=extra_env)


def _detect_oom(stage, result, stderr_text):
    if result.returncode == -9:
        return True
    combined = (result.stdout or "") + (result.stderr or "") + stderr_text
    for pattern in _OOM_PATTERNS:
        if pattern.search(combined):
            return True
    return False


def _detect_signal(result):
    rc = result.returncode
    if rc < 0:
        info = _SIGNAL_MAP.get(rc)
        if info:
            return info
        return (f"signal {-rc}", -rc)
    if rc > 128:
        signum = rc - 128
        signame = signal.Signals(signum).name if signum in signal.Signals.__members__.values() else f"signal {signum}"
        return (signame, signum)
    return None


def _oom_hint():
    lines = [
        "",
        "  Execution terminated due to insufficient memory.",
        "  Suggested remediation:",
        "    - Increase system RAM or swap",
        "    - Reduce design utilization (smaller die, fewer macros)",
        "    - Set --memory flag to limit concurrent processes",
        "    - Close other applications to free memory",
        "",
    ]
    return "\n".join(lines)


def run(
    cmd,
    *,
    stage=None,
    capture_output=True,
    text=True,
    timeout=None,
    cwd=None,
    extra_env=None,
    check=True,
    **kwargs,
):
    try:
        result = subprocess.run(
            cmd,
            env=safe_env(extra=extra_env),
            capture_output=capture_output,
            text=text,
            timeout=timeout,
            cwd=cwd,
            **kwargs,
        )
    except FileNotFoundError:
        raise FileNotFoundError(f"Tool not found: {cmd[0] if cmd else 'unknown'}. Install it via `gli-flow install`.")
    except subprocess.TimeoutExpired as e:
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout, output=e.output, stderr=e.stderr)

    stderr_text = result.stderr if result.stderr else ""

    if _detect_oom(stage or "unknown", result, stderr_text):
        from gli_flow.core.exceptions import StageOOMError
        raise StageOOMError(stage or "unknown")

    sig = _detect_signal(result)
    if sig:
        from gli_flow.core.exceptions import StageSignalError
        raise StageSignalError(stage or "unknown", sig[1], sig[0])

    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, output=result.stdout, stderr=result.stderr)

    return result


def format_called_process_error(e, stage=None):
    lines = []
    if stage:
        lines.append(f"  Stage '{stage}' failed (exit code {e.returncode})")
    else:
        lines.append(f"  Command failed (exit code {e.returncode})")
    if e.returncode < 0:
        sig_name = _SIGNAL_MAP.get(e.returncode, (f"signal {-e.returncode}",))[0]
        lines.append(f"  Process terminated by {sig_name}")
    if e.stderr:
        tail = e.stderr.strip().split("\n")[-10:]
        lines.append("  Last stderr lines:")
        for line in tail:
            lines.append(f"    {line}")
    if e.returncode == -9 or (e.stderr and "Killed" in e.stderr):
        lines.append(_oom_hint())
    lines.append("")
    lines.append("  To run without EDA tools, use: gli-flow run <design> --mock")
    return "\n".join(lines)
