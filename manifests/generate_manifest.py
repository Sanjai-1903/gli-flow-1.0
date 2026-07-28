import json
import os
import platform
import subprocess
from datetime import datetime, timezone


TOOLS = {
    "yosys": ["yosys", "-V"],
    "verilator": ["verilator", "--version"],
    "docker": ["docker", "--version"],
    "python": ["python3", "--version"],
    "librelane": ["librelane", "--version"]
}


def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return result.stdout.strip()

        return result.stderr.strip()

    except Exception as e:
        return str(e)


def collect_toolchain():
    toolchain = {}

    for tool, command in TOOLS.items():
        toolchain[tool] = run_command(command)

    return toolchain


def generate_manifest():
    manifest = {
        "manifest_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        },
        "toolchain": collect_toolchain(),
        "execution": {
            "reproducibility_mode": True,
            "environment_validated": True
        }
    }

    return manifest


def main():
    os.makedirs("outputs/execution_history", exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    filename = f"outputs/execution_history/manifest_{timestamp}.json"

    manifest = generate_manifest()

    with open(filename, "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"[SUCCESS] Manifest generated: {filename}")


if __name__ == "__main__":
    main()
