import importlib
import os
import sys
import tempfile
from pathlib import Path


def test_migrated_schema_has_entry_level_and_validates():
    from gli_flow.database.migrations import MigrationEngine, EXPECTED_COLUMNS, migrate_if_needed

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        migrate_if_needed(db_path)
        engine = MigrationEngine(db_path)
        try:
            ok, errors = engine.validate_runtime_schema()
            assert ok, errors
            cols = {
                row[1]
                for row in engine.conn.execute("PRAGMA table_info(failure_atlas_entries)").fetchall()
            }
            assert EXPECTED_COLUMNS["failure_atlas_entries"].issubset(cols)
            assert "entry_level" in cols
        finally:
            engine.close()
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_success_run_cleanup_removes_failure_level_entries_only():
    from failure_atlas.repository import FailureAtlasRepository

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        repo = FailureAtlasRepository(db_path=db_path)
        try:
            repo.insert_entry({
                "run_id": "run_success",
                "failure_type": "SETUP_VIOLATION",
                "severity": "HIGH",
                "title": "real failure",
            })
            repo.insert_entry({
                "run_id": "run_success",
                "failure_type": "FLOW_NOTE",
                "severity": "WARNING",
                "title": "warning only",
            })
            removed = repo.delete_failure_level_entries_for_run("run_success")
            remaining = repo.get_failures_for_run("run_success")
            assert removed == 1
            assert len(remaining) == 1
            assert remaining[0]["entry_level"] == "WARNING"
        finally:
            repo.close()
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_backend_rejects_report_path_traversal():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    old_env = os.environ.get("GLI_FLOW_DB_PATH")
    os.environ["GLI_FLOW_DB_PATH"] = db_path
    try:
        for mod in list(sys.modules):
            if mod == "backend.server":
                del sys.modules[mod]
        import backend.server
        importlib.reload(backend.server)
        from fastapi import HTTPException

        try:
            backend.server._safe_run_path("run_safe", "..", "..", "README.md")
            assert False, "path traversal was not rejected"
        except HTTPException as exc:
            assert exc.status_code == 400
    finally:
        if old_env is None:
            os.environ.pop("GLI_FLOW_DB_PATH", None)
        else:
            os.environ["GLI_FLOW_DB_PATH"] = old_env
        Path(db_path).unlink(missing_ok=True)
