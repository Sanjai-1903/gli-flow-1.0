import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class TestCrossToolDRCAnalyzer(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.tmp_dir.name)
        self.run_id = "test_run_cross_tool"
        self.design_name = "test_design"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _make_analyzer(self, run_dir=None, design_name=None, run_id=None):
        from gli_flow.core.cross_tool_drc import CrossToolDRCAnalyzer
        return CrossToolDRCAnalyzer(
            run_dir=str(run_dir or self.run_dir),
            design_name=design_name or self.design_name,
            run_id=run_id or self.run_id,
        )

    def _klayout_pass(self):
        return {"tool": "klayout", "run": True, "violations": 0, "returncode": 0}

    def _klayout_fail(self, count=5):
        return {"tool": "klayout", "run": True, "violations": count, "returncode": 0}

    def _magic_pass(self):
        return {"tool": "magic", "run": True, "violations": 0, "returncode": 0}

    def _magic_fail(self, count=2):
        return {"tool": "magic", "run": True, "violations": count, "returncode": 0}

    def _magic_not_run(self):
        return {"tool": "magic", "run": False, "error": "magicdnull not found", "violations": None}

    def _klayout_not_run(self):
        return {"tool": "klayout", "run": False, "error": "KLayout not found", "violations": None}

    # --- CONSISTENT_PASS ---

    def test_consistent_pass(self):
        analyzer = self._make_analyzer()
        result = analyzer.analyze(self._magic_pass(), self._klayout_pass())
        self.assertEqual(result["tool_agreement"], "CONSISTENT_PASS")
        self.assertEqual(result["magic_violations"], 0)
        self.assertEqual(result["klayout_violations"], 0)
        self.assertIsNone(result["disagreement_type"])
        self.assertIsNone(result["incident_id"])
        telemetry_path = self.run_dir / "telemetry" / "drc_agreement.json"
        self.assertTrue(telemetry_path.exists())
        data = json.loads(telemetry_path.read_text())
        self.assertEqual(data["tool_agreement"], "CONSISTENT_PASS")

    # --- CONSISTENT_FAIL ---

    def test_consistent_fail(self):
        analyzer = self._make_analyzer()
        result = analyzer.analyze(self._magic_fail(3), self._klayout_fail(7))
        self.assertEqual(result["tool_agreement"], "CONSISTENT_FAIL")
        self.assertEqual(result["magic_violations"], 3)
        self.assertEqual(result["klayout_violations"], 7)
        self.assertIsNone(result["disagreement_type"])
        self.assertIsNone(result["incident_id"])

    # --- TOOL_DISAGREEMENT: Magic Fail, KLayout Pass ---

    @patch("failure_atlas.repository.FailureAtlasRepository")
    def test_disagreement_magic_fail_klayout_pass(self, mock_repo_class):
        mock_repo_instance = unittest.mock.MagicMock()
        mock_repo_instance.insert_entry_if_not_exists.return_value = "mock_incident_id"
        mock_repo_class.return_value = mock_repo_instance

        analyzer = self._make_analyzer()
        result = analyzer.analyze(self._magic_fail(2), self._klayout_pass())
        self.assertEqual(result["tool_agreement"], "TOOL_DISAGREEMENT")
        self.assertEqual(result["disagreement_type"], "MAGIC_FAIL_KLAYOUT_PASS")
        self.assertEqual(result["magic_violations"], 2)
        self.assertEqual(result["klayout_violations"], 0)
        self.assertIsNotNone(result["incident_id"])

        mock_repo_instance.insert_entry_if_not_exists.assert_called_once()
        call_args = mock_repo_instance.insert_entry_if_not_exists.call_args[0][0]
        self.assertEqual(call_args["run_id"], self.run_id)
        self.assertEqual(call_args["failure_type"], "CROSS_TOOL_DRC_DISAGREEMENT")

    # --- TOOL_DISAGREEMENT: Magic Pass, KLayout Fail ---

    @patch("failure_atlas.repository.FailureAtlasRepository")
    def test_disagreement_magic_pass_klayout_fail(self, mock_repo_class):
        mock_repo_instance = unittest.mock.MagicMock()
        mock_repo_instance.insert_entry.return_value = "mock_incident_id"
        mock_repo_class.return_value = mock_repo_instance

        analyzer = self._make_analyzer()
        result = analyzer.analyze(self._magic_pass(), self._klayout_fail(5))
        self.assertEqual(result["tool_agreement"], "TOOL_DISAGREEMENT")
        self.assertEqual(result["disagreement_type"], "MAGIC_PASS_KLAYOUT_FAIL")
        self.assertEqual(result["magic_violations"], 0)
        self.assertEqual(result["klayout_violations"], 5)
        self.assertIsNotNone(result["incident_id"])

    # --- Single tool only (Magic not run) ---

    def test_single_tool_klayout_only(self):
        analyzer = self._make_analyzer()
        result = analyzer.analyze(self._magic_not_run(), self._klayout_pass())
        self.assertEqual(result["tool_agreement"], "CONSISTENT_PASS")
        self.assertIsNone(result["magic_violations"])
        self.assertEqual(result["klayout_violations"], 0)
        self.assertIsNone(result["incident_id"])

    def test_single_tool_magic_only(self):
        analyzer = self._make_analyzer()
        result = analyzer.analyze(self._magic_fail(3), self._klayout_not_run())
        self.assertEqual(result["tool_agreement"], "CONSISTENT_FAIL")
        self.assertEqual(result["magic_violations"], 3)
        self.assertIsNone(result["klayout_violations"])
        self.assertIsNone(result["incident_id"])

    # --- Neither tool ran ---

    def test_neither_tool_ran(self):
        analyzer = self._make_analyzer()
        result = analyzer.analyze(self._magic_not_run(), self._klayout_not_run())
        self.assertEqual(result["tool_agreement"], "NO_ANALYSIS")
        self.assertIsNone(result["magic_violations"])
        self.assertIsNone(result["klayout_violations"])

    # --- Edge case: violations = -1 (parse error) ---

    def test_parse_error_violations(self):
        magic_err = {"tool": "magic", "run": True, "violations": -1, "returncode": 1}
        klayout_err = {"tool": "klayout", "run": True, "violations": -1, "returncode": 1}
        analyzer = self._make_analyzer()
        result = analyzer.analyze(magic_err, klayout_err)
        self.assertEqual(result["tool_agreement"], "CONSISTENT_FAIL")


if __name__ == "__main__":
    unittest.main()
