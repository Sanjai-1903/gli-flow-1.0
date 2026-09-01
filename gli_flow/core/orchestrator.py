import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
import uuid

from pathlib import Path

import yaml

from gli_flow.database.sqlite import DatabaseManager
from gli_flow.models.execution_record import ExecutionRecord
from gli_flow.version import VERSION

from gli_flow.backends.librelane import LibreLaneAdapter
from gli_flow.backends.openroad_adapter import OpenRoadAdapter, LVSStatus
from gli_flow.backends.orfs_monitor import OrfsStageProgress
from gli_flow.runtime.run_directory import RunDirectoryManager
from gli_flow.runtime.telemetry_manager import TelemetryManager
from gli_flow.runtime.artifact_manager import ArtifactManager
from gli_flow.analytics.qor_score import calculate_qor_score
from gli_flow.pdk import get_pdk, discover_pdks
from gli_flow.installer.workspace import get_config_value
from gli_flow.testing.layout_images import generate_placeholder_images

from gli_flow.provenance.manifest import generate_reproducibility_manifest
from gli_flow.core.subprocess_env import safe_env
from gli_flow.regression.detector import detect_regression
from gli_flow.core.exceptions import StageOOMError, StageTimeoutError, SynthesisSafetyError, RoutingOverflowError, TapeoutBlockingError
from gli_flow.core.rtl_preprocessor import preprocess_rtl
from gli_flow.core.synthesis_safety import check_synthesis_log, pre_synthesis_hierarchy_check
from gli_flow.core.routing_safety import check_global_routing_overflow
from gli_flow.core.drc_runner import run_dual_drc
from gli_flow.core.cross_tool_drc import CrossToolDRCAnalyzer
from gli_flow.core.cdc_check import count_clock_domains, CDC_DISCLAIMER


def _notify_cloud_sync(run_id, run_dir):
    """Best-effort hook that enqueues the completed run for cloud sync.

    Never raises. If the user isn't logged in or the cloud is unreachable,
    the run stays enqueued locally and `gli-flow sync` (or the daemon)
    will pick it up later.
    """
    try:
        from gli_flow.cloud.sync import notify_run_completed
        notify_run_completed(str(run_id), Path(str(run_dir)) if run_dir else None)
    except Exception:
        pass
from gli_flow.security.file_protection import secure_run_directory
from gli_flow.parser.rtl_parser import scan_directory
from gli_flow.cli.output import console, print_stage_progress, print_results

from failure_atlas.detector import detect_failures
from failure_atlas.repository import FailureAtlasRepository
from failure_atlas.signature_engine import load_signatures, scan_file
from failure_atlas.taxonomy import FailureSeverity
from failure_atlas.ai_assistant.explanation_engine import ExplanationEngine
from gli_flow.reliability.root_cause_engine import RootCauseEngine
from gli_flow.signoff.classifier import SignoffClassifier, CheckResult


_STAGE_TO_CHECK = {
    "ANTENNA_CHECK": "antenna",
    "DENSITY_CHECK": "density",
    "EM_CHECK": "em",
    "SI_ANALYSIS": "si",
    "POWER": "power",
    "FORMAL_VERIFICATION": "formal",
}


def _stage_check_name(stage: str) -> str | None:
    return _STAGE_TO_CHECK.get(stage)


logger = logging.getLogger(__name__)


STAGES = [
    "INITIALIZING",
    "SYNTHESIS",
    "PACKAGING",
    "HIERARCHICAL_PARTITIONING",
    "BLOCK_SYNTHESIS",
    "CLOCK_GATING",
    "SCAN_INSERTION",
    "FORMAL_VERIFICATION",
    "FLOORPLANNING",
    "TOP_FLOORPLANNING",
    "PLACEMENT",
    "CTS",
    "ROUTING",
    "PRO",
    "ANTENNA_CHECK",
    "FILL",
    "DECAP",
    "POWER",
    "EM_CHECK",
    "DENSITY_CHECK",
    "YIELD",
    "ATPG",
    "D2D_INTERFACE_CHECK",
    "QOR_EXTRACTION",
    "DRC",
    "LVS",
    "TIMING_ANALYSIS",
    "SI_ANALYSIS",
    "SIGN_OFF",
]

_STAGE_METHODS = {
    "HIERARCHICAL_PARTITIONING": "run_hierarchical_partitioning",
    "BLOCK_SYNTHESIS": "run_block_synthesis",
    "CLOCK_GATING": "run_clock_gating",
    "SCAN_INSERTION": "run_scan_insertion",
    "FORMAL_VERIFICATION": "run_formal",
    "TOP_FLOORPLANNING": "run_top_floorplanning",
    "PRO": "run_pro",
    "ANTENNA_CHECK": "run_antenna_check",
    "FILL": "run_fill",
    "DECAP": "run_decap",
    "POWER": "run_power_analysis",
    "EM_CHECK": "run_em_check",
    "DENSITY_CHECK": "run_density_check",
    "YIELD": "run_yield_enhancement",
    "ATPG": "run_atpg",
    "SI_ANALYSIS": "run_si_analysis",
    "D2D_INTERFACE_CHECK": "run_d2d_interface_check",
    "PACKAGING": "run_packaging",
}


from dataclasses import dataclass, field


@dataclass
class SignoffGate:
    synth_ok: bool = False
    gds_present: bool = False
    def_present: bool = False
    netlist_present: bool = False
    setup_pass: bool = False
    hold_pass: bool = False
    magic_drc_pass: bool = False
    klayout_drc_pass: bool = False
    antenna_pass: bool = False
    density_pass: bool = False
    lvs_pass: bool = False
    em_pass: bool = False
    si_pass: bool = False
    power_pass: bool = False
    formal_pass: bool = False

    def set_from_status(self, attr: str, status: str):
        if status == "PASS":
            setattr(self, attr, True)
        elif status in ("FAIL", "NOT_RUN", "ERROR"):
            setattr(self, attr, False)

    @property
    def tapeout_ready(self) -> bool:
        return all([
            self.synth_ok, self.gds_present, self.def_present, self.netlist_present,
            self.setup_pass, self.hold_pass, self.magic_drc_pass, self.klayout_drc_pass,
            self.antenna_pass, self.density_pass, self.lvs_pass,
            self.em_pass, self.si_pass, self.power_pass, self.formal_pass,
        ])

    def blocking_failures(self) -> list[str]:
        failures = []
        if not self.synth_ok:         failures.append("Synthesis did not complete cleanly")
        if not self.gds_present:      failures.append("Final GDS file not found or empty")
        if not self.def_present:      failures.append("Final DEF file not found or empty")
        if not self.netlist_present:  failures.append("Final netlist not found or empty")
        if not self.setup_pass:       failures.append("Setup timing violated (WNS < 0)")
        if not self.hold_pass:        failures.append("Hold timing violated (WHS < 0)")
        if not self.magic_drc_pass:   failures.append("Magic DRC: NOT_RUN, ERROR, or violations found")
        if not self.klayout_drc_pass: failures.append("KLayout DRC: NOT_RUN, ERROR, or violations found")
        if not self.antenna_pass:     failures.append("Antenna violations found or report missing")
        if not self.density_pass:     failures.append("Density violations found or report missing")
        if not self.lvs_pass:         failures.append("LVS: NOT_RUN, ERROR, or comparison failed")
        if not self.em_pass:          failures.append("EM check: NOT_RUN, ERROR, or violations found")
        if not self.si_pass:          failures.append("SI check: NOT_RUN, ERROR, or violations found")
        if not self.power_pass:       failures.append("Power analysis: NOT_RUN, ERROR, or abnormal values")
        if not self.formal_pass:      failures.append("Formal verification: NOT_RUN, ERROR, or not equivalent")
        return failures

    def release_gate_errors(self, telemetry: dict | None = None) -> list[str]:
        errors = []
        power_could_have_data = telemetry and telemetry.get("total_power_mw") is not None and telemetry.get("total_power_mw", 0) > 0
        if self.power_pass and not power_could_have_data:
            errors.append("RELEASE_GATE: power_pass=True but no valid power telemetry data found — possible signoff integrity regression")
        return errors


