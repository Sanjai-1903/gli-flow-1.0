"""
Release gate: LVS signoff integrity validation.

Ensures the LVS pipeline cannot produce false PASS by running:
  1. LVS false-clean prevention tests
  2. LVS gate integrity tests
  3. Adversarial LVS tests
  4. Netgen argument construction regression tests

All must pass before release.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_SUITES = [
    "tests/reliability/test_lvs_false_clean_prevention.py",
    "tests/signoff/test_lvs_gate_integrity.py",
    "tests/signoff/test_lvs_comparison_evidence_required.py",
    "tests/adversarial/lvs/test_lvs_adversarial.py",
    "tests/regressions/test_netgen_argument_construction.py",
    "tests/regressions/test_inf_lvs_002.py",
]

REQUIRED_IMPORTS = [
    "from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus",
    "from gli_flow.backends.openroad_adapter import OpenRoadAdapter",
    "from gli_flow.core.orchestrator import FlowOrchestrator",
]

INVARIANT_CHECKS = [
    ("Default LVSResult status is NOT_RUN", """
from gli_flow.backends.openroad_adapter import LVSResult
r = LVSResult()
assert r.status == "NOT_RUN", f"Expected NOT_RUN, got {r.status!r}"
"""),
    ("Default LVSResult is_clean is False", """
from gli_flow.backends.openroad_adapter import LVSResult
r = LVSResult()
assert r.is_clean is False
"""),
    ("Default LVSResult comparison_completed is False", """
from gli_flow.backends.openroad_adapter import LVSResult
r = LVSResult()
assert r.comparison_completed is False
"""),
    ("Default LVSResult report_exists is False", """
from gli_flow.backends.openroad_adapter import LVSResult
r = LVSResult()
assert r.report_exists is False
"""),
    ("LVSResult PASS has correct fields", """
from gli_flow.backends.openroad_adapter import LVSResult, LVSStatus
r = LVSResult(status=LVSStatus.PASS, comparison_completed=True, report_exists=True)
assert r.status == LVSStatus.PASS
assert r.comparison_completed
assert r.report_exists
assert r.return_code == -1  # default, must be set explicitly
"""),
    ("SignoffGate.set_from_status PASS", """
from gli_flow.core.orchestrator import SignoffGate
gate = SignoffGate()
gate.set_from_status("lvs_pass", "PASS")
assert gate.lvs_pass
"""),
    ("SignoffGate.set_from_status ERROR", """
from gli_flow.core.orchestrator import SignoffGate
gate = SignoffGate()
gate.set_from_status("lvs_pass", "ERROR")
assert not gate.lvs_pass
"""),
    ("SignoffGate.set_from_status NOT_RUN", """
