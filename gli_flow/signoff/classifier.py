from enum import Enum
from typing import Optional


class CheckResult(str, Enum):
    PASS = "PASS"
    CONDITIONAL_PASS = "CONDITIONAL_PASS"
    FAIL = "FAIL"
    NOT_RUN = "NOT_RUN"
    ERROR = "ERROR"
    FLOW_BUG = "FLOW_BUG"
    NOT_APPLICABLE = "NOT_APPLICABLE"


PRIORITY = {
    CheckResult.FAIL: 0,
    CheckResult.ERROR: 1,
    CheckResult.NOT_RUN: 2,
    CheckResult.CONDITIONAL_PASS: 3,
    CheckResult.FLOW_BUG: 4,
    CheckResult.PASS: 5,
    CheckResult.NOT_APPLICABLE: 6,
}


class SignoffEvidence:
    CHECK_NAMES = [
        "synthesis", "gds", "def", "netlist",
        "setup_timing", "hold_timing",
        "magic_drc", "klayout_drc",
        "antenna", "density", "lvs",
        "em", "si", "power", "formal",
        "cdc",
    ]


class SignoffClassifier:
    @staticmethod
    def classify(
        checks: dict[str, CheckResult],
        evidence_gaps: Optional[list[str]] = None,
        false_positives: Optional[list[str]] = None,
        flow_bugs: Optional[list[str]] = None,
    ) -> dict:
        if not checks:
            return {
                "signoff_status": "NOT_RUN",
                "tapeout_ready": False,
                "signoff_score": None,
                "blocking_reasons": [],
                "warnings": [],
                "evidence_gaps": evidence_gaps or [],
            }

        all_results = list(checks.values())
        worst = min(all_results, key=lambda r: PRIORITY.get(r, 99))

        blocking_reasons = []
        warnings = []
        gaps = list(evidence_gaps) if evidence_gaps else []

        for name, result in sorted(checks.items()):
            if result == CheckResult.FAIL:
                blocking_reasons.append(f"{name}: real violations found")
            elif result == CheckResult.ERROR:
                gaps.append(f"{name}: tool error during execution")
            elif result == CheckResult.NOT_RUN:
                gaps.append(f"{name}: not executed")
            elif result == CheckResult.FLOW_BUG:
                warnings.append(f"{name}: known flow/tool bug")
            elif result == CheckResult.CONDITIONAL_PASS:
                warnings.append(f"{name}: passed with false positives")

        if flow_bugs:
            for bug in flow_bugs:
                warnings.append(f"Flow bug: {bug}")
        if false_positives:
            for fp in false_positives:
                warnings.append(f"False positive: {fp}")

        if worst == CheckResult.FAIL:
            signoff_status = "FAIL"
            tapeout_ready = False
            signoff_score = 0.0
        elif worst in (CheckResult.ERROR, CheckResult.NOT_RUN):
            signoff_status = "INCOMPLETE"
            tapeout_ready = False
            signoff_score = 0.3
        elif worst == CheckResult.CONDITIONAL_PASS:
            signoff_status = "CONDITIONAL_PASS"
            tapeout_ready = True
            signoff_score = 0.8
        elif worst == CheckResult.FLOW_BUG:
            signoff_status = "CONDITIONAL_PASS"
            tapeout_ready = True
            signoff_score = 0.9
        elif worst == CheckResult.PASS:
            signoff_status = "PASS"
            tapeout_ready = True
            signoff_score = 1.0
        else:
            signoff_status = "NOT_RUN"
            tapeout_ready = False
            signoff_score = None

        return {
            "signoff_status": signoff_status,
            "tapeout_ready": tapeout_ready,
            "signoff_score": signoff_score,
            "blocking_reasons": blocking_reasons,
            "warnings": warnings,
            "evidence_gaps": gaps,
        }

    @staticmethod
    def check_result_from_bool(passed: bool, was_run: bool = True) -> CheckResult:
        if not was_run:
            return CheckResult.NOT_RUN
        return CheckResult.PASS if passed else CheckResult.FAIL

    @staticmethod
    def has_real_blockers(checks: dict[str, CheckResult]) -> bool:
        return any(r == CheckResult.FAIL for r in checks.values())

    @staticmethod
    def is_incomplete(checks: dict[str, CheckResult]) -> bool:
        return any(r in (CheckResult.NOT_RUN, CheckResult.ERROR) for r in checks.values())
