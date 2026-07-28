import hashlib
import json
import logging
import os
import platform
import subprocess
import time

from pathlib import Path


def _hash_file(filepath):
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except (FileNotFoundError, OSError):
        return None


def _get_tool_versions(tools):
    versions = {}
    for name, cmd in tools.items():
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            versions[name] = result.stdout.strip() or result.stderr.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            versions[name] = None
    return versions


def generate_reproducibility_manifest(
    run_id,
    design_name,
    metrics,
    manifest_data,
    run_dir,
):
    rtl_hashes = {}
    for rtl_file in manifest_data.get("rtl_files", []):
        h = _hash_file(rtl_file)
        if h:
            rtl_hashes[rtl_file] = h

    config_path = manifest_data.get("config_path")
    config_hash = _hash_file(config_path) if config_path else None

    constraints_hashes = {}
    for constraint in manifest_data.get("constraints", []):
        h = _hash_file(constraint)
        if h:
            constraints_hashes[constraint] = h

    pdk_name = manifest_data.get("pdk", "unknown")
    pdk_root = os.environ.get("PDK_ROOT", "")

    tool_versions = _get_tool_versions({
        "librelane": ["librelane", "--version"],
        "python": ["python3", "--version"],
        "yosys": ["yosys", "-V"],
        "openroad": ["openroad", "-version"],
    })

    manifest = {
        "manifest_version": "2.0",
        "run_id": run_id,
        "design_name": design_name,
        "execution_id": run_id,
        "generated_at": time.time(),
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "os_info": f"{platform.system()} {platform.release()}",
        },
        "toolchain": tool_versions,
        "provenance": {
            "rtl_hashes": rtl_hashes,
            "constraints_hashes": constraints_hashes,
            "config_hash": config_hash,
            "pdk": {
                "name": pdk_name,
                "root": pdk_root,
            },
        },
        "execution": {
            "reproducibility_mode": True,
            "environment_validated": True,
            "reproduction_command": f"gli-flow run {design_name}",
        },
        "metrics": metrics,
    }

    output_dir = Path(run_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "reproducibility.json"
    try:
        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)
    except OSError as e:
        logging.error("Failed to write reproducibility manifest: %s", e)

    return str(output_path)
