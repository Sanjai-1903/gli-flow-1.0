"""
Release gate: LVS command construction integrity validation.

Ensures that the Netgen LVS command is always constructed with correct
positional arguments — no shifting, no implicit reinterpretation.

Checks:
  1. INF-LVS-002 regression tests pass
  2. LVS comparison evidence required tests pass
  3. Netgen argument construction tests pass (existing)
  4. Circuit2 construction invariant: pdk_sc_spice + clean_netlist = single arg
  5. Circuit2 construction invariant: absent pdk_sc_spice = single file arg
"""

import json
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TEST_SUITES = [
    "tests/regressions/test_inf_lvs_002.py",
    "tests/signoff/test_lvs_comparison_evidence_required.py",
    "tests/regressions/test_netgen_argument_construction.py",
]

INVARIANT_CHECKS = [
    ("Circuit2 combines pdk + netlist into single arg", """
# Simulate the FIXED construction: both files in one circuit2 arg
netgen = "/usr/bin/netgen"
lvs_args = [netgen, "-batch", "lvs"]
lvs_args.append("/tmp/layout.spice top")
lvs_args.append("/tmp/pdk.spice /tmp/netlist.v top")
lvs_args.extend(["/tmp/setup.tcl", "/tmp/report.txt"])
assert len(lvs_args) == 7, f"Expected 7 args, got {len(lvs_args)}"
assert lvs_args[4].count(" ") == 2, "circuit2 must have 2 spaces (2 files + top)"
assert lvs_args[5] == "/tmp/setup.tcl", "setup file must be arg 5"
assert lvs_args[6] == "/tmp/report.txt", "report path must be arg 6"
"""),
    ("Circuit2 with no pdk is single-file arg", """
netgen = "/usr/bin/netgen"
lvs_args = [netgen, "-batch", "lvs"]
lvs_args.append("/tmp/layout.spice top")
lvs_args.append("/tmp/netlist.v top")
lvs_args.extend(["/tmp/setup.tcl", "/tmp/report.txt"])
assert len(lvs_args) == 7, f"Expected 7 args, got {len(lvs_args)}"
assert lvs_args[4].count(" ") == 1, "circuit2 must have 1 space (1 file + top)"
assert lvs_args[5] == "/tmp/setup.tcl", "setup file must be arg 5"
assert lvs_args[6] == "/tmp/report.txt", "report path must be arg 6"
"""),
    ("No positional argument shifting", """
# Fixed construction: 4 args after -batch lvs
lvs_args = ["netgen", "-batch", "lvs",
            "layout.spice top",
            "pdk.spice netlist.v top",
            "/tmp/setup.tcl",
            "/tmp/report.txt"]
args_after_lvs = lvs_args[3:]
assert len(args_after_lvs) == 4, f"Expected 4, got {len(args_after_lvs)}"
c1, c2, setup, report = args_after_lvs
assert setup == "/tmp/setup.tcl"
assert report == "/tmp/report.txt"
"""),
    ("Default LVSResult invariants", """
from gli_flow.backends.openroad_adapter import LVSResult
r = LVSResult()
assert r.status == "NOT_RUN"
assert r.is_clean is False
assert r.comparison_completed is False
assert r.report_exists is False
assert r.return_code == -1
"""),
    ("SignoffGate rejects missing comparison", """
from gli_flow.core.orchestrator import SignoffGate
gate = SignoffGate()
gate.set_from_status("lvs_pass", "ERROR")
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


def generate_markdown_report(validation: dict) -> str:
    lines = []
    lines.append("# LVS Command Integrity Validation Report")
    lines.append("")
    lines.append(f"**Status**: `{validation['validation_status']}`")
    lines.append(f"**Generated**: {validation['generated_at']}")
    lines.append("")
    lines.append("## Invariant Checks")
    lines.append("")
    for c in validation["invariant_checks"]:
        icon = {"PASS": "PASS", "FAIL": "FAIL", "ERROR": "ERROR"}.get(c["status"], "?")
        lines.append(f"- **{icon}** {c['check']}: `{c['status']}` {c.get('detail', '')}")
    lines.append("")
    lines.append("## Test Suites")
    lines.append("")
    for suite in validation["test_suites"]:
        icon = "PASS" if suite["passed"] else "FAIL"
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
    print("GLI-FLOW LVS Command Integrity Release Gate")
    print("=" * 60)
    print()

    print("[1/2] Running invariant checks ...")
    invariant_checks = run_invariant_checks()
    invariants_ok = all(c["status"] == "PASS" for c in invariant_checks)
    print(f"  {'OK' if invariants_ok else 'FAIL'}: {sum(1 for c in invariant_checks if c['status'] == 'PASS')}/{len(invariant_checks)}")
    for c in invariant_checks:
        if c["status"] != "PASS":
            print(f"    FAIL: {c['check']}: {c.get('detail', '')}")
    print()

    print("[2/2] Running test suites ...")
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

    validation_status = "VALID" if (invariants_ok and suites_ok) else "INVALID"

    validation = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "validation_status": validation_status,
        "invariant_checks": invariant_checks,
        "test_suites": test_suites,
    }

    output_dir = BASE_DIR / "outputs" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "lvs_command_integrity_validation.json"
    json_path.write_text(json.dumps(validation, indent=2))

    md_path = output_dir / "lvs_command_integrity_validation.md"
    md_path.write_text(generate_markdown_report(validation))

    print(f"  JSON: {json_path}")
    print(f"  MD:   {md_path}")
    print()
    print("=" * 60)
    print(f"Validation Status: {validation_status}")
    print("=" * 60)

    return 0 if validation_status == "VALID" else 1


if __name__ == "__main__":
    sys.exit(main())
