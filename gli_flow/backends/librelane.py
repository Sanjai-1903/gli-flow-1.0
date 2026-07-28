import json
import os
import shutil
import subprocess
import time

from pathlib import Path

from gli_flow.core.subprocess_env import safe_env


class LibreLaneAdapter:

    def __init__(self, pdk_root=None):
        self.pdk_root = pdk_root or os.environ.get("PDK_ROOT")

    def validate_environment(self):
        issues = []

        if shutil.which("librelane") is None:
            try:
                subprocess.run(
                    ["python3", "-m", "librelane", "--version"],
                    capture_output=True, text=True, timeout=10,
                    env=safe_env(),
                )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                issues.append("LibreLane not available (tried librelane and python3 -m librelane)")

            if not self.pdk_root:
                if shutil.which("librelane") is None:
                    issues.append("PDK_ROOT not set and librelane not in PATH")

        if self.pdk_root and not Path(self.pdk_root).is_dir():
            issues.append(f"PDK root directory not found: {self.pdk_root}")

        return issues

    def generate_config(self, manifest, run_dir):
        config = {
            "design_name": manifest.get("design_name", "unnamed"),
            "rtl_files": manifest.get("rtl_files", []),
            "top_module": manifest.get("top_module", "top"),
            "pdk": manifest.get("pdk", "sky130A"),
            "clock_port": manifest.get("clock_port", "clk"),
            "clock_period_ns": manifest.get("clock_period_ns", 10.0),
            "constraints": manifest.get("constraints", []),
        }

        config_path = Path(run_dir) / "config.json"
        try:
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
        except OSError as e:
            return {"success": False, "error": f"Failed to write config: {e}"}

        return {"success": True, "config_path": config_path}

    def run_packaging(self, run_dir, design_name, pdk, **kwargs):
        return self.run(
            config_path=str(Path(run_dir) / "config.json"),
            design_dir=run_dir,
            run_dir=run_dir,
            **kwargs,
        )

    def run(self, config_path, design_dir, run_dir, timeout=3600, **kwargs):
        reports_dir = Path(run_dir) / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        logs_dir = Path(run_dir) / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        log_file = logs_dir / "librelane.log"

        command = self._build_command(config_path)

        if command is None:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Cannot form a valid command: LibreLane not found and PDK_ROOT not set",
                "duration": 0,
                "log_file": str(log_file),
                "reports_dir": str(reports_dir),
                "output_dir": str(run_dir),
                "error": "LibreLane not available and PDK_ROOT not set",
            }

        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                cwd=str(design_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=safe_env(),
            )

            with open(log_file, "w") as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\n--- STDERR ---\n")
                    f.write(result.stderr)

            duration = round(time.time() - start_time, 2)

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration,
                "log_file": str(log_file),
                "reports_dir": str(reports_dir),
                "output_dir": str(run_dir),
            }

        except FileNotFoundError:
            duration = round(time.time() - start_time, 2)
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "LibreLane executable not found",
                "duration": duration,
                "log_file": str(log_file),
                "reports_dir": str(reports_dir),
                "output_dir": str(run_dir),
                "error": "LibreLane executable not found",
            }

        except subprocess.TimeoutExpired:
            duration = round(time.time() - start_time, 2)
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"LibreLane execution timed out after {timeout}s",
                "duration": duration,
                "log_file": str(log_file),
                "reports_dir": str(reports_dir),
                "output_dir": str(run_dir),
                "error": f"Timed out after {timeout}s",
            }

    def _build_command(self, config_path):
        if shutil.which("librelane") is not None:
            return ["librelane", str(config_path)]

        if self.pdk_root is not None:
            return [
                "python3", "-m", "librelane",
                "--pdk-root", str(self.pdk_root),
                str(config_path),
            ]

        try:
            subprocess.run(
                ["python3", "-m", "librelane", "--version"],
                capture_output=True, text=True, timeout=10,
                env=safe_env(),
            )
            return ["python3", "-m", "librelane", str(config_path)]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return None
