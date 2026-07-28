# CI Recovery Report

## Summary

The `gli-flow ci` command was functionally intact but hidden from users and labeled as broken.

## Root Cause

Two mechanisms suppressed the CI command:

1. `BROKEN_COMMANDS = {"ci"}` at `main.py:48` — defined but never enforced (the if/elif dispatch chain still routed to `ci_command`). This was confusing dead code.

2. `ci_parser._category = "broken"` at `main.py:2014` — the `CategorizedHelpFormatter` only displays `"production"` and `"experimental"` categories. The `"broken"` category was silently invisible.

## Fix Applied

1. Removed `"ci"` from `BROKEN_COMMANDS` set (now empty set)
2. Changed `ci_parser._category` from `"broken"` to `"production"`

## CI Runner Status

The CI runner (`gli_flow/ci/runner.py`) invokes `gli-flow run` as a subprocess and extracts metrics from the database. It supports:
- JUnit XML output
- Markdown report output
- Baseline comparison (QoR, WNS thresholds)
- Regression detection

## CI Test Status

All 9 CI-related tests pass:
- `tests/test_ci_runner.py` — 3 tests
- CI validation in GitHub Actions workflow passes
- Import chain verification passes

## CI Pipeline (GitHub Actions)

The CI workflow covers:
- 2 OS × 2 Python versions (ubuntu-22.04, ubuntu-24.04 × 3.10, 3.11)
- Infrastructure tests
- Installer tests
- Core unit tests
- Import chain verification
- CI module validation
- Mock adapter validation
- Hardening module imports
- LVS integrity (4 jobs)
- Failure corpus validation
- Doctor validation
- Release asset validation
