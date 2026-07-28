import json
import os
import tempfile

import pytest


@pytest.fixture
def sample_orfs_report():
    return {
        "wns": -0.12,
        "tns": -3.45,
        "utilization": 45.2,
        "cell_count": 4231,
        "runtime_sec": 89.0,
    }


@pytest.fixture
def temp_run_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_signatures():
    return [
        {
            "atlas_id": "SYNTH-0001",
            "category": "synthesis",
            "severity": "critical",
            "trigger_conditions": {"log_pattern": "ERROR: Unsupported RTL construct"},
            "observed_signature": "Unsupported RTL construct",
            "confirmed_by_runs": ["run_001"],
            "pdk": "sky130hd",
            "backend": "yosys",
            "remediation": "Use supported Verilog constructs",
            "confidence": 0.95,
            "public": True,
        }
    ]
