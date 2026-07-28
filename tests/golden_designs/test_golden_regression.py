import os
import tempfile
import yaml
from pathlib import Path
from tests.golden_designs.baseline import GOLDEN_DESIGNS, compare_baseline, get_design


GOLDEN_RTL = Path(__file__).parent / "rtl"
EXAMPLES = Path(__file__).parent.parent.parent / "examples"


def test_all_golden_designs_have_rtl():
    for d in GOLDEN_DESIGNS:
        for rtl_file in d.rtl_files:
            assert (GOLDEN_RTL / rtl_file).exists(), (
                f"{d.name}: missing RTL {rtl_file}"
            )


def test_all_golden_designs_have_manifest():
    for d in GOLDEN_DESIGNS:
        manifest_path = EXAMPLES / d.name / "gli_manifest.yaml"
        assert manifest_path.exists(), f"{d.name}: missing manifest at {manifest_path}"
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        assert manifest.get("design_name") == d.name or manifest.get("top_module") == d.top_module, (
            f"{d.name}: manifest top_module mismatch"
        )


def test_compare_baseline_passes_with_good_results():
    for d in GOLDEN_DESIGNS:
        alerts = compare_baseline(
            design=d,
            actual_qor=d.expected_qor_min + 0.05,
            actual_wns=d.expected_wns_min + 0.1,
            actual_tns=d.expected_tns_min + 1.0,
            actual_util=d.expected_util_max - 5.0,
            actual_runtime=d.expected_max_runtime_s - 10.0,
            drc_clean=True,
            lvs_clean=True,
        )
        assert not alerts, f"{d.name}: unexpected alerts with good results: {alerts}"


def test_compare_baseline_detects_qor_regression():
    d = get_design("counter")
    alerts = compare_baseline(
        design=d,
        actual_qor=d.expected_qor_min - 0.1,
        actual_wns=d.expected_wns_min,
        actual_tns=d.expected_tns_min,
        actual_util=d.expected_util_max,
        actual_runtime=d.expected_max_runtime_s,
        drc_clean=True,
        lvs_clean=True,
    )
    assert any("QoR" in a for a in alerts)


def test_compare_baseline_detects_drc_regression():
    d = get_design("counter")
    alerts = compare_baseline(
        design=d,
        actual_qor=d.expected_qor_min,
        actual_wns=d.expected_wns_min,
        actual_tns=d.expected_tns_min,
        actual_util=d.expected_util_max,
        actual_runtime=d.expected_max_runtime_s,
        drc_clean=False,
        lvs_clean=True,
    )
    assert any("DRC" in a for a in alerts)


def test_compare_baseline_detects_lvs_regression():
    d = get_design("counter")
    alerts = compare_baseline(
        design=d,
        actual_qor=d.expected_qor_min,
        actual_wns=d.expected_wns_min,
        actual_tns=d.expected_tns_min,
        actual_util=d.expected_util_max,
        actual_runtime=d.expected_max_runtime_s,
        drc_clean=True,
        lvs_clean=False,
    )
    assert any("LVS" in a for a in alerts)


def test_compare_baseline_detects_utilization_regression():
    d = get_design("counter")
    alerts = compare_baseline(
        design=d,
        actual_qor=d.expected_qor_min,
        actual_wns=d.expected_wns_min,
        actual_tns=d.expected_tns_min,
        actual_util=d.expected_util_max + 10.0,
        actual_runtime=d.expected_max_runtime_s,
        drc_clean=True,
        lvs_clean=True,
    )
    assert any("Utilization" in a for a in alerts)


def test_compare_baseline_detects_runtime_regression():
    d = get_design("counter")
    alerts = compare_baseline(
        design=d,
        actual_qor=d.expected_qor_min,
        actual_wns=d.expected_wns_min,
        actual_tns=d.expected_tns_min,
        actual_util=d.expected_util_max,
        actual_runtime=d.expected_max_runtime_s + 100.0,
        drc_clean=True,
        lvs_clean=True,
    )
    assert any("Runtime" in a for a in alerts)


def test_get_design_returns_none_for_unknown():
    assert get_design("nonexistent") is None
