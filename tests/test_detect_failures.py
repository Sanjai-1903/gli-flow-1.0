import tempfile
from pathlib import Path

from failure_atlas.detect_failures import detect_failures_in_log


def test_no_match():
    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "test.log"
        log.write_text("everything is fine")
        results = detect_failures_in_log(str(log))
        assert results == []


def test_drc_match():
    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "test.log"
        log.write_text("Found 142 DRC violations: 96 min spacing, 46 min area")
        results = detect_failures_in_log(str(log))
        assert len(results) == 1
        assert results[0]["failure_id"] == "FA-0003"
        assert results[0]["severity"] == "HIGH"
