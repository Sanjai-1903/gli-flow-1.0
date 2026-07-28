import json
import os
from pathlib import Path
from typing import Optional


DEFAULT_GLI_FLOW_DIR = os.path.join(os.path.expanduser("~"), ".gli-flow")
CONFIG_FILE = "config.json"


def ensure_dirs(gli_flow_dir: str = None) -> dict[str, str]:
    base = Path(gli_flow_dir or DEFAULT_GLI_FLOW_DIR)
    dirs = {
        "root": str(base),
        "orfs": str(base / "orfs"),
        "pdk": str(base / "pdk"),
        "designs": str(base / "designs"),
        "runs": str(base / "runs"),
    }
    for d in dirs.values():
        Path(d).mkdir(parents=True, exist_ok=True)
    return dirs


def load_config(gli_flow_dir: str = None) -> dict:
    config_path = Path(gli_flow_dir or DEFAULT_GLI_FLOW_DIR) / CONFIG_FILE
    if config_path.exists():
        try:
            return json.loads(config_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_config(config: dict, gli_flow_dir: str = None) -> None:
    config_path = Path(gli_flow_dir or DEFAULT_GLI_FLOW_DIR) / CONFIG_FILE
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2))


def write_default_config(
    orfs_root: str = None,
    pdk_root: str = None,
    gli_flow_dir: str = None,
) -> dict:
    dirs = ensure_dirs(gli_flow_dir)
    existing = load_config(gli_flow_dir)

    config = {
        **existing,
        "orfs_root": str(orfs_root or dirs["orfs"]),
        "pdk_root": str(pdk_root or dirs["pdk"]),
        "workspace_dir": dirs["designs"],
        "runs_dir": dirs["runs"],
    }

    save_config(config, gli_flow_dir)
    return config


def get_config_value(key: str, default: str = None) -> Optional[str]:
    config = load_config()
    return config.get(key, default)
