import json
import unittest
from pathlib import Path


class TestIncidentHierarchy(unittest.TestCase):

    def setUp(self):
        from gli_flow.core.incident_hierarchy import (
            classify_entry_role, classify_run_entries, build_hierarchy, get_root_summary,
            INCIDENT_ROLE_ROOT_CAUSE, INCIDENT_ROLE_DERIVED, INCIDENT_ROLE_CONSEQUENCE,
            INCIDENT_ROLE_UNCLASSIFIED,
        )
        self.classify_entry_role = classify_entry_role
        self.classify_run_entries = classify_run_entries
        self.build_hierarchy = build_hierarchy
        self.get_root_summary = get_root_summary
        self.ROOT_CAUSE = INCIDENT_ROLE_ROOT_CAUSE
        self.DERIVED = INCIDENT_ROLE_DERIVED
        self.CONSEQUENCE = INCIDENT_ROLE_CONSEQUENCE
        self.UNCLASSIFIED = INCIDENT_ROLE_UNCLASSIFIED

    def _cross_tool_entry(self):
        return {
            "id": "1",
            "run_id": "run_test",
            "failure_type": "CROSS_TOOL_DRC_DISAGREEMENT",
            "severity": "MEDIUM",
            "signature": "inf_magic_002_cross_tool_disagreement",
        }

    def _drc_failure_entry(self):
        return {
            "id": "2",
            "run_id": "run_test",
            "failure_type": "DRC_SPACING",
            "severity": "TAPEOUT_BLOCKING",
            "signature": "DRC failed: 2 violations, categories: []",
        }

    def _signoff_entry(self):
        return {
            "id": "3",
            "run_id": "run_test",
            "failure_type": "SIGNOFF_FAILURE",
            "severity": "TAPEOUT_BLOCKING",
            "signature": "signoff_magic_drc_not_run_error_or_violations_found",
        }

    def _pipeline_entry(self):
        return {
            "id": "4",
            "run_id": "run_test",
            "failure_type": "PIPELINE_FAILURE",
            "severity": "HIGH",
            "signature": "pipeline_failure_SIGN_OFF",
        }

    def _timing_entry(self):
        return {
            "id": "5",
            "run_id": "run_test",
            "failure_type": "SETUP_VIOLATION",
            "severity": "TAPEOUT_BLOCKING",
            "signature": "Setup timing violated: WNS=-0.500ns",
        }

    # --- Single entry classification ---

    def test_cross_tool_is_root_cause(self):
        role = self.classify_entry_role(self._cross_tool_entry())
        self.assertEqual(role, self.ROOT_CAUSE)

    def test_drc_failure_is_derived(self):
        role = self.classify_entry_role(self._drc_failure_entry())
        self.assertEqual(role, self.DERIVED)

    def test_signoff_is_consequence(self):
        role = self.classify_entry_role(self._signoff_entry())
        self.assertEqual(role, self.CONSEQUENCE)

    def test_pipeline_is_consequence(self):
        role = self.classify_entry_role(self._pipeline_entry())
        self.assertEqual(role, self.CONSEQUENCE)

    def test_timing_is_unclassified(self):
        role = self.classify_entry_role(self._timing_entry())
        self.assertEqual(role, self.UNCLASSIFIED)

    # --- Run-level classification (UART pattern) ---

    def test_uart_pattern_root_cause(self):
        entries = [
            self._pipeline_entry(),
            self._signoff_entry(),
            self._drc_failure_entry(),
            self._cross_tool_entry(),
        ]
        classified = self.classify_run_entries(entries)
        roles = {e["id"]: e["incident_role"] for e in classified}

        self.assertEqual(roles["1"], self.ROOT_CAUSE)
        self.assertEqual(roles["2"], self.DERIVED)
        self.assertEqual(roles["3"], self.CONSEQUENCE)
        self.assertEqual(roles["4"], self.CONSEQUENCE)

    def test_uart_root_count(self):
        entries = [
            self._pipeline_entry(),
            self._signoff_entry(),
            self._drc_failure_entry(),
            self._cross_tool_entry(),
        ]
        summary = self.get_root_summary(entries)
        self.assertEqual(summary["root_count"], 1)
        self.assertEqual(summary["total_entries"], 4)
        self.assertEqual(summary["derived_count"], 1)
        self.assertEqual(summary["consequence_count"], 2)
        self.assertEqual(summary["unclassified_count"], 0)

    # --- Build hierarchy ---

    def test_build_hierarchy_uart(self):
        entries = [
            self._pipeline_entry(),
            self._signoff_entry(),
            self._drc_failure_entry(),
            self._cross_tool_entry(),
        ]
        tree = self.build_hierarchy(entries)
        self.assertEqual(len(tree), 1)
        root = tree[0]
        self.assertEqual(root["failure_type"], "CROSS_TOOL_DRC_DISAGREEMENT")
        self.assertEqual(len(root["children"]), 3)

    # --- No root cause present ---

    def test_no_root_cause_drc_becomes_root(self):
        entries = [self._drc_failure_entry(), self._signoff_entry()]
        classified = self.classify_run_entries(entries)
        roles = {e["id"]: e["incident_role"] for e in classified}
        self.assertEqual(roles["2"], self.ROOT_CAUSE)
        self.assertEqual(roles["3"], self.CONSEQUENCE)

    def test_no_root_cause_no_drc(self):
        entries = [self._signoff_entry(), self._pipeline_entry()]
        classified = self.classify_run_entries(entries)
        roles = {e["id"]: e["incident_role"] for e in classified}
        self.assertEqual(roles["3"], self.CONSEQUENCE)
        self.assertEqual(roles["4"], self.CONSEQUENCE)

    # --- Unrelated entries ---

    def test_timing_entry_unrelated(self):
        entries = [self._cross_tool_entry(), self._timing_entry()]
        classified = self.classify_run_entries(entries)
        roles = {e["id"]: e["incident_role"] for e in classified}
        self.assertEqual(roles["1"], self.ROOT_CAUSE)
        self.assertEqual(roles["5"], self.UNCLASSIFIED)

    # --- Empty / edge cases ---

    def test_empty_entries(self):
        summary = self.get_root_summary([])
        self.assertEqual(summary["root_count"], 0)
        self.assertEqual(summary["total_entries"], 0)

    def test_build_hierarchy_empty(self):
        tree = self.build_hierarchy([])
        self.assertEqual(len(tree), 0)

    def test_build_hierarchy_single_unrelated(self):
        tree = self.build_hierarchy([self._timing_entry()])
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]["failure_type"], "UNCLASSIFIED_ROOT")


if __name__ == "__main__":
    unittest.main()
