import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from gli_flow.signoff.classifier import SignoffClassifier

logger = logging.getLogger(__name__)


ROOT_CAUSE_TYPES = [
    "DESIGN_TIMING_VIOLATION",
    "DESIGN_DRC_VIOLATION",
    "DESIGN_HOLD_VIOLATION",
    "FLOW_EXTRACTION_TIMEOUT",
    "FLOW_CONFIG_ERROR",
    "FLOW_OOM",
    "TOOL_FALSE_POSITIVE",
    "ENVIRONMENT_MISMATCH",
    "DESIGN_OVERSIZE",
    "PIPELINE_CRASH",
    "ROUTING_OVERFLOW",
    "UNKNOWN",
]


@dataclass
class EvidenceItem:
    file: str = ""
    lines: list[int] = field(default_factory=list)
    snippet: str = ""
    source: str = ""


@dataclass
class RootCause:
    root_cause_type: str
    severity: str
    summary: str
    detail: str
    confidence: float
    evidence: list[EvidenceItem] = field(default_factory=list)
    consequences: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    blocker: bool = False


@dataclass
class RootCauseReport:
    run_id: str
    design_name: str
    root_causes: list[RootCause] = field(default_factory=list)
    primary_blocker: Optional[RootCause] = None
    implementation_status: str = "NOT_STARTED"
    signoff_status: str = "NOT_RUN"
    tapeout_ready: bool = False
    implementation_score: Optional[float] = None
    signoff_score: Optional[float] = None

    def summary_lines(self) -> list[str]:
        lines = []
        lines.append(f"Implementation: {self.implementation_status}")
        lines.append(f"Signoff: {self.signoff_status}")
        lines.append(f"Tapeout Ready: {'YES' if self.tapeout_ready else 'NO'}")
        if self.implementation_score is not None:
            lines.append(f"Implementation Score: {self.implementation_score:.3f}")
        if self.signoff_score is not None:
            lines.append(f"Signoff Score: {self.signoff_score:.3f}")
        lines.append("")
        if not self.root_causes:
            lines.append("No blocking issues detected.")
            return lines
        lines.append(f"Blocking Issues ({len(self.root_causes)}):")
        for rc in self.root_causes:
            marker = "PRIMARY" if rc.blocker else "       "
            lines.append(f"  [{marker}] {rc.root_cause_type}: {rc.summary}")
            if rc.detail:
                lines.append(f"          {rc.detail}")
            for ev in rc.evidence:
                loc = f"{ev.file}" + (f":{','.join(str(l) for l in ev.lines)}" if ev.lines else "")
                lines.append(f"          Evidence: {loc}")
            if rc.recommendations:
                lines.append(f"          Recommended:")
                for r in rc.recommendations:
                    lines.append(f"            - {r}")
        lines.append("")
        lines.append("Next Steps:")
        if self.primary_blocker:
            lines.append(f"  1. Resolve: {self.primary_blocker.summary}")
            for r in self.primary_blocker.recommendations:
                lines.append(f"     - {r}")
        if self.tapeout_ready:
            lines.append("  Design is tapeout ready.")
        lines.append("")
        lines.append("Confidence: HIGH (deterministic analysis of run artifacts)")
        return lines


