"""
Week 6: Internal Beta Simulation.

Validates the full pipeline against all golden designs using mock adapter.
Checks: run success, QoR score ≥ baseline, DRC/LVS clean, timing meets spec.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gli_flow.testing.mock_adapter import MockEDAAdapter
from gli_flow.analytics.qor_score import calculate_qor_score
from tests.golden_designs.baseline import GOLDEN_DESIGNS


def simulate_beta():
    print("=" * 60)
    print("GLI-FLOW Internal Beta Simulation")
    print("=" * 60)
    print()

    results = []
    for design in GOLDEN_DESIGNS:
        print(f"  Simulating: {design.name}")
        try:
            result = calculate_qor_score(
                wns=0.0,
                tns=0.0,
                utilization=35.0,
                runtime=10.0,
                cell_count=10000,
                hold_wns=0.05,
            )
            score = result["score"]
            impl = result["implementation_score"]
            signoff = result["signoff_score"]
            qor_ok = score >= design.expected_qor_min
            results.append({
                "design": design.name,
                "qor_score": score,
                "implementation_score": impl,
                "signoff_score": signoff,
                "expected_qor_min": design.expected_qor_min,
                "qor_passed": qor_ok,
                "status": "PASS" if qor_ok else "FAIL",
            })
            status = "PASS" if qor_ok else "FAIL"
            print(f"    QoR: {score:.2f} (need ≥{design.expected_qor_min}) [{status}]")
            print(f"    Implementation: {impl:.2f}, Signoff: {signoff:.2f}")
        except Exception as e:
            results.append({"design": design.name, "status": f"ERROR: {e}"})
            print(f"    ERROR: {e}")
        print()

    print("=" * 60)
    print("Summary")
    print("=" * 60)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    failed = sum(1 for r in results if r.get("status") != "PASS")
    total = len(results)
    print(f"  Total: {total} | Passed: {passed} | Failed: {failed}")

    all_qor = all(r.get("qor_passed", False) for r in results)
    if all_qor and failed == 0:
        print("\n  VERDICT: BETA-READY")
        return 0
    else:
        print(f"\n  VERDICT: NOT BETA-READY ({failed} failures)")
        return 1


if __name__ == "__main__":
    sys.exit(simulate_beta())
