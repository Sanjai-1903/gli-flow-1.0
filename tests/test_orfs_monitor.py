"""Week 5: ORFS monitor validation tests."""

import tempfile
from pathlib import Path

from gli_flow.backends.orfs_monitor import OrfsMonitor, OrfsStageProgress, STAGE_LABELS


def test_stage_labels_exist():
    assert "1_2_yosys" in STAGE_LABELS
    assert "2_1_floorplan" in STAGE_LABELS
    assert "3_3_place_gp" in STAGE_LABELS
    assert "4_1_cts" in STAGE_LABELS
    assert "5_2_route" in STAGE_LABELS
    assert "6_1_fill" in STAGE_LABELS


def test_orfs_progress_dataclass():
    p = OrfsStageProgress(
        stage_key="1_2_yosys",
        stage_label="Yosys Synth",
        progress_pct=50.0,
        elapsed_sec=10.0,
    )
    assert p.stage_key == "1_2_yosys"
    assert p.progress_pct == 50.0


def test_orfs_monitor_init():
    with tempfile.TemporaryDirectory() as tmp:
        monitor = OrfsMonitor(
            flow_dir=tmp,
            platform="sky130A",
            design_name="counter",
        )
        log_dir = Path(tmp) / "logs" / "sky130A" / "counter" / "base"
        assert monitor._orfs_log_dir == log_dir


def test_orfs_monitor_stage_labels_match():
    with tempfile.TemporaryDirectory() as tmp:
        monitor = OrfsMonitor(tmp, "sky130A", "counter")
        p = monitor._build_progress(progress_pct=50.0)
        assert p.progress_pct == 50.0
        assert p.stage_label == ""
        assert p.elapsed_sec >= 0.0


def test_orfs_monitor_routing_log_poll_nonexistent():
    with tempfile.TemporaryDirectory() as tmp:
        monitor = OrfsMonitor(tmp, "sky130A", "counter")
        callback_called = False

        def cb(p):
            nonlocal callback_called
            callback_called = True

        monitor._poll_routing_log(cb)
        assert not callback_called
