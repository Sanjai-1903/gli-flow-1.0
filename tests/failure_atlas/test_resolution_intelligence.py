import pytest
import sqlite3
import os
import tempfile
from failure_atlas.correlation_engine import get_correlation_data

# Use unique temp DB to avoid cross-test contamination
DB_PATH = tempfile.mktemp(suffix="_resolution_test.db")

def setup_module():
    os.environ["GLI_FLOW_DB"] = DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS failure_atlas_entries (
            id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL DEFAULT '',
            failure_id TEXT,
            failure_type TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'MEDIUM',
            title TEXT,
            description TEXT,
            recommended_fix TEXT,
            confidence REAL DEFAULT 0.8,
            signature TEXT,
            domain TEXT,
            category TEXT,
            evidence TEXT,
            detected_at TEXT DEFAULT (datetime('now')),
            parent_run_id TEXT,
            fix_applied INTEGER DEFAULT 0,
            fix_type TEXT,
            fix_description TEXT,
            fix_run_id TEXT,
            before_metrics TEXT,
            after_metrics TEXT,
            resolution_confidence TEXT
        )
    """)
    # Insert mock data
    conn.execute("INSERT OR IGNORE INTO failure_atlas_entries (id, run_id, failure_type, severity, fix_applied, fix_type, fix_description, detected_at, after_metrics) VALUES ('1', 'run_a', 'licon.8a', 'HIGH', 1, 'Die Padding', 'Added die padding', '2026-06-01', '{\"is_clean\": 1}')")
    conn.execute("INSERT OR IGNORE INTO failure_atlas_entries (id, run_id, failure_type, severity, fix_applied, fix_type, fix_description, detected_at, after_metrics) VALUES ('2', 'run_b', 'licon.8a', 'HIGH', 1, 'Die Padding', 'Added die padding', '2026-06-02', '{\"is_clean\": 1}')")
    conn.execute("INSERT OR IGNORE INTO failure_atlas_entries (id, run_id, failure_type, severity, fix_applied, fix_type, fix_description, detected_at, after_metrics) VALUES ('3', 'run_c', 'licon.8a', 'TAPEOUT_BLOCKING', 1, 'Util Reduction', 'Reduced utilization', '2026-06-03', '{\"drc_total\": 5}')")
    conn.commit()
    conn.close()

def teardown_module():
    os.environ.pop("GLI_FLOW_DB", None)
    if os.path.exists(DB_PATH):
        os.unlink(DB_PATH)

def test_resolution_intelligence_stats():
    data = get_correlation_data('licon.8a')
    eff = data['resolution_effectiveness']
    
    # Check "Die Padding" stats (2 attempts, 2 success = 100%)
    padding_fix = next(f for f in eff if f['fix_type'] == 'Die Padding')
    assert padding_fix['attempts'] == 2
    assert padding_fix['success_rate'] == 100.0
    
    # Check "Util Reduction" stats (1 attempt, 0 success = 0%)
    util_fix = next(f for f in eff if f['fix_type'] == 'Util Reduction')
    assert util_fix['attempts'] == 1
    assert util_fix['success_rate'] == 0.0

def test_important_run_correlation():
    data = get_correlation_data('licon.8a')
    padding_fix = next(f for f in data['resolution_effectiveness'] if f['fix_type'] == 'Die Padding')
    util_fix = next(f for f in data['resolution_effectiveness'] if f['fix_type'] == 'Util Reduction')
    
    # No important runs in the mock data for padding, 1 for util reduction
    assert padding_fix['important_runs'] == 0
    assert util_fix['important_runs'] == 1
