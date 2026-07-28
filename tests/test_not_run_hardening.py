import os
import tempfile
from pathlib import Path
import subprocess
import hashlib

import pytest

from gli_flow.telemetry.parser import TelemetryParser
from gli_flow.core.drc_runner import run_dual_drc
from gli_flow.backends.openroad_adapter import DRCResult, DRCReportMissingError
from gli_flow.security.file_protection import get_or_create_user_key


class TestEMParserHardening:
    def test_em_missing_file_returns_not_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = TelemetryParser(tmp)
            metrics = p.parse_em_report(str(Path(tmp) / "nonexistent.txt"))
            assert metrics["em_status"] == "NOT_RUN"
            assert metrics["em_is_clean"] is False
            assert metrics["em_total_violations"] is None
            assert metrics["em_max_current_density_ma_um"] is None

    def test_em_unreadable_file_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            em_file = Path(tmp) / "em_report.txt"
            em_file.touch()
            em_file.chmod(0o000)
            try:
                p = TelemetryParser(tmp)
                metrics = p.parse_em_report(str(em_file))
                assert metrics["em_status"] == "ERROR"
                assert metrics["em_is_clean"] is False
            finally:
                em_file.chmod(0o644)

    def test_em_clean_report_returns_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            em_file = Path(tmp) / "em_report.txt"
            em_file.write_text("EM analysis complete. No violations found.\n")
            p = TelemetryParser(tmp)
            metrics = p.parse_em_report(str(em_file))
            assert metrics["em_status"] == "PASS"
            assert metrics["em_is_clean"] is True
            assert metrics["em_total_violations"] == 0

    def test_em_violation_report_returns_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            em_file = Path(tmp) / "em_report.txt"
            em_file.write_text(
                "EM Violation on net VDD: 2.5 (limit 1.0)\n"
                "Max current density: 2.5\n"
            )
            p = TelemetryParser(tmp)
            metrics = p.parse_em_report(str(em_file))
            assert metrics["em_status"] == "FAIL"
            assert metrics["em_is_clean"] is False
            assert metrics["em_total_violations"] == 1


class TestSIParserHardening:
    def test_si_missing_file_returns_not_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = TelemetryParser(tmp)
            metrics = p.parse_si_report(str(Path(tmp) / "nonexistent.txt"))
            assert metrics["si_status"] == "NOT_RUN"
            assert metrics["si_is_clean"] is False
            assert metrics["si_crosstalk_violations"] is None

    def test_si_unreadable_file_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            si_file = Path(tmp) / "si_report.txt"
            si_file.touch()
            si_file.chmod(0o000)
            try:
                p = TelemetryParser(tmp)
                metrics = p.parse_si_report(str(si_file))
                assert metrics["si_status"] == "ERROR"
                assert metrics["si_is_clean"] is False
            finally:
                si_file.chmod(0o644)

    def test_si_clean_report_returns_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            si_file = Path(tmp) / "si_report.txt"
            si_file.write_text("Crosstalk violations: 0\nMax delta delay: 0.0\n")
            p = TelemetryParser(tmp)
            metrics = p.parse_si_report(str(si_file))
            assert metrics["si_status"] == "PASS"
            assert metrics["si_is_clean"] is True

    def test_si_violation_report_returns_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            si_file = Path(tmp) / "si_report.txt"
            si_file.write_text("Crosstalk violations: 3\nMax delta delay: 0.25\n")
            p = TelemetryParser(tmp)
            metrics = p.parse_si_report(str(si_file))
            assert metrics["si_status"] == "FAIL"
            assert metrics["si_is_clean"] is False
            assert metrics["si_crosstalk_violations"] == 3


