from __future__ import annotations

import logging
import os
import signal
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from gli_flow.scheduler.resource import ResourceSpec
from gli_flow.core.subprocess_env import safe_env

log = logging.getLogger(__name__)


@dataclass
class WorkerResult:
    success: bool
    run_id: str
    design_name: str
    duration: float
    returncode: int
    log_file: Optional[str] = None
    error: Optional[str] = None


class LocalWorker:

    def __init__(self, name: str = "local", resource: ResourceSpec = None):
        self.name = name
        self.resource = resource or ResourceSpec()

    def run(self, design_dir: str, run_id: str = None) -> WorkerResult:
        design_path = Path(design_dir)
        design_name = design_path.name
        run_id = run_id or f"run_{int(time.time())}_{design_name}"

        env = safe_env()
        env.update(self.resource.to_env())

        if self.resource.threads > 0:
            try:
                affinity = list(range(self.resource.threads))
                env["GLI_FLOW_CPU_AFFINITY"] = ",".join(str(a) for a in affinity)
            except Exception:
                log.warning("Failed to set CPU affinity")

        start = time.time()

        try:
            log_dir = Path(design_dir) / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "scheduler.log"

            proc = subprocess.Popen(
                ["gli-flow", "run", design_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                preexec_fn=self._apply_limits if self.resource.memory_mb > 0 else None,
            )

            try:
                stdout, stderr = proc.communicate(timeout=86400)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                duration = round(time.time() - start, 2)
                with open(log_file, "w") as f:
                    f.write(stdout)
                    if stderr:
                        f.write("\n--- STDERR ---\n")
                        f.write(stderr)
                return WorkerResult(
                    success=False,
                    run_id=run_id,
                    design_name=design_name,
                    duration=duration,
                    returncode=-1,
                    log_file=str(log_file),
                    error="Timed out after 24h",
                )

            duration = round(time.time() - start, 2)
            with open(log_file, "w") as f:
                f.write(stdout)
                if stderr:
                    f.write("\n--- STDERR ---\n")
                    f.write(stderr)

            return WorkerResult(
                success=proc.returncode == 0,
                run_id=run_id,
                design_name=design_name,
                duration=duration,
                returncode=proc.returncode,
                log_file=str(log_file),
            )

        except FileNotFoundError:
            duration = round(time.time() - start, 2)
            return WorkerResult(
                success=False,
                run_id=run_id,
                design_name=design_name,
                duration=duration,
                returncode=-1,
                error="gli-flow not found in PATH",
            )

    def _apply_limits(self):
        if self.resource.memory_mb <= 0:
            return
        try:
            import resource as rsrc
            limit_bytes = self.resource.memory_mb * 1024 * 1024
            rsrc.setrlimit(rsrc.RLIMIT_AS, (limit_bytes, limit_bytes))
        except (ImportError, ValueError, rsrc.error):
            pass