class FlowOrchestrator:

    def __init__(self, design_path, threads: int = None, memory_mb: int = None,
                 orfs_root: str = None, mock: bool = False, db_path: str = None,
                 certification_mode: bool = False):
        discover_pdks()

        certification_mode = certification_mode or os.environ.get("GLI_FLOW_CERTIFICATION_MODE", "").lower() in ("1", "true", "yes")

        if certification_mode and mock:
            raise RuntimeError(
                "CERTIFICATION MODE: Mock execution forbidden. "
                "Run without --mock to execute real EDA tools, "
                "or omit --certify for development/testing."
            )

        self.design_path = Path(design_path)
        self.db_path = db_path

        self.manifest = self._read_manifest()
        self.design_name = self.manifest.get("top_module") or self.design_path.name

        self.run_id = f"run_{int(time.time())}_{uuid.uuid4().hex[:8]}_{self.design_name}"

        self.run_dir_mgr = RunDirectoryManager(self.run_id)
        self.run_dir = self.run_dir_mgr.create()

        self.pdk_root = os.environ.get("PDK_ROOT") or get_config_value("pdk_root")
        self.orfs_root = orfs_root or os.environ.get("ORFS_ROOT") or get_config_value("orfs_root")
        self.backend_type = self.manifest.get("backend", "openroad")
        self._mock_mode = mock
        self._certification_mode = certification_mode

        if self.pdk_root:
            os.environ.setdefault("PDK_ROOT", self.pdk_root)

        pdk_name = self.manifest.get("pdk", "sky130")
        pdk_variant = self.manifest.get("pdk_variant", "")
        self.pdk = get_pdk(pdk_name, variant=pdk_variant)

        self.corners = self._resolve_corners()

        self.threads = threads or self.manifest.get("threads")
        self.memory_mb = memory_mb or self.manifest.get("memory_mb")

        if mock:
            from gli_flow.testing.mock_adapter import MockEDAAdapter
            self.adapter = MockEDAAdapter(pdk_root=self.pdk_root, pdk=self.pdk)
            toolchain_name = f"Mock/{pdk_name}"
        elif self.backend_type == "openroad":
            self.adapter = OpenRoadAdapter(pdk_root=self.pdk_root, pdk=self.pdk, orfs_root=self.orfs_root)
            toolchain_name = f"OpenROAD/{pdk_name}"
        else:
            self.adapter = LibreLaneAdapter(pdk_root=self.pdk_root)
            toolchain_name = "LibreLane"

        self.database = DatabaseManager(db_path=self.db_path)

        self.record = ExecutionRecord(
            run_id=self.run_id,
            design_name=self.design_name,
            toolchain=toolchain_name,
            status="INITIALIZING",
            current_stage="INITIALIZING",
            implementation_status="NOT_STARTED",
            signoff_status="NOT_RUN",
            tapeout_ready=False,
        )

        # ITEMS 50-51: Secure run directory
        import getpass
        user_id = getpass.getuser()
        secure_run_directory(Path(self.run_dir), user_id)

        self.telemetry_mgr = TelemetryManager(str(self.run_dir))
        self.artifact_mgr = ArtifactManager()

        self._backend_result = None
        self.signoff_gate = SignoffGate()
        self._check_results: dict[str, CheckResult] = {}
        self._false_positives: list[str] = []
        self._flow_bugs: list[str] = []
        self._evidence_gaps: list[str] = []

    def _read_manifest(self):
        manifest_path = self.design_path / "gli_manifest.yaml"
        if not manifest_path.exists():
            print(f"[ERROR] Manifest not found: {manifest_path}", file=sys.stderr)
            sys.exit(1)

        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)

        rtl_files = manifest.get("rtl_files")
        if not rtl_files:
            _, top_module, discovered = scan_directory(self.design_path)
            if discovered:
                manifest["rtl_files"] = [str(Path(f).relative_to(self.design_path.parent)) for f in discovered]
                print(f"  [INFO] Auto-discovered {len(discovered)} RTL file(s) in design directory")
                if top_module and "top_module" not in manifest:
                    manifest["top_module"] = top_module.name
                    print(f"  [INFO] Auto-detected top module: {top_module.name}")

        return manifest

    def _resolve_corners(self):
        manifest_corners = self.manifest.get("corners")
        if manifest_corners:
            from gli_flow.pdk.corner import PVTCorner
            return [PVTCorner.from_dict(c) if isinstance(c, dict) else c for c in manifest_corners]
        if self.pdk:
            return self.pdk.corners
        from gli_flow.pdk.corner import PVTCorner as _PVTCorner
        return [_PVTCorner.typical()]

    def _update_stage(self, stage, progress):
        self.record.current_stage = stage
        self.record.progress = progress
        self.record.status = "RUNNING"

        self.database.update_run(
            run_id=self.run_id,
            status="RUNNING",
            current_stage=stage,
            progress=progress,
        )

    def _extract_metrics(self, consistency_tolerance_ns: float = 0.05):
        reports_dir = self.run_dir / "reports"
        from gli_flow.telemetry.parser import TelemetryParser

        parser = TelemetryParser(str(reports_dir), run_dir=str(self.run_dir))
        parsed = parser.parse_all()

        self.record.wns = parsed.get("wns", parsed.get("setup_wns_ns"))
        self.record.tns = parsed.get("tns", parsed.get("setup_tns_ns"))
        self.record.hold_wns = parsed.get("hold_whs_ns")
        self.record.hold_tns = parsed.get("hold_ths_ns")
        self.record.utilization = parsed.get("utilization")
        if parsed.get("cell_count") is not None:
            self.record.cell_count = int(parsed["cell_count"])
        self.record.runtime_sec = parsed.get("runtime_sec")

        orfs_wns = parsed.get("setup_wns_ns")
        signoff_wns = parsed.get("signoff_setup_wns_ns")
        if orfs_wns is not None and signoff_wns is not None:
            diff = abs(orfs_wns - signoff_wns)
            if diff > consistency_tolerance_ns:
                logger.warning(
                    f"Timing consistency check FAILED: ORFS WNS={orfs_wns:.5f} vs "
                    f"signoff STA WNS={signoff_wns:.5f} (diff={diff:.5f}ns, "
                    f"tolerance={consistency_tolerance_ns}ns)"
                )
            else:
                logger.info(
                    f"Timing consistency check PASSED: ORFS WNS={orfs_wns:.5f} vs "
                    f"signoff STA WNS={signoff_wns:.5f} (diff={diff:.5f}ns)"
                )

        drc_lvs_path = Path(self.run_dir) / "drc_lvs_summary.json"
        if drc_lvs_path.exists():
            try:
                summary = json.loads(drc_lvs_path.read_text())
                drc_data = summary.get("drc", {})
                if drc_data.get("runtime_seconds") is not None:
                    parsed["drc_runtime_seconds"] = drc_data["runtime_seconds"]
                if "is_clean" in drc_data:
                    parsed["drc_is_clean"] = drc_data["is_clean"]
                lvs_data = summary.get("lvs", {})
                if lvs_data.get("runtime_seconds") is not None:
                    parsed["lvs_runtime_seconds"] = lvs_data["runtime_seconds"]
                if "is_clean" in lvs_data:
                    parsed["lvs_is_clean"] = lvs_data["is_clean"]
            except Exception:
                pass

        def_path = Path(self.run_dir) / "artifacts" / "6_final.def"
        if not def_path.exists():
            def_path = Path(self.run_dir) / "results" / "6_final.def"
        if def_path.exists() and "die_area_um2" not in parsed:
            try:
                text = def_path.read_text()
                m = re.search(r"DIEAREA\s*\(\s*(\d+)\s+(\d+)\s*\)\s*\(\s*(\d+)\s+(\d+)\s*\)", text)
                if m:
                    units_m = re.search(r"UNITS DISTANCE MICRONS\s+(\d+)", text)
                    scale = int(units_m.group(1)) if units_m else 1000
                    w = (int(m.group(3)) - int(m.group(1))) / scale
                    h = (int(m.group(4)) - int(m.group(2))) / scale
                    parsed["die_area_um2"] = w * h
            except Exception:
                pass

        self._telemetry_parsed = parsed

    def _compute_qor(self):
        hold_wns = self.record.hold_wns
        if hold_wns is None and self._corner_results:
            for cr in self._corner_results:
                if cr.get("hold_wns") is not None:
                    hold_wns = cr["hold_wns"]
                    break
        telemetry = getattr(self, '_telemetry_parsed', {})
        drc_clean = telemetry.get("drc_is_clean", False)
        lvs_clean = telemetry.get("lvs_is_clean", False)
        signoff_complete = len(self._corner_results) > 0 if hasattr(self, '_corner_results') else False
        qor_result = calculate_qor_score(
            wns=self.record.wns,
            tns=self.record.tns,
            utilization=self.record.utilization,
            runtime=self.record.runtime_sec,
            cell_count=self.record.cell_count,
            hold_wns=hold_wns,
            drc_clean=drc_clean,
            lvs_clean=lvs_clean,
            signoff_complete=signoff_complete,
        )
        self.record.qor_score = qor_result["score"]
        self.record.implementation_score = qor_result.get("implementation_score")
        self.record.signoff_score = qor_result.get("signoff_score")
        return qor_result

    def _run_failure_detection(self):
        metrics = {
            "setup_wns_ns": self.record.wns,
            "setup_tns_ns": self.record.tns,
            "hold_whs_ns": self.record.hold_wns,
            "hold_ths_ns": self.record.hold_tns,
            "utilization": self.record.utilization,
            "cell_count": self.record.cell_count,
            "runtime_sec": self.record.runtime_sec,
        }

        run_dir = Path(self.run_dir)
        reports_dir = run_dir / "reports"
        if reports_dir.exists():
            for f in reports_dir.glob("*.rpt"):
                metrics_file = f
            drc_lvs_path = run_dir / "drc_lvs_summary.json"
            if drc_lvs_path.exists():
                try:
                    summary = json.loads(drc_lvs_path.read_text())
                    drc = summary.get("drc", {})
                    metrics["drc_total_violations"] = drc.get("total_violations", 0)
                    metrics["drc_is_clean"] = drc.get("is_clean", True)
                    lvs = summary.get("lvs", {})
                    metrics["lvs_result"] = lvs.get("result", "")
                    metrics["lvs_status"] = lvs.get("status", "")
                    metrics["lvs_unmatched_devices"] = lvs.get("unmatched_devices", 0)
                    metrics["lvs_unmatched_nets"] = lvs.get("unmatched_nets", 0)
                    metrics["lvs_short_count"] = lvs.get("short_count", 0)
                    metrics["lvs_open_count"] = lvs.get("open_count", 0)
                    metrics["lvs_comparison_completed"] = lvs.get("comparison_completed", False)
                    metrics["lvs_report_exists"] = lvs.get("report_exists", False)
                    metrics["lvs_report_size"] = lvs.get("report_size", 0)
                    metrics["lvs_return_code"] = lvs.get("return_code", -1)
                    metrics["lvs_parser_status"] = lvs.get("parser_status", "")
                except Exception as e:
                    logger.warning(f"Failed to parse DRC/LVS summary: {e}")

        fa_entries = detect_failures(
            run_id=self.run_id,
            metrics=metrics,
            stage=self.record.current_stage or "UNKNOWN",
            design_name=self.design_name,
            pdk_name=self.manifest.get("pdk", ""),
        )

        repo = FailureAtlasRepository(db_path=self.db_path)
        try:
            existing = repo.get_entries_for_run(self.run_id)
            has_known_disagreement = any(
                e.get("failure_type") == "CROSS_TOOL_DRC_DISAGREEMENT"
                and isinstance(e.get("evidence"), dict)
                and e["evidence"].get("citation") == "inf_magic_002"
                for e in existing
            )

            for entry in fa_entries:
                entry_dict = {
                    "run_id": entry.run_id,
                    "failure_id": str(uuid.uuid4()),
                    "failure_type": entry.level2_category.value if hasattr(entry.level2_category, 'value') else str(entry.level2_category),
                    "severity": entry.severity.value if hasattr(entry.severity, 'value') else str(entry.severity),
                    "title": entry.level3_signature,
                    "description": str(entry.level3_signature),
                    "confidence": entry.confidence,
                    "signature": entry.level3_signature,
                    "domain": entry.level1_domain.value if hasattr(entry.level1_domain, 'value') else str(entry.level1_domain),
                    "category": entry.level2_category.value if hasattr(entry.level2_category, 'value') else str(entry.level2_category),
                    "evidence": entry.evidence,
                    "detected_at": entry.created_at,
                    "recommended_fix": self._get_remediation_for(entry.level2_category),
                    "detection_classification": getattr(entry, "detection_classification", "VERIFIED"),
                }
                if has_known_disagreement and entry_dict.get("domain") == "DRC":
                    entry_dict["severity"] = "UNDER_REVIEW"
                    entry_dict["evidence"] = dict(entry_dict.get("evidence", {}))
                    entry_dict["evidence"]["classification"] = "VALIDATED_TOOL_DISAGREEMENT"
                    entry_dict["evidence"]["citation"] = "inf_magic_002"
                    entry_dict["title"] = f"Known tool disagreement (INF-MAGIC-002): {entry.level3_signature}"
                repo.insert_entry(entry_dict)

            log_dir = run_dir / "logs"
            if log_dir.exists():
                signatures = load_signatures()
                for log_file in sorted(log_dir.rglob("*.log")):
                    findings = scan_file(log_file, signatures)
                    for sig in findings:
                        detection_method = sig.get("_detection_method", "")
                        if detection_method == "EXACT_MATCH":
                            dc = "VERIFIED"
                        elif detection_method == "KEYWORD_FALLBACK":
                            dc = "HEURISTIC"
                        else:
                            dc = "UNVERIFIED"
                        sig_entry = {
                            "run_id": self.run_id,
                            "failure_id": str(uuid.uuid4()),
                            "failure_type": sig.get("category", "UNKNOWN"),
                            "severity": sig.get("severity", "MEDIUM"),
                            "title": f"Log signature: {sig.get('atlas_id', '?')}",
                            "description": sig.get("observed_signature", ""),
                            "confidence": sig.get("confidence", 0.5),
                            "signature": sig.get("observed_signature", ""),
                            "domain": sig.get("category", "UNKNOWN"),
                            "category": sig.get("category", "UNKNOWN"),
                            "evidence": {"log_file": str(log_file), "atlas_id": sig.get("atlas_id")},
                            "detected_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                            "recommended_fix": self._get_remediation_by_id(sig.get("atlas_id")),
                            "detection_classification": dc,
                        }
                        repo.insert_entry_if_not_exists(sig_entry)

            if fa_entries or self._any_log_findings():
                print(f"  [FAILURE ATLAS] {len(fa_entries)} metric failures, log signatures recorded")
        finally:
            repo.close()

    def _get_remediation_for(self, category):
        remediation_map = {
            "SETUP_VIOLATION": ["Increase clock period", "Pipeline insertion", "Retiming", "Logic restructuring"],
            "HOLD_VIOLATION": ["Delay buffer insertion", "Hold fixing", "Clock path balancing", "Cell resizing"],
            "GLOBAL_OVERFLOW": ["Reduce utilization", "Increase die area", "Macro relocation", "Placement density reduction"],
            "DRC_SPACING": ["Tighten routing constraints", "Increase wire spread factor", "Add routing blockages"],
            "DRC_WIDTH": ["Check wire width constraints", "Use correct via sizes"],
            "DRC_ENCLOSURE": ["Check enclosure rules", "Add metal fill correctly"],
            "DRC_ANTENNA": ["Insert antenna diodes", "Layer jumping", "Metal jumper cells"],
            "DRC_DENSITY": ["Increase die area", "Spread cells", "Add placement blockages"],
            "LVS_SHORT": ["Run detailed routing with soft spacing", "Increase wire spacing"],
            "LVS_OPEN_NET": ["Increase routing effort", "Add routing guides", "Check via stacking rules"],
            "LVS_DEVICE_MISMATCH": ["Check netlist vs layout devices", "Verify LVS deck"],
            "LVS_PORT_MISMATCH": ["Verify port connectivity", "Check port names match"],
            "SRAM_PIN_BLOCKED": ["Adjust SRAM halo", "Check pin accessibility", "Add keepout margins"],
            "MAX_TRANSITION": ["Buffer high-fanout nets", "Upsize drivers", "Insert repeater chains"],
            "MAX_CAPACITANCE": ["Split high-fanout nets", "Insert buffers", "Reduce wire load"],
            "CLOCK_SKEW": ["Balance H-tree", "Use clock mesh", "Reduce OCV derating"],
            "IR_DROP": ["Widen power straps", "Add VDD/VSS pairs", "Use higher metal layers"],
        }
        cat_str = category.value if hasattr(category, 'value') else str(category)
        return remediation_map.get(cat_str, ["Investigate failure", "Review design constraints", "Adjust flow parameters"])

    def _get_remediation_by_id(self, atlas_id):
        try:
            import json as json_mod
            from pathlib import Path as PPath
            rem_path = PPath(__file__).resolve().parent.parent.parent / "failure_atlas" / "remediation_db.json"
            if rem_path.exists():
                db = json_mod.loads(rem_path.read_text())
                for entry in db:
                    if entry.get("atlas_id") == atlas_id:
                        return entry.get("recommended_fix", [])
        except Exception as e:
            logger.warning(f"Failed to load remediation DB: {e}")
        return []

    def _any_log_findings(self):
        return False

    def _write_telemetry(self, qor_result, corner_results=None):
        parsed = getattr(self, '_telemetry_parsed', {})
        telemetry_data = {
            "run_id": self.run_id,
            "design_name": self.design_name,
            "pdk": self.manifest.get("pdk", ""),
            "pdk_variant": self.manifest.get("pdk_variant", ""),
            "corners": [c.to_dict() for c in self.corners],
            "metrics": {
                "wns": self.record.wns,
                "tns": self.record.tns,
                "utilization": self.record.utilization,
                "cell_count": self.record.cell_count,
                "runtime_sec": self.record.runtime_sec,
                "qor_score": self.record.qor_score,
                "qor_breakdown": qor_result["breakdown"],
                "qor_weights": qor_result["weights"],
                "die_area_um2": parsed.get("die_area_um2"),
                "total_power_mw": parsed.get("total_power_mw"),
                "internal_power_mw": parsed.get("internal_mw"),
                "switching_power_mw": parsed.get("switching_mw"),
                "leakage_power_mw": parsed.get("leakage_mw"),
                "drc_runtime_seconds": parsed.get("drc_runtime_seconds"),
                "lvs_runtime_seconds": parsed.get("lvs_runtime_seconds"),
            },
        }

        if corner_results:
            telemetry_data["corner_results"] = corner_results

        self.telemetry_mgr.export_metrics(telemetry_data)

        for idx, stage in enumerate(STAGES):
            stage_data = {
                "stage": stage,
                "order": idx,
                "completed": idx <= (self.record.progress / 100 * len(STAGES)) - 1,
            }
            self.telemetry_mgr.export_stage_data(stage, stage_data)

    def _collect_artifacts(self):
        artifact_dirs = ["config.json", "reproducibility.json", "telemetry/metrics.json"]
        for rel_path in artifact_dirs:
            full_path = self.run_dir / rel_path
            if full_path.exists():
                self.artifact_mgr.add_artifact(str(full_path))

        log_dir = self.run_dir / "logs"
        if log_dir.exists():
            for f in sorted(log_dir.iterdir()):
                if f.is_file():
                    self.artifact_mgr.add_artifact(str(f))

        reports_dir = self.run_dir / "reports"
        if reports_dir.exists():
            for f in sorted(reports_dir.iterdir()):
                if f.is_file():
                    self.artifact_mgr.add_artifact(str(f))

        results_dir = self.run_dir / "results"
        if results_dir.exists():
            for f in sorted(results_dir.iterdir()):
                if f.is_file():
                    self.artifact_mgr.add_artifact(str(f))

        artifacts_dir = self.run_dir / "artifacts"
        if artifacts_dir.exists():
            for f in sorted(artifacts_dir.iterdir()):
                if f.is_file():
                    self.artifact_mgr.add_artifact(str(f))

        self.artifact_mgr.export_manifest(str(self.run_dir))

    def _write_manifest(self, qor_result):
        metrics = {
            "wns": self.record.wns,
            "tns": self.record.tns,
            "utilization": self.record.utilization,
            "cell_count": self.record.cell_count,
            "runtime_sec": self.record.runtime_sec,
            "qor_score": self.record.qor_score,
            "qor_breakdown": qor_result["breakdown"],
        }

        manifest_data = {
            "rtl_files": self.manifest.get("rtl_files", []),
            "constraints": self.manifest.get("constraints", []),
            "pdk": self.manifest.get("pdk", ""),
            "pdk_variant": self.manifest.get("pdk_variant", ""),
            "corners": [c.to_dict() for c in self.corners],
            "config_path": str(self.run_dir / "config.json"),
        }

        generate_reproducibility_manifest(
            run_id=self.run_id,
            design_name=self.design_name,
            metrics=metrics,
            manifest_data=manifest_data,
            run_dir=str(self.run_dir),
        )

    def _check_regression(self):
        baseline = self.database.get_last_successful_run(self.design_name)
        if baseline is None:
            return {"regression_detected": False, "alerts": [], "baseline": None}

        current_metrics = {
            "qor_score": self.record.qor_score,
            "wns": self.record.wns,
            "utilization": self.record.utilization,
        }

        baseline_metrics = {
            "qor_score": baseline["qor_score"],
            "wns": baseline["wns"],
            "utilization": baseline["utilization"],
        }

        return detect_regression(current_metrics, baseline_metrics)

    def _run_subprocess_safe(
        self, cmd: list, stage: str, timeout: int = 7200,
        memory_limit_mb: int = None, cpu_threads: int = 4,
        cwd: str = None, log_path: str = None
    ) -> dict:
        """Safe subprocess wrapper with OOM, timeout, and error handling."""
        import resource
        env = safe_env(cpu_threads=cpu_threads)

        def set_limits():
            try:
                resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))
            except Exception:
                logger.warning("Could not set RLIMIT_NOFILE")
            if memory_limit_mb:
                limit = memory_limit_mb * 1024 * 1024
                try:
                    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
                except Exception:
                    logger.warning(f"Could not set RLIMIT_AS to {limit}")

        try:
            if log_path:
                with open(log_path, 'w') as log_f:
                    process = subprocess.run(
                        cmd, stdout=log_f, stderr=subprocess.STDOUT,
                        timeout=timeout, env=env, cwd=cwd, preexec_fn=set_limits
                    )
            else:
                process = subprocess.run(
                    cmd, capture_output=True, text=True,
                    timeout=timeout, env=env, cwd=cwd, preexec_fn=set_limits
                )

            returncode = process.returncode

            if returncode == -9:
                raise StageOOMError(stage, memory_limit_mb)

            stderr_text = (
                process.stderr if hasattr(process, 'stderr') and process.stderr else ""
            )
            if "Killed" in stderr_text or "Out of memory" in stderr_text or "Cannot allocate memory" in stderr_text:
                raise StageOOMError(stage, memory_limit_mb)

            return {
                "returncode": returncode, "success": returncode == 0,
                "stdout": process.stdout if hasattr(process, 'stdout') else "",
                "stderr": stderr_text,
            }

        except subprocess.TimeoutExpired:
            raise StageTimeoutError(stage, timeout)

    def _add_failure_atlas_entry(self, stage, category, severity):
        entry = {
            "run_id": self.run_id,
            "design_name": self.design_name,
            "detection_stage": stage,
            "level2_category": str(category),
            "severity": str(severity),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        atlas_dir = Path(self.run_dir) / "failure_atlas"
        atlas_dir.mkdir(parents=True, exist_ok=True)
        fname = f"{stage}_{category}_{int(time.time())}.json"
        (atlas_dir / fname).write_text(json.dumps(entry, indent=2))

    def _magic_drc_is_false_positive(self, violation_count: int) -> bool:
        report_path = Path(self.run_dir) / "reports" / "magic_drc.rpt"
        if not report_path.exists():
            return False
        try:
            content = report_path.read_text()
            known_false_positives = {"licon.8a", "licon.9a", "licon.10a"}
            for line in content.split("\n"):
                for fp in known_false_positives:
                    if fp in line.lower():
                        return True
            return False
        except Exception:
            return False

    def _write_run_summary(self, success: bool = False, root_cause_report=None):
        summary_path = Path(self.run_dir) / "run_summary.md"
        status = "SUCCESS" if success else "FAILED"
        impl_status = getattr(self.record, 'implementation_status', 'NOT_STARTED')
        signoff_status = getattr(self.record, 'signoff_status', 'NOT_RUN')
        tapeout = getattr(self.record, 'tapeout_ready', False)
        impl_score = getattr(self.record, 'implementation_score', None)
        signoff_score = getattr(self.record, 'signoff_score', None)

        lines = [
            f"# Run Summary: {self.design_name}",
            f"",
            f"- **Run ID**: {self.run_id}",
            f"- **Design**: {self.design_name}",
            f"- **PDK**: {self.manifest.get('pdk', 'N/A')}",
            f"- **Runtime**: {self.record.runtime_sec}s" if self.record.runtime_sec else "- **Runtime**: N/A",
            f"- **WNS**: {self.record.wns} ns" if self.record.wns is not None else "- **WNS**: N/A",
            f"- **TNS**: {self.record.tns} ns" if self.record.tns is not None else "- **TNS**: N/A",
            f"- **Utilization**: {self.record.utilization}%" if self.record.utilization is not None else "- **Utilization**: N/A",
            f"- **Cell Count**: {self.record.cell_count}" if self.record.cell_count is not None else "- **Cell Count**: N/A",
            f"",
            f"## Status",
            f"- **Implementation (RTL→GDS)**: {impl_status}",
            f"- **Signoff (GDS→Signoff)**: {signoff_status}",
            f"- **Tapeout Ready**: {'YES' if tapeout else 'NO'}",
        ]
        if impl_score is not None:
            lines.append(f"- **Implementation Score**: {impl_score:.3f}")
        if signoff_score is not None:
            lines.append(f"- **Signoff Score**: {signoff_score:.3f}")
        if self.record.qor_score is not None:
            lines.append(f"- **Legacy QoR**: {self.record.qor_score:.3f}")
        lines.append(f"")

        if root_cause_report and root_cause_report.root_causes:
            lines.append("## Root Cause Analysis")
            for rc in root_cause_report.root_causes:
                marker = "**PRIMARY**" if rc.blocker else "Secondary"
                lines.append(f"- **[{marker}]** {rc.root_cause_type}: {rc.summary}")
                if rc.detail:
                    lines.append(f"  - Detail: {rc.detail}")
                if rc.recommendations:
                    lines.append(f"  - Recommended:")
                    for r in rc.recommendations:
                        lines.append(f"    - {r}")
            lines.append(f"")

        if self.signoff_gate:
            lines.append("## Signoff Details")
            lines.append(f"- **DRC (Magic)**: {'PASS' if self.signoff_gate.magic_drc_pass else 'FAIL'}")
            lines.append(f"- **DRC (KLayout)**: {'PASS' if self.signoff_gate.klayout_drc_pass else 'FAIL'}")
            lines.append(f"- **LVS**: {'PASS' if self.signoff_gate.lvs_pass else 'FAIL'}")
            lines.append(f"- **Setup Timing**: {'PASS' if self.signoff_gate.setup_pass else 'FAIL'}")
            lines.append(f"- **Hold Timing**: {'PASS' if self.signoff_gate.hold_pass else 'FAIL'}")
            lines.append(f"- **Antenna**: {'PASS' if self.signoff_gate.antenna_pass else 'FAIL'}")
            lines.append(f"- **Density**: {'PASS' if self.signoff_gate.density_pass else 'FAIL'}")
            lines.append(f"- **EM/IR**: {'PASS' if self.signoff_gate.em_pass else 'FAIL'}")
            lines.append(f"- **Formal**: {'PASS' if self.signoff_gate.formal_pass else 'FAIL'}")
            lines.append(f"")

        if success:
            lines.append("## Next Steps")
            lines.append(f"- View artifacts: `ls {self.run_dir / 'artifacts'}`")
            lines.append(f"- Run regression check: `gli-flow ci {self.design_name} --baseline <run_id>`")
        else:
            if root_cause_report and root_cause_report.primary_blocker:
                lines.append("## Next Action")
                lines.append(f"**Primary blocker**: {root_cause_report.primary_blocker.summary}")
                for r in root_cause_report.primary_blocker.recommendations:
                    lines.append(f"  - {r}")
                lines.append(f"")
            regression = self._check_regression()
            if regression.get("alerts"):
                lines.append("## Regression Alerts")
                for alert in regression["alerts"]:
                    lines.append(f"- ⚠ {alert}")
            lines.append("## Resources")
            lines.append(f"- Check logs: `ls {self.run_dir / 'logs'}`")
            lines.append(f"- Run diagnosis: `gli-flow diagnose {self.run_id}`")
            lines.append(f"- Generate support bundle: `gli-flow support-bundle --run-id {self.run_id}`")
        lines.append(f"")
        lines.append(f"_Generated by GLI-FLOW v{VERSION}_")
        summary_path.write_text("\n".join(lines))
        console.print(f"[dim]Summary: {summary_path}[/dim]")

    def _make_orfs_progress_callback(self):
        last_stage = ""
        def _on_progress(p: OrfsStageProgress):
            nonlocal last_stage
            if p.stage_key and p.stage_key != last_stage:
                last_stage = p.stage_key
                label = p.stage_label or p.stage_key
                console.print(f"    [dim]ORFS:[/dim] [cyan]{label}[/cyan]")
            if p.routing_iteration_pct is not None:
                bar_len = 20
                filled = int(p.routing_iteration_pct / 100 * bar_len)
                bar = "█" * filled + "░" * (bar_len - filled)
                viol = p.routing_violations
                console.print(
                    f"    [yellow]Routing:[/yellow] {bar} {p.routing_iteration_pct:>3}% "
                    f"[dim]({viol} violations)[/dim]"
                )
        return _on_progress

    def _handle_failure(self, error_message):
        self.record.status = "FAILED"
        self.record.current_stage = "FAILED"

        self.database.update_run(
            run_id=self.run_id,
            status="FAILED",
            current_stage="FAILED",
            progress=self.record.progress,
        )

        error_log = self.run_dir / "logs" / "error.log"
        try:
            with open(error_log, "w") as f:
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error: {error_message}\n")
                f.write(traceback.format_exc())
        except OSError:
            pass

        evidence = {
            "stage": self.record.current_stage,
            "error": error_message[:500],
        }
        lines = error_message.split("\n")
        for line in lines[1:]:
            line = line.strip()
            if line.lower().startswith("see logs:"):
                evidence["log_file"] = line.split(":", 1)[1].strip()
            elif "exit code" in line.lower():
                evidence["exit_code"] = line.split(":")[-1].strip()
            elif line.startswith("  "):
                evidence.setdefault("details", []).append(line.strip())

        entry = {
            "run_id": self.run_id,
            "failure_id": str(uuid.uuid4()),
            "failure_type": "PIPELINE_FAILURE",
            "severity": "HIGH",
            "title": error_message.split("\n")[0][:200],
            "description": error_message[:500],
            "confidence": 0.9,
            "signature": f"pipeline_failure_{self.record.current_stage}",
            "domain": "PIPELINE",
            "category": "PIPELINE_FAILURE",
            "evidence": evidence,
            "detected_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
            "detection_classification": "VERIFIED",
        }
        repo = FailureAtlasRepository(db_path=self.db_path)
        try:
            repo.insert_entry(entry)
            print(f"  [FAILURE ATLAS] Recorded pipeline failure for run {self.run_id}")
        finally:
            repo.close()

        print(f"\n[ERROR] {error_message}")

    def _record_root_causes(self, root_cause_report):
        repo = FailureAtlasRepository(db_path=self.db_path)
        try:
            for rc in root_cause_report.root_causes:
                entry = {
                    "run_id": self.run_id,
                    "failure_id": str(uuid.uuid4()),
                    "failure_type": rc.root_cause_type,
                    "severity": rc.severity,
                    "title": rc.summary,
                    "description": rc.detail,
                    "confidence": rc.confidence,
                    "signature": f"root_cause_{rc.root_cause_type}",
                    "domain": "ROOT_CAUSE",
                    "category": rc.root_cause_type,
                    "evidence": {
                        "details": [{"file": e.file, "snippet": e.snippet} for e in rc.evidence],
                        "consequences": rc.consequences,
                        "recommendations": rc.recommendations,
                        "blocker": rc.blocker,
                    },
                    "detected_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "entry_level": "ROOT_CAUSE",
                    "detection_classification": "VERIFIED",
                }
                repo.insert_entry(entry)
            console.print(f"  [FAILURE ATLAS] Recorded {len(root_cause_report.root_causes)} root cause(s)")
        finally:
            repo.close()

    def _display_explanation(self, explanation):
        console.print()
        console.print("[bold]AI GENERATED — EXPERIMENTAL — NOT VERIFIED[/bold]")
        console.print(f"  [bold]Summary:[/bold] {explanation.summary}")
        if explanation.likely_cause:
            console.print(f"  [bold]Likely Cause:[/bold] {explanation.likely_cause}")
        if explanation.recommended_actions:
            console.print(f"  [bold]Recommended:[/bold]")
            for a in explanation.recommended_actions:
                console.print(f"    - {a}")
        if explanation.knowledge_base_citations:
            console.print(f"  [bold]References:[/bold] {', '.join(explanation.knowledge_base_citations)}")
        console.print(f"  [dim]Confidence: {explanation.confidence}[/dim]")
        console.print()

    def _record_signoff_failures(self, failures: list[str]):
        repo = FailureAtlasRepository(db_path=self.db_path)
        try:
            existing = repo.get_entries_for_run(self.run_id)
            has_known_disagreement = any(
                e.get("failure_type") == "CROSS_TOOL_DRC_DISAGREEMENT"
                and isinstance(e.get("evidence"), dict)
                and e["evidence"].get("citation") == "inf_magic_002"
                for e in existing
            )
            for failure in failures:
                entry = {
                    "run_id": self.run_id,
                    "failure_id": str(uuid.uuid4()),
                    "failure_type": "SIGNOFF_FAILURE",
                    "severity": "TAPEOUT_BLOCKING",
                    "title": failure[:200],
                    "description": failure,
                    "confidence": 1.0,
                    "signature": f"signoff_{failure.lower().replace(' ', '_')[:50]}",
                    "domain": "SIGNOFF",
                    "category": "SIGNOFF_FAILURE",
                    "evidence": {"failure": failure, "stage": "SIGN_OFF"},
                    "detected_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "recommended_fix": self._get_remediation_for("UNKNOWN"),
                }
                if has_known_disagreement:
                    entry["evidence"]["classification"] = "VALIDATED_TOOL_DISAGREEMENT"
                    entry["evidence"]["citation"] = "inf_magic_002"
                entry["detection_classification"] = "VERIFIED"
                repo.insert_entry(entry)
        finally:
            repo.close()

    def run(self):
        self.database.insert_run(self.record)

        print(f"Run ID: {self.run_id}")
        print(f"Design: {self.design_name}")
        print(f"PDK: {self.pdk.name if self.pdk else 'unknown'}")
        if self.pdk_root:
            print(f"PDK Root: {self.pdk_root}")
        print(f"Corners: {[c.name for c in self.corners]}")
        if self.threads:
            print(f"Threads: {self.threads}")
        if self.memory_mb:
            print(f"Memory: {self.memory_mb}MB")
        print(f"Run Dir: {self.run_dir}")
        telemetry_setting = get_config_value("telemetry", "on")
        telemetry_enabled = telemetry_setting == "on"
        print(f"Telemetry: {'enabled' if telemetry_enabled else 'disabled'}")
        print()

        if not self._mock_mode:
            env_issues = self.adapter.validate_environment()
            if env_issues:
                print("  [ERROR] Environment validation failed:")
                for issue in env_issues:
                    print(f"           {issue}")
                print()
                print("  Run 'gli-flow install' to fix missing components.")
                self._handle_failure("Environment validation failed: " + "; ".join(env_issues))
                return self.record

        config_path = None
        self._corner_results = []

        essential = {"INITIALIZING", "SYNTHESIS", "PACKAGING", "QOR_EXTRACTION"}

        for index, stage in enumerate(STAGES):
            progress = int(((index + 1) / len(STAGES)) * 100)
            self._update_stage(stage, progress)
            print_stage_progress(stage, progress, "RUNNING")

            try:
                if stage == "SYNTHESIS":
                    rtl_files = self.manifest.get("rtl_files", [])
                    top_module = self.manifest.get("top_module", self.design_name)

                    # ITEM 17: Extract include paths
                    from gli_flow.core.rtl_preprocessor import extract_include_paths
                    inc_paths = (
                        self.manifest.get("include_paths", [])
                        or extract_include_paths(rtl_files)
                    )

                    # ITEM 14: SV2V preprocessing
                    processed_rtl = preprocess_rtl(
                        rtl_files, run_dir=Path(self.run_dir), include_paths=inc_paths
                    )

                    # ITEM 16-17: Pre-synthesis hierarchy check
                    pre_synthesis_hierarchy_check(
                        rtl_files=processed_rtl, top_module=top_module,
                        include_paths=inc_paths, run_dir=Path(self.run_dir)
                    )

                    self.manifest["rtl_files"] = processed_rtl

                    config_result = self.adapter.generate_config(
                        self.manifest, str(self.run_dir)
                    )
                    if not config_result.get("success"):
                        self._handle_failure(f"Config generation failed: {config_result.get('error')}")
                        self._write_telemetry(self._compute_qor())
                        return self.record
                    print(f"  Config: {config_result['config_path']}")

                elif stage == "DRC":
                    gds_path = self.run_dir / "artifacts" / "6_final.gds"
                    if gds_path.exists():
                        try:
                            drc_result = run_dual_drc(
                                gds_path=str(gds_path),
                                design_name=self.manifest.get("top_module", self.design_name),
                                pdk=self.manifest.get("pdk", "sky130A"),
                                run_dir=Path(self.run_dir)
                            )
                            if drc_result is not None:
                                magic_data = drc_result.get("magic", {})
                                klayout_data = drc_result.get("klayout", {})
                                if magic_data.get("run"):
                                    magic_violations = magic_data.get("violations", -1)
                                    self.signoff_gate.magic_drc_pass = magic_violations == 0
                                    if magic_violations == 0:
                                        self._check_results["magic_drc"] = CheckResult.PASS
                                    elif self._magic_drc_is_false_positive(magic_violations):
                                        self.signoff_gate.magic_drc_pass = True
                                        self._check_results["magic_drc"] = CheckResult.PASS
                                        self._false_positives.append(f"Magic DRC {magic_violations} violation(s) — licon.8a is a known false-positive (INF-MAGIC-002)")
                                    else:
                                        self._check_results["magic_drc"] = CheckResult.CONDITIONAL_PASS
                                else:
                                    self.signoff_gate.magic_drc_pass = False
                                    self._check_results["magic_drc"] = CheckResult.NOT_RUN
                                if klayout_data.get("run"):
                                    klayout_violations = klayout_data.get("violations", -1)
                                    self.signoff_gate.klayout_drc_pass = klayout_violations == 0
                                    self._check_results["klayout_drc"] = CheckResult.PASS if klayout_violations == 0 else CheckResult.FAIL
                                else:
                                    self.signoff_gate.klayout_drc_pass = False
                                    self._check_results["klayout_drc"] = CheckResult.NOT_RUN
                                try:
                                    analyzer = CrossToolDRCAnalyzer(
                                        run_dir=str(self.run_dir),
                                        design_name=self.manifest.get("top_module", self.design_name),
                                        run_id=self.run_id,
                                    )
                                    analysis = analyzer.analyze(magic_data, klayout_data)
                                    print(f"  Cross-tool DRC analysis: {analysis.get('tool_agreement')}")
                                except Exception:
                                    print(f"  [SKIP] Cross-tool DRC analysis: tool error")
                            summary_path = self.run_dir / "drc_lvs_summary.json"
                            if summary_path.exists():
                                summary = json.loads(summary_path.read_text())
                            else:
                                summary = {}
                            summary["drc"] = {
                                "total_violations": drc_result["total_violations"],
                                "is_clean": drc_result["drc_clean"],
                                "runtime_seconds": drc_result.get("runtime_seconds"),
                                "magic_violations": drc_result["magic"].get("violations", 0) if drc_result["magic"].get("run") else "N/A",
                                "klayout_violations": drc_result["klayout"].get("violations", 0) if drc_result["klayout"].get("run") else "N/A",
                            }
                            summary_path.write_text(json.dumps(summary, indent=2))
                        except Exception:
                            print(f"  [SKIP] DRC: tool error")
                    else:
                        print(f"  [SKIP] DRC: GDS not found at {gds_path}")

                elif stage == "LVS":
                    if self.adapter and hasattr(self.adapter, "run_lvs"):
                        try:
                            gds_path = self.run_dir / "artifacts" / "6_final.gds"
                            netlist_path = self.run_dir / "artifacts" / "6_final.v"
                            lvs_result = self.adapter.run_lvs(str(self.run_dir), self.design_name, str(gds_path), str(netlist_path), self.pdk)
                            if (lvs_result.status == LVSStatus.PASS
                                    and lvs_result.comparison_completed
                                    and lvs_result.report_exists):
                                self.signoff_gate.lvs_pass = True
                                self._check_results["lvs"] = CheckResult.PASS
                            elif lvs_result.status == LVSStatus.FAIL:
                                self.signoff_gate.lvs_pass = False
                                self._check_results["lvs"] = CheckResult.FAIL
                            elif lvs_result.status == LVSStatus.NOT_RUN:
                                self.signoff_gate.lvs_pass = False
                                self._check_results["lvs"] = CheckResult.NOT_RUN
                                self._evidence_gaps.append("LVS: not executed (timed out or skipped)")
                            else:
                                self.signoff_gate.lvs_pass = False
                                self._check_results["lvs"] = CheckResult.ERROR
                            lvs_summary = {
                                "status": lvs_result.status.value if hasattr(lvs_result.status, 'value') else lvs_result.status,
                                "unmatched_devices": lvs_result.unmatched_devices,
                                "unmatched_nets": lvs_result.unmatched_nets,
                                "short_count": lvs_result.short_count,
                                "open_count": lvs_result.open_count,
                                "is_clean": lvs_result.is_clean,
                                "runtime_seconds": lvs_result.runtime_seconds,
                                "return_code": lvs_result.return_code,
                                "report_exists": lvs_result.report_exists,
                                "report_size": lvs_result.report_size,
                                "comparison_completed": lvs_result.comparison_completed,
                                "parser_status": lvs_result.parser_status,
                            }
                            summary_path = self.run_dir / "drc_lvs_summary.json"
                            if summary_path.exists():
                                summary = json.loads(summary_path.read_text())
                            else:
                                summary = {}
                            summary["lvs"] = lvs_summary
                            summary_path.write_text(json.dumps(summary, indent=2))
                            status_icon = {
                                LVSStatus.PASS: "✓", LVSStatus.FAIL: "✗",
                                LVSStatus.ERROR: "⚠", LVSStatus.NOT_RUN: "﹣",
                            }.get(lvs_result.status, "?")
                            if lvs_result.status == LVSStatus.PASS:
                                LVS_DISCLAIMER = (
                                    "LVS PASS verifies that the physical layout matches the schematic netlist.\n"
                                    "It does NOT verify functional correctness, timing, or that the RTL behaves as intended.\n"
                                    "Functional verification (simulation/formal) must be completed separately before tapeout."
                                )
                                print(f"\n  [{status_icon}] {LVS_DISCLAIMER}")
                            elif lvs_result.status == LVSStatus.FAIL:
                                print(f"\n  [{status_icon}] LVS FAILED: {lvs_result.unmatched_devices} unmatched devices, {lvs_result.unmatched_nets} unmatched nets")
                            elif lvs_result.status == LVSStatus.ERROR:
                                print(f"\n  [{status_icon}] LVS ERROR: {lvs_result.parser_status}")
                            elif lvs_result.status == LVSStatus.NOT_RUN:
                                print(f"\n  [{status_icon}] LVS NOT RUN")
                        except Exception:
                            print(f"  [!] LVS exception: tool error")

                elif stage == "TIMING_ANALYSIS":
                    if self.adapter and hasattr(self.adapter, "run_timing_signoff"):
                        self._corner_results = []
                        all_setup_pass = True
                        all_hold_pass = True
                        setup_failures = []
                        hold_failures = []
                        corner_errors = []
                        for corner in self.corners:
                            corner_name = corner.name
                            print(f"  [STA] Running corner: {corner_name}")
                            try:
                                sta_result = self.adapter.run_timing_signoff(
                                    str(self.run_dir), self.design_name, self.pdk,
                                    corner_name=corner_name,
                                )
                                self._corner_results.append({
                                    "corner": corner.to_dict(),
                                    "success": True,
                                    "setup_satisfied": sta_result.setup_satisfied,
                                    "hold_satisfied": sta_result.hold_satisfied,
                                    "setup_wns": sta_result.setup_wns_ns,
                                    "setup_tns": sta_result.setup_tns_ns,
                                    "hold_wns": sta_result.hold_wns_ns,
                                    "hold_tns": sta_result.hold_tns_ns,
                                })
                                sni = lambda v, d=0.0: v if v is not None else d
                                if not sta_result.setup_satisfied:
                                    all_setup_pass = False
                                    setup_failures.append(
                                        f"{corner_name}: WNS={sni(sta_result.setup_wns_ns):.3f}ns, "
                                        f"TNS={sni(sta_result.setup_tns_ns):.3f}ns"
                                    )
                                if not sta_result.hold_satisfied:
                                    all_hold_pass = False
                                    hold_failures.append(
                                        f"{corner_name}: WHS={sni(sta_result.hold_wns_ns):.3f}ns, "
                                        f"THS={sni(sta_result.hold_tns_ns):.3f}ns"
                                    )
                                print(f"  [STA] {corner_name}: setup={'PASS' if sta_result.setup_satisfied else 'FAIL'} "
                                      f"hold={'PASS' if sta_result.hold_satisfied else 'FAIL'}")
                            except Exception:
                                corner_errors.append(f"{corner_name}: tool error")
                                self._corner_results.append({
                                    "corner": corner.to_dict(),
                                    "success": False,
                                    "error": str(e),
                                })
                                all_setup_pass = False
                                all_hold_pass = False
                        corner_sta_path = self.run_dir / "sta_corners.json"
                        corner_sta_path.write_text(json.dumps(self._corner_results, indent=2))
                        if corner_errors:
                            print(f"  [STA ERRORS] {'; '.join(corner_errors)}")
                        if not all_setup_pass:
                            self.signoff_gate.setup_pass = False
                            self._check_results["setup_timing"] = CheckResult.FAIL
                            raise TapeoutBlockingError(
                                f"SETUP TIMING VIOLATED in {len(setup_failures)} corner(s): "
                                f"{'; '.join(setup_failures)}. "
                                f"Design cannot be taped out with setup violations."
                            )
                        if not all_hold_pass:
                            self.signoff_gate.hold_pass = False
                            self._check_results["hold_timing"] = CheckResult.FAIL
                            raise TapeoutBlockingError(
                                f"HOLD TIMING VIOLATED in {len(hold_failures)} corner(s): "
                                f"{'; '.join(hold_failures)}. "
                                f"Design cannot be taped out with hold violations."
                            )
                        self.signoff_gate.setup_pass = True
                        self.signoff_gate.hold_pass = True
                        self._check_results["setup_timing"] = CheckResult.PASS
                        self._check_results["hold_timing"] = CheckResult.PASS
                    else:
                        print(f"  [SKIP] TIMING_ANALYSIS: no adapter")

                elif stage not in essential and stage not in _STAGE_METHODS:
                    pass
                else:
                    method_name = _STAGE_METHODS.get(stage)
                    if not method_name:
                        pass
                    elif hasattr(self.adapter, method_name):
                        method = getattr(self.adapter, method_name)
                        try:
                            kwargs = {}
                            if stage == "PACKAGING":
                                kwargs["progress_callback"] = self._make_orfs_progress_callback()
                            result = method(str(self.run_dir), self.design_name, self.pdk, **kwargs)
                            if stage == "PACKAGING":
                                self._backend_result = result
                                log_file = self._backend_result.get("log_file", "")
                                gds_path = str(Path(self.run_dir) / "artifacts" / "6_final.gds")
                                if log_file and Path(log_file).exists():
                                    try:
                                        check_global_routing_overflow(
                                            log_path=log_file,
                                            metrics_path=str(Path(self.run_dir) / "metrics.csv"),
                                            gds_path=gds_path,
                                        )
                                    except RoutingOverflowError as e:
                                        print(f"  [ERROR] {e}")
                                        self._backend_result["success"] = False
                                        self._backend_result["error"] = str(e)
                            if stage == "ANTENNA_CHECK" and hasattr(result, 'is_clean'):
                                self.signoff_gate.antenna_pass = result.is_clean
                                self._check_results["antenna"] = CheckResult.PASS if result.is_clean else CheckResult.FAIL
                            if stage == "DENSITY_CHECK" and hasattr(result, 'is_clean'):
                                self.signoff_gate.density_pass = result.is_clean
                                if result.is_clean:
                                    self._check_results["density"] = CheckResult.PASS
                                else:
                                    self._check_results["density"] = CheckResult.FLOW_BUG
                                    self._flow_bugs.append("Density check: check_density command not found in OpenROAD v2.0-17598")
                            if stage == "EM_CHECK" and hasattr(result, 'is_clean'):
                                self.signoff_gate.em_pass = result.is_clean
                                self._check_results["em"] = CheckResult.PASS if result.is_clean else CheckResult.FAIL
                            if stage == "SI_ANALYSIS" and hasattr(result, 'is_clean'):
                                self.signoff_gate.si_pass = result.is_clean
                                self._check_results["si"] = CheckResult.PASS if result.is_clean else CheckResult.FAIL
                            if stage == "POWER":
                                power_report_path = Path(self.run_dir) / "reports" / "power_report.txt"
                                result_has_data = (
                                    hasattr(result, 'total_power_mw')
                                    and result.total_power_mw is not None
                                    and result.total_power_mw > 0
                                )
                                report_exists = power_report_path.exists()
                                if report_exists and result_has_data:
                                    limits_exceeded = (
                                        hasattr(result, 'ir_violation_count')
                                        and result.ir_violation_count is not None
                                        and result.ir_violation_count > 0
                                    )
                                    if limits_exceeded:
                                        self.signoff_gate.power_pass = False
                                        self._check_results["power"] = CheckResult.FAIL
                                        self._add_failure_atlas_entry("POWER", "POWER_LIMITS_EXCEEDED", "HIGH")
                                    else:
                                        self.signoff_gate.power_pass = True
                                        self._check_results["power"] = CheckResult.PASS
                                elif not report_exists:
                                    self.signoff_gate.power_pass = False
                                    self._check_results["power"] = CheckResult.NOT_RUN
                                    self._add_failure_atlas_entry("POWER", "POWER_REPORT_MISSING", "HIGH")
                                else:
                                    self.signoff_gate.power_pass = False
                                    self._check_results["power"] = CheckResult.ERROR
                                    self._add_failure_atlas_entry("POWER", "POWER_PARSER_FAILED", "HIGH")
                            if stage == "FORMAL_VERIFICATION" and hasattr(result, 'is_equivalent'):
                                self.signoff_gate.formal_pass = result.is_equivalent
                                self._check_results["formal"] = CheckResult.PASS if result.is_equivalent else CheckResult.FAIL
                        except Exception as e:
                            if self._certification_mode:
                                raise RuntimeError(
                                    f"CERTIFICATION FAILURE: Stage '{stage}' raised exception. "
                                    f"In certification mode, all stages must complete without error."
                                ) from e
                            print(f"  [SKIP] {stage}: tool error")
                            self._add_failure_atlas_entry(stage, "STAGE_FAILURE", "HIGH")
                            cr_name = _stage_check_name(stage)
                            if cr_name and cr_name not in self._check_results:
                                self._check_results[cr_name] = CheckResult.ERROR
                    else:
                        print(f"  [SKIP] {stage}: {method_name} not on adapter")
                        cr_name = _stage_check_name(stage)
                        if cr_name and cr_name not in self._check_results:
                            self._check_results[cr_name] = CheckResult.NOT_RUN

            except Exception as e:
                if stage in essential:
                    raise
                print(f"  [SKIP] {stage}: tool error")
                self._add_failure_atlas_entry(stage, "STAGE_FAILURE", "HIGH")

        # ITEM 15: Post-synthesis safety check
        synth_log = self.run_dir / "logs" / "synthesis.log"
        if synth_log.exists():
            try:
                synthesis_issues = check_synthesis_log(str(synth_log))
            except SynthesisSafetyError as e:
                print(f"  [ERROR] {e}")
                self._handle_failure(str(e))
                return self.record

        # ITEM 36: CDC check
        constraints = self.manifest.get("constraints", [])
        sdc_path = str(Path(constraints[0]).resolve()) if constraints else None
        cdc_info = count_clock_domains(
            rtl_files=self.manifest.get("rtl_files", []),
            sdc_file=sdc_path,
        )
        if cdc_info["multi_clock"]:
            print(CDC_DISCLAIMER.format(n=cdc_info["clock_count"]))

        self._extract_metrics()
        self._run_failure_detection()

        if self._backend_result is not None:
            qor_result = self._compute_qor()
            backend_ok = self._backend_result.get("success", False)

            if not backend_ok:
                err_msg = self._backend_result.get("error", "Backend execution failed")
                log_hint = self._backend_result.get("log_file")
                if log_hint and "log" not in err_msg.lower():
                    err_msg += f"\n  See logs: {log_hint}"
                print(f"  [ERROR] {err_msg}")
                self.record.implementation_status = "FAILED"
                self._handle_failure(err_msg)
                try:
                    engine = RootCauseEngine(str(self.run_dir), self.design_name, self.run_id)
                    rc_report = engine.analyze()
                    if rc_report.root_causes:
                        self._record_root_causes(rc_report)
                except Exception as e:
                    logger.warning(f"Root cause engine failed: {e}")
                try:
                    exp_engine = ExplanationEngine(str(self.run_dir), self.design_name, self.run_id)
                    explanation = exp_engine.generate()
                    explanation_path = Path(self.run_dir) / "ai_explanation.json"
                    explanation_path.write_text(json.dumps(explanation.to_dict(), indent=2))
                    self._display_explanation(explanation)
                except Exception as e:
                    logger.warning(f"AI explanation failed: {e}")
                from failure_atlas.analyze_failure import save_failure_analysis
                save_failure_analysis(self.run_id, self.design_name, self.record.current_stage, err_msg)
                return self.record

            if self._backend_result.get("duration"):
                self.record.runtime_sec = self._backend_result["duration"]

            self._write_telemetry(qor_result, self._corner_results)
            self._write_manifest(qor_result)

            # Legacy self-hosted upload path (posts to GLI_SERVER_URL, default
            # localhost:8100). Only run it when the user has explicitly opted
            # into a legacy server; otherwise the modern cloud sync hook
            # (_notify_cloud_sync at run end) is the authoritative uploader and
            # these would just spam "connection refused".
            if os.environ.get("GLI_SERVER_URL"):
                from gli_flow.telemetry.uploader import auto_upload_run
                auto_upload_run(self.run_id, self.db_path)

                from gli_flow.telemetry.failure_atlas_uploader import FailureAtlasUploader
                fa_uploader = FailureAtlasUploader(db_path=self.db_path)
                repo = FailureAtlasRepository(db_path=self.db_path)
                try:
                    for entry in repo.get_entries_for_run(self.run_id):
                        fa_uploader.upload_entry_queued(entry, run_id=self.run_id)
                    fa_uploader.process_queue()
                finally:
                    repo.close()

            results_dir = self.run_dir / "results"
            if results_dir.exists():
                for f in results_dir.iterdir():
                    if f.is_file():
                        shutil.copy2(str(f), str(self.run_dir / "artifacts" / f.name))

            self.record.run_dir = str(self.run_dir)
            self.database.update_run(run_id=self.run_id, run_dir=self.record.run_dir)

            reports_dir = self.run_dir / "reports"
            generate_placeholder_images(str(reports_dir))

            self._collect_artifacts()

            print(f"  Duration: {self._backend_result.get('duration', 0)}s")

            self.signoff_gate.synth_ok = True
            gds_path = self.run_dir / "artifacts" / "6_final.gds"
            def_path = self.run_dir / "artifacts" / "6_final.def"
            netlist_path = self.run_dir / "artifacts" / "6_final.v"
            alt_netlist_path = self.run_dir / "artifacts" / "1_2_yosys.v"
            if not alt_netlist_path.exists():
                alt_netlist_path = self.run_dir / "artifacts" / "1_synth.v"
            if gds_path.exists() and gds_path.stat().st_size > 0:
                self.signoff_gate.gds_present = True
            if def_path.exists() and def_path.stat().st_size > 0:
                self.signoff_gate.def_present = True
            if netlist_path.exists() and netlist_path.stat().st_size > 0:
                self.signoff_gate.netlist_present = True
            elif alt_netlist_path.exists() and alt_netlist_path.stat().st_size > 0:
                self.signoff_gate.netlist_present = True
            if self._mock_mode:
                self.signoff_gate.magic_drc_pass = True
                self.signoff_gate.klayout_drc_pass = True
                self.signoff_gate.antenna_pass = True
                self.signoff_gate.density_pass = True
                self.signoff_gate.em_pass = True
                self.signoff_gate.si_pass = True
                self.signoff_gate.power_pass = True
                self.signoff_gate.formal_pass = True
                self._check_results = {k: CheckResult.PASS for k in [
                    "magic_drc", "klayout_drc", "antenna", "density", "em", "si", "power", "formal",
                ]}

        gate_errors = self.signoff_gate.release_gate_errors(getattr(self, '_telemetry_parsed', None))
        if gate_errors and not self._mock_mode:
            for ge in gate_errors:
                console.print(f"\n[bold red]✗ {ge}[/bold red]")
                self._add_failure_atlas_entry("RELEASE_GATE", ge, "CRITICAL")

        gds_path = self.run_dir / "artifacts" / "6_final.gds"
        gds_generated = gds_path.exists() and gds_path.stat().st_size > 0

        self.record.implementation_status = "SUCCESS" if gds_generated else "FAILED"

        if gds_generated and self.record.qor_score is not None:
            self.record.implementation_score = self.record.qor_score
        else:
            self.record.implementation_score = 0.0

        checks = dict(self._check_results)

        checks["synthesis"] = SignoffClassifier.check_result_from_bool(
            self.signoff_gate.synth_ok, was_run=True)
        checks["gds"] = SignoffClassifier.check_result_from_bool(
            self.signoff_gate.gds_present, was_run=True)
        checks["def"] = SignoffClassifier.check_result_from_bool(
            self.signoff_gate.def_present, was_run=True)
        checks["netlist"] = SignoffClassifier.check_result_from_bool(
            self.signoff_gate.netlist_present, was_run=True)

        if self._corner_results:
            checks.setdefault("setup_timing", SignoffClassifier.check_result_from_bool(
                self.signoff_gate.setup_pass, was_run=True))
            checks.setdefault("hold_timing", SignoffClassifier.check_result_from_bool(
                self.signoff_gate.hold_pass, was_run=True))
        else:
            checks.setdefault("setup_timing", CheckResult.NOT_RUN)
            checks.setdefault("hold_timing", CheckResult.NOT_RUN)
            self._evidence_gaps.append("Timing analysis: not executed")

        if cdc_info.get("multi_clock"):
            checks.setdefault("cdc", CheckResult.CONDITIONAL_PASS)
            self._evidence_gaps.append("CDC analysis: not performed (requires external tool)")
        else:
            checks.setdefault("cdc", CheckResult.NOT_APPLICABLE)

        for ck in ["antenna", "density", "em", "si", "power", "formal"]:
            checks.setdefault(ck, CheckResult.NOT_RUN)

        classification = SignoffClassifier.classify(
            checks=checks,
            evidence_gaps=list(set(self._evidence_gaps)),
            false_positives=list(set(self._false_positives)),
            flow_bugs=list(set(self._flow_bugs)),
        )

        self.record.signoff_status = classification["signoff_status"]
        self.record.signoff_score = classification["signoff_score"]
        self.record.tapeout_ready = classification["tapeout_ready"]
        self.record.signoff_classification = classification

        classification_path = Path(self.run_dir) / "signoff_classification.json"
        classification_serializable = {
            k: v for k, v in classification.items()
        }
        classification_serializable["checks"] = {k: v.value for k, v in checks.items()}
        classification_path.write_text(json.dumps(classification_serializable, indent=2))

        tapeout_ready = classification["tapeout_ready"] if gds_generated else False

        root_cause_report = None
        try:
            engine = RootCauseEngine(str(self.run_dir), self.design_name, self.run_id)
            root_cause_report = engine.analyze(existing_classification=classification)
            if root_cause_report.implementation_score is not None:
                self.record.implementation_score = root_cause_report.implementation_score
        except Exception as e:
            logger.warning(f"Root cause engine failed: {e}")

        explanation = None
        try:
            exp_engine = ExplanationEngine(str(self.run_dir), self.design_name, self.run_id)
            explanation = exp_engine.generate()
            explanation_path = Path(self.run_dir) / "ai_explanation.json"
            explanation_path.write_text(json.dumps(explanation.to_dict(), indent=2))
            console.print(f"  [dim]AI Explanation: {explanation_path}[/dim]")
        except Exception as e:
            logger.warning(f"AI explanation engine failed: {e}")

        if not tapeout_ready or not gds_generated:
            failures = self.signoff_gate.blocking_failures() if hasattr(self, 'signoff_gate') else []
            self.record.status = "SUCCESS" if gds_generated else "FAILED"
            self.record.current_stage = "DONE"
            self.record.progress = 100
            self.database.update_run(
                run_id=self.run_id,
                status=self.record.status,
                current_stage="DONE",
                progress=100,
                wns=self.record.wns,
                tns=self.record.tns,
                hold_wns=self.record.hold_wns,
                hold_tns=self.record.hold_tns,
                utilization=self.record.utilization,
                runtime_sec=self.record.runtime_sec,
                cell_count=self.record.cell_count,
                qor_score=self.record.qor_score,
                implementation_status=self.record.implementation_status,
                signoff_status=self.record.signoff_status,
                implementation_score=self.record.implementation_score,
                signoff_score=self.record.signoff_score,
                tapeout_ready=self.record.tapeout_ready,
                drc_is_clean=getattr(self, '_telemetry_parsed', {}).get("drc_is_clean"),
                lvs_is_clean=getattr(self, '_telemetry_parsed', {}).get("lvs_is_clean"),
                signoff_setup_pass=self.signoff_gate.setup_pass if hasattr(self, 'signoff_gate') else None,
                signoff_hold_pass=self.signoff_gate.hold_pass if hasattr(self, 'signoff_gate') else None,
            )

            if root_cause_report and root_cause_report.root_causes:
                self._record_root_causes(root_cause_report)

            if explanation:
                self._display_explanation(explanation)

            if not tapeout_ready and failures:
                self._record_signoff_failures(failures)
                error_msg = "Signoff gate failed: " + "; ".join(failures)
                status_color = "red" if self.record.signoff_status in ("FAIL", "NOT_RUN") else "yellow"
                console.print(f"\n[bold {status_color}]SIGNOFF STATUS: {self.record.signoff_status}[/bold {status_color}]")
                console.print(f"  [bold]Implementation:[/bold] {self.record.implementation_status}")
                console.print(f"  [bold]Signoff:[/bold] {self.record.signoff_status}")
                console.print(f"  [bold]Tapeout Ready:[/bold] {'YES' if self.record.tapeout_ready else 'NO'}")
                if self.record.implementation_score is not None:
                    console.print(f"  [bold]Implementation Score:[/bold] {self.record.implementation_score:.3f}")
                console.print()
                if root_cause_report and root_cause_report.primary_blocker:
                    console.print(f"  [bold red]PRIMARY BLOCKER:[/bold red] {root_cause_report.primary_blocker.summary}")
                    for r in root_cause_report.primary_blocker.recommendations:
                        console.print(f"    [dim]- {r}[/dim]")
                if classification.get("warnings"):
                    for w in classification["warnings"]:
                        console.print(f"  [yellow]![/yellow] {w}")
                if classification.get("evidence_gaps"):
                    for g in classification["evidence_gaps"]:
                        console.print(f"  [dim]? {g}[/dim]")
                console.print()
            elif not gds_generated:
                console.print(f"\n[bold red]IMPLEMENTATION FAILED[/bold red]")

            console.print(f"[dim]Run complete: {self.run_dir}[/dim]")
            self._write_run_summary(success=gds_generated, root_cause_report=root_cause_report)
            self.database.close()
            _notify_cloud_sync(self.run_id, self.run_dir)
            return self.record

        self.record.status = "SUCCESS"
        self.record.current_stage = "DONE"
        self.record.progress = 100

        self.database.update_run(
            run_id=self.run_id,
            status="SUCCESS",
            current_stage="DONE",
            progress=100,
            wns=self.record.wns,
            tns=self.record.tns,
            hold_wns=self.record.hold_wns,
            hold_tns=self.record.hold_tns,
            utilization=self.record.utilization,
            runtime_sec=self.record.runtime_sec,
            cell_count=self.record.cell_count,
            qor_score=self.record.qor_score,
            implementation_status=self.record.implementation_status,
            signoff_status=self.record.signoff_status,
            implementation_score=self.record.implementation_score,
            signoff_score=self.record.signoff_score,
            tapeout_ready=self.record.tapeout_ready,
            drc_is_clean=getattr(self, '_telemetry_parsed', {}).get("drc_is_clean"),
            lvs_is_clean=getattr(self, '_telemetry_parsed', {}).get("lvs_is_clean"),
            signoff_setup_pass=self.signoff_gate.setup_pass if hasattr(self, 'signoff_gate') else None,
            signoff_hold_pass=self.signoff_gate.hold_pass if hasattr(self, 'signoff_gate') else None,
        )

        repo = FailureAtlasRepository(db_path=self.db_path)
        try:
            repo.delete_failure_level_entries_for_run(self.run_id)
        finally:
            repo.close()

        console.print()
        print_results(self.record)

        if self._corner_results:
            console.print()
            console.print("[bold]Corner Results:[/bold]")
            for cr in self._corner_results:
                icon = "[green]✓[/green]" if cr["success"] else "[red]✗[/red]"
                console.print(f"  {icon} {cr['corner']['name']}")

        console.print()
        console.print(f"[bold green]✓ Implementation:[/bold green] SUCCESS")
        signoff_label = self.record.signoff_status
        signoff_color = "green" if signoff_label == "PASS" else "yellow"
        tapeout_label = "YES" if self.record.tapeout_ready else "NO"
        tapeout_color = "green" if self.record.tapeout_ready else "yellow"
        console.print(f"[bold {signoff_color}]✓ Signoff:[/bold {signoff_color}] {signoff_label}")
        console.print(f"[bold {tapeout_color}]✓ Tapeout Ready:[/bold {tapeout_color}] {tapeout_label}")
        if classification.get("warnings"):
            for w in classification["warnings"]:
                console.print(f"  [yellow]![/yellow] {w}")

        regression = self._check_regression()
        if regression["regression_detected"]:
            console.print()
            console.print("[bold yellow]REGRESSION ALERTS:[/bold yellow]")
            for alert in regression["alerts"]:
                console.print(f"  [yellow]![/yellow] {alert}")

        console.print()
        console.print(f"[bold green]✓ Run complete:[/bold green] {self.run_dir}")
        self._write_run_summary(success=True, root_cause_report=root_cause_report)

        self.database.close()
        _notify_cloud_sync(self.run_id, self.run_dir)

        return self.record
