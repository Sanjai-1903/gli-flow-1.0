import logging
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class HeartbeatMonitor:
    def __init__(self, run_dir: str, interval_sec: float = 30.0):
        self._run_dir = Path(run_dir)
        self._interval = interval_sec
        self._last_beat: float = time.monotonic()
        self._stopped = False
        self._thread: threading.Thread | None = None

    def start(self):
        self._last_beat = time.monotonic()
        self._run_dir.mkdir(parents=True, exist_ok=True)
        self._write_beat()
        self._stopped = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stopped = True
        self._write_beat()

    def _write_beat(self):
        try:
            (self._run_dir / "heartbeat.txt").write_text(str(time.monotonic()))
        except OSError as e:
            logger.warning(f"Heartbeat write failed: {e}")

    def _run(self):
        while not self._stopped:
            time.sleep(self._interval)
            self._last_beat = time.monotonic()
            self._write_beat()

    def is_alive(self, timeout_sec: float = 120.0) -> bool:
        if not (self._run_dir / "heartbeat.txt").exists():
            return False
        return time.monotonic() - self._last_beat < timeout_sec

    def seconds_since_last_beat(self) -> float:
        return time.monotonic() - self._last_beat
