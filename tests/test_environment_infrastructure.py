"""Tests for environment detection, validation, repair, and database migration."""

import os
import shutil
import sqlite3
import tempfile
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestToolDetector:
    def test_detect_yosys(self):
        from gli_flow.installer.tool_detector import detect_yosys
        r = detect_yosys()
        assert r.tool == "yosys"
        assert r.exists == (shutil.which("yosys") is not None)
        assert r.confidence.value in ("HIGH", "LOW", "UNKNOWN")

    def test_detect_git(self):
        from gli_flow.installer.tool_detector import detect_git
        r = detect_git()
        assert r.tool == "git"
        if r.exists:
            assert r.confidence.value == "HIGH"

    def test_detect_missing_tool(self):
        from gli_flow.installer.tool_detector import ToolDetector
        d = ToolDetector("nonexistent_tool_xyz")
        d.add_method("which", lambda: None)
        d.add_version_method("version", ["nonexistent_tool_xyz", "--version"])
        r = d.combine()
        assert r.exists is False
        assert r.confidence.value == "UNKNOWN"

    def test_confidence_scoring(self):
        from gli_flow.installer.tool_detector import Confidence, DetectionResult
        r = DetectionResult(tool="test")
        r.confidence = Confidence.HIGH
        assert r.score == 1.0
        r.confidence = Confidence.MEDIUM
        assert r.score == 0.6
        r.confidence = Confidence.LOW
        assert r.score == 0.3
        r.confidence = Confidence.UNKNOWN
        assert r.score == 0.0

    def test_meets_min_version(self):
        from gli_flow.installer.tool_detector import meets_min_version
        assert meets_min_version("1.0.0", "0.9.0")
        assert meets_min_version("2.0", "1.5")
        assert not meets_min_version("0.5", "1.0")
        assert not meets_min_version(None, "1.0")
        assert meets_min_version("8.3.411", "8.3")

    def test_netgen_lib_detection(self):
        from gli_flow.installer.tool_detector import detect_netgen_lib_dir
        result = detect_netgen_lib_dir()
        assert result is None or Path(result).is_dir()

    def test_netgenexec_detection(self):
        from gli_flow.installer.tool_detector import detect_netgenexec
        result = detect_netgenexec()
        assert result is None or Path(result).exists()

    def test_magic_multi_method(self):
        from gli_flow.installer.tool_detector import detect_magic
        r = detect_magic()
        assert len(r.methods_tried) >= 3
        if r.exists:
            assert any("which" in m for m in r.methods_succeeded)


class TestDatabaseMigrations:
    @pytest.fixture
    def tmp_db(self):
        tmpdir = tempfile.mkdtemp()
        db_path = os.path.join(tmpdir, "test.db")
        yield db_path
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_migration_engine_creates_schema_version(self, tmp_db):
        from gli_flow.database.migrations import MigrationEngine, RUNS_MIGRATIONS
        engine = MigrationEngine(tmp_db)
        try:
            cursor = engine.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
            assert cursor.fetchone() is not None
        finally:
            engine.close()

    def test_fresh_database_needs_migration(self, tmp_db):
        from gli_flow.database.migrations import MigrationEngine, RUNS_MIGRATIONS
        engine = MigrationEngine(tmp_db)
        try:
            state = engine.state("runs", RUNS_MIGRATIONS)
            assert state.current_version == 0
            assert len(state.pending) == len(RUNS_MIGRATIONS)
        finally:
            engine.close()

    def test_apply_migrations(self, tmp_db):
        from gli_flow.database.migrations import MigrationEngine, RUNS_MIGRATIONS, FAILURE_ATLAS_MIGRATIONS
        engine = MigrationEngine(tmp_db)
        try:
            r1 = engine.migrate("runs", RUNS_MIGRATIONS)
            assert r1.ok
            assert r1.current_version == len(RUNS_MIGRATIONS)
            r2 = engine.migrate("failure_atlas", FAILURE_ATLAS_MIGRATIONS)
            assert r2.ok
            assert engine.validate_schema("runs", RUNS_MIGRATIONS)
            assert engine.validate_schema("failure_atlas", FAILURE_ATLAS_MIGRATIONS)
        finally:
            engine.close()

    def test_migrate_if_needed(self, tmp_db):
        from gli_flow.database.migrations import migrate_if_needed
        migrate_if_needed(tmp_db)
        conn = sqlite3.connect(tmp_db)
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='runs'")
            assert cursor.fetchone() is not None
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='failure_atlas_entries'")
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_repair_migration(self, tmp_db):
        from gli_flow.database.migrations import MigrationEngine, RUNS_MIGRATIONS
        engine = MigrationEngine(tmp_db)
        try:
            state = engine.repair("runs", RUNS_MIGRATIONS)
            assert state.ok
        finally:
            engine.close()

    def test_idempotent_migrations(self, tmp_db):
        from gli_flow.database.migrations import MigrationEngine, RUNS_MIGRATIONS
        engine = MigrationEngine(tmp_db)
        try:
            engine.migrate("runs", RUNS_MIGRATIONS)
            engine.migrate("runs", RUNS_MIGRATIONS)
            assert engine.validate_schema("runs", RUNS_MIGRATIONS)
        finally:
            engine.close()


