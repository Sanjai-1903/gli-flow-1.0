"""Week 5: Heartbeat system tests."""

import time
import tempfile
from pathlib import Path

from gli_flow.runtime.heartbeat import HeartbeatMonitor


def test_heartbeat_start_stop():
    with tempfile.TemporaryDirectory() as tmp:
        hb = HeartbeatMonitor(tmp, interval_sec=0.1)
        hb.start()
        assert hb.is_alive()
        hb.stop()


def test_heartbeat_writes_file():
    with tempfile.TemporaryDirectory() as tmp:
        hb = HeartbeatMonitor(tmp, interval_sec=0.1)
        hb.start()
        time.sleep(0.15)
        hb.stop()
        assert (Path(tmp) / "heartbeat.txt").exists()
        content = (Path(tmp) / "heartbeat.txt").read_text().strip()
        assert float(content) > 0


def test_heartbeat_not_alive_when_stopped():
    with tempfile.TemporaryDirectory() as tmp:
        hb = HeartbeatMonitor(tmp, interval_sec=0.1)
        assert not hb.is_alive()


def test_heartbeat_seconds_since():
    with tempfile.TemporaryDirectory() as tmp:
        hb = HeartbeatMonitor(tmp, interval_sec=0.05)
        hb.start()
        time.sleep(0.1)
        secs = hb.seconds_since_last_beat()
        hb.stop()
        assert 0 < secs < 5.0
