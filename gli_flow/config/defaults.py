"""
Built-in default configuration values.

Overridden by user config → project config → environment variables.
No hardcoded paths, versions, or PDK references outside this file.
"""

import os
from pathlib import Path

_HOME = Path.home()

DEFAULTS = {
    "pdk_root": str(_HOME / ".gli-flow" / "pdk"),
    "pdk": "sky130A",
    "workspace": str(_HOME / "gli-flow-workspace"),
    "db_path": str(_HOME / ".gli-flow" / "gli_flow.db"),
    "telemetry": "on",
    "orfs_root": str(_HOME / ".gli-flow" / "orfs"),
    "log_level": "INFO",
    "log_dir": str(_HOME / ".gli-flow" / "logs"),
    "backend_port": 8000,
    "max_threads": os.cpu_count() or 4,
    "memory_limit_mb": 8192,
    "timeout_seconds": 7200,
    "docker": {
        "image": "ghcr.io/Jegadiswar-SM/gli-flow-asic:latest",
    },
    "cloud": {
        "provider": "s3",
        "bucket": "gli-flow-runs",
        "prefix": "runs",
    },
    "doctor": {
        "auto_fix": False,
    },
}