class TestPowerParserHardening:
    def test_power_missing_file_returns_not_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = TelemetryParser(tmp)
            metrics = p.parse_power_report(str(Path(tmp) / "nonexistent.txt"))
            assert metrics["power_status"] == "NOT_RUN"
            assert metrics["total_power_mw"] is None

    def test_power_unreadable_file_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            pwr_file = Path(tmp) / "power_report.txt"
            pwr_file.touch()
            pwr_file.chmod(0o000)
            try:
                p = TelemetryParser(tmp)
                metrics = p.parse_power_report(str(pwr_file))
                assert metrics["power_status"] == "ERROR"
            finally:
                pwr_file.chmod(0o644)

    def test_power_valid_returns_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            pwr_file = Path(tmp) / "power_report.txt"
            pwr_file.write_text("Total 1.0 2.0 3.0 6.0\n")
            p = TelemetryParser(tmp)
            metrics = p.parse_power_report(str(pwr_file))
            assert metrics["power_status"] == "DONE"
            assert metrics["total_power_mw"] == 6.0


class TestFormalParserHardening:
    def test_formal_missing_file_returns_not_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = TelemetryParser(tmp)
            metrics = p.parse_formal_report(str(Path(tmp) / "nonexistent.txt"))
            assert metrics["formal_status"] == "NOT_RUN"
            assert metrics["formal_is_equivalent"] is False
            assert metrics["formal_compare_points"] is None

    def test_formal_unreadable_file_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fm_file = Path(tmp) / "formal_log.txt"
            fm_file.touch()
            fm_file.chmod(0o000)
            try:
                p = TelemetryParser(tmp)
                metrics = p.parse_formal_report(str(fm_file))
                assert metrics["formal_status"] == "ERROR"
                assert metrics["formal_is_equivalent"] is False
            finally:
                fm_file.chmod(0o644)

    def test_formal_equivalent_returns_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            fm_file = Path(tmp) / "formal_log.txt"
            fm_file.write_text("Compare points: 5000\nBoth designs are equivalent.\n")
            p = TelemetryParser(tmp)
            metrics = p.parse_formal_report(str(fm_file))
            assert metrics["formal_status"] == "PASS"
            assert metrics["formal_is_equivalent"] is True

    def test_formal_not_equivalent_returns_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            fm_file = Path(tmp) / "formal_log.txt"
            fm_file.write_text("Compare points: 5000\nNot equivalent: mismatch at point 42\n")
            p = TelemetryParser(tmp)
            metrics = p.parse_formal_report(str(fm_file))
            assert metrics["formal_status"] == "FAIL"
            assert metrics["formal_is_equivalent"] is False


class TestParseAllHardening:
    def test_parse_all_empty_sets_all_not_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = TelemetryParser(tmp)
            metrics = p.parse_all()
            assert metrics.get("em_status") == "NOT_RUN"
            assert metrics.get("si_status") == "NOT_RUN"
            assert metrics.get("power_status") == "NOT_RUN"
            assert metrics.get("formal_status") == "NOT_RUN"
            assert metrics.get("drc_status") == "NOT_RUN"
            assert metrics.get("lvs_status") == "NOT_RUN"
            assert metrics.get("antenna_status") == "NOT_RUN"
            assert metrics.get("density_status") == "NOT_RUN"
            assert metrics.get("timing_status") == "NOT_RUN"
            assert metrics.get("decap_status") == "NOT_RUN"
            assert metrics.get("scan_status") == "NOT_RUN"
            assert metrics.get("atpg_status") == "NOT_RUN"
            assert metrics.get("cg_status") == "NOT_RUN"
            assert metrics.get("pro_status") == "NOT_RUN"
            assert metrics.get("yield_status") == "NOT_RUN"
            assert metrics.get("drc_is_clean") is False
            assert metrics.get("formal_is_equivalent") is False
            assert metrics.get("antenna_is_clean") is False
            assert metrics.get("lvs_is_clean") is False

    def test_parse_all_with_data_reports_correctly(self):
        with tempfile.TemporaryDirectory() as tmp:
            em_file = Path(tmp) / "em_report.txt"
            em_file.write_text("EM Violation: test 2.0\n")
            p = TelemetryParser(tmp)
            metrics = p.parse_all()
            assert metrics.get("em_status") == "FAIL"
            assert metrics.get("em_is_clean") is False
            assert metrics.get("em_total_violations") == 1


