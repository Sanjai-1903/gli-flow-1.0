from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from gli_flow.scheduler.resource import ResourceSpec
from gli_flow.scheduler.worker import LocalWorker, WorkerResult


class JobStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class BatchRun:
    design_dir: str
    name: str = ""
    status: JobStatus = JobStatus.PENDING
    result: Optional[WorkerResult] = None
    worker: Optional[LocalWorker] = None
    resource: Optional[ResourceSpec] = None
    error: Optional[str] = None

    def __post_init__(self):
        if not self.name:
            self.name = Path(self.design_dir).name
        if self.resource is None:
            self.resource = ResourceSpec()


class JobQueue:

    def __init__(self, max_parallel: int = 1, default_resource: ResourceSpec = None):
        self.max_parallel = max_parallel
        self.default_resource = default_resource or ResourceSpec()
        self._queue: list[BatchRun] = []
        self._running: list[BatchRun] = []
        self._done: list[BatchRun] = []
        self._lock = threading.Lock()
        self._on_progress: Optional[Callable] = None

    def add(self, design_dir: str, resource: ResourceSpec = None) -> BatchRun:
        run = BatchRun(
            design_dir=design_dir,
            resource=resource or self.default_resource,
        )
        with self._lock:
            self._queue.append(run)
        return run

    def add_many(self, design_dirs: list[str], resource: ResourceSpec = None) -> list[BatchRun]:
        return [self.add(d, resource) for d in design_dirs]

    def set_progress_callback(self, cb: Callable) -> None:
        self._on_progress = cb

    @property
    def total(self) -> int:
        return len(self._queue) + len(self._running) + len(self._done)

    @property
    def remaining(self) -> int:
        return len(self._queue) + len(self._running)

    def run_all(self) -> list[BatchRun]:
        while self._queue or self._running:
            self._dispatch()
            time.sleep(1)
        return self._done

    def _dispatch(self) -> None:
        with self._lock:
            available = self.max_parallel - len(self._running)
            if available <= 0 or not self._queue:
                return

            to_start = []
            for _ in range(min(available, len(self._queue))):
                run = self._queue.pop(0)
                run.status = JobStatus.RUNNING
                self._running.append(run)
                to_start.append(run)

        for run in to_start:
            thread = threading.Thread(target=self._execute, args=(run,), daemon=True)
            thread.start()

        self._check_done()

    def _execute(self, run: BatchRun) -> None:
        try:
            worker = LocalWorker(
                name=run.name,
                resource=run.resource or self.default_resource,
            )
            run.worker = worker
            result = worker.run(run.design_dir)
            run.result = result
            run.status = JobStatus.SUCCESS if result.success else JobStatus.FAILED
        except Exception as e:
            run.status = JobStatus.FAILED
            run.error = str(e)

        with self._lock:
            if run in self._running:
                self._running.remove(run)
            self._done.append(run)

        if self._on_progress:
            self._on_progress(run)

    def _check_done(self) -> None:
        with self._lock:
            finished = [r for r in self._running if r.status in (JobStatus.SUCCESS, JobStatus.FAILED)]
            for run in finished:
                self._running.remove(run)
                self._done.append(run)

    def cancel_all(self) -> None:
        with self._lock:
            for run in self._queue:
                run.status = JobStatus.CANCELLED
            self._queue.clear()

    def summary(self) -> dict:
        with self._lock:
            return {
                "total": self.total,
                "pending": len(self._queue),
                "running": len(self._running),
                "done": len(self._done),
                "success": sum(1 for r in self._done if r.status == JobStatus.SUCCESS),
                "failed": sum(1 for r in self._done if r.status == JobStatus.FAILED),
            }
