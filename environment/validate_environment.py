import os
import shutil
import subprocess
import sys


REQUIRED_TOOLS = {
    "yosys": ["yosys", "-V"],
    "verilator": ["verilator", "--version"],
    "docker": ["docker", "--version"],
    "python3": ["python3", "--version"],
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
            return True, result.stdout.strip()

        return False, result.stderr.strip()

    except Exception as e:
        return False, str(e)


def check_tool(tool, command):
    print(f"\n[CHECK] {tool}")

    path = shutil.which(tool)

    if path is None:
        print(f"[FAIL] {tool} not found in PATH")
        return False

    print(f"[PASS] Found at: {path}")

    success, output = run_command(command)

    if success:
        print(f"[PASS] Version Check OK")
        print(output)
        return True

    print(f"[FAIL] Command execution failed")
    print(output)

    return False


def main():
    print("=" * 60)
    print("GLI-FLOW Environment Validator v1")
    print("=" * 60)

    failures = 0

    for tool, command in REQUIRED_TOOLS.items():
        success = check_tool(tool, command)

        if not success:
            failures += 1

    print("\n" + "=" * 60)

    if failures == 0:
        print("[SUCCESS] Environment validation passed")
        sys.exit(0)

    print(f"[FAILED] {failures} validation checks failed")
    sys.exit(1)


if __name__ == "__main__":
    main()
