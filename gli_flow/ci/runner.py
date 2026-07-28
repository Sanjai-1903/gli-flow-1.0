from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from gli_flow.ci.config import CIConfig
from gli_flow.core.subprocess_env import safe_env
from gli_flow.ci.reporter import CIReport, generate_junit_xml, generate_markdown_report


class CIRunner:

    def __init__(self, config: CIConfig):
        self.config = config

    def run(self) -> CIReport:
        design_path = Path(self.config.design_path)
        design_name = design_path.name
        run_id = f"ci_{int(time.time())}_{design_name}"

        start = time.time()
        try:
            result = subprocess.run(
                [sys.executable, "-m", "gli_flow", "run", str(design_path)],
                capture_output=True, text=True,
                timeout=86400,
                env=safe_env(),
            )
            duration = time.time() - start
            success = result.returncode == 0
        except subprocess.TimeoutExpired:
            duration = time.time() - start
            return CIReport(
                success=False, run_id=run_id,
                design_name=design_name, metrics={},
                baseline_metrics=None, regressions=["Timed out"],
                duration=duration, error="Execution timed out",
            )

        metrics = self._extract_metrics()
        baseline_metrics = self._load_baseline()
        regressions = self._check_regressions(metrics, baseline_metrics)

        report = CIReport(
            success=success and len(regressions) == 0,
            run_id=run_id,
            design_name=design_name,
            metrics=metrics,
            baseline_metrics=baseline_metrics,
            regressions=regressions,
            duration=duration,
            error=None if success else "Run failed",
        )

        if self.config.junit_output:
            junit_path = Path(self.config.junit_output)
            junit_path.write_text(generate_junit_xml(report))

        if self.config.markdown_output:
            md_path = Path(self.config.markdown_output)
            md_path.write_text(generate_markdown_report(report))

        return report

    def _extract_metrics(self) -> dict:
        from gli_flow.database.sqlite import DatabaseManager
        db = DatabaseManager(db_path=self.config.db_path)
        runs = db.get_recent_runs(limit=1)
        if runs:
            run = runs[0]
            return {
                "qor_score": run.get("qor_score"),
                "wns": run.get("wns"),
                "tns": run.get("tns"),
                "utilization": run.get("utilization"),
                "runtime_sec": run.get("runtime_sec"),
                "cell_count": run.get("cell_count"),
                "status": run.get("status"),
            }
        return {}

    def _load_baseline(self) -> Optional[dict]:
        from gli_flow.database.sqlite import DatabaseManager
        from pathlib import Path
        db = DatabaseManager(db_path=self.config.db_path)

        if not self.config.baseline_run_id:
            baseline = db.get_last_successful_run(Path(self.config.design_path).name)
            if baseline:
                return {
                    "qor_score": baseline.get("qor_score"),
                    "wns": baseline.get("wns"),
                    "tns": baseline.get("tns"),
                    "utilization": baseline.get("utilization"),
                    "runtime_sec": baseline.get("runtime_sec"),
                    "cell_count": baseline.get("cell_count"),
                }
            return None

        conn = db.connection
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM runs WHERE run_id = ?", (self.config.baseline_run_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "qor_score": row[10] if len(row) > 10 else None,
            "wns": row[5] if len(row) > 5 else None,
            "tns": row[6] if len(row) > 6 else None,
            "utilization": row[7] if len(row) > 7 else None,
            "runtime_sec": row[8] if len(row) > 8 else None,
            "cell_count": row[9] if len(row) > 9 else None,
        }

    def _check_regressions(self, metrics: dict, baseline: Optional[dict]) -> list[str]:
        regressions = []
        if not baseline:
            return regressions

        if self.config.qor_score_min is not None:
            qor = metrics.get("qor_score")
            if qor is not None and qor < self.config.qor_score_min:
                regressions.append(f"QoR score {qor:.1f} < minimum {self.config.qor_score_min:.1f}")

        if self.config.wns_max is not None:
            wns = metrics.get("wns")
            if wns is not None and wns < self.config.wns_max:
                regressions.append(f"WNS {wns:.3f}ns < threshold {self.config.wns_max:.3f}ns")

        if self.config.utilization_max is not None:
            util = metrics.get("utilization")
            if util is not None and util > self.config.utilization_max:
                regressions.append(f"Utilization {util:.1f}% > maximum {self.config.utilization_max:.1f}%")

        if metrics.get("status") == "FAILED":
            regressions.append("Run status is FAILED")

        qor = metrics.get("qor_score")
        b_qor = baseline.get("qor_score")
        if qor is not None and b_qor is not None and qor < b_qor * 0.9:
            regressions.append(f"QoR score regressed {qor:.1f} vs baseline {b_qor:.1f} (>10% drop)")

        return regressions
