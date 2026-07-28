"""Tests for Resolution Intelligence v1."""

import json
import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

import pytest

from gli_flow.resolution_intelligence import (
    ResolutionPattern,
    ResolutionFeedback,
    ResolutionRepository,
    ResolutionCapture,
    ResolutionScorer,
    TrustScorer,
    RunComparisonEngine,
    AtlasCandidateGenerator,
)


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS resolution_patterns (
            id TEXT PRIMARY KEY,
            failure_fingerprint TEXT NOT NULL,
            failure_type TEXT NOT NULL,
            root_cause TEXT,
            resolution TEXT NOT NULL,
            resolution_type TEXT,
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            confidence REAL DEFAULT 0.0,
            first_seen TEXT,
            last_seen TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            unique_runs INTEGER DEFAULT 0,
            unique_designs INTEGER DEFAULT 0,
            engineer_confirmations INTEGER DEFAULT 0,
            contradictory_reports INTEGER DEFAULT 0,
            trust_score REAL DEFAULT 0.0,
            trust_level TEXT DEFAULT 'LOW',
            trust_reason TEXT DEFAULT '',
            tracked_run_ids TEXT DEFAULT '[]',
            tracked_design_names TEXT DEFAULT '[]'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS resolution_feedback (
            id TEXT PRIMARY KEY,
            pattern_id TEXT NOT NULL,
            run_id TEXT NOT NULL,
            feedback_type TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS failure_atlas_entries (
            id TEXT PRIMARY KEY,
            run_id TEXT,
            failure_type TEXT,
            severity TEXT,
            title TEXT,
            description TEXT,
            signature TEXT,
            recommended_fix TEXT,
            confidence REAL,
            fix_applied INTEGER DEFAULT 0,
            fix_type TEXT,
            fix_description TEXT,
            fix_run_id TEXT,
            before_metrics TEXT,
            after_metrics TEXT,
            resolution_confidence TEXT,
            entry_level TEXT,
            evidence TEXT,
            detected_at TEXT
        )
    """)
    yield conn
    conn.close()


class TestResolutionScoring:

    def test_no_data_zero_confidence(self):
        scorer = ResolutionScorer()
        assert scorer.calculate(0, 0) == 0.0

    def test_all_success_high_confidence(self):
        scorer = ResolutionScorer()
        conf = scorer.calculate(18, 2)
        assert conf >= 0.80
        assert conf <= 0.95

    def test_all_failures_low_confidence(self):
        scorer = ResolutionScorer()
        conf = scorer.calculate(0, 5)
        assert conf <= 0.30

    def test_single_success_moderate_confidence(self):
        scorer = ResolutionScorer()
        conf = scorer.calculate(1, 0)
        assert 0.50 <= conf <= 0.80

    def test_equal_success_failure(self):
        scorer = ResolutionScorer()
        conf = scorer.calculate(5, 5)
        assert conf == 0.50

    def test_confidence_labels(self):
        scorer = ResolutionScorer()
        assert scorer.get_confidence_label(0.85) == "HIGH"
        assert scorer.get_confidence_label(0.60) == "MEDIUM"
        assert scorer.get_confidence_label(0.30) == "LOW"

    def test_is_reliable(self):
        scorer = ResolutionScorer()
        assert scorer.is_reliable(0.75, 4)
        assert not scorer.is_reliable(0.75, 2)
        assert not scorer.is_reliable(0.50, 5)


class TestResolutionRepository:

    def test_upsert_and_retrieve_pattern(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pattern = ResolutionPattern(
            id="",
            failure_fingerprint="drc_violation:li.3",
            failure_type="DRC_VIOLATION",
            root_cause="Spacing violation",
            resolution="Increase routing spacing",
            resolution_type="config_change",
            success_count=5,
            failure_count=1,
        )
        pattern_id = repo.upsert_pattern(pattern)
        assert pattern_id

        retrieved = repo.get_pattern(pattern_id)
        assert retrieved is not None
        assert retrieved.failure_fingerprint == "drc_violation:li.3"
        assert retrieved.resolution == "Increase routing spacing"
        assert retrieved.success_count == 5

    def test_find_by_fingerprint(self, db_conn):
        repo = ResolutionRepository(db_conn)
        fp = "timing:hold_violation"
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint=fp, failure_type="TIMING",
            resolution="Add hold buffers", success_count=3, failure_count=0,
        ))
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint=fp, failure_type="TIMING",
            resolution="Reduce clock skew", success_count=1, failure_count=2,
        ))

        results = repo.find_by_fingerprint(fp)
        assert len(results) == 2
        assert results[0].confidence >= results[1].confidence

    def test_find_by_failure_type(self, db_conn):
        repo = ResolutionRepository(db_conn)
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp1", failure_type="DRC",
            resolution="Fix spacing", success_count=5, failure_count=0,
        ))
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp2", failure_type="LVS",
            resolution="Fix short", success_count=2, failure_count=1,
        ))

        drc_results = repo.find_by_failure_type("DRC")
        assert len(drc_results) == 1
        assert drc_results[0].resolution == "Fix spacing"

    def test_increment_success(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pid = repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp", failure_type="T",
            resolution="Fix", success_count=1, failure_count=0,
        ))
        repo.increment_success(pid)
        pattern = repo.get_pattern(pid)
        assert pattern.success_count == 2

    def test_increment_failure(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pid = repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp", failure_type="T",
            resolution="Fix", success_count=1, failure_count=0,
        ))
        repo.increment_failure(pid)
        pattern = repo.get_pattern(pid)
        assert pattern.failure_count == 1

    def test_get_top_resolved(self, db_conn):
        repo = ResolutionRepository(db_conn)
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp1", failure_type="A",
            resolution="Fix A", success_count=10, failure_count=0,
        ))
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp2", failure_type="B",
            resolution="Fix B", success_count=1, failure_count=5,
        ))
        top = repo.get_top_resolved(limit=5)
        assert len(top) >= 1
        assert top[0].failure_fingerprint == "fp1"

    def test_get_top_unresolved(self, db_conn):
        repo = ResolutionRepository(db_conn)
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp1", failure_type="A",
            resolution="Fix A", success_count=0, failure_count=10,
        ))
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp2", failure_type="B",
            resolution="Fix B", success_count=5, failure_count=1,
        ))
        top = repo.get_top_unresolved(limit=5)
        assert len(top) >= 1
        assert top[0].failure_fingerprint == "fp1"

    def test_get_summary_stats(self, db_conn):
        repo = ResolutionRepository(db_conn)
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp1", failure_type="T",
            resolution="Fix", success_count=8, failure_count=2,
        ))
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp2", failure_type="T",
            resolution="Fix2", success_count=5, failure_count=5,
        ))
        stats = repo.get_summary_stats()
        assert stats["total_patterns"] == 2
        assert stats["total_successes"] == 13
        assert stats["total_failures"] == 7


class TestResolutionCapture:

    def test_capture_new_pattern(self, db_conn):
        capture = ResolutionCapture(db_conn)
        pid = capture.capture_from_run_recovery(
            failed_run_id="run_001",
            successful_run_id="run_002",
            failure_fingerprint="drc:li.3",
            failure_type="DRC",
            resolution="Increase routing spacing",
        )
        assert pid

        repo = ResolutionRepository(db_conn)
        pattern = repo.get_pattern(pid)
        assert pattern.success_count == 1
        assert pattern.failure_count == 0

    def test_capture_existing_pattern_increments_success(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pid = repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="timing:hold", failure_type="TIMING",
            resolution="Add hold buffers", success_count=3, failure_count=0,
        ))

        capture = ResolutionCapture(db_conn)
        capture.capture_from_run_recovery(
            failed_run_id="run_003",
            successful_run_id="run_004",
            failure_fingerprint="timing:hold",
            failure_type="TIMING",
            resolution="Add hold buffers",
        )

        pattern = repo.get_pattern(pid)
        assert pattern.success_count == 4

    def test_capture_failed_attempt(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pid = repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="drc:space",
            failure_type="DRC", resolution="Widen spacing",
            success_count=1, failure_count=0,
        ))

        capture = ResolutionCapture(db_conn)
        capture.capture_failed_attempt(
            failure_fingerprint="drc:space",
            failure_type="DRC",
            resolution="Widen spacing",
        )

        pattern = repo.get_pattern(pid)
        assert pattern.failure_count == 1


class TestRunComparison:

    def test_compare_identical_runs(self):
        engine = RunComparisonEngine()
        run_a = {"run_id": "run_001", "wns": -0.5, "tns": -10.0, "utilization": 70.0, "cell_count": 10000, "qor_score": 0.85, "runtime_sec": 3600}
        run_b = {"run_id": "run_002", "wns": -0.5, "tns": -10.0, "utilization": 70.0, "cell_count": 10000, "qor_score": 0.85, "runtime_sec": 3600}

        result = engine.compare(run_a, run_b)
        assert result.fields["wns"]["delta"] == 0
        assert result.fields["tns"]["delta"] == 0

    def test_compare_improved_run(self):
        engine = RunComparisonEngine()
        run_a = {"run_id": "run_001", "wns": -1.0, "tns": -20.0, "utilization": 75.0, "cell_count": 12000, "qor_score": 0.60, "runtime_sec": 4000}
        run_b = {"run_id": "run_002", "wns": -0.3, "tns": -5.0, "utilization": 68.0, "cell_count": 11000, "qor_score": 0.85, "runtime_sec": 3200}

        result = engine.compare(run_a, run_b)
        assert result.fields["wns"]["delta"] > 0
        assert result.fields["qor_score"]["delta"] > 0

    def test_compare_with_failures(self):
        engine = RunComparisonEngine()
        run_a = {"run_id": "run_001", "wns": -1.0, "tns": -20.0, "utilization": 75.0, "cell_count": 12000, "qor_score": 0.60, "runtime_sec": 4000}
        run_b = {"run_id": "run_002", "wns": -0.3, "tns": -5.0, "utilization": 68.0, "cell_count": 11000, "qor_score": 0.85, "runtime_sec": 3200}
        failures_a = [{"failure_type": "DRC"}, {"failure_type": "TIMING"}]
        failures_b = [{"failure_type": "TIMING"}]

        result = engine.compare_with_failures(run_a, run_b, failures_a, failures_b)
        resolved = [d for d in result.failure_diffs if d["type"] == "resolved"]
        assert len(resolved) > 0
        assert "DRC" in resolved[0]["failures"]


class TestAtlasCandidateGenerator:

    def test_generate_candidates(self, db_conn):
        repo = ResolutionRepository(db_conn)
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="unknown:fp1", failure_type="UNKNOWN",
            resolution="Increase drive strength",
            success_count=10, failure_count=0,
        ))
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="known:fp2", failure_type="KNOWN",
            resolution="Fix spacing",
            success_count=2, failure_count=3,
        ))

        generator = AtlasCandidateGenerator(db_conn)
        candidates = generator.generate_candidates(min_confidence=0.70, min_occurrences=3)
        assert len(candidates) >= 1
        assert candidates[0]["failure_fingerprint"] == "unknown:fp1"

    def test_promote_to_atlas(self, db_conn):
        generator = AtlasCandidateGenerator(db_conn)
        with patch("failure_atlas.repository.FailureAtlasRepository") as MockRepo:
            mock_instance = MagicMock()
            mock_instance.insert_entry.return_value = "atlas_entry_001"
            MockRepo.return_value = mock_instance
            MockRepo.return_value.close.return_value = None

            entry_id = generator.promote_to_atlas(
                {
                    "failure_fingerprint": "unknown:test",
                    "failure_type": "TIMING",
                    "resolution": "Add hold buffers",
                    "confidence": 0.85,
                    "occurrence_count": 5,
                    "first_seen": "2025-01-01",
                    "last_seen": "2025-06-01",
                },
                reviewer_notes="Reviewed and confirmed",
            )
            assert entry_id == "atlas_entry_001"


class TestResolutionFeedback:

    def test_record_feedback_confirmed(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pid = repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp", failure_type="T",
            resolution="Fix", success_count=5, failure_count=0,
        ))

        repo.record_feedback(pid, "run_001", "confirmed")
        pattern = repo.get_pattern(pid)
        assert pattern.success_count == 6

    def test_record_feedback_rejected(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pid = repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp", failure_type="T",
            resolution="Fix", success_count=5, failure_count=0,
        ))

        repo.record_feedback(pid, "run_001", "rejected")
        pattern = repo.get_pattern(pid)
        assert pattern.failure_count == 1

    def test_get_feedback(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pid = repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp", failure_type="T",
            resolution="Fix", success_count=5, failure_count=0,
        ))

        repo.record_feedback(pid, "run_001", "confirmed")
        feedback = repo.get_feedback(pid)
        assert len(feedback) >= 1
        assert feedback[0].feedback_type == "confirmed"


class TestResolutionPatternModel:

    def test_total_attempts(self):
        p = ResolutionPattern(
            id="test", failure_fingerprint="fp", failure_type="T",
            resolution="Fix", success_count=5, failure_count=3,
        )
        assert p.total_attempts == 8

    def test_zero_attempts(self):
        p = ResolutionPattern(
            id="test", failure_fingerprint="fp", failure_type="T",
            resolution="Fix", success_count=0, failure_count=0,
        )
        assert p.total_attempts == 0


class TestResolutionCaptureEdgeCases:

    def test_capture_with_root_cause(self, db_conn):
        capture = ResolutionCapture(db_conn)
        pid = capture.capture_from_run_recovery(
            failed_run_id="run_001",
            successful_run_id="run_002",
            failure_fingerprint="drc:li.3",
            failure_type="DRC",
            resolution="Increase routing spacing",
            root_cause="Insufficient routing tracks",
        )
        repo = ResolutionRepository(db_conn)
        pattern = repo.get_pattern(pid)
        assert pattern.root_cause == "Insufficient routing tracks"

    def test_capture_failed_attempt_new_pattern(self, db_conn):
        capture = ResolutionCapture(db_conn)
        pid = capture.capture_failed_attempt(
            failure_fingerprint="timing:setup",
            failure_type="TIMING",
            resolution="Reduce clock frequency",
        )
        repo = ResolutionRepository(db_conn)
        pattern = repo.get_pattern(pid)
        assert pattern.failure_count == 1
        assert pattern.success_count == 0

    def test_capture_existing_failed_pattern_increments_failure(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pid = repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp", failure_type="T",
            resolution="Fix", success_count=0, failure_count=2,
        ))
        capture = ResolutionCapture(db_conn)
        capture.capture_failed_attempt("fp", "T", "Fix")
        pattern = repo.get_pattern(pid)
        assert pattern.failure_count == 3


class TestTrustScorer:

    def test_trust_no_data(self):
        scorer = TrustScorer()
        result = scorer.calculate_trust(0, 0)
        assert result["trust_level"] == "LOW"
        assert result["trust_score"] == 0.0
        assert "No data" in result["trust_reason"]

    def test_trust_high_confidence_many_runs_designs(self):
        scorer = TrustScorer()
        result = scorer.calculate_trust(
            success_count=50, failure_count=2,
            unique_runs=25, unique_designs=12,
            last_seen="2026-06-14T12:00:00",
            engineer_confirmations=8, contradictory_reports=0,
        )
        assert result["trust_level"] == "HIGH"
        assert result["trust_score"] >= 0.80
        assert "52 attempts" in result["trust_reason"]
        assert "25 runs" in result["trust_reason"]
        assert "12 designs" in result["trust_reason"]
        assert "confirmed" in result["trust_reason"]

    def test_trust_low_due_to_contradictions(self):
        scorer = TrustScorer()
        result = scorer.calculate_trust(
            success_count=10, failure_count=10,
            unique_runs=5, unique_designs=3,
            last_seen="2026-06-14T12:00:00",
            engineer_confirmations=1, contradictory_reports=5,
        )
        assert result["trust_level"] == "LOW"
        assert "contradiction" in result["trust_reason"]

    def test_trust_moderate_breadth(self):
        scorer = TrustScorer()
        result = scorer.calculate_trust(
            success_count=5, failure_count=2,
            unique_runs=2, unique_designs=1,
            last_seen="2026-06-14T12:00:00",
            engineer_confirmations=0, contradictory_reports=0,
        )
        assert result["trust_level"] in ("MEDIUM", "LOW")

    def test_trust_engineer_confirmations_boost(self):
        scorer = TrustScorer()
        without = scorer.calculate_trust(
            success_count=5, failure_count=0,
            unique_runs=3, unique_designs=2,
            last_seen="2026-06-14T12:00:00",
            engineer_confirmations=0, contradictory_reports=0,
        )
        with_conf = scorer.calculate_trust(
            success_count=5, failure_count=0,
            unique_runs=3, unique_designs=2,
            last_seen="2026-06-14T12:00:00",
            engineer_confirmations=3, contradictory_reports=0,
        )
        assert with_conf["trust_score"] > without["trust_score"]
        assert "confirmed" in with_conf["trust_reason"]

    def test_trust_recency_decay(self):
        scorer = TrustScorer()
        recent = scorer.calculate_trust(
            success_count=10, failure_count=1,
            unique_runs=5, unique_designs=2,
            last_seen="2026-06-14T12:00:00",
        )
        old = scorer.calculate_trust(
            success_count=10, failure_count=1,
            unique_runs=5, unique_designs=2,
            last_seen="2025-01-01T12:00:00",
        )
        assert recent["trust_score"] > old["trust_score"]
        assert "long ago" in old["trust_reason"]

    def test_trust_clamped_to_zero_one(self):
        scorer = TrustScorer()
        perfect = scorer.calculate_trust(
            success_count=1000, failure_count=0,
            unique_runs=100, unique_designs=50,
            last_seen="2026-06-14T12:00:00",
            engineer_confirmations=50, contradictory_reports=0,
        )
        assert 0.0 <= perfect["trust_score"] <= 1.0
        assert perfect["trust_level"] == "HIGH"

    def test_trust_score_formats(self):
        scorer = TrustScorer()
        result = scorer.calculate_trust(1, 0, unique_runs=1)
        assert isinstance(result["trust_score"], float)
        assert result["trust_level"] in ("HIGH", "MEDIUM", "LOW")
        assert isinstance(result["trust_reason"], str)
        assert len(result["trust_reason"]) > 0


class TestTrustRepository:

    def test_upsert_pattern_sets_trust(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pattern = ResolutionPattern(
            id="", failure_fingerprint="drc:test",
            failure_type="DRC", resolution="Fix spacing",
            success_count=10, failure_count=0,
            unique_runs=5, unique_designs=3,
            engineer_confirmations=2, contradictory_reports=0,
        )
        pid = repo.upsert_pattern(pattern)
        retrieved = repo.get_pattern(pid)
        assert retrieved.trust_score > 0
        assert retrieved.trust_level in ("HIGH", "MEDIUM", "LOW")
        assert len(retrieved.trust_reason) > 0

    def test_increment_success_tracks_unique_runs(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pid = repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp", failure_type="T",
            resolution="Fix", success_count=0, failure_count=0,
        ))
        repo.increment_success(pid, run_id="run_001", design_name="design_a")
        repo.increment_success(pid, run_id="run_002", design_name="design_a")
        repo.increment_success(pid, run_id="run_001", design_name="design_b")
        pattern = repo.get_pattern(pid)
        assert pattern.unique_runs == 2
        assert pattern.unique_designs == 2

    def test_record_feedback_tracks_confirmations(self, db_conn):
        repo = ResolutionRepository(db_conn)
        pid = repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp", failure_type="T",
            resolution="Fix", success_count=5, failure_count=0,
        ))
        repo.record_feedback(pid, "run_001", "confirmed")
        repo.record_feedback(pid, "run_002", "confirmed")
        repo.record_feedback(pid, "run_003", "rejected")
        pattern = repo.get_pattern(pid)
        assert pattern.engineer_confirmations == 2
        assert pattern.contradictory_reports == 1
        assert pattern.success_count == 7
        assert pattern.failure_count == 1

    def test_get_trust_summary(self, db_conn):
        repo = ResolutionRepository(db_conn)
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp1", failure_type="T",
            resolution="Fix1", success_count=50, failure_count=2,
            unique_runs=20, unique_designs=10,
            engineer_confirmations=5, contradictory_reports=0,
        ))
        repo.upsert_pattern(ResolutionPattern(
            id="", failure_fingerprint="fp2", failure_type="T",
            resolution="Fix2", success_count=0, failure_count=3,
        ))
        summary = repo.get_trust_summary()
        assert summary["total_patterns"] == 2
        assert summary["high_count"] >= 1
        assert summary["avg_trust_score"] > 0
