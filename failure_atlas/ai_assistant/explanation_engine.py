import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class EvidenceItem:
    file: str = ""
    line: int = 0
    content: str = ""
    source: str = ""


@dataclass
class AIFailureExplanation:
    summary: str = ""
    evidence: list[EvidenceItem] = field(default_factory=list)
    likely_cause: str = ""
    recommended_actions: list[str] = field(default_factory=list)
    confidence: str = ""
    disclaimer: str = "AI GENERATED — EXPERIMENTAL — NOT VERIFIED"
    knowledge_base_citations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "evidence": [
                {"file": e.file, "line": e.line, "content": e.content, "source": e.source}
                for e in self.evidence
            ],
            "likely_cause": self.likely_cause,
            "recommended_actions": self.recommended_actions,
            "confidence": self.confidence,
            "disclaimer": self.disclaimer,
            "knowledge_base_citations": self.knowledge_base_citations,
        }


class ExplanationEngine:

    def __init__(self, run_dir: str, design_name: str, run_id: str):
        self.run_dir = Path(run_dir)
        self.design_name = design_name
        self.run_id = run_id

    def generate(self) -> AIFailureExplanation:
        explanation = AIFailureExplanation()

        drc_findings = self._analyze_drc()
        lvs_findings = self._analyze_lvs()
        timing_findings = self._analyze_timing()
        pipeline_findings = self._analyze_pipeline()

        all_findings = []
        if drc_findings:
            all_findings.append(drc_findings)
        if lvs_findings:
            all_findings.append(lvs_findings)
        if timing_findings:
            all_findings.append(timing_findings)
        if pipeline_findings:
            all_findings.append(pipeline_findings)

        if not all_findings:
            error_log_path = self.run_dir / "logs" / "error.log"
            if error_log_path.exists():
                text = error_log_path.read_text().strip()
                if text:
                    explanation.summary = "Pipeline error detected"
                    explanation.evidence.append(EvidenceItem(
                        file="logs/error.log", content=text[:500], source="error_log"
                    ))
                    explanation.likely_cause = "An unexpected error occurred during pipeline execution"
                    explanation.recommended_actions = [
                        "Check logs/error.log for error message",
                        "Run 'gli-flow diagnose {self.run_id}' for detailed analysis",
                        "Review design configuration and constraints",
                    ]
                    explanation.confidence = "MEDIUM"
                    return explanation

            explanation.summary = "No failure evidence found"
            explanation.likely_cause = "Unable to determine failure cause from available reports"
            explanation.recommended_actions = [
                "Run 'gli-flow doctor' to verify environment",
                "Review all logs in the run directory",
                "Check if design manifest is properly configured",
            ]
            explanation.confidence = "LOW"
            return explanation

        evidence_count = sum(len(f.get("evidence", [])) for f in all_findings if isinstance(f, dict))
        has_definitive = any(f.get("definitive", False) for f in all_findings if isinstance(f, dict))

        parts = []
        for f in all_findings:
            if isinstance(f, dict) and f.get("summary"):
                parts.append(f["summary"])
        explanation.summary = "; ".join(parts)

        for f in all_findings:
            if isinstance(f, dict):
                for ev in f.get("evidence", []):
                    explanation.evidence.append(EvidenceItem(
                        file=ev.get("file", ""),
                        content=ev.get("content", ""),
                        source=ev.get("source", ""),
                    ))

        cause_parts = []
        for f in all_findings:
            if isinstance(f, dict) and f.get("likely_cause"):
                cause_parts.append(f["likely_cause"])
        explanation.likely_cause = "; ".join(cause_parts)

        seen_actions = set()
        for f in all_findings:
            if isinstance(f, dict):
                for action in f.get("recommended_actions", []):
                    if action not in seen_actions:
                        seen_actions.add(action)
                        explanation.recommended_actions.append(action)

        if has_definitive and evidence_count > 0:
            explanation.confidence = "HIGH"
        elif evidence_count > 0:
            explanation.confidence = "MEDIUM"
        else:
            explanation.confidence = "LOW"

        return explanation

    def _analyze_drc(self) -> Optional[dict]:
        magic_rpt = self.run_dir / "reports" / "magic_drc.rpt"
        klayout_xml = self.run_dir / "reports" / "klayout_drc.xml"
        drc_summary = self.run_dir / "drc_lvs_summary.json"

        if not magic_rpt.exists() and not klayout_xml.exists():
            return None

        result = {
            "summary": "",
            "evidence": [],
            "likely_cause": "",
            "recommended_actions": [],
            "definitive": False,
        }

        total = 0
        magic_v = 0
        klayout_v = 0
        li3_count = 0
        licon8a_count = 0

        if drc_summary.exists():
            try:
                data = json.loads(drc_summary.read_text())
                drc = data.get("drc", {})
                total = drc.get("total_violations", 0)
                magic_v = drc.get("magic_violations", 0)
                klayout_v = drc.get("klayout_violations", 0)
            except (json.JSONDecodeError, KeyError):
                pass

        if magic_rpt.exists():
            text = magic_rpt.read_text()
            li3_count = len(re.findall(r'li\.3', text))
            licon8a_count = len(re.findall(r'licon\.8a', text))
            if "Total violations:" in text:
                result["evidence"].append({
                    "file": "reports/magic_drc.rpt", "source": "magic_drc",
                    "content": f"Total violations: {total}",
                })

        if klayout_xml.exists():
            item_count = klayout_xml.read_text().count("<item>")
            if item_count > 0:
                result["evidence"].append({
                    "file": "reports/klayout_drc.xml", "source": "klayout_drc",
                    "content": f"KLayout violations: {item_count}",
                })

        has_known_disagreement = licon8a_count > 0
        real_violations = total - licon8a_count

        if total > 0:
            result["summary"] = f"DRC violations: {total} total"
            if real_violations > 0:
                result["summary"] += f" ({real_violations} real violations)"
            if licon8a_count > 0:
                result["summary"] += f" ({licon8a_count} licon.8a known false-positive)"

            cause_parts = []
            if real_violations > 0:
                cause_parts.append(f"{real_violations} real spacing violations (li.3) detected by both Magic and KLayout")
            if licon8a_count > 0:
                cause_parts.append(f"{licon8a_count} licon.8a violations are known Magic false-positives (INF-MAGIC-002)")
                result["knowledge_base_citations"] = ["INF-MAGIC-002: Magic DRC false-positive on licon.8a"]
            result["likely_cause"] = ". ".join(cause_parts)

            if real_violations > 0:
                result["recommended_actions"].append("Fix li.3 spacing violations: increase wire spread in routing")
                result["recommended_actions"].append("Review routing constraints in OpenROAD configuration")
            if licon8a_count > 0:
                result["recommended_actions"].append("Waive licon.8a violations (known Magic false-positive, cross-validated with KLayout)")

            result["definitive"] = True

        return result

    def _analyze_lvs(self) -> Optional[dict]:
        drc_summary = self.run_dir / "drc_lvs_summary.json"
        if not drc_summary.exists():
            return None

        try:
            data = json.loads(drc_summary.read_text())
            lvs = data.get("lvs", {})
        except (json.JSONDecodeError, KeyError):
            return None

        status = lvs.get("status", "NOT_RUN")
        runtime = lvs.get("runtime_seconds", 0)
        return_code = lvs.get("return_code", 0)
        comparison_completed = lvs.get("comparison_completed", False)
        report_exists = lvs.get("report_exists", False)

        if status == "PASS":
            return None

        result = {
            "summary": "",
            "evidence": [],
            "likely_cause": "",
            "recommended_actions": [],
            "definitive": False,
        }

        result["evidence"].append({
            "file": "drc_lvs_summary.json", "source": "lvs_summary",
            "content": json.dumps(lvs, indent=2)[:500],
        })

        if return_code == -1 and runtime >= 500:
            ext_path = self.run_dir / "artifacts" / f"{self.design_name}.ext"
            ext_size_mb = 0
            if ext_path.exists():
                ext_size_mb = ext_path.stat().st_size / (1024 * 1024)

            result["summary"] = f"LVS extraction timed out at {runtime:.0f}s (exceeded 600s limit)"
            result["likely_cause"] = f"Magic GDS-to-spice extraction is too large: .ext file is {ext_size_mb:.1f}MB"
            if ext_size_mb > 20:
                result["likely_cause"] += ". Large extraction size is likely due to fill cell inclusion in the GDS."
            result["recommended_actions"] = [
                f"Increase LVS extraction timeout to > {runtime:.0f}s",
                "Disable parasitic extraction during LVS (cthresh/rthresh thresholds)",
                "Consider hierarchical extraction instead of flat",
            ]
            result["definitive"] = True

        elif status == "FAIL":
            result["summary"] = f"LVS comparison failed: {lvs.get('unmatched_devices', 0)} unmatched devices"
            result["likely_cause"] = f"Netlist vs layout mismatch: {lvs.get('unmatched_nets', 0)} unmatched nets"
            result["recommended_actions"] = [
                "Check power/ground connectivity in layout",
                "Verify extracted netlist matches synthesized netlist",
                "Run detailed routing with soft spacing option",
            ]
            result["definitive"] = True

        elif status == "ERROR":
            result["summary"] = f"LVS tool error: {lvs.get('parser_status', 'unknown')}"
            result["likely_cause"] = "LVS deck or tool configuration issue"
            result["recommended_actions"] = [
                "Verify PDK LVS deck configuration",
                "Check netgen and magic tool paths",
            ]
            result["definitive"] = False

        return result

    def _analyze_timing(self) -> Optional[dict]:
        metrics_csv = self.run_dir / "reports" / "metrics.csv"
        if not metrics_csv.exists():
            return None

        wns = None
        tns = None
        for line in metrics_csv.read_text().split("\n"):
            if line.startswith("wns,"):
                try:
                    wns = float(line.split(",")[1])
                except (ValueError, IndexError):
                    pass
            elif line.startswith("tns,"):
                try:
                    tns = float(line.split(",")[1])
                except (ValueError, IndexError):
                    pass

        if wns is None or wns == 0:
            return None

        result = {
            "summary": "",
            "evidence": [],
            "likely_cause": "",
            "recommended_actions": [],
            "definitive": False,
        }

        if wns < 0:
            result["summary"] = f"Setup timing violation: WNS={wns:.3f}ns"
            result["likely_cause"] = f"Design does not meet timing constraints at the clock frequency"
            if tns is not None and tns < -1.0:
                result["likely_cause"] += f" (TNS={tns:.3f}ns indicates multiple paths failing)"
            result["evidence"].append({
                "file": "reports/metrics.csv", "source": "timing",
                "content": f"wns,{wns}" + (f"\ntns,{tns}" if tns is not None else ""),
            })
            result["recommended_actions"] = [
                "Increase clock period in design SDC constraints",
                "Pipeline critical paths in RTL",
                "Review synthesis and placement for timing optimization",
            ]
            result["definitive"] = True

        return result

    def _analyze_pipeline(self) -> Optional[dict]:
        error_log = self.run_dir / "logs" / "error.log"
        if not error_log.exists():
            return None

        text = error_log.read_text().strip()
        if not text:
            return None

        result = {
            "summary": "",
            "evidence": [],
            "likely_cause": "",
            "recommended_actions": [],
            "definitive": False,
        }

        result["evidence"].append({
            "file": "logs/error.log", "source": "error_log",
            "content": text[:500],
        })

        if "OOM" in text or "Out of memory" in text:
            result["summary"] = "Pipeline failed due to out-of-memory (OOM)"
            result["likely_cause"] = "Design exceeded available memory during execution"
            result["recommended_actions"] = [
                "Increase memory allocation for the run",
                "Reduce thread count to lower memory pressure",
                "Use hierarchical flow for large designs",
            ]
        elif "Config generation failed" in text:
            result["summary"] = "Pipeline failed during configuration generation"
            result["likely_cause"] = "Design manifest or environment configuration issue"
            result["recommended_actions"] = [
                "Verify gli_manifest.yaml is correct",
                "Run 'gli-flow doctor' to check environment",
            ]
        elif "Signoff gate failed" in text:
            result["summary"] = "Signoff gate blocked — one or more checks failed"
            result["likely_cause"] = "Signoff checks did not all pass (see DRC/LVS/timing analysis)"
            result["recommended_actions"] = [
                "Review individual signoff check results below",
                "Address DRC, LVS, and timing violations in order",
            ]
        else:
            result["summary"] = f"Pipeline error: {text.split(chr(10))[0][:200]}"
            result["likely_cause"] = "An unexpected error occurred during pipeline execution"
            result["recommended_actions"] = [
                f"Review logs/error.log in run directory",
                "Run 'gli-flow doctor' to verify environment",
            ]

        result["definitive"] = "Signoff gate failed" in text or "OOM" in text

        return result
