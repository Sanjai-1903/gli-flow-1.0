#!/usr/bin/env python3
"""
GLI-Flow automation for the 4×4 Systolic MAC Array.
Run:  python3 run_systolic.py

This script drives the full RTL→GDSII flow through the gli-flow orchestrator.
For custom ORFS or PDK paths, set environment variables:
  export ORFS_ROOT=/path/to/openroad-flow-scripts
  export PDK_ROOT=/path/to/pdk
"""

import os
import sys
import subprocess
from pathlib import Path

DESIGN_DIR = Path(__file__).resolve().parent
RTL_DIR = DESIGN_DIR / "rtl"
CONSTRAINTS_DIR = DESIGN_DIR / "constraints"
PROJECT_ROOT = DESIGN_DIR.parent.parent  # gli-flow/


def check_prerequisites():
    """Verify all tools and PDK are available before launching the flow."""
    checks = {
        "yosys": subprocess.run(["yosys", "-V"], capture_output=True, text=True),
        "openroad": subprocess.run(["openroad", "-version"], capture_output=True, text=True),
        "klayout": subprocess.run(["klayout", "-b", "-v"], capture_output=True, text=True),
    }
    all_ok = True
    for name, result in checks.items():
        if result.returncode != 0:
            print(f"  [FAIL] {name} not found")
            all_ok = False
        else:
            ver = result.stdout.strip().split("\n")[0][:60]
            print(f"  [OK]   {name}: {ver}")

    if not all_ok:
        print("\nRun 'gli-flow install' to install missing tools.\n")
        sys.exit(1)


def check_rtl():
    """Quick syntax check with yosys."""
    rtl_files = sorted(RTL_DIR.glob("*.sv"))
    if not rtl_files:
        print("  [FAIL] No RTL files found in rtl/")
        sys.exit(1)

    synth_script = "; ".join([
        f"read_verilog -sv {' '.join(str(f) for f in rtl_files)}",
        "hierarchy -check -top systolic_array_4x4",
        "synth -noalumacc",
    ])
    result = subprocess.run(
        ["yosys", "-p", synth_script],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("  [FAIL] RTL syntax check:")
        print(result.stderr[:1000])
        sys.exit(1)
    print("  [OK]   RTL syntax check passed")


def run_flow():
    """Invoke gli-flow run with appropriate resource settings."""
    cmd = [
        "gli-flow", "run",
        str(DESIGN_DIR),
        "--threads", str(os.cpu_count() or 4),
    ]
    if "ORFS_ROOT" in os.environ:
        cmd += ["--orfs-root", os.environ["ORFS_ROOT"]]

    print(f"\n  Command: {' '.join(cmd)}\n")

    # Must run from the gli-flow project root (or wherever gli-flow is installed as pip -e)
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))

    if result.returncode != 0:
        print(f"\n  [FAIL] Flow exited with code {result.returncode}")
        sys.exit(result.returncode)


def show_results():
    """Display final results."""
    # Default runs dir from ORFS config; check the workspace runs directory
    config_path = Path.home() / ".gli-flow" / "config.json"
    import json
    if config_path.exists():
        config = json.loads(config_path.read_text())
        runs_dir = Path(config.get("runs_dir", config.get("workspace_dir", ""))) / "runs"
    else:
        runs_dir = PROJECT_ROOT / "runs"

    if not runs_dir.exists():
        print("  [INFO] No runs directory found yet.")
        return

    runs = sorted(runs_dir.iterdir())
    if not runs:
        print("  [INFO] No runs found.")
        return

    latest = runs[-1]
    artifacts = latest / "artifacts"

    print(f"\n  Results: {latest.name}")
    if artifacts.exists():
        for f in artifacts.glob("*"):
            size = f.stat().st_size
            print(f"    {f.name:<20} {size:>8} bytes")

        gds = artifacts / "6_final.gds"
        if gds.exists():
            print(f"\n  [OK]   GDSII: {gds}")
        else:
            print("\n  [WARN] No GDSII found — flow may not have completed.")
    else:
        print("  [WARN] No artifacts directory.")


if __name__ == "__main__":
    os.chdir(str(PROJECT_ROOT))

    print("=" * 55)
    print("  4×4 Systolic MAC Array — GLI-Flow Automation")
    print("=" * 55)
    print()

    print("[1/4] Checking prerequisites...")
    check_prerequisites()

    print("\n[2/4] Checking RTL...")
    check_rtl()

    print("\n[3/4] Running gli-flow (RTL → GDSII)...")
    run_flow()

    print("\n[4/4] Results summary...")
    show_results()

    print("\nDone.")
