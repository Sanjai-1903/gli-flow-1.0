from __future__ import annotations

import logging
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from gli_flow.core.subprocess_env import safe_env


logger = logging.getLogger(__name__)


STAGE_LABELS: Dict[str, str] = {
    "1_1_yosys_canonicalize": "Yosys Synth (canonicalize)",
    "1_2_yosys":              "Yosys Synth",
    "2_1_floorplan":          "Floorplan",
    "2_2_floorplan_macro":    "Floorplan (macro)",
    "2_3_floorplan_tapcell":  "Floorplan (tapcell)",
    "2_4_floorplan_pdn":      "Floorplan (PDN)",
    "3_1_place_gp_skip_io":   "Global Place (skip IO)",
    "3_2_place_iop":          "IO Placement",
    "3_3_place_gp":           "Global Placement",
    "3_4_place_resized":      "Placement (resize)",
    "3_5_place_dp":           "Detail Placement",
    "3_6_place_repair_timing":"Placement (timing repair)",
    "4_1_cts":                "Clock Tree Synth",
    "5_1_grt":                "Global Route",
    "5_2_route":              "Detail Route",
    "5_3_fillcell":           "Fill Cell",
    "6_1_fill":               "Density Fill",
    "6_report":               "Final Report",
}

_RE_STAGE_START = re.compile(r"Running\s+\S+\.tcl,\s*stage\s+(\S+)")
_RE_ROUTING_ITER = re.compile(r"(?:Completing|Completed)\s*(\d+)%\s*with\s*(\d+)\s*violations?")
_RE_DRC_VIOLATION = re.compile(r"(\d+)\s+DRC\s+violations?\s*$", re.IGNORECASE)
_RE_ROUTING_DRC = re.compile(r"(\d+)\s+violations?\s+after\s+routing")


@dataclass
class OrfsStageProgress:
    stage_key: str = ""
    stage_label: str = ""
    progress_pct: float = 0.0
    routing_iteration_pct: Optional[int] = None
    routing_violations: Optional[int] = None
    drc_violations: Optional[int] = None
    drc_trend: Optional[str] = None
    elapsed_sec: float = 0.0
    idle_sec: float = 0.0
    stage_elapsed_sec: float = 0.0


