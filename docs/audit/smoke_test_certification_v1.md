# Smoke Test Certification v1

**Date:** 2026-06-18
**Component:** `gli-flow smoke-test`
**Module:** `gli_flow/cli/smoke_test.py`

---

## Checks Implemented

| Check | What It Validates | Method |
|-------|------------------|--------|
| **Environment** | Python version (3.9+), EDA tools (openroad, yosys, magic, netgen, klayout, sv2v) | `shutil.which` + `subprocess.run(..., --version)` |
| **Database** | DB file exists, schema valid for runs/failure_atlas tables, migrations applied | `MigrationEngine.validate_schema()` |
| **Telemetry** | Settings file readable, consent state checkable, queue DB healthy | `get_telemetry_settings()` |
| **Dashboard** | Backend Python deps (fastapi, uvicorn), frontend tooling (node, npm) | `importlib.find_spec()` + `shutil.which` |
| **Example Design** | `examples/counter/gli_manifest.yaml` exists and passes validation | `validate_manifest()` |

## Failure Scenarios Tested

| Scenario | Expected Behavior | Result |
|----------|------------------|--------|
| All tools installed, DB ready | All 5 checks pass, exit 0 | ✅ |
| Missing EDA tool (netgen) | Environment fails, exit 1, tool listed with `✗` | ✅ |
| No database file | Database shows "will be created on first run", passes | ✅ |
| Missing manifest directory | Example Design fails, exit 1 | ✅ |
| No dashboard deps | Dashboard shows missing deps, continues (not fatal) | ✅ |
| No node/npm | Dashboard shows warnings, continues (uses --backend-only) | ✅ |

## User-Facing Output Examples

### Success case:
```
Smoke Test Summary

  ✓ Environment
  ✓ Database
  ✓ Telemetry
  ✓ Dashboard
  ✓ Example Design

Result: GLI-FLOW is ready for use.
```

### Partial failure case:
```
Smoke Test Summary

  ✗ Environment
  ✓ Database
  ...

Details:

Environment:
  ✓ Python 3.14.4
  ✓ openroad v2.0-17598-ga008522d8
  ✗ netgen not found

Result: GLI-FLOW has issues that need attention.
```

## Documentation Changes Made

| Document | Change |
|----------|--------|
| `README.md` | Added `smoke-test` to Quick Start code block. Added features line. Added "run smoke-test after install" note. |
| `docs/user_guide/getting_started.md` | New Step 3: Smoke Test (inserted before Doctor). Renumbered steps 4-9. |
| `docs/user_guide/user_manual.md` | Smoke test section added after EDA tools section in Installation. |
| `docs/reference/cli_reference.md` | Full command reference with flags and examples. Added to Common Workflows. |
| `gli_flow/cli/main.py` | Added to parser epilog (Common Workflows). |

## Success Criteria Verification

> **A first-time user can determine whether GLI-FLOW is correctly installed in under 30 seconds using one command.**

| Criterion | Verification |
|-----------|-------------|
| One command | `gli-flow smoke-test` — no subcommands, no flags required |
| Clear pass/fail | Summary per check with `✓` / `✗` |
| Actionable failures | Each failure shows what is missing and how to fix |
| No internal details | No tracebacks, no Python exceptions, no internal paths |
| Under 30 seconds | Runs in ~1-2 seconds (no network, no heavy computation) |

**Result: ✅ PASS**
