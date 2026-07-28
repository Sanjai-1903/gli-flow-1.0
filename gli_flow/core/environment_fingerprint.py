"""
Environment Fingerprinting.

Every run must capture:
  GLI version, Git commit, OS, Kernel, CPU, RAM,
  Docker version, Magic version, Netgen version, OpenROAD version,
  OpenSTA version, Yosys version, PDK version, PDK hash

Stored as run_environment.json and persisted to telemetry database.
Failure Atlas entries must reference environment fingerprints.
"""

import json
import logging
import os
import platform
import re
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

from gli_flow.core.subprocess_env import safe_env
from gli_flow.version import VERSION

log = logging.getLogger(__name__)


@dataclass
class EnvironmentFingerprint:
    gli_version: str = ""
    git_commit: str = ""
    git_branch: str = ""
    os_name: str = ""
    os_version: str = ""
    kernel: str = ""
    cpu_model: str = ""
    cpu_count: int = 0
    ram_total_gb: float = 0.0
    ram_available_gb: float = 0.0
    docker_version: str = ""
    magic_version: str = ""
    netgen_version: str = ""
    openroad_version: str = ""
    opensta_version: str = ""
    yosys_version: str = ""
    klayout_version: str = ""
    sv2v_version: str = ""
    pdk_name: str = ""
    pdk_version: str = ""
    pdk_hash: str = ""
    python_version: str = ""
    timestamp: str = ""
    fingerprint_id: str = ""
    tool_discovery_duration_ms: float = 0.0
    tool_discovery_timeout: bool = False
    tool_discovery_fallback_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


def _run_cmd(args: list[str], timeout: int = 5) -> Optional[str]:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=safe_env())
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def _get_tool_version(tool_name: str, args: list[str]) -> str:
    out = _run_cmd(args)
    if out:
        m = re.search(r"(\d+\.\d+(?:\.\d+)?)", out)
        if m:
            return m.group(0)
    return ""


def _get_git_info() -> tuple[str, str]:
    commit = _run_cmd(["git", "rev-parse", "HEAD"]) or ""
    branch = _run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or ""
    return commit, branch


def _get_cpu_info() -> tuple[str, int]:
    cpu_model = ""
    cpu_count = 0
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name") and not cpu_model:
                    cpu_model = line.split(":", 1)[1].strip()
                if line.startswith("processor"):
                    cpu_count += 1
    except OSError:
        cpu_model = platform.processor() or ""
        cpu_count = os.cpu_count() or 0
    return cpu_model, cpu_count


def _get_ram_info() -> tuple[float, float]:
    try:
        with open("/proc/meminfo") as f:
            data = f.read()
        total_match = re.search(r"MemTotal:\s+(\d+)", data)
        avail_match = re.search(r"MemAvailable:\s+(\d+)", data)
        total_kb = int(total_match.group(1)) if total_match else 0
        avail_kb = int(avail_match.group(1)) if avail_match else 0
        return round(total_kb / 1024 / 1024, 1), round(avail_kb / 1024 / 1024, 1)
    except (OSError, AttributeError):
        return 0.0, 0.0


def _get_docker_version() -> str:
    return _get_tool_version("docker", ["docker", "--version"])


def capture_fingerprint(
    pdk_name: str = "",
    pdk_version: str = "",
    pdk_hash: str = "",
) -> EnvironmentFingerprint:
    commit, branch = _get_git_info()
    cpu_model, cpu_count = _get_cpu_info()
    ram_total, ram_avail = _get_ram_info()

    from gli_flow.core.tool_discovery import get_discovery_telemetry, reset_discovery_telemetry
    dt = get_discovery_telemetry()
    reset_discovery_telemetry()

    fp = EnvironmentFingerprint(
        gli_version=VERSION,
        git_commit=commit,
        git_branch=branch,
        os_name=platform.system(),
        os_version=platform.release(),
        kernel=platform.version(),
        cpu_model=cpu_model,
        cpu_count=cpu_count,
        ram_total_gb=ram_total,
        ram_available_gb=ram_avail,
        docker_version=_get_docker_version(),
        magic_version=_get_tool_version("magic", ["magic", "--version"]),
        netgen_version=_get_tool_version("netgen", ["netgen", "-batch", "quit"]),
        openroad_version=_get_tool_version("openroad", ["openroad", "-version"]),
        opensta_version=_get_tool_version("sta", ["sta", "-version"]),
        yosys_version=_get_tool_version("yosys", ["yosys", "-V"]),
        klayout_version=_get_tool_version("klayout", ["klayout", "-b", "-v"]),
        sv2v_version=_get_tool_version("sv2v", ["sv2v", "--version"]),
        pdk_name=pdk_name,
        pdk_version=pdk_version,
        pdk_hash=pdk_hash,
        python_version=platform.python_version(),
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
        tool_discovery_duration_ms=dt["total_duration_ms"],
        tool_discovery_timeout=dt["timeout_occurred"],
        tool_discovery_fallback_count=dt["fallback_count"],
    )

    return fp


def save_fingerprint(run_dir: str, fingerprint: EnvironmentFingerprint) -> str:
    path = Path(run_dir) / "run_environment.json"
    path.write_text(fingerprint.to_json())
    log.info(f"Environment fingerprint saved to {path}")
    return str(path)


def load_fingerprint(run_dir: str) -> Optional[EnvironmentFingerprint]:
    path = Path(run_dir) / "run_environment.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return EnvironmentFingerprint(**data)
    except (json.JSONDecodeError, OSError, TypeError) as e:
        log.warning(f"Failed to load environment fingerprint: {e}")
        return None
