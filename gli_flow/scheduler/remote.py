import shlex

from dataclasses import dataclass, field
from typing import Optional

from gli_flow.core.subprocess_env import safe_env


@dataclass
class RemoteWorkerConfig:
    host: str
    port: int = 22
    user: str = ""
    key_path: str = ""
    max_concurrent: int = 1
    gli_flow_path: str = "gli-flow"
    work_dir: str = ""

    @property
    def ssh_host(self) -> str:
        if self.user:
            return f"{self.user}@{self.host}"
        return self.host


@dataclass
class RemoteWorkerResult:
    success: bool
    run_id: str
    design_name: str
    duration: float
    returncode: int = -1
    remote_log: str = ""
    error: str = ""


class RemoteWorker:

    def __init__(self, name: str, config: RemoteWorkerConfig):
        self.name = name
        self.config = config

    def _build_ssh_cmd(self, remote_cmd: str) -> list[str]:
        cmd = ["ssh", "-o", "ConnectTimeout=30", "-o", "StrictHostKeyChecking=accept-new"]
        if self.config.port != 22:
            cmd.extend(["-p", str(self.config.port)])
        if self.config.key_path:
            cmd.extend(["-i", self.config.key_path])
        cmd.append(self.config.ssh_host)
        cmd.append(remote_cmd)
        return cmd

    def run(self, design_dir: str, run_id: str = None) -> RemoteWorkerResult:
        import os
        import subprocess
        import time
        from pathlib import Path

        design_name = Path(design_dir).name
        run_id = run_id or f"run_{int(time.time())}_{design_name}"
        work_dir = self.config.work_dir or f"~/gli-flow-runs/{run_id}"

        remote_cmd = (
            f"mkdir -p {shlex.quote(work_dir)} && "
            f"rsync -aq {shlex.quote(str(design_dir))}/ {shlex.quote(work_dir)}/design/ && "
            f"cd {shlex.quote(work_dir)} && "
            f"{shlex.quote(self.config.gli_flow_path)} run {shlex.quote(work_dir + '/design')}"
        )

        cmd = self._build_ssh_cmd(remote_cmd)
        start = time.time()

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=86400,
                env=safe_env(),
            )
            duration = time.time() - start
            return RemoteWorkerResult(
                success=result.returncode == 0,
                run_id=run_id,
                design_name=design_name,
                duration=duration,
                returncode=result.returncode,
                remote_log=result.stdout + result.stderr,
            )
        except subprocess.TimeoutExpired:
            duration = time.time() - start
            return RemoteWorkerResult(
                success=False, run_id=run_id,
                design_name=design_name, duration=duration,
                error="Remote execution timed out after 24h",
            )
        except FileNotFoundError:
            duration = time.time() - start
            return RemoteWorkerResult(
                success=False, run_id=run_id,
                design_name=design_name, duration=duration,
                error="ssh not found in PATH",
            )

    def check_connection(self) -> bool:
        import subprocess
        try:
            result = subprocess.run(
                self._build_ssh_cmd("echo ok"),
                capture_output=True, text=True, timeout=30,
                env=safe_env(),
            )
            return result.returncode == 0 and "ok" in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
