#!/usr/bin/env python3
"""
Run UART RTL→GDSII via ORFS directly.
Usage:  python3 run_uart.py
"""
import os, sys, json, shutil, subprocess, time
from pathlib import Path

DESIGN = Path(__file__).resolve().parent
PROJECT = DESIGN.parent.parent
ORFS = Path(os.environ.get("ORFS_ROOT", "/home/gli/OpenROAD-flow-scripts"))
PDK_ROOT = Path(os.environ.get("PDK_ROOT", "/pdk"))
PLATFORM = "sky130hd"
DESIGN_NAME = "uart_top"
FLOW_DIR = ORFS / "flow"

os.chdir(str(PROJECT))

def run(cmd, **kw):
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, **kw)

print("=" * 55)
print("  UART Loopback — RTL → GDSII")
print("=" * 55)

# 1. Generate ORFS config
print("\n[1/4] Generating ORFS config...")
design_dir = FLOW_DIR / "designs" / PLATFORM / DESIGN_NAME
src_dir    = FLOW_DIR / "designs" / "src" / DESIGN_NAME
design_dir.mkdir(parents=True, exist_ok=True)
src_dir.mkdir(parents=True, exist_ok=True)

# Copy RTL
for f in sorted((DESIGN / "rtl").glob("*.sv")):
    shutil.copy2(str(f), str(src_dir / f.name))
    print(f"  RTL: {f.name}")

# Write config.mk
config_mk = f"""export DESIGN_NAME  = {DESIGN_NAME}
export DESIGN_NICKNAME = {DESIGN_NAME}
export PLATFORM     = {PLATFORM}
export VERILOG_FILES = $(CURDIR)/designs/src/$(DESIGN_NICKNAME)/uart_tx.sv $(CURDIR)/designs/src/$(DESIGN_NICKNAME)/uart_rx.sv $(CURDIR)/designs/src/$(DESIGN_NICKNAME)/uart_top.sv
export SDC_FILE      = $(CURDIR)/designs/$(PLATFORM)/$(DESIGN_NICKNAME)/constraint.sdc
export CORE_UTILIZATION = 30
export TNS_END_PERCENT = 100
export CORNER = ss_100C_1v60
export LIB_SYNTH = -l $(OBJECTS_DIR)/sky130_fd_sc_hd__ss_100C_1v60.lib
export LIB_FASTEST = $(OBJECTS_DIR)/sky130_fd_sc_hd__ff_100C_1v95.lib
export LIB_SLOWEST = $(OBJECTS_DIR)/sky130_fd_sc_hd__ss_100C_1v60.lib
"""
(design_dir / "config.mk").write_text(config_mk)
print("  config.mk written")

# Copy constraints
shutil.copy2(str(DESIGN / "constraints" / "top.sdc"), str(design_dir / "constraint.sdc"))
print("  constraint.sdc copied")

# 2. Clean previous run
print("\n[2/4] Cleaning previous run...")
run(["make", f"DESIGN_CONFIG=./designs/{PLATFORM}/{DESIGN_NAME}/config.mk", "clean_all"],
    cwd=str(FLOW_DIR), capture_output=True)

# 3. Run the flow
print("\n[3/4] Running ORFS (RTL → GDSII)...")
env = os.environ.copy()
env["PDK_ROOT"] = str(PDK_ROOT)
env["NUM_CORES"] = str(os.cpu_count() or 4)

t0 = time.time()
result = run(
    ["make", f"DESIGN_CONFIG=./designs/{PLATFORM}/{DESIGN_NAME}/config.mk"],
    cwd=str(FLOW_DIR), env=env, capture_output=True, text=True, timeout=7200,
)
elapsed = time.time() - t0

# Save log
log_dir = PROJECT / "outputs" / "runs" / f"uart_{int(time.time())}"
log_dir.mkdir(parents=True, exist_ok=True)
(log_dir / "orfs.log").write_text(result.stdout + "\n--- STDERR ---\n" + result.stderr)

if result.returncode == 0:
    print(f"  [OK] Flow completed in {elapsed:.0f}s")
else:
    print(f"  [FAIL] Return code {result.returncode} after {elapsed:.0f}s")
    # Show last 30 lines of output
    lines = result.stdout.strip().split("\n")
    print("\n  Last 30 lines of output:")
    for l in lines[-30:]:
        print(f"    {l}")
    sys.exit(1)

# 4. Collect artifacts
print("\n[4/4] Artifacts...")
results_dir = FLOW_DIR / "results" / PLATFORM / DESIGN_NAME / "base"
reports_dir = FLOW_DIR / "reports" / PLATFORM / DESIGN_NAME / "base"

for src_name in ["6_final.gds", "6_final.def", "1_synth.v"]:
    src = results_dir / src_name
    if src.exists():
        dst = log_dir / src_name
        shutil.copy2(str(src), str(dst))
        size = src.stat().st_size
        print(f"  {src_name:<20} {size:>8} bytes")

if (results_dir / "6_final.gds").exists():
    print(f"\n  GDSII: {results_dir / '6_final.gds'}")
    print(f"  Log:   {log_dir}/orfs.log")
else:
    print("\n  [WARN] No GDSII found")

# Show timing summary
for line in result.stdout.split("\n"):
    if "wns" in line.lower() or "tns" in line.lower() or "Total cell area" in line.lower() or "Design area" in line.lower():
        print(f"  {line.strip()}")

print("\nDone.")
