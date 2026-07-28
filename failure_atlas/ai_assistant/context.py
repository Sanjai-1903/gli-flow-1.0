import dataclasses
import os
from pathlib import Path
from typing import Optional, Dict, Any, List


@dataclasses.dataclass
class AIContext:
    tool: str
    stage: str
    error_text: str
    log_snippet: str
    failure_type: str
    metrics: Dict[str, Any]
    design_metadata: Dict[str, Any]
    run_metadata: Dict[str, Any]
    known_evidence: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "stage": self.stage,
            "error_text": self.error_text,
            "log_snippet": self.log_snippet,
            "failure_type": self.failure_type,
            "metrics": self.metrics,
            "design_metadata": self.design_metadata,
            "run_metadata": self.run_metadata,
            "known_evidence": self.known_evidence,
        }

    def to_prompt_context(self) -> str:
        lines = [
            f"Tool: {self.tool}",
            f"Stage: {self.stage}",
            f"Failure Type: {self.failure_type}",
            "",
            "Error Text:",
            self.error_text,
            "",
            "Log Snippet (last 100 lines):",
            self.log_snippet,
            "",
        ]
        if self.metrics:
            lines.append("Metrics:")
            for k, v in self.metrics.items():
                lines.append(f"  {k}: {v}")
            lines.append("")
        if self.design_metadata:
            lines.append("Design Info:")
            for k, v in self.design_metadata.items():
                lines.append(f"  {k}: {v}")
            lines.append("")
        if self.known_evidence:
            lines.append("Known Evidence:")
            for k, v in self.known_evidence.items():
                lines.append(f"  {k}: {v}")
        return "\n".join(lines)


def build_context(
    tool: str = "",
    stage: str = "",
    error_text: str = "",
    log_snippet: str = "",
    failure_type: str = "",
    metrics: Optional[Dict[str, Any]] = None,
    design_metadata: Optional[Dict[str, Any]] = None,
    run_metadata: Optional[Dict[str, Any]] = None,
    known_evidence: Optional[Dict[str, Any]] = None,
    run_dir: Optional[str] = None,
) -> AIContext:
    """Build a context package for AI investigation.

    Collects all available information about a failure without
    including sensitive data (RTL, GDS, netlists, customer IP).
    """
    if run_dir and not log_snippet:
        log_snippet = _extract_log_snippet(run_dir)

    if run_dir and not run_metadata:
        run_metadata = _extract_run_metadata(run_dir)

    return AIContext(
        tool=tool or "",
        stage=stage or "",
        error_text=error_text or "",
        log_snippet=log_snippet or "",
        failure_type=failure_type or "UNKNOWN",
        metrics=metrics or {},
        design_metadata=design_metadata or {},
        run_metadata=run_metadata or {},
        known_evidence=known_evidence or {},
    )


def _extract_log_snippet(run_dir: str, max_lines: int = 100) -> str:
    run_path = Path(run_dir)
    if not run_path.exists():
        return ""

    log_files = sorted(run_path.rglob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    for log_file in log_files[:3]:
        try:
            lines = log_file.read_text(errors="replace").splitlines()
            snippet = lines[-max_lines:]
            return "\n".join(snippet)
        except Exception:
            continue
    return ""


def _extract_run_metadata(run_dir: str) -> Dict[str, Any]:
    run_path = Path(run_dir)
    if not run_path.exists():
        return {}

    meta = {"run_dir": str(run_dir)}

    telemetry_file = run_path / "telemetry.json"
    if telemetry_file.exists():
        try:
            import json
            data = json.loads(telemetry_file.read_text())
            meta["telemetry"] = {
                "status": data.get("flow", {}).get("status"),
                "failure_stage": data.get("flow", {}).get("failure_stage"),
            }
        except Exception:
            pass

    manifest_files = list(run_path.glob("*manifest*")) + list(run_path.glob("*.yaml"))
    for mf in manifest_files[:1]:
        try:
            meta["manifest"] = mf.name
        except Exception:
            pass

    return meta
