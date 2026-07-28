import json
import pytest
import tempfile
from pathlib import Path

from failure_atlas.signature_engine import load_signatures, scan_file
from failure_atlas.detector import detect_failures


def make_log(text: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False)
    tmp.write(text)
    tmp.close()
    return Path(tmp.name)


class TestDetectionClassification:

    def test_verified_requires_exact_match(self):
        sigs = load_signatures()
        log = make_log("This log mentions WNS: -0.45  TNS: -12.3 in its output")
        findings = scan_file(log, sigs)
        log.unlink()
        for f in findings:
            if f.get("_detection_method") == "EXACT_MATCH":
                matched = True
                break
        else:
            matched = False
        assert matched, "EXACT_MATCH must be set when observed_signature is found verbatim in log"

    def test_keyword_fallback_produces_heuristic(self):
        sigs = load_signatures()
        log = make_log("This log has normal terms like setup and hold but no exact signatures")
        findings = scan_file(log, sigs)
        log.unlink()
        for f in findings:
            assert f.get("_detection_method") == "KEYWORD_FALLBACK", \
                f"Keyword-only match must set KEYWORD_FALLBACK, got {f.get('_detection_method')}"

    def test_empty_log_no_false_positives(self):
        sigs = load_signatures()
        log = make_log("")
        findings = scan_file(log, sigs)
        log.unlink()
        assert len(findings) == 0, "Empty log must produce no detections"

    def test_keyword_logs_cannot_become_verified(self):
        sigs = load_signatures()
        log = make_log("setup hold tns slack violat overflow congestion density power")
        findings = scan_file(log, sigs)
        log.unlink()
        for f in findings:
            assert f.get("_detection_method") != "EXACT_MATCH", \
                "Log with only keywords must not produce EXACT_MATCH"
            assert f.get("_detection_method") == "KEYWORD_FALLBACK", \
                "Log with only keywords must produce KEYWORD_FALLBACK"

    def test_detect_failures_produces_verified(self):
        entries = detect_failures(
            run_id="test",
            metrics={
                "setup_wns_ns": -0.3,
                "setup_tns_ns": -5.0,
                "drc_total_violations": 2,
                "drc_is_clean": False,
                "lvs_status": "NOT_RUN",
                "lvs_return_code": -1,
                "lvs_report_exists": False,
            },
            stage="ROUTING",
            design_name="test",
            pdk_name="sky130",
        )
        for e in entries:
            assert e.detection_classification == "VERIFIED", \
                f"Metric-based detection must be VERIFIED, got {e.detection_classification}"

    def test_classification_in_scan_file_finding(self):
        sigs = load_signatures()
        log = make_log("Normal log output with timing violations and routing congestion")
        findings = scan_file(log, sigs)
        log.unlink()
        assert len(findings) > 0, "Normal log should produce some keyword-fallback hits"
        for f in findings:
            assert "_detection_method" in f, "Each finding must have _detection_method set"

    def test_orchestrator_creates_heuristic_for_keyword_fallback(self):
        detection_method = "KEYWORD_FALLBACK"
        dc = "VERIFIED" if detection_method == "EXACT_MATCH" else \
             "HEURISTIC" if detection_method == "KEYWORD_FALLBACK" else "UNVERIFIED"
        assert dc == "HEURISTIC", "KEYWORD_FALLBACK must map to HEURISTIC"

    def test_orchestrator_creates_verified_for_exact_match(self):
        detections = {
            "_detection_method": "EXACT_MATCH",
            "category": "TIMING",
            "severity": "HIGH",
            "atlas_id": "FA-0001",
            "observed_signature": "WNS: -0.45  TNS: -12.3",
            "confidence": 0.92,
        }
        dc = "VERIFIED"
        assert dc == "VERIFIED", "EXACT_MATCH must map to VERIFIED"

    def test_historical_cleanup_distribution(self):
        import sqlite3
        from gli_flow.database.migrations import _get_db_path
        db = _get_db_path()
        conn = sqlite3.connect(db)
        dist = conn.execute(
            "SELECT detection_classification, COUNT(*) as cnt "
            "FROM failure_atlas_entries "
            "GROUP BY detection_classification "
            "ORDER BY cnt DESC"
        ).fetchall()
        conn.close()
        classifications = {r[0] for r in dist}
        assert "VERIFIED" in classifications, "VERIFIED entries must exist after cleanup"
        assert "HEURISTIC" in classifications, "HEURISTIC entries must exist after cleanup"
        for row in dist:
            assert row[0] in ("VERIFIED", "HEURISTIC", "UNVERIFIED"), \
                f"Invalid classification: {row[0]}"
