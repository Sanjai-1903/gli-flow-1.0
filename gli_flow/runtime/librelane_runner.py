import logging
import os
import shutil
import subprocess

from gli_flow.core.subprocess_env import safe_env


class LibreLaneRunner:

    def __init__(self, design_name, run_dir, librelane_python=None):

        self.design_name = design_name
        self.run_dir = run_dir
        self.librelane_python = librelane_python

    def run(self):

        print()
        print("=" * 70)
        print("[GLI-FLOW] STARTING LIBRELANE")
        print("=" * 70)
        print()

        os.makedirs(self.run_dir, exist_ok=True)

        if self.librelane_python and os.path.isfile(self.librelane_python):
            command = [
                self.librelane_python,
                "-m",
                "librelane",
                "--version"
            ]
        else:
            librelane_path = shutil.which("librelane")
            if librelane_path:
                command = [librelane_path, "--version"]
            else:
                command = ["python3", "-m", "librelane", "--version"]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
                env=safe_env(),
            )

            if result.returncode != 0:
                status = "FAILED"
                logging.warning(
                    "librelane exited with code %d: %s",
                    result.returncode, result.stderr
                )
            else:
                status = "SUCCESS"
                print(result.stdout)

            if result.stderr:
                print(result.stderr)

            print()
            print(f"[GLI-FLOW] LIBRELANE EXECUTION {status}")
            print()

            return {
                "status": status,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except FileNotFoundError:
            logging.error("librelane executable not found")
            return {"status": "FAILED", "error": "not found"}
        except subprocess.TimeoutExpired:
            logging.error("librelane execution timed out")
            return {"status": "FAILED", "error": "timeout"}
