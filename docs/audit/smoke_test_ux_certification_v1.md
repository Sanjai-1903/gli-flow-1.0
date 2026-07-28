# Smoke Test UX Certification v1

**Date:** 2026-06-20
**Component:** `gli-flow smoke-test`
**Module:** `gli_flow/cli/smoke_test.py`

---

## Tiers Implemented

### 1. Mock-Mode Ready (top-level pass/fail)
| Check | Description | Exit-if-missing |
|-------|-------------|-----------------|
| Python | Version ≥ 3.9 | Yes |
| Database | Schema valid, migrations runnable | Yes |
| Telemetry | Config readable | Yes |
| Example Designs | Manifest exists and validates | Yes |

### 2. Real ASIC Flow (warnings only)
| Check | Description | Exit-if-missing |
|-------|-------------|-----------------|
| yosys | Tool found + version string | No |
| openroad | Tool found + version string | No |
| magic | Tool found + version string | No |
| netgen | Tool found + version string | No |
| klayout | Tool found + version string | No |
| sv2v | Tool found + version string | No |

### 3. Optional (info only)
| Check | Description |
|-------|-------------|
| Dashboard deps | fastapi + uvicorn installed |
| Node.js | Available for frontend dev server |
| npm | Available for frontend dev server |

---

## UX Requirements

- [x] Missing real-flow tools display `⚠` (yellow) — not `✗` (red)
- [x] Missing optional deps display `—` (dim dash) — not `✗` (red)
- [x] Mock-mode summary line uses ✓/✗ and dictates exit code
- [x] No red `✗` shown for tools that aren't needed for mock mode
- [x] Output shows clear "Next" steps on both pass and fail

## Verified Output

```
Smoke Test — GLI-FLOW Environment Check

  Mock-Mode Ready
  ✓ Python — 3.10.12
  ✓ Database — Database at /home/gli/.gli_flow/gli_flow.db
  ✓ Telemetry — Config readable (mode: atlas)
  ✓ Example Designs — Manifest valid

  Real ASIC Flow:
  ✓ yosys — Yosys 0.40 ...
  ✓ openroad — v2.0-17598-ga008522d8
  ✓ magic — 8.3.659
  ⚠ netgen — netgen not found — required only for real ASIC runs
  ✓ klayout — KLayout 0.30.7
  ✓ sv2v — sv2v v0.0.13

  Optional:
  ✓ Dashboard deps — Backend dependencies installed
  ✓ Node.js — v22.22.3
  ✓ npm — 10.9.8

✓ Mock-mode ready. Add EDA tools for real ASIC runs.
```

## Exit Code Behavior
- Exit code `0` when all mock-mode checks pass (regardless of real-flow or optional status)
- Exit code `1` when any mock-mode check fails

## Certification
**Status:** PASS
**Reviewer:** Automated audit
**Evidence:** Actual CLI output verified on 2026-06-20 with netgen missing
