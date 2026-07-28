"""
Cross-tool DRC validation framework INF-MAGIC-002.
Compares Magic and KLayout DRC results, detects tool disagreements,
and optionally records Failure Atlas incidents and telemetry.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

log = logging.getLogger(__name__)

CONSISTENT_PASS = "CONSISTENT_PASS"
CONSISTENT_FAIL = "CONSISTENT_FAIL"
TOOL_DISAGREEMENT = "TOOL_DISAGREEMENT"


class CrossToolDRCAnalyzer:
    """Compare Magic and KLayout DRC results and classify agreement."""

    def __init__(self, run_dir: str, design_name: str = "", run_id: str = ""):
        self.run_dir = Path(run_dir)
        self.design_name = design_name
        self.run_id = run_id or os.path.basename(run_dir)

    def analyze(self, magic_result: dict, klayout_result: dict) -> dict:
        """Compare DRC results and return analysis dict.

        Args:
            magic_result: Dict from drc_runner.py run_magic_drc() result.
            klayout_result: Dict from drc_runner.py run_klayout_drc() result.

        Returns:
            Dict with keys:
                tool_agreement: CONSISTENT_PASS|CONSISTENT_FAIL|TOOL_DISAGREEMENT
                magic_violations: int or None
                klayout_violations: int or None
                disagreement_type: str or None
                incident_id: str or None  (if Failure Atlas incident created)
        """
        magic_ran = magic_result.get("run", False)
        klayout_ran = klayout_result.get("run", False)

        if not magic_ran and not klayout_ran:
            return self._no_analysis_needed("Neither tool ran")

        magic_violations = self._count_total_violations(magic_result)
        klayout_violations = self._count_total_violations(klayout_result)

        magic_pass = magic_violations == 0 if magic_ran else None
        klayout_pass = klayout_violations == 0 if klayout_ran else None

        result = {
            "tool_agreement": None,
            "magic_violations": magic_violations,
            "klayout_violations": klayout_violations,
            "disagreement_type": None,
            "incident_id": None,
        }

        if not magic_ran or not klayout_ran:
            result["tool_agreement"] = self._single_tool_consensus(magic_ran, klayout_ran, magic_pass, klayout_pass)
            self._record_telemetry(result)
            return result

        comparison = self._compare_results(magic_violations, klayout_violations, magic_pass, klayout_pass)
        result.update(comparison)

        if result["tool_agreement"] == TOOL_DISAGREEMENT:
            incident_id = self._create_disagreement_incident(magic_result, klayout_result, magic_violations, klayout_violations)
            result["incident_id"] = incident_id

        self._record_telemetry(result)

        return result

    def _no_analysis_needed(self, reason: str) -> dict:
        return {
            "tool_agreement": "NO_ANALYSIS",
            "magic_violations": None,
            "klayout_violations": None,
            "disagreement_type": reason,
            "incident_id": None,
        }

    def _single_tool_consensus(self, magic_ran: bool, klayout_ran: bool,
                                magic_pass: Optional[bool], klayout_pass: Optional[bool]) -> str:
        if magic_ran:
            return CONSISTENT_PASS if magic_pass else CONSISTENT_FAIL
        return CONSISTENT_PASS if klayout_pass else CONSISTENT_FAIL

    def _count_total_violations(self, result: dict) -> Optional[int]:
        if not result.get("run"):
            return None
        violations = result.get("violations")
        if violations is not None:
            return violations
        return None

    def _compare_results(self, magic_violations: int, klayout_violations: int,
                         magic_pass: bool, klayout_pass: bool) -> dict:
        if magic_pass and klayout_pass:
            return {
                "tool_agreement": CONSISTENT_PASS,
                "disagreement_type": None,
            }

        if not magic_pass and not klayout_pass:
            return {
                "tool_agreement": CONSISTENT_FAIL,
                "disagreement_type": None,
            }

        if not magic_pass and klayout_pass:
            return {
                "tool_agreement": TOOL_DISAGREEMENT,
                "disagreement_type": "MAGIC_FAIL_KLAYOUT_PASS",
            }

        if magic_pass and not klayout_pass:
            return {
                "tool_agreement": TOOL_DISAGREEMENT,
                "disagreement_type": "MAGIC_PASS_KLAYOUT_FAIL",
            }

        return {
            "tool_agreement": CONSISTENT_FAIL,
            "disagreement_type": None,
        }

    def _create_disagreement_incident(self, magic_result: dict, klayout_result: dict,
                                      magic_violations: int, klayout_violations: int) -> Optional[str]:
        try:
            from failure_atlas.repository import FailureAtlasRepository

            repo = FailureAtlasRepository()
            try:
                incident_id = str(uuid.uuid4())
                magic_notes = magic_result.get("error", "") if not magic_result.get("run") else ""
                klayout_notes = klayout_result.get("error", "") if not klayout_result.get("run") else ""

                entry = {
                    "id": incident_id,
                    "run_id": self.run_id,
                    "failure_type": "CROSS_TOOL_DRC_DISAGREEMENT",
                    "severity": "MEDIUM",
                    "title": f"Cross-tool DRC disagreement: Magic={magic_violations} KLayout={klayout_violations}",
                    "description": (
                        f"Tool disagreement detected for design '{self.design_name}' (run {self.run_id}). "
                        f"Magic reports {magic_violations} violations, "
                        f"KLayout reports {klayout_violations} violations. "
                        f"Requires engineer review to determine which tool is correct."
                    ),
                    "confidence": 0.6,
                    "signature": "inf_magic_002_cross_tool_disagreement",
                    "domain": "DRC",
                    "category": "DRC_SPACING",
                    "evidence": {
                        "magic_result": magic_result,
                        "klayout_result": klayout_result,
                        "analysis_type": "cross_tool_comparison",
                        "classification": "VALIDATED_TOOL_DISAGREEMENT",
                        "citation": "inf_magic_002",
                    },
                    "recommended_fix": {
                        "description": "Review violation coordinates in GDS viewer. Cross-check with KLayout. "
                                       "If Magic false-positive (boundary/edge-effect), file Failure Atlas incident and whitelist.",
                        "steps": [
                            "Inspect each violation location in GDS",
                            "Cross-reference with KLayout DRC results",
                            "Check if violations are at cell boundaries",
                            "Verify with PDK design rules",
                        ],
                    },
                    "fix_applied": False,
                    "detection_classification": "VERIFIED",
                }
                if magic_notes:
                    entry["evidence"]["magic_notes"] = magic_notes
                if klayout_notes:
                    entry["evidence"]["klayout_notes"] = klayout_notes

                repo.insert_entry_if_not_exists(entry)
                log.info(f"Created Failure Atlas incident {incident_id} for tool disagreement at run {self.run_id}")
                return incident_id
            finally:
                repo.close()
        except Exception as e:
            log.warning(f"Failed to create Failure Atlas incident for tool disagreement: {e}")
            return None

    def _record_telemetry(self, analysis: dict):
        try:
            telemetry_dir = self.run_dir / "telemetry"
            telemetry_dir.mkdir(parents=True, exist_ok=True)
            telemetry_path = telemetry_dir / "drc_agreement.json"

            record = {
                "run_id": self.run_id,
                "design_name": self.design_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tool_agreement": analysis.get("tool_agreement"),
                "magic_violations": analysis.get("magic_violations"),
                "klayout_violations": analysis.get("klayout_violations"),
                "disagreement_type": analysis.get("disagreement_type"),
                "incident_id": analysis.get("incident_id"),
            }

            with open(telemetry_path, "w") as f:
                json.dump(record, f, indent=2)

            log.info(f"DRC agreement telemetry written to {telemetry_path}")
        except Exception as e:
            log.warning(f"Failed to record DRC agreement telemetry: {e}")