class TestEnvironmentValidator:
    @pytest.fixture
    def validator(self):
        from gli_flow.infrastructure.environment_validator import EnvironmentValidator
        return EnvironmentValidator()

    def test_validate_all_returns_report(self, validator):
        report = validator.validate_all()
        assert hasattr(report, "sections")
        assert len(report.sections) > 0
        assert "SYSTEM" in report.sections
        assert "TOOLS" in report.sections

    def test_system_section(self, validator):
        report = validator.validate_all()
        system_items = report.sections["SYSTEM"]
        names = [i.name for i in system_items]
        assert "Platform" in names
        assert "Python" in names

    def test_tools_section(self, validator):
        report = validator.validate_all()
        tools_items = report.sections["TOOLS"]
        names = [i.name for i in tools_items]
        assert "git" in names
        assert "yosys" in names
        assert "magic" in names
        assert "netgen" in names

    def test_database_section(self, validator):
        report = validator.validate_all()
        db_items = report.sections["DATABASE"]
        names = [i.name for i in db_items]
        assert "Schema" in names
        assert "File" in names

    def test_pdk_section(self, validator):
        report = validator.validate_all()
        assert "PDK" in report.sections

    def test_readiness_format(self, validator):
        report = validator.validate_all()
        assert "READY" in report.readiness or "WARNINGS" in report.readiness

    def test_validation_item_statuses(self, validator):
        report = validator.validate_all()
        valid_statuses = {"PASS", "FAIL", "WARN", "INFO"}
        for items in report.sections.values():
            for item in items:
                assert item.status in valid_statuses, f"Invalid status {item.status} for {item.name}"
                assert isinstance(item.name, str)
                assert isinstance(item.detail, str)


class TestRepairActions:
    @pytest.fixture
    def tmp_db(self):
        tmpdir = tempfile.mkdtemp()
        db_path = os.path.join(tmpdir, "test.db")
        yield db_path
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_schema_migration_repair_detect(self, tmp_db):
        from gli_flow.infrastructure.repair_actions import SchemaMigrationRepair
        r = SchemaMigrationRepair(db_path=tmp_db)
        can_repair = r.detect()
        assert isinstance(can_repair, bool)

    def test_schema_migration_repair_apply(self, tmp_db):
        from gli_flow.infrastructure.repair_actions import SchemaMigrationRepair
        r = SchemaMigrationRepair(db_path=tmp_db)
        result = r.repair()
        assert result.success
        assert r.verify()

    def test_cache_repair(self):
        from gli_flow.infrastructure.repair_actions import CacheRepair
        r = CacheRepair(cache_dirs=[])
        assert r.detect()
        result = r.repair()
        assert result.success
        assert r.verify()

    def test_repair_registry(self, tmp_db):
        from gli_flow.infrastructure.repair_actions import get_repair_actions
        actions = get_repair_actions(db_path=tmp_db)
        assert len(actions) > 0

    def test_run_repairs(self, tmp_db):
        from gli_flow.infrastructure.repair_actions import run_repairs
        results = run_repairs(db_path=tmp_db)
        assert len(results) > 0
        for r in results:
            assert isinstance(r.success, bool)
            assert isinstance(r.action, str)


class TestFailFast:
    def test_environment_validator_blocks_invalid(self):
        from gli_flow.infrastructure.environment_validator import EnvironmentValidator
        v = EnvironmentValidator()
        report = v.validate_all()
        if not report.all_pass:
            for items in report.sections.values():
                for item in items:
                    if item.failed:
                        assert item.status == "FAIL"
                        assert item.detail

    def test_readiness_blocks_execution(self):
        from gli_flow.infrastructure.environment_validator import EnvironmentValidator
        v = EnvironmentValidator()
        report = v.validate_all()
        if report.all_pass:
            assert "READY" in report.readiness
        else:
            assert "NOT READY" in report.readiness


class TestCLIIntegration:
    def test_cli_doctor_imports(self):
        from gli_flow.cli.main import doctor_command
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--fix", action="store_true")
        parser.add_argument("--db-path", type=str, default=None)
        args = parser.parse_args([])
        assert hasattr(args, "fix")

    def test_cli_db_imports(self):
        from gli_flow.cli.main import db_command
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("db_action", nargs="?", default="status")
        parser.add_argument("--db-path", type=str, default=None)
        args = parser.parse_args(["status"])
        assert hasattr(args, "db_action")

    def test_cli_doctor_parser(self):
        from gli_flow.cli.main import build_parser
        parser = build_parser()
        args = parser.parse_args(["doctor"])
        assert args.command == "doctor"

    def test_cli_db_parser(self):
        from gli_flow.cli.main import build_parser
        parser = build_parser()
        args = parser.parse_args(["db", "status"])
        assert args.command == "db"
        assert args.db_action == "status"

    def test_cli_doctor_fix_parser(self):
        from gli_flow.cli.main import build_parser
        parser = build_parser()
        args = parser.parse_args(["doctor", "--fix"])
        assert args.command == "doctor"
        assert args.fix is True