from gli_flow.core.orchestrator import SignoffGate
gate = SignoffGate()
gate.set_from_status("lvs_pass", "NOT_RUN")
assert not gate.lvs_pass
"""),
]


def run_invariant_checks() -> list[dict]:
    results = []
    for name, code in INVARIANT_CHECKS:
        start = time.time()
        try:
            exec(code.strip(), {"__builtins__": __builtins__})
            results.append({
                "check": name,
                "status": "PASS",
                "duration_seconds": round(time.time() - start, 3),
            })
        except AssertionError as e:
            msg = str(e) if str(e) else "assertion failed"
            results.append({
                "check": name,
                "status": "FAIL",
                "detail": msg,
                "duration_seconds": round(time.time() - start, 3),
            })
        except Exception as e:
            results.append({
                "check": name,
                "status": "ERROR",
                "detail": str(e),
                "duration_seconds": round(time.time() - start, 3),
            })
    return results


def run_pytest(suite_path: str) -> dict:
    start = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", suite_path, "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    elapsed = round(time.time() - start, 2)
    passed = result.returncode == 0
    summary = result.stdout.split("===")[-1].strip() if "===" in result.stdout else result.stdout[-500:]
    return {
        "suite": suite_path,
        "passed": passed,
        "return_code": result.returncode,
        "duration_seconds": elapsed,
        "summary": summary[:200],
        "failures": result.stdout.count("FAILED"),
    }


def validate_imports() -> list[dict]:
    results = []
    for imp in REQUIRED_IMPORTS:
        start = time.time()
        try:
            exec(imp.strip(), {"__builtins__": __builtins__})
            results.append({
                "import": imp,
                "status": "PASS",
                "duration_seconds": round(time.time() - start, 3),
            })
        except ImportError as e:
            results.append({
                "import": imp,
                "status": "FAIL",
                "detail": str(e),
                "duration_seconds": round(time.time() - start, 3),
            })
        except Exception as e:
            results.append({
                "import": imp,
                "status": "ERROR",
                "detail": str(e),
                "duration_seconds": round(time.time() - start, 3),
            })
    return results


def generate_markdown_report(validation: dict) -> str:
    lines = []
    lines.append("# LVS Integrity Validation Report")
    lines.append("")
    lines.append(f"**Status**: `{validation['validation_status']}`")
    lines.append(f"**Generated**: {validation['generated_at']}")
    lines.append("")
    lines.append("## Invariant Checks")
    lines.append("")
    for c in validation["invariant_checks"]:
        icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "⚠️"}.get(c["status"], "?")
        lines.append(f"- {icon} **{c['check']}**: `{c['status']}` {c.get('detail', '')}")
    lines.append("")
    lines.append("## Import Validation")
    lines.append("")
    for i in validation["import_checks"]:
        icon = {"PASS": "✅", "FAIL": "❌"}.get(i["status"], "?")
        lines.append(f"- {icon} `{i['import']}`: `{i['status']}`")
    lines.append("")
    lines.append("## Test Suites")
    lines.append("")
    for suite in validation["test_suites"]:
        icon = "✅" if suite["passed"] else "❌"
        lines.append(f"### {icon} {suite['suite']}")
        lines.append(f"- **Status**: `{'PASS' if suite['passed'] else 'FAIL'}`")
        lines.append(f"- **Duration**: {suite['duration_seconds']}s")
        lines.append(f"- **Failures**: {suite['failures']}")
        lines.append("")
        lines.append(f"```")
        lines.append(suite["summary"])
        lines.append("```")
        lines.append("")
    lines.append("---")
    lines.append("")
    n_pass = sum(1 for s in validation["test_suites"] if s["passed"])
    n_total = len(validation["test_suites"])
    n_invariant_pass = sum(1 for c in validation["invariant_checks"] if c["status"] == "PASS")
    n_invariant_total = len(validation["invariant_checks"])
    lines.append(f"**Test suites**: {n_pass}/{n_total} passed")
    lines.append(f"**Invariant checks**: {n_invariant_pass}/{n_invariant_total} passed")
    lines.append(f"**Overall**: `{validation['validation_status']}`")
    return "\n".join(lines)


def main() -> int:
    print("=" * 60)
    print("GLI-FLOW LVS Integrity Release Gate")
    print("=" * 60)
    print()

    print("[1/4] Validating imports ...")
    import_checks = validate_imports()
    imports_ok = all(c["status"] == "PASS" for c in import_checks)
    print(f"  {'OK' if imports_ok else 'FAIL'}: {sum(1 for c in import_checks if c['status'] == 'PASS')}/{len(import_checks)}")
    print()

    print("[2/4] Running invariant checks ...")
    invariant_checks = run_invariant_checks()
    invariants_ok = all(c["status"] == "PASS" for c in invariant_checks)
    print(f"  {'OK' if invariants_ok else 'FAIL'}: {sum(1 for c in invariant_checks if c['status'] == 'PASS')}/{len(invariant_checks)}")
    for c in invariant_checks:
        if c["status"] != "PASS":
            print(f"    FAIL: {c['check']}: {c.get('detail', '')}")
    print()

    print("[3/4] Running test suites ...")
    test_suites = []
    for suite in TEST_SUITES:
        print(f"  Running {suite} ...", end=" ", flush=True)
        result = run_pytest(suite)
        test_suites.append(result)
        print(f"{'OK' if result['passed'] else 'FAIL'} ({result['duration_seconds']}s)")
        if not result["passed"]:
            print(f"    {result['summary']}")
    suites_ok = all(s["passed"] for s in test_suites)
    print()

    print("[4/4] Generating report ...")
    validation_status = "VALID" if (imports_ok and invariants_ok and suites_ok) else "INVALID"

    validation = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "validation_status": validation_status,
        "import_checks": import_checks,
        "invariant_checks": invariant_checks,
        "test_suites": test_suites,
    }

    output_dir = BASE_DIR / "outputs" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "lvs_integrity_validation_report.json"
    json_path.write_text(json.dumps(validation, indent=2))

    md_path = output_dir / "lvs_integrity_validation_report.md"
    md_path.write_text(generate_markdown_report(validation))

    print()
    print(f"  JSON: {json_path}")
    print(f"  MD:   {md_path}")
    print()
    print("=" * 60)
    print(f"Validation Status: {validation_status}")
    print("=" * 60)

    return 0 if validation_status == "VALID" else 1


if __name__ == "__main__":
    sys.exit(main())
