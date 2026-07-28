import json
import logging
import logging.handlers
import os
import sys
from pathlib import Path


class _JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, default=str)


def _load_config():
    config_path = Path.home() / ".gli-flow" / "config.json"
    if config_path.exists():
        import json as _json
        return _json.loads(config_path.read_text())
    return {}


def _resolve_level(override=None):
    env_level = os.environ.get("GLI_FLOW_LOG_LEVEL", "").upper()
    if env_level in ("DEBUG", "INFO", "WARNING", "ERROR"):
        return getattr(logging, env_level)
    if override:
        override = override.upper()
        if override in ("DEBUG", "INFO", "WARNING", "ERROR"):
            return getattr(logging, override)
    config = _load_config()
    cfg_level = config.get("log_level", "").upper()
    if cfg_level in ("DEBUG", "INFO", "WARNING", "ERROR"):
        return getattr(logging, cfg_level)
    return logging.INFO


def _make_formatter(log_format):
    if log_format == "json":
        return _JsonFormatter()
    return logging.Formatter(
        "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


_initialized = False
_added_run_dirs = set()


def setup_logging(run_dir=None, level=None):
    global _initialized

    log_format = os.environ.get("GLI_FLOW_LOG_FORMAT", "text").lower()
    log_level = _resolve_level(level)
    formatter = _make_formatter(log_format)

    root = logging.getLogger()

    if not _initialized:
        root.setLevel(logging.DEBUG)
        root.handlers.clear()

        log_dir = Path.home() / ".gli-flow" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "gli-flow.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)

        _initialized = True

    if run_dir:
        resolved = Path(run_dir).resolve()
        if resolved not in _added_run_dirs:
            _added_run_dirs.add(resolved)
            run_log_dir = resolved / "logs"
            run_log_dir.mkdir(parents=True, exist_ok=True)
            run_handler = logging.handlers.RotatingFileHandler(
                run_log_dir / "run.log",
                maxBytes=10 * 1024 * 1024,
                backupCount=3,
            )
            run_handler.setLevel(logging.DEBUG)
            run_handler.setFormatter(formatter)
            root.addHandler(run_handler)


def get_logger(name):
    return logging.getLogger(name)