class OrfsMonitor:

    def __init__(
        self,
        flow_dir: str,
        platform: str,
        design_name: str,
    ):
        self._flow_dir = Path(flow_dir)
        self._platform = platform
        self._design_name = design_name
        self._orfs_log_dir = self._flow_dir / "logs" / platform / design_name / "base"

        self._current_stage = ""
        self._stage_start_time = 0.0
        self._process_start_time = 0.0
        self._last_line_time = 0.0
        self._routing_iterations: List[Tuple[int, int]] = []
        self._routing_poll_interval = 2.0
        self._drc_violations_seen: List[int] = []
        self._current_substage_start_time: float = 0.0

    def run(
        self,
        command: List[str],
        cwd: Optional[str] = None,
        timeout: Optional[float] = None,
        extra_env: Optional[Dict[str, str]] = None,
        progress_callback: Optional[Callable[[OrfsStageProgress], None]] = None,
    ) -> subprocess.CompletedProcess:
        self._process_start_time = time.monotonic()
        self._last_line_time = self._process_start_time

        proc = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=safe_env(extra=extra_env),
        )

        stdout_chunks: List[str] = []
        last_poll = 0.0

        try:
            for line in iter(proc.stdout.readline, ""):
                if not line:
                    break
                stdout_chunks.append(line)
                self._last_line_time = time.monotonic()
                self._on_stdout_line(line, progress_callback)

                now = time.monotonic()
                if now - last_poll > self._routing_poll_interval:
                    self._poll_routing_log(progress_callback)
                    last_poll = now

            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            raise
        except BaseException:
            proc.kill()
            proc.wait()
            raise

        stdout = "".join(stdout_chunks)
        return subprocess.CompletedProcess(
            args=command,
            returncode=proc.returncode,
            stdout=stdout,
            stderr="",
        )

    def _on_stdout_line(
        self,
        line: str,
        progress_callback: Optional[Callable[[OrfsStageProgress], None]],
    ) -> None:
        stripped = line.strip()

        m = _RE_STAGE_START.search(stripped)
        if m:
            self._on_stage_start(m.group(1), progress_callback)
            return

        m = _RE_DRC_VIOLATION.search(stripped)
        if m:
            drc_count = int(m.group(1))
            self._drc_violations_seen.append(drc_count)
            trend = "improving" if len(self._drc_violations_seen) > 1 and self._drc_violations_seen[-1] < self._drc_violations_seen[-2] else "worsening" if len(self._drc_violations_seen) > 1 and self._drc_violations_seen[-1] > self._drc_violations_seen[-2] else "stable"
            if progress_callback:
                progress_callback(self._build_progress(
                    progress_pct=0.0,
                    drc_violations=drc_count,
                    drc_trend=trend,
                ))
            return

        m = _RE_ROUTING_DRC.search(stripped)
        if m:
            drc_count = int(m.group(1))
            self._drc_violations_seen.append(drc_count)
            if progress_callback:
                progress_callback(self._build_progress(
                    progress_pct=0.0,
                    drc_violations=drc_count,
                    drc_trend="improving" if len(self._drc_violations_seen) > 1 and self._drc_violations_seen[-1] < self._drc_violations_seen[-2] else "worsening" if len(self._drc_violations_seen) > 1 and self._drc_violations_seen[-1] > self._drc_violations_seen[-2] else "stable",
                ))
            return

        m = _RE_ROUTING_ITER.search(stripped)
        if m:
            pct = int(m.group(1))
            violations = int(m.group(2))
            self._routing_iterations.append((pct, violations))
            if progress_callback:
                progress_callback(self._build_progress(
                    progress_pct=min(pct + 50, 100),
                    routing_iteration_pct=pct,
                    routing_violations=violations,
                ))
            return

    def _on_stage_start(
        self,
        stage_key: str,
        progress_callback: Optional[Callable[[OrfsStageProgress], None]],
    ) -> None:
        self._current_stage = stage_key
        self._stage_start_time = time.monotonic()
        self._current_substage_start_time = time.monotonic()
        if stage_key != "5_2_route":
            self._routing_iterations = []
        if "drc" not in stage_key.lower():
            self._drc_violations_seen = []
        if progress_callback:
            progress_callback(self._build_progress(progress_pct=0.0))

    def _poll_routing_log(
        self,
        progress_callback: Optional[Callable[[OrfsStageProgress], None]],
    ) -> None:
        log = self._orfs_log_dir / "5_2_route.tmp.log"
        if not log.exists():
            return
        try:
            text = log.read_text(errors="replace")
            matches = list(_RE_ROUTING_ITER.finditer(text))
            if not matches:
                return
            last = matches[-1]
            pct = int(last.group(1))
            violations = int(last.group(2))
            if not self._routing_iterations or self._routing_iterations[-1] != (pct, violations):
                self._routing_iterations.append((pct, violations))
                if progress_callback:
                    progress_callback(self._build_progress(
                        progress_pct=min(pct + 50, 100),
                        routing_iteration_pct=pct,
                        routing_violations=violations,
                    ))
        except OSError:
            pass

    def _build_progress(
        self,
        progress_pct: float = 0.0,
        routing_iteration_pct: Optional[int] = None,
        routing_violations: Optional[int] = None,
        drc_violations: Optional[int] = None,
        drc_trend: Optional[str] = None,
    ) -> OrfsStageProgress:
        now = time.monotonic()
        return OrfsStageProgress(
            stage_key=self._current_stage,
            stage_label=STAGE_LABELS.get(self._current_stage, self._current_stage),
            progress_pct=progress_pct,
            routing_iteration_pct=routing_iteration_pct,
            routing_violations=routing_violations,
            drc_violations=drc_violations,
            drc_trend=drc_trend,
            elapsed_sec=now - self._process_start_time,
            idle_sec=now - self._last_line_time,
            stage_elapsed_sec=now - self._current_substage_start_time,
        )
