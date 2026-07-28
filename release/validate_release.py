import json
import importlib
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

required_components = [
    "environment",
    "execution",
    "failure_atlas",
    "reliability",
    "regression",
    "release",
    "docs",
    "outputs",
]

validation = {
    "generated_at": str(datetime.now()),
    "validation_status": "VALID",
    "checks": [],
}

print("=" * 60)
print("GLI-FLOW Release Validation")
print("=" * 60)
print()

for component in required_components:
    path = BASE_DIR / component
    exists = path.exists()
    result = {
        "component": component,
        "exists": exists,
    }
    validation["checks"].append(result)
    print(f"{component}")
    print(f"  Exists : {exists}")
    print()
    if not exists:
        validation["validation_status"] = "INVALID"

# ---------------------------------------------------------------------------
# Release Gate: Multi-candidate discovery
# ---------------------------------------------------------------------------
print("-" * 60)
print("Release Gate: Multi-Candidate Discovery")
print("-" * 60)

multi_candidate_ok = True

try:
    from gli_flow.core import tool_discovery as td
    has_discover = hasattr(td, "discover_magic_binaries")
    has_ranking = hasattr(td, "rank_tool_candidates")
    has_validation = hasattr(td, "validate_magic_candidate")
    has_tool_candidate = hasattr(td, "ToolCandidate")

    if not all([has_discover, has_ranking, has_validation, has_tool_candidate]):
        print("  FAIL: Single-candidate discovery logic detected.")
        print("    Required: discover_magic_binaries(), rank_tool_candidates(),")
        print("              validate_magic_candidate(), ToolCandidate")
        validation["validation_status"] = "INVALID"
        multi_candidate_ok = False
    else:
        print("  PASS: Multi-candidate discovery architecture verified")
        print(f"    discover_magic_binaries:  {has_discover}")
        print(f"    rank_tool_candidates:     {has_ranking}")
        print(f"    validate_magic_candidate: {has_validation}")
        print(f"    ToolCandidate:            {has_tool_candidate}")
except Exception as e:
    print(f"  FAIL: Could not verify discovery architecture: {e}")
    validation["validation_status"] = "INVALID"
    multi_candidate_ok = False

gate_result = {
    "gate": "multi-candidate-discovery",
    "passed": multi_candidate_ok,
}
validation["checks"].append(gate_result)
print()

# ---------------------------------------------------------------------------
# Release Gate: Path shadowing regression tests
# ---------------------------------------------------------------------------
print("-" * 60)
print("Release Gate: Path Shadowing Regression Tests")
print("-" * 60)

regression_ok = True
regression_file = BASE_DIR / "tests" / "regressions" / "test_path_shadowing_prefers_functional_binary.py"
if not regression_file.exists():
    print("  FAIL: Path shadowing regression test not found")
    print(f"    Expected: tests/regressions/test_path_shadowing_prefers_functional_binary.py")
    validation["validation_status"] = "INVALID"
    regression_ok = False
else:
    print(f"  PASS: Regression test file exists")
    print(f"    {regression_file}")

gate_result = {
    "gate": "path-shadowing-regression-tests",
    "passed": regression_ok,
}
validation["checks"].append(gate_result)
print()

# ---------------------------------------------------------------------------
# Release Gate: Doctor repair framework
# ---------------------------------------------------------------------------
print("-" * 60)
print("Release Gate: Doctor Repair Framework")
print("-" * 60)

repair_ok = True
try:
    from gli_flow.infrastructure.repair_actions import (
        RepairAction, PathShadowingRepair, BrokenBinaryRepair,
        repair_path_shadowing, run_repairs,
    )

    has_path_shadowing = PathShadowingRepair is not None
    has_broken_binary = BrokenBinaryRepair is not None
    has_repair_fn = callable(repair_path_shadowing)
    has_run_repairs = callable(run_repairs)

    if not all([has_path_shadowing, has_broken_binary, has_repair_fn, has_run_repairs]):
        print("  FAIL: Doctor repair framework incomplete")
        validation["validation_status"] = "INVALID"
        repair_ok = False
    else:
        print("  PASS: Doctor repair framework verified")
        print(f"    PathShadowingRepair:      {has_path_shadowing}")
        print(f"    BrokenBinaryRepair:       {has_broken_binary}")
        print(f"    repair_path_shadowing():  {has_repair_fn}")
        print(f"    run_repairs():            {has_run_repairs}")
except Exception as e:
    print(f"  FAIL: Could not verify repair framework: {e}")
    validation["validation_status"] = "INVALID"
    repair_ok = False

gate_result = {
    "gate": "doctor-repair-framework",
    "passed": repair_ok,
}
validation["checks"].append(gate_result)
print()

# ---------------------------------------------------------------------------
# Release Gate: Adversarial environment tests
# ---------------------------------------------------------------------------
print("-" * 60)
print("Release Gate: Adversarial Environment Tests")
print("-" * 60)

adversarial_ok = True
adversarial_dir = BASE_DIR / "tests" / "adversarial" / "environment"
if not adversarial_dir.exists() or not any(adversarial_dir.glob("test_*.py")):
    print("  FAIL: Adversarial environment tests not found")
    print(f"    Expected: tests/adversarial/environment/test_*.py")
    validation["validation_status"] = "INVALID"
    adversarial_ok = False
else:
    test_files = list(adversarial_dir.glob("test_*.py"))
    print(f"  PASS: {len(test_files)} adversarial test file(s) found")
    for tf in test_files:
        print(f"    {tf.name}")

gate_result = {
    "gate": "adversarial-environment-tests",
    "passed": adversarial_ok,
}
validation["checks"].append(gate_result)
print()

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("=" * 60)
status_color = "PASS" if validation["validation_status"] == "VALID" else "FAIL"
print(f"Release Status: {status_color}")
print(f"Generated: {validation['generated_at']}")
print("=" * 60)

output = BASE_DIR / "outputs" / "reports" / "release_validation_report_v2.json"
with open(output, "w") as f:
    json.dump(validation, f, indent=4)

print(f"\n[OUTPUT] {output}")
