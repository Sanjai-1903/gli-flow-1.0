"""
Hierarchical Configuration System.

Resolution order (last wins):
  1. Built-in defaults   (gli_flow/config/defaults.py)
  2. User config         (~/.gli-flow/config.yaml)
  3. Project config      (<project>/.gli-flow/config.yaml or <project>/gli_manifest.yaml)
  4. Environment vars    (GLI_FLOW_*)

Usage:
    from gli_flow.config import get_config
    cfg = get_config()
    cfg.get("pdk_root")
    cfg.get("workspace")
"""

import os
from pathlib import Path
from typing import Any, Optional

import yaml

from gli_flow.config.defaults import DEFAULTS


def _merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def load_yaml(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}


def _get_project_config(start_dir: Optional[Path] = None) -> dict:
    search = start_dir or Path.cwd()
    for candidate in [
        search / ".gli-flow" / "config.yaml",
        search / "gli_manifest.yaml",
    ]:
        if candidate.exists():
            return load_yaml(candidate)
    return {}


def _get_env_overrides() -> dict:
    mapping = {
        "GLI_FLOW_PDK_ROOT": "pdk_root",
        "GLI_FLOW_WORKSPACE": "workspace",
        "GLI_FLOW_DB_PATH": "db_path",
        "GLI_FLOW_TELEMETRY": "telemetry",
        "GLI_FLOW_ORFS_ROOT": "orfs_root",
        "GLI_FLOW_BACKEND_PORT": "backend_port",
        "GLI_FLOW_LOG_LEVEL": "log_level",
        "GLI_FLOW_LOG_DIR": "log_dir",
    }
    overrides = {}
    for env_key, config_key in mapping.items():
        value = os.environ.get(env_key)
        if value is not None:
            if value.lower() in ("true", "1", "yes"):
                value = True
            elif value.lower() in ("false", "0", "no"):
                value = False
            overrides[config_key] = value
    return overrides


def get_config(start_dir: Optional[Path] = None) -> dict:
    config = DEFAULTS.copy()
    config = _merge(config, _load_user_config())
    config = _merge(config, _get_project_config(start_dir))
    config = _merge(config, _get_env_overrides())
    return config


def _load_user_config() -> dict:
    for path in [
        Path.home() / ".gli-flow" / "config.yaml",
        Path.home() / ".gli-flow" / "config.json",
    ]:
        if path.exists():
            return load_yaml(path) if path.suffix == ".yaml" else _load_json(path)
    return {}


def _load_json(path: Path) -> dict:
    import json
    with open(path) as f:
        return json.load(f)


def save_user_config(config: dict) -> Path:
    cfg_dir = Path.home() / ".gli-flow"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    path = cfg_dir / "config.yaml"
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    # Remove legacy JSON config if present
    legacy = cfg_dir / "config.json"
    if legacy.exists():
        legacy.unlink()
    return path