class TestDRCRunnerHardening:
    def test_run_dual_drc_both_tools_fail(self, monkeypatch):
        monkeypatch.setattr("gli_flow.core.drc_runner.run_magic_drc", lambda *a, **kw: {
            "tool": "magic", "run": False, "error": "simulated failure", "violations": None,
        })
        monkeypatch.setattr("gli_flow.core.drc_runner.run_klayout_drc", lambda *a, **kw: {
            "tool": "klayout", "run": False, "error": "simulated failure", "violations": None,
        })
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            result = run_dual_drc(
                gds_path="/nonexistent/input.gds",
                design_name="test",
                pdk="sky130A",
                run_dir=run_dir,
            )
            assert result["drc_clean"] is False
            assert result["drc_status"] == "NOT_RUN"
            assert result["total_violations"] is None
            assert "Both Magic and KLayout DRC skipped or failed" in result["note"]


class TestDRCAdapterHardening:
    def test_run_drc_missing_gds_raises(self):
        from gli_flow.backends.openroad_adapter import OpenRoadAdapter
        from gli_flow.pdk import get_pdk

        pdk = get_pdk("sky130")
        adapter = OpenRoadAdapter(pdk_root="/tmp", pdk=pdk)
        with pytest.raises(FileNotFoundError, match="GDS file not found"):
            adapter.run_drc("/tmp", "test", "/nonexistent/input.gds", pdk)

    def test_parse_drc_output_missing_file_raises(self):
        from gli_flow.backends.openroad_adapter import OpenRoadAdapter, DRCReportMissingError
        from gli_flow.pdk import get_pdk

        pdk = get_pdk("sky130")
        adapter = OpenRoadAdapter(pdk_root="/tmp", pdk=pdk)
        with pytest.raises(DRCReportMissingError, match="DRC raw output not found"):
            adapter._parse_drc_output("/nonexistent/drc_raw.txt", 0.0)


class TestSignoffShellSafe:
    def test_signoff_no_shell_true(self):
        import ast, pathlib

        for f in pathlib.Path("gli_flow").rglob("*.py"):
            skip_vendors = {"examples", "vendor"}
            parts = f.parts
            if any(s in parts for s in skip_vendors):
                continue
            source = f.read_text()
            if "shell=True" in source:
                pytest.fail(f"{f} contains shell=True")


class TestEncryptionSecretHardening:
    def test_missing_secret_raises(self):
        key = "GLI_ENCRYPTION_SECRET"
        old = os.environ.pop(key, None)
        try:
            with pytest.raises(RuntimeError, match="GLI_ENCRYPTION_SECRET"):
                get_or_create_user_key("test_user")
        finally:
            if old is not None:
                os.environ[key] = old

    def test_valid_secret_produces_key(self):
        key = "GLI_ENCRYPTION_SECRET"
        old = os.environ.get(key)
        os.environ[key] = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"
        try:
            result = get_or_create_user_key("test_user")
            assert isinstance(result, bytes)
            assert len(result) == 32
        finally:
            if old is not None:
                os.environ[key] = old
            else:
                del os.environ[key]

    def test_different_users_different_keys(self):
        key = "GLI_ENCRYPTION_SECRET"
        old = os.environ.get(key)
        os.environ[key] = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"
        try:
            k1 = get_or_create_user_key("user_a")
            k2 = get_or_create_user_key("user_b")
            assert k1 != k2
        finally:
            if old is not None:
                os.environ[key] = old
            else:
                del os.environ[key]


class TestIntegrationTestRunDiscovery:
    def test_get_latest_run_dir_filesystem_fallback(self):
        import sys, pathlib
        sys.path.insert(0, str(pathlib.Path("tests/integration").resolve()))
        try:
            from test_e2e_counter import get_latest_run_dir
            run_dir = get_latest_run_dir()
            assert run_dir is None or pathlib.Path(run_dir).is_dir()
        finally:
            sys.path.pop(0)
