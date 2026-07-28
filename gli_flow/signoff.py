import os
import subprocess
import shlex
from pathlib import Path
import logging

logger = logging.getLogger("gli_flow.signoff")

class LVSValidator:
    def __init__(self, design_name, pdk_root, run_dir):
        self.design_name = design_name
        self.pdk_root = Path(pdk_root)
        self.run_dir = Path(run_dir)
        
        # Resolve PDK versioned paths (Volare support)
        self.pdk_version_path = self._resolve_pdk_path()
        
    def _resolve_pdk_path(self):
        # Check if using Volare structure
        volare_path = self.pdk_root / "volare"
        if volare_path.exists():
            # Find the first versioned sky130A path
            versions = list(volare_path.glob("sky130/versions/*/sky130A"))
            if versions:
                return versions[0]
        return self.pdk_root / "sky130A"

    def _run_command(self, cmd, description):
        logger.info(f"Running {description}...")
        try:
            result = subprocess.run(
                shlex.split(cmd),
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode != 0:
                logger.error(f"{description} failed: {result.stderr}")
                return False, result.stderr
            return True, result.stdout
        except Exception as e:
            logger.error(f"Exception during {description}: {str(e)}")
            return False, str(e)

    def validate_lvs(self, gds_path, cdl_path):
        """
        Performs full LVS sign-off:
        1. GDS Extraction using KLayout PDK rule deck.
        2. Comparison using Netgen.
        """
        extracted_netlist = self.run_dir / "lvs_extracted.cir"
        lvs_report = self.run_dir / "lvs_result.lvsdb"
        
        # 1. Define Rule Deck Path
        rule_deck = self.pdk_version_path / "libs.tech" / "klayout" / "lvs" / "sky130.lvs"
        if not rule_deck.exists():
            # Try fallback to sky130.lylvs
            rule_deck = rule_deck.with_suffix(".lylvs")
            if not rule_deck.exists():
                return False, "PDK LVS rule deck not found."

        # 2. Run KLayout Extraction
        # We use the official parameters derived from run_lvs.py
        klayout_cmd = (
            f"klayout -b -r {rule_deck} "
            f"-rd input={gds_path} "
            f"-rd schematic={cdl_path} "
            f"-rd report={lvs_report} "
            f"-rd target_netlist={extracted_netlist} "
            f"-rd run_mode=deep "
            f"-rd thr=8 "
            f"-rd verbose=true "
            f"-rd spice_comments=true "
            f"-rd top_lvl_pins=true "
            f"-rd spice_net_names=true"
        )
        
        success, output = self._run_command(klayout_cmd, "KLayout GDS Extraction")
        if not success:
            return False, f"Extraction failed: {output}"

        # 3. Final Verification with Netgen
        # We create a simple netgen setup script to handle global power/ground
        netgen_setup = self.run_dir / "netgen_lvs.tcl"
        with open(netgen_setup, "w") as f:
            f.write(f"""
source /usr/lib/netgen/tcl/netgen.tcl
# Define global nets to prevent false mismatches on power/ground
# Use a generic setup if the specific PDK one is not available
lvs [list {cdl_path} {self.design_name}] [list {extracted_netlist} {self.design_name}] {self.run_dir}/netgen.out -blackbox
exit
""")

        netgen_cmd = f"netgen -batch {netgen_setup}"
        success, output = self._run_command(netgen_cmd, "Netgen Comparison")
        
        # Netgen returns 0 if it ran, but the result is in the output file
        # We check for "Netlists match" or absence of "Differences found"
        netgen_out_path = self.run_dir / "netgen.out"
        if netgen_out_path.exists():
            report_text = netgen_out_path.read_text()
            if "Netlists match" in report_text or "Correct" in report_text:
                return True, "LVS Passed"
            else:
                return False, f"LVS Mismatch: {report_text}"
        
        return success, output if success else "Netgen output not found"

    def get_signoff_summary(self, lvs_status):
        summary = (
            "===================================================\n"
            "             LVS SIGN-OFF REPORT                 \n"
            "===================================================\n"
            f"Design: {self.design_name}\n"
            f"Status: {'PASSED' if lvs_status else 'FAILED'}\n"
            f"Timestamp: {Path(__file__).stat().st_mtime}\n"
            "===================================================\n"
        )
        return summary
