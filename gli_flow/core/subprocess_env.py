import os
from pathlib import Path
from typing import Optional

def safe_env(
    extra: Optional[dict] = None,
    memory_limit_mb: Optional[int] = None,
    cpu_threads: Optional[int] = None
) -> dict:
    env = {
        **os.environ,
        "LC_ALL": "C",
        "LANG": "C",
        "LANGUAGE": "C",
        "PYTHONIOENCODING": "utf-8",
        "DISPLAY": os.environ.get("DISPLAY", ":0"),
    }

    if cpu_threads is not None:
        env["OMP_NUM_THREADS"] = str(cpu_threads)
        env["OPENBLAS_NUM_THREADS"] = str(cpu_threads)
        env["MKL_NUM_THREADS"] = str(cpu_threads)

    if extra:
        env.update(extra)

    return env
