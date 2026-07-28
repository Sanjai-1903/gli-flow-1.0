import json
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MANIFEST = (
    BASE_DIR
    / "environment"
    / "manifests"
    / "base_environment.json"
)

with open(MANIFEST) as f:
    env_manifest = json.load(f)

print("=" * 60)
print("GLI-FLOW Environment Validation")
print("=" * 60)
print()

validation_results = []

def validate_tool(tool_name, command):

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        version_output = (
            result.stdout.strip()
            or result.stderr.strip()
        )

        validation_results.append({

            "tool": tool_name,
            "status": "FOUND",
            "details": version_output
        })

        print(f"[FOUND] {tool_name}")
        print(f"         {version_output}")

    except FileNotFoundError:

        validation_results.append({

            "tool": tool_name,
            "status": "MISSING",
            "details": None
        })

        print(f"[MISSING] {tool_name}")

    print()

validate_tool(
    "Python",
    ["python3", "--version"]
)

validate_tool(
    "Docker",
    ["docker", "--version"]
)

validate_tool(
    "Git",
    ["git", "--version"]
)

validate_tool(
    "LibreLane",
    ["librelane", "--version"]
)

print("=" * 60)
print("Validation Summary")
print("=" * 60)

found = 0

for item in validation_results:

    print(
        f"{item['tool']}: "
        f"{item['status']}"
    )

    if item["status"] == "FOUND":
        found += 1

print()

print(
    f"Validated "
    f"{found}/{len(validation_results)} tools"
)

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "environment_validation_report.json"
)

with open(output, "w") as f:
    json.dump(
        validation_results,
        f,
        indent=4
    )

print()
print(f"[OUTPUT] {output}")
