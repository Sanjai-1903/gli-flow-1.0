import tempfile
from pathlib import Path

from gli_flow.provenance.manifest import generate_reproducibility_manifest


def test_manifest_generates_json():
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp) / "run_001"
        result = generate_reproducibility_manifest(
            run_id="test-run",
            design_name="test",
            metrics={"wns": -0.1, "tns": -1.0, "utilization": 50},
            manifest_data={
                "rtl_files": [],
                "constraints": [],
                "pdk": "sky130hd",
            },
            run_dir=str(run_dir),
        )
        assert result.endswith("reproducibility.json")
        output = Path(result)
        assert output.exists()


def test_manifest_contains_expected_fields():
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp) / "run_002"
        result_path = generate_reproducibility_manifest(
            run_id="test-002",
            design_name="systolic_array",
            metrics={"wns": 0.0},
            manifest_data={
                "rtl_files": [],
                "constraints": [],
                "pdk": "sky130hd",
                "config_path": None,
            },
            run_dir=str(run_dir),
        )
        import json
        with open(result_path) as f:
            manifest = json.load(f)
        assert manifest["manifest_version"] == "2.0"
        assert manifest["design_name"] == "systolic_array"
        assert manifest["run_id"] == "test-002"
