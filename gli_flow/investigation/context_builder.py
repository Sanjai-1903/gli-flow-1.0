"""Investigation context builder.

Collects compact summaries from existing deterministic systems.
Never sends raw logs, RTL, netlists, GDS, or source code.
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

BLOCKED_EXTENSIONS = {
    ".v", ".vh", ".sv", ".gds", ".def", ".lef", ".lib",
    ".db", ".sdc", ".spice", ".cdl", ".lvs.v", ".bitstream",
    ".bin", ".elf",
}


class InvestigationContextBuilder:

    def __init__(self, run_dir: str):
        self.run_dir = Path(run_dir)
        self._cache: dict[str, Any] = {}

    def _read_text_safe(self, path: Path, max_len: int = 2000) -> Optional[str]:
        if not path.exists():
            return None
        try:
            text = path.read_text(errors="replace")
            if len(text) > max_len:
                text = text[:max_len] + "\n... [truncated]"
            return text
        except Exception:
            return None

    def _get_drc_summary(self) -> str:
        drc_lvs_path = self.run_dir / "drc_lvs_summary.json"
        if drc_lvs_path.exists():
            try:
                data = json.loads(drc_lvs_path.read_text())
                drc = data.get("drc", {})
                parts = []
                if drc.get("total_violations") is not None:
                    parts.append(f"Total DRC violations: {drc['total_violations']}")
                if drc.get("is_clean") is not None:
                    parts.append(f"DRC clean: {drc['is_clean']}")
                if drc.get("magic_violations") is not None:
                    parts.append(f"Magic violations: {drc['magic_violations']}")
                if drc.get("klayout_violations") is not None:
                    parts.append(f"KLayout violations: {drc['klayout_violations']}")
                if drc.get("by_rule"):
                    parts.append(f"By rule: {json.dumps(drc['by_rule'])}")
                return "; ".join(parts) if parts else "DRC summary unavailable"
            except Exception:
                pass

        magic_rpt = self.run_dir / "reports" / "magic_drc.rpt"
        if magic_rpt.exists():
            content = self._read_text_safe(magic_rpt, 500)
            if content:
                return f"Magic DRC: {len(content.splitlines())} lines"

        klayout_rpt = self.run_dir / "reports" / "klayout_drc.xml"
        if klayout_rpt.exists():
            content = self._read_text_safe(klayout_rpt, 500)
            if content:
                return "KLayout DRC report present"

        return "No DRC data available"

    def _get_lvs_summary(self) -> str:
        drc_lvs_path = self.run_dir / "drc_lvs_summary.json"
        if drc_lvs_path.exists():
            try:
                data = json.loads(drc_lvs_path.read_text())
                lvs = data.get("lvs", {})
                parts = []
                if lvs.get("result"):
                    parts.append(f"LVS result: {lvs['result']}")
                if lvs.get("is_clean") is not None:
                    parts.append(f"LVS clean: {lvs['is_clean']}")
                if lvs.get("unmatched_devices") is not None:
                    parts.append(f"Unmatched devices: {lvs['unmatched_devices']}")
                if lvs.get("unmatched_nets") is not None:
                    parts.append(f"Unmatched nets: {lvs['unmatched_nets']}")
                return "; ".join(parts) if parts else "LVS summary unavailable"
            except Exception:
                pass
        return "No LVS data available"

    def _get_timing_summary(self) -> str:
        metrics_csv = self.run_dir / "reports" / "metrics.csv"
        if metrics_csv.exists():
            try:
                lines = metrics_csv.read_text().splitlines()
                if len(lines) > 1:
                    headers = [h.strip() for h in lines[0].split(",")]
                    values = [v.strip() for v in lines[1].split(",")]
                    relevant = {}
                    for h, v in zip(headers, values):
                        if any(k in h.lower() for k in ["wns", "tns", "fmax", "hold", "setup", "tns", "wns"]):
                            relevant[h] = v
                    if relevant:
                        return json.dumps(relevant)
                    return f"Timing metrics: {len(lines) - 1} data rows"
            except Exception:
                pass
        return "No timing data available"

    def _get_pipeline_summary(self) -> str:
        error_log = self.run_dir / "logs" / "error.log"
        if error_log.exists():
            content = self._read_text_safe(error_log, 1000)
            if content:
                return content[:300]
        return "No pipeline errors"

    def _get_root_cause(self) -> str:
        engine_path = self.run_dir.parent.parent / "reliability" / "root_cause_engine.py"
        return "Root cause engine available (check database for output)"

    def _get_deterministic_explanation(self) -> Optional[str]:
        ai_exp_path = self.run_dir / "ai_explanation.json"
        if ai_exp_path.exists():
            try:
                data = json.loads(ai_exp_path.read_text())
                return data.get("summary", "")
            except Exception:
                pass
        return None

    def _get_telemetry_metrics(self) -> dict:
        metrics = {}
        metrics_csv = self.run_dir / "reports" / "metrics.csv"
        if metrics_csv.exists():
            try:
                lines = metrics_csv.read_text().splitlines()
                if len(lines) > 1:
                    headers = [h.strip() for h in lines[0].split(",")]
                    values = [v.strip() for v in lines[1].split(",")]
                    for h, v in zip(headers, values):
                        try:
                            metrics[h] = float(v) if "." in v else int(v)
                        except (ValueError, TypeError):
                            metrics[h] = v
            except Exception:
                pass
        return metrics

    def build(self) -> dict:
        telemetry = self._get_telemetry_metrics()

        context = {
            "run_id": self.run_dir.name,
            "drc_summary": self._get_drc_summary(),
            "lvs_summary": self._get_lvs_summary(),
            "timing_summary": self._get_timing_summary(),
            "pipeline_summary": self._get_pipeline_summary(),
            "telemetry": {
                "wns": telemetry.get("wns"),
                "tns": telemetry.get("tns"),
                "runtime_sec": telemetry.get("runtime_sec"),
            },
        }

        explanation = self._get_deterministic_explanation()
        if explanation:
            context["deterministic_explanation"] = explanation

        return context

    def build_for_api(self) -> tuple[dict, str]:
        context = self.build()
        summary_lines = []
        for key, value in context.items():
            if key == "telemetry":
                continue
            if value:
                summary_lines.append(f"{key}: {value}")
        if context.get("telemetry"):
            t = context["telemetry"]
            parts = []
            if t.get("wns") is not None:
                parts.append(f"WNS={t['wns']}")
            if t.get("tns") is not None:
                parts.append(f"TNS={t['tns']}")
            if t.get("runtime_sec") is not None:
                parts.append(f"runtime={t['runtime_sec']}s")
            if parts:
                summary_lines.append(f"telemetry: {', '.join(parts)}")

        context_str = "\n".join(summary_lines)
        return context, context_str
