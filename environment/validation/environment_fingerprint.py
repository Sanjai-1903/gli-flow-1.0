import json
import platform
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def get_command_output(command):

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        return (
            result.stdout.strip()
            or result.stderr.strip()
        )

    except (OSError, subprocess.TimeoutExpired):
        return "UNAVAILABLE"

fingerprint = {

    "generated_at": str(
        datetime.now()
    ),

    "platform": {

        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python_version": platform.python_version()
    },

    "toolchain": {

        "docker": get_command_output(
            ["docker", "--version"]
        ),

        "git": get_command_output(
            ["git", "--version"]
        ),

        "librelane": get_command_output(
            ["librelane", "--version"]
        )
    }
}

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "environment_fingerprint.json"
)

with open(output, "w") as f:
    json.dump(
        fingerprint,
        f,
        indent=4
    )

print("=" * 60)
print("GLI-FLOW Environment Fingerprint")
print("=" * 60)
print()

print(json.dumps(
    fingerprint,
    indent=4
))

print()
print(f"[OUTPUT] {output}")
