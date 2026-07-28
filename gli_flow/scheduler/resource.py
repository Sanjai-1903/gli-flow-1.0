from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResourceSpec:
    threads: int = 0
    memory_mb: int = 0

    @property
    def has_limits(self) -> bool:
        return self.threads > 0 or self.memory_mb > 0

    def to_env(self) -> dict[str, str]:
        env = {}
        if self.threads > 0:
            env["NUM_CORES"] = str(self.threads)
            env["OMP_NUM_THREADS"] = str(self.threads)
            env["MAKEFLAGS"] = f"-j{self.threads}"
        if self.memory_mb > 0:
            env["GLI_FLOW_MEMORY_MB"] = str(self.memory_mb)
        return env

    @classmethod
    def from_system(cls) -> ResourceSpec:
        cpus = os.cpu_count() or 1
        return cls(threads=max(1, cpus // 2))

    @classmethod
    def from_dict(cls, d: dict) -> ResourceSpec:
        return cls(
            threads=d.get("threads", 0),
            memory_mb=d.get("memory_mb", 0),
        )


def detect_available_cores() -> int:
    try:
        import multiprocessing
        return multiprocessing.cpu_count()
    except (ImportError, NotImplementedError):
        return 1


def detect_available_memory_mb() -> int:
    try:
        import os
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        return (pages * page_size) // (1024 * 1024)
    except (ValueError, AttributeError, KeyError):
        return 0
