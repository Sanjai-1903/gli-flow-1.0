import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from gli_flow.core.subprocess_env import safe_env
from gli_flow.installer.system import check_command


ORFS_REPO = "https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts.git"
# Use master — tracks the latest OpenROAD binary from the PPA.
ORFS_TAG = None


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = "echo"
    return env


def default_orfs_root() -> str:
    return os.path.join(os.path.expanduser("~"), ".gli-flow", "orfs")


def is_installed(orfs_root: str = None) -> bool:
    root = Path(orfs_root or default_orfs_root())
    return (root / "flow" / "Makefile").exists()


def install(orfs_root: str = None, force: bool = False) -> bool:
    root = Path(orfs_root or default_orfs_root())

    if not force and is_installed(str(root)):
        _apply_orfs_compat_patches(str(root))
        return True

    if not check_command("git"):
        return False

    if (root / ".git").exists():
        if is_installed(str(root)):
            try:
                subprocess.run(
                    ["git", "-C", str(root), "pull", "--ff-only"],
                    check=True, capture_output=True, timeout=120, env=safe_env(extra={"GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "echo"}),
                )
                _apply_orfs_compat_patches(str(root))
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass

    shutil.rmtree(str(root), ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    try:
        if ORFS_TAG:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", ORFS_TAG,
                 ORFS_REPO, str(root)],
                check=True, capture_output=True, timeout=600, env=safe_env(extra={"GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "echo"}),
            )
        else:
            subprocess.run(
                ["git", "clone", "--depth", "1", ORFS_REPO, str(root)],
                check=True, capture_output=True, timeout=600, env=safe_env(extra={"GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "echo"}),
            )

        if not is_installed(str(root)):
            return False

    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()[:200]
        print(f"  [WARN] ORFS clone failed: {stderr}")
        return False

    except subprocess.TimeoutExpired:
        print("  [WARN] ORFS clone timed out (repo is large, retry with --force)")
        return False

    _apply_orfs_compat_patches(str(root))
    return True


def _apply_orfs_compat_patches(orfs_root: str) -> None:
    patches = [
        ("flow/scripts/synth.tcl",
         "stat -hierarchy {*}$lib_args",
         "stat {*}$lib_args"),
        ("flow/scripts/synth.tcl",
         "stat -hierarchy",
         "stat"),
        ("flow/scripts/floorplan.tcl",
         "repair_timing_helper -setup -skip_last_gasp -sequence \"unbuffer,sizeup,swap,buffer,vt_swap\"",
         "repair_timing_helper -setup -skip_last_gasp"),
        ("flow/scripts/floorplan.tcl",
         "repair_timing_helper -setup -skip_last_gasp -sequence \"unbuffer,sizeup,swap,vt_swap\"",
         "repair_timing_helper -setup -skip_last_gasp"),
        ("flow/scripts/floorplan.tcl",
         "report_layer_rc\n",
         ""),
        ("flow/scripts/report_metrics.tcl",
         "  report_fmax_metric\n",
         ""),
        ("flow/scripts/global_place_skip_io.tcl",
         '} elseif { [all_pins_placed] } {\n  puts "All pins are placed. Skipping global placement without IOs"\n',
         ""),
        ("flow/scripts/global_place.tcl",
         "lappend global_placement_args -force_center_initial_place\n",
         ""),
        ("flow/scripts/cts.tcl",
         "  -repair_clock_nets]\n",
         "]\n"),
        ("flow/scripts/final_report.tcl",
         'if { [ord::openroad_gui_compiled] } {\n  gui::show "source $::env(SCRIPTS_DIR)/save_images.tcl" false\n}',
         'if { [ord::openroad_gui_compiled] } {\n  catch { gui::show "source $::env(SCRIPTS_DIR)/save_images.tcl" false }\n}'),
    ]
    for relpath, old, new in patches:
        path = Path(orfs_root) / relpath
        if not path.exists():
            continue
        try:
            text = path.read_text()
            if old in text:
                path.write_text(text.replace(old, new))
                print(f"  [INFO] Patched {relpath}")
        except OSError:
            pass


def installed_version(orfs_root: str = None) -> Optional[str]:
    root = Path(orfs_root or default_orfs_root())
    head = root / ".git" / "HEAD"
    if head.exists():
        try:
            return head.read_text().strip()
        except OSError:
            pass
    return None
