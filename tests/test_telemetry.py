import tempfile
from pathlib import Path

from gli_flow.telemetry.parser import TelemetryParser


def test_parser_init():
    p = TelemetryParser("/tmp")
    assert p.reports_dir == Path("/tmp")


def test_parse_empty_dir():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_all()
        assert metrics.get("timing_unit") == "ns"
        assert metrics.get("sta_setup_status") == "NOT_RUN"
        assert metrics.get("sta_hold_status") == "NOT_RUN"


def test_parse_timing_rpt():
    with tempfile.TemporaryDirectory() as tmp:
        rpt = Path(tmp) / "timing.rpt"
        rpt.write_text("wns: -0.12\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_timing()
        assert "setup_wns_ns" in metrics
        assert metrics["setup_wns_ns"] == -0.12


def test_parse_utilization():
    with tempfile.TemporaryDirectory() as tmp:
        rpt = Path(tmp) / "utilization.rpt"
        rpt.write_text("Core Utilization: 45.2%\nTotal Cells: 4231\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_utilization()
        assert metrics["utilization"] == 45.2
        assert metrics["cell_count"] == 4231


def test_parse_runtime():
    with tempfile.TemporaryDirectory() as tmp:
        rpt = Path(tmp) / "runtime.rpt"
        rpt.write_text("Total Runtime: 89.4 sec\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_runtime()
        assert metrics["runtime_sec"] == 89.4


def test_parse_drc_clean():
    with tempfile.TemporaryDirectory() as tmp:
        drc_file = Path(tmp) / "drc_raw.txt"
        drc_file.write_text("DRC_TOTAL: 0\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_drc_report(str(drc_file))
        assert metrics["drc_total_violations"] == 0
        assert metrics["drc_is_clean"] is True
        assert metrics["drc_by_category"] == {}


def test_parse_drc_violations():
    with tempfile.TemporaryDirectory() as tmp:
        drc_file = Path(tmp) / "drc_raw.txt"
        drc_file.write_text(
            "DRC_TOTAL: 3\n"
            "VIOLATION: DRC_001 metal2 (10 20) (30 40)\n"
            "VIOLATION: DRC_002 metal3 (50 60) (70 80)\n"
            "VIOLATION: DRC_001 metal2 (90 100) (110 120)\n"
        )
        p = TelemetryParser(tmp)
        metrics = p.parse_drc_report(str(drc_file))
        assert metrics["drc_total_violations"] == 3
        assert metrics["drc_is_clean"] is False
        assert metrics["drc_by_category"]["DRC_001"] == 2
        assert metrics["drc_by_category"]["DRC_002"] == 1
        assert len(metrics["drc_locations"]) == 3


def test_parse_drc_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_drc_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["drc_total_violations"] is None
        assert metrics["drc_is_clean"] is False


def test_parse_drc_malformed():
    with tempfile.TemporaryDirectory() as tmp:
        drc_file = Path(tmp) / "drc_raw.txt"
        drc_file.write_text("not a valid drc output\nrandom text\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_drc_report(str(drc_file))
        assert metrics["drc_total_violations"] == 0
        assert metrics["drc_is_clean"] is True


def test_parse_lvs_clean():
    with tempfile.TemporaryDirectory() as tmp:
        lvs_file = Path(tmp) / "lvs_comp.out"
        lvs_file.write_text(
            "Circuit 1: counter\n"
            "Circuit 2: counter\n"
            "Circuits match uniquely.\n"
            "Unmatched Devices: 0\n"
            "Unmatched Nets: 0\n"
            "Shorts: 0\n"
            "Opens: 0\n"
            "Parameter mismatches: 0\n"
        )
        p = TelemetryParser(tmp)
        metrics = p.parse_lvs_report(str(lvs_file))
        assert metrics["lvs_result"] == "CLEAN"
        assert metrics["lvs_is_clean"] is True
        assert metrics["lvs_unmatched_devices"] == 0
        assert metrics["lvs_unmatched_nets"] == 0


def test_parse_lvs_fail():
    with tempfile.TemporaryDirectory() as tmp:
        lvs_file = Path(tmp) / "lvs_comp.out"
        lvs_file.write_text(
            "Circuit 1: counter\n"
            "Circuit 2: counter\n"
            "Unmatched Devices: 2\n"
            "Unmatched Nets: 3\n"
            "Shorts: 1\n"
            "Opens: 2\n"
            "Parameter mismatches: 1\n"
            "Net A[3] open at coordinate (450, 210)\n"
        )
        p = TelemetryParser(tmp)
        metrics = p.parse_lvs_report(str(lvs_file))
        assert metrics["lvs_result"] == "FAIL"
        assert metrics["lvs_is_clean"] is False
        assert metrics["lvs_unmatched_nets"] == 3
        assert metrics["lvs_short_count"] == 1
        assert metrics["lvs_open_count"] == 2