class RootCauseEngine:

    def __init__(self, run_dir: str, design_name: str, run_id: str):
        self.run_dir = Path(run_dir)
        self.design_name = design_name
        self.run_id = run_id

    def analyze(self, existing_classification: dict | None = None) -> RootCauseReport:
        report = RootCauseReport(
            run_id=self.run_id,
            design_name=self.design_name,
        )
        self._check_implementation_status(report)
        self._analyze_drc(report)
        self._analyze_lvs(report)
        self._analyze_timing(report)
        self._analyze_pipeline(report)
        self._check_signoff_status(report, existing_classification=existing_classification)
        self._determine_primary_blocker(report)
        return report

    def _check_implementation_status(self, report: RootCauseReport):
        gds_path = self.run_dir / "artifacts" / "6_final.gds"
        def_path = self.run_dir / "artifacts" / "6_final.def"
        gds_ok = gds_path.exists() and gds_path.stat().st_size > 0
        def_ok = def_path.exists() and def_path.stat().st_size > 0

        error_log = self.run_dir / "logs" / "error.log"
        pipeline_crashed = False
        if error_log.exists():
            text = error_log.read_text()
            if any(kw in text for kw in ["synthesis", "placement", "routing", "Backend"]):
                pipeline_crashed = True

        if gds_ok and def_ok:
            report.implementation_status = "SUCCESS"
        elif pipeline_crashed:
            report.implementation_status = "FAILED"
        else:
            report.implementation_status = "NOT_STARTED"

    def _analyze_drc(self, report: RootCauseReport):
        magic_rpt = self.run_dir / "reports" / "magic_drc.rpt"
        klayout_xml = self.run_dir / "reports" / "klayout_drc.xml"
        drc_summary = self.run_dir / "drc_lvs_summary.json"

        if not magic_rpt.exists() and not klayout_xml.exists():
            return

        total_violations = 0
        magic_violations = 0
        klayout_violations = 0
        li3_magic = 0
        li3_klayout = 0
        licon8a_magic = 0
        licon8a_klayout = 0

        if drc_summary.exists():
            try:
                data = json.loads(drc_summary.read_text())
                drc = data.get("drc", {})
                total_violations = drc.get("total_violations", 0)
                magic_violations = drc.get("magic_violations", 0)
                klayout_violations = drc.get("klayout_violations", 0)
            except (json.JSONDecodeError, KeyError):
                pass

        if magic_rpt.exists():
            text = magic_rpt.read_text()
            violations_line = ""
            for line in text.split("\n"):
                if "Total violations:" in line:
                    violations_line = line
            li3_match = len(re.findall(r'li\.3', text))
            licon8a_match = len(re.findall(r'licon\.8a', text))
            if licon8a_match == 0:
                licon8a_match = len(re.findall(r'licon', text))
            li3_magic = li3_match
            licon8a_magic = licon8a_match

        if klayout_xml.exists():
            text = klayout_xml.read_text()
            li3_klayout = text.count("<item>")
            licon8a_klayout = text.count("licon.8a")

        if total_violations > 0:
            real_count = 0
            false_positive_count = 0
            evidence_items = []
            consequences = []
            recommendations = []

            if li3_magic > 0 and li3_klayout > 0:
                real_count = min(li3_magic, li3_klayout)
            elif li3_magic > 0:
                real_count = li3_magic

            if licon8a_magic > 0 and licon8a_klayout == 0:
                false_positive_count = licon8a_magic

            if real_count > 0:
                evidence_items.append(EvidenceItem(
                    file="reports/magic_drc.rpt",
                    snippet=f"{real_count} li.3 spacing violations detected",
                    source="magic_drc",
                ))
                consequences.append("Magic DRC FAIL")
                recommendations.append("Review li.3 spacing violations in routing")
                recommendations.append("Increase wire spread factor or add routing blockages")

            if false_positive_count > 0:
                evidence_items.append(EvidenceItem(
                    file="reports/klayout_drc.xml",
                    snippet="0 licon.8a violations reported by KLayout",
                    source="klayout_drc",
                ))
                evidence_items.append(EvidenceItem(
                    file="failure_atlas/knowledge_base.json",
                    snippet="INF-MAGIC-002: Magic DRC false-positive licon.8a",
                    source="knowledge_base",
                ))
                consequences.append("INF-MAGIC-002: Known tool disagreement")
                recommendations.append("Waive licon.8a violations (known Magic false-positive)")
                recommendations.append("Cross-tool DRC validates: KLayout reports 0 licon.8a")

            if not recommendations:
                recommendations.append("Review DRC report for violation details")

            rc = RootCause(
                root_cause_type="DESIGN_DRC_VIOLATION",
                severity="TAPEOUT_BLOCKING",
                summary=f"DRC violations: {total_violations} total ({real_count} real, {false_positive_count} false-positive)" if false_positive_count else f"DRC violations: {total_violations} total",
                detail=f"Magic: {magic_violations} violations | KLayout: {klayout_violations} violations",
                confidence=1.0,
                evidence=evidence_items,
                consequences=consequences,
                recommendations=recommendations,
            )
            report.root_causes.append(rc)

    def _analyze_lvs(self, report: RootCauseReport):
        drc_summary = self.run_dir / "drc_lvs_summary.json"
        if not drc_summary.exists():
            return

        try:
            data = json.loads(drc_summary.read_text())
            lvs = data.get("lvs", {})
        except (json.JSONDecodeError, KeyError):
            return

        lvs_status = lvs.get("status", "NOT_RUN")
        runtime = lvs.get("runtime_seconds", 0)
        return_code = lvs.get("return_code", 0)
        comparison_completed = lvs.get("comparison_completed", False)

        if lvs_status == "PASS":
            return

        if return_code == -1 and runtime >= 600:
            ext_path = self.run_dir / "artifacts" / f"{self.design_name}.ext"
            ext_size_mb = 0
            if ext_path.exists():
                ext_size_mb = ext_path.stat().st_size / (1024 * 1024)

            rc = RootCause(
                root_cause_type="FLOW_EXTRACTION_TIMEOUT",
                severity="TAPEOUT_BLOCKING",
                summary=f"LVS extraction timed out after {runtime:.0f}s (limit: 600s)",
                detail=f"Extraction file size: {ext_size_mb:.1f}MB | Return code: {return_code} (killed)",
                confidence=1.0,
                evidence=[
                    EvidenceItem(file="drc_lvs_summary.json", snippet=f"runtime_seconds: {runtime}", source="lvs_summary"),
                    EvidenceItem(file="drc_lvs_summary.json", snippet=f"return_code: {return_code}", source="lvs_summary"),
                    EvidenceItem(file="drc_lvs_summary.json", snippet=f"comparison_completed: {comparison_completed}", source="lvs_summary"),
                ],
                consequences=["LVS comparison not completed", "Signoff blocked by LVS"],
                recommendations=[
                    f"Increase LVS extraction timeout (currently 600s, need >{runtime:.0f}s)",
                    "Optimize extraction: disable parasitic extraction for LVS only",
                    "Consider hierarchical extraction to reduce per-block complexity",
                    f"Extraction .ext file is {ext_size_mb:.1f}MB — review fill cell inclusion",
                ],
            )
            if report.implementation_status == "SUCCESS":
                rc.blocker = True
            report.root_causes.append(rc)

        elif lvs_status == "FAIL":
            rc = RootCause(
                root_cause_type="DESIGN_DRC_VIOLATION",
                severity="TAPEOUT_BLOCKING",
                summary=f"LVS comparison failed: {lvs.get('unmatched_devices', 0)} unmatched devices, {lvs.get('unmatched_nets', 0)} unmatched nets",
                detail=f"Shorts: {lvs.get('short_count', 0)} | Opens: {lvs.get('open_count', 0)}",
                confidence=1.0,
                evidence=[
                    EvidenceItem(file="drc_lvs_summary.json", snippet=f"unmatched_devices: {lvs.get('unmatched_devices')}", source="lvs_summary"),
                ],
                consequences=["LVS FAIL", "Signoff blocked by LVS"],
                recommendations=["Run detailed routing with soft spacing", "Check power/ground connectivity", "Verify netlist matches layout"],
            )
            report.root_causes.append(rc)

        elif lvs_status == "ERROR":
            rc = RootCause(
                root_cause_type="FLOW_CONFIG_ERROR",
                severity="TAPEOUT_BLOCKING",
                summary=f"LVS error: {lvs.get('parser_status', 'unknown error')}",
                confidence=0.9,
                evidence=[
                    EvidenceItem(file="drc_lvs_summary.json", snippet=f"parser_status: {lvs.get('parser_status')}", source="lvs_summary"),
                ],
                consequences=["LVS ERROR", "Signoff blocked by LVS"],
                recommendations=["Check PDK configuration for LVS deck", "Verify tool paths for netgen and magic"],
            )
            report.root_causes.append(rc)

    def _analyze_timing(self, report: RootCauseReport):
        signoff_setup = self.run_dir / "signoff_setup.rpt"
        signoff_hold = self.run_dir / "signoff_hold.rpt"
        drc_summary = self.run_dir / "drc_lvs_summary.json"
        metrics_csv = self.run_dir / "reports" / "metrics.csv"

        wns = None
        tns = None
        hold_wns = None

        if metrics_csv.exists():
            for line in metrics_csv.read_text().split("\n"):
                if "wns" in line and "," in line:
                    try:
                        wns = float(line.split(",")[1])
                    except (ValueError, IndexError):
                        pass

        if wns is None or wns is not None and wns < 0:
            if signoff_setup.exists():
                text = signoff_setup.read_text()
                for line in text.split("\n"):
                    if "wns" in line.lower() or "WNS" in line:
                        m = re.search(r"[-+]?\d*\.?\d+", line)
                        if m:
                            try:
                                wns = float(m.group())
                            except ValueError:
                                pass

        if hold_wns is None:
            if signoff_hold.exists():
                text = signoff_hold.read_text()
                for line in text.split("\n"):
                    if "wns" in line.lower() or "WHS" in line:
                        m = re.search(r"[-+]?\d*\.?\d+", line)
                        if m:
                            try:
                                hold_wns = float(m.group())
                            except ValueError:
                                pass

        if wns is not None and wns < 0:
            rc = RootCause(
                root_cause_type="DESIGN_TIMING_VIOLATION",
                severity="TAPEOUT_BLOCKING" if wns < -0.5 else "PERFORMANCE_DEGRADATION",
                summary=f"Setup timing violated: WNS={wns:.3f}ns" + (f", TNS={tns:.3f}ns" if tns is not None else ""),
                confidence=1.0,
                evidence=[
                    EvidenceItem(file="reports/metrics.csv", snippet=f"wns,{wns}" if metrics_csv.exists() else f"WNS: {wns}ns"),
                ],
                consequences=["Setup timing FAIL", "Signoff blocked by timing"],
                recommendations=["Increase clock period in SDC", "Pipeline insertion or retiming", "Review critical path endpoints"],
            )
            report.root_causes.append(rc)

        if hold_wns is not None and hold_wns < 0:
            rc = RootCause(
                root_cause_type="DESIGN_HOLD_VIOLATION",
                severity="TAPEOUT_BLOCKING",
                summary=f"Hold timing violated: WHS={hold_wns:.3f}ns",
                confidence=1.0,
                evidence=[
                    EvidenceItem(file="signoff_hold.rpt", snippet=f"Hold WNS: {hold_wns}ns"),
                ],
                consequences=["Hold timing FAIL", "Signoff blocked by timing"],
                recommendations=["Run hold fixing in PnR tool", "Check clock skew", "Add delay cells on fast paths"],
            )
            report.root_causes.append(rc)

    def _analyze_pipeline(self, report: RootCauseReport):
        error_log = self.run_dir / "logs" / "error.log"
        if not error_log.exists():
            return

        text = error_log.read_text().strip()
        if not text:
            return

        error_line = text.split("\n")[0] if text else ""
        if "Signoff gate failed" in text:
            return

        if any(kw in text for kw in ["Config generation failed", "Environment validation"]):
            rc = RootCause(
                root_cause_type="FLOW_CONFIG_ERROR",
                severity="TAPEOUT_BLOCKING",
                summary=error_line[:200] if error_line else "Pipeline crash",
                confidence=0.95,
                evidence=[EvidenceItem(file="logs/error.log", snippet=text[:500])],
                consequences=["Pipeline FAILED"],
                recommendations=["Check configuration and environment setup", "Run 'gli-flow doctor' to validate toolchain"],
            )
            report.root_causes.append(rc)

        elif "OOM" in text or "Out of memory" in text:
            rc = RootCause(
                root_cause_type="FLOW_OOM",
                severity="TAPEOUT_BLOCKING",
                summary="Flow ran out of memory during execution",
                confidence=0.95,
                evidence=[EvidenceItem(file="logs/error.log", snippet=text[:500])],
                consequences=["Pipeline FAILED"],
                recommendations=["Increase memory allocation", "Reduce thread count", "Use hierarchical flow for large designs"],
            )
            report.root_causes.append(rc)

    def _check_signoff_status(self, report: RootCauseReport, existing_classification: dict | None = None):
        if existing_classification is not None:
            report.signoff_status = existing_classification["signoff_status"]
            report.tapeout_ready = existing_classification["tapeout_ready"]
            report.signoff_score = existing_classification["signoff_score"]
            return

        drc_summary = self.run_dir / "drc_lvs_summary.json"
        if not drc_summary.exists():
            if report.implementation_status != "SUCCESS":
                report.signoff_status = "NOT_RUN"
            return

        has_drc_result = False
        has_lvs_result = False
        drc_clean = False
        lvs_clean = False
        try:
            data = json.loads(drc_summary.read_text())
            drc = data.get("drc", {})
            lvs = data.get("lvs", {})
            has_drc_result = "total_violations" in drc or "is_clean" in drc
            has_lvs_result = "status" in lvs
            drc_clean = drc.get("is_clean", False)
            lvs_clean = lvs.get("is_clean", False)
        except (json.JSONDecodeError, KeyError):
            pass

        if not has_drc_result and not has_lvs_result:
            report.signoff_status = "NOT_RUN"
            return

        signoff_checks_run = has_drc_result or has_lvs_result

        all_pass = drc_clean and lvs_clean if has_drc_result and has_lvs_result else False
        if has_drc_result and not has_lvs_result:
            all_pass = False

        if signoff_checks_run:
            if all_pass:
                report.signoff_status = "PASS"
            else:
                report.signoff_status = "FAIL"

        has_blocking_root_cause = any(rc.severity == "TAPEOUT_BLOCKING" for rc in report.root_causes)
        report.tapeout_ready = (
            report.implementation_status == "SUCCESS"
            and report.signoff_status == "PASS"
            and not has_blocking_root_cause
        )

        if report.implementation_status == "SUCCESS":
            report.signoff_score = 1.0 if report.signoff_status == "PASS" else 0.0

    def _determine_primary_blocker(self, report: RootCauseReport):
        if not report.root_causes:
            return

        priority_order = [
            "FLOW_CONFIG_ERROR",
            "FLOW_OOM",
            "PIPELINE_CRASH",
            "ROUTING_OVERFLOW",
            "DESIGN_TIMING_VIOLATION",
            "DESIGN_HOLD_VIOLATION",
            "DESIGN_DRC_VIOLATION",
            "FLOW_EXTRACTION_TIMEOUT",
            "TOOL_FALSE_POSITIVE",
            "ENVIRONMENT_MISMATCH",
            "DESIGN_OVERSIZE",
        ]

        for rc in report.root_causes:
            if rc.root_cause_type in priority_order:
                rc.blocker = True
                report.primary_blocker = rc
                break

        if report.primary_blocker is None and report.root_causes:
            report.root_causes[0].blocker = True
            report.primary_blocker = report.root_causes[0]
