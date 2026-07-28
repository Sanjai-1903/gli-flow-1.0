import subprocess
import os

from gli_flow.core.subprocess_env import safe_env


class LibreLaneRunner:

    def __init__(
        self,
        design_name,
        config_file,
        design_dir,
        pdk_root,
        run_dir
    ):

        self.design_name = design_name
        self.config_file = config_file
        self.design_dir = design_dir
        self.pdk_root = pdk_root
        self.run_dir = run_dir

    def run(self):

        reports_dir = os.path.join(
            self.run_dir,
            "reports"
        )

        os.makedirs(
            reports_dir,
            exist_ok=True
        )

        command = [
            "python3",
            "-m",
            "librelane",
            "--pdk-root",
            self.pdk_root,
            self.config_file
        ]

        print()
        print("===================================================")
        print("[GLI-FLOW] STARTING LIBRELANE")
        print("===================================================")

        try:
            result = subprocess.run(
                command,
                cwd=self.design_dir,
                text=True,
                capture_output=True,
                timeout=3600,
                env=safe_env(),
            )

            if result.returncode != 0:
                print("[GLI-FLOW] LIBRELANE EXECUTION FAILED")
                print(result.stderr)
            else:
                print("[GLI-FLOW] LIBRELANE EXECUTION FINISHED")

        except FileNotFoundError:
            print("[GLI-FLOW] librelane executable not found")
        except subprocess.TimeoutExpired:
            print("[GLI-FLOW] librelane execution timed out")
