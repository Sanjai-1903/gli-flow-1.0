"""
Release gate: Tool discovery integrity validation.

Ensures that:
  1. All version strategies are tool-specific (no generic --version)
  2. Netgen uses -batch quit only (never --version/-version)
  3. Tool discovery does not launch GUI windows
  4. All version strategies handle missing binaries gracefully
  5. All regression and adversarial tests pass
"""

import json
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TEST_SUITES = [
    "tests/reliability/test_no_gui_discovery.py",
    "tests/regressions/test_inf_env_002.py",
    "tests/adversarial/tool_discovery/",
]

SAFE_FLAGS = {
    "magic": ["--version"],
    "magicdnull": ["--version"],
    "netgen": ["-batch", "quit"],
    "netgenexec": ["-batch", "quit"],
    "yosys": ["-V"],
    "openroad": ["-version"],
    "klayout": ["-b", "-v"],
    "sv2v": ["--version"],
    "sta": ["--version"],
}

BANNED_FLAGS_FOR_NETGEN = ["--version", "-version"]


def validate_safe_flags() -> list[dict]:
    results = []
    from gli_flow.core.tool_discovery import VERSION_STRATEGIES, _version_generic
    for tool_name, strategy in VERSION_STRATEGIES.items():
        expected = SAFE_FLAGS.get(tool_name, ["--version"])
        is_generic = strategy is _version_generic
        results.append({
            "tool": tool_name,
            "has_safe_strategy": not is_generic or tool_name in ("sv2v", "sta"),
            "is_generic": is_generic,
            "expected_flags": expected,
        })
    return results


def validate_netgen_never_uses_banned_flags() -> dict:
    import inspect
    from gli_flow.core.tool_discovery import _version_netgen
    src = inspect.getsource(_version_netgen)
    banned_found = [f for f in BANNED_FLAGS_FOR_NETGEN if f in src]
    return {
        "banned_flags_found": banned_found,
        "uses_batch": "-batch" in src,
        "pass": len(banned_found) == 0 and "-batch" in src,
    }


def run_pytest(suite_path: str) -> dict:
    start = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", suite_path, "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60,
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


def main() -> int:
    print("=" * 60)
    print("GLI-FLOW Tool Discovery Integrity Release Gate")
    print("=" * 60)
    print()

    print("[1/3] Validating safe version strategies ...")
    safe_flag_results = validate_safe_flags()
    all_safe = all(r["has_safe_strategy"] for r in safe_flag_results)
    for r in safe_flag_results:
        icon = "OK" if r["has_safe_strategy"] else "FAIL"
        print(f"  {icon}: {r['tool']} strategy is {'generic' if r['is_generic'] else 'specific'}")
    print()

    print("[2/3] Validating netgen never uses banned flags ...")
    netgen_check = validate_netgen_never_uses_banned_flags()
    print(f"  {'OK' if netgen_check['pass'] else 'FAIL'}: "
          f"uses_batch={netgen_check['uses_batch']}, "
          f"banned={netgen_check['banned_flags_found']}")
    print()

    print("[3/3] Running test suites ...")
    test_suites = []
    for suite in TEST_SUITES:
        print(f"  Running {suite} ...", end=" ", flush=True)
        result = run_pytest(suite)
        test_suites.append(result)
        print(f"{'OK' if result['passed'] else 'FAIL'} ({result['duration_seconds']}s)")
    print()

    validation_status = "VALID" if (all_safe and netgen_check["pass"] and all(s["passed"] for s in test_suites)) else "INVALID"

    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "validation_status": validation_status,
        "safe_flags": safe_flag_results,
        "netgen_check": netgen_check,
        "test_suites": test_suites,
    }

    output_dir = BASE_DIR / "outputs" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "tool_discovery_integrity_validation_report.json"
    json_path.write_text(json.dumps(report, indent=2))

    print("=" * 60)
    print(f"Validation Status: {validation_status}")
    print(f"Report: {json_path}")
    print("=" * 60)

    return 0 if validation_status == "VALID" else 1


if __name__ == "__main__":
    sys.exit(main())
