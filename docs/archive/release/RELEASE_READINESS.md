# Release Readiness

## Scorecard

| Category | Score | Rationale |
|---|---:|---|
| Installation | 5/10 | Installer and doctor exist, but clean Ubuntu 22.04, Ubuntu 24.04, and WSL2 validation was not run. DB fallback was fixed. |
| Execution | 7/10 | Mock and existing counter/UART/GCD smoke paths pass. Real full benchmark suite was not run. |
| Signoff | 4/10 | Signoff gate exists and blocks missing DRC/LVS/timing, but Magic/Netgen/OpenROAD fixes need real multi-environment validation. |
| Reliability | 4/10 | No `counter x20`/`uart x20` real reliability run was completed. |
| Observability | 7/10 | Dashboard/API/Failure Atlas work and build passes. Real screenshot/artifact phantom issue was fixed. |
| Documentation | 6/10 | User docs exist; production limitations and benchmark gaps need front-page clarity. |
| Testing | 6/10 | 277 non-API tests pass; API harness and coverage tooling are blockers. |
| Security | 7/10 | Obvious artifact path traversal fixed; Tcl path escaping and deployment auth remain. |

Overall readiness: 5.8/10.

## Release Decision

Do not call this production-ready for real tapeout signoff yet.

It is acceptable as an engineering alpha/beta for controlled local use with mock-mode CI and selected known-good real designs, provided limitations are documented.

## Required Before Production Release

1. Run real ORFS regression suite for all supported examples that actually exist.
2. Add/curate missing benchmark manifests or remove them from claimed coverage.
3. Run `counter x20` and `uart x20` real-flow reliability tests.
4. Run fresh install tests on Ubuntu 22.04, Ubuntu 24.04, and WSL2.
5. Fix ASGI API test harness.
6. Install coverage tooling and publish coverage numbers.
7. Qualify Magic/Netgen LVS workarounds against real clean and failing layouts.

## Smoke Results From This Audit

| Design | Mode | Result | Runtime | WNS | TNS | Utilization | Cell Count |
|---|---|---|---:|---:|---:|---:|---:|
| counter | mock | PASS | 42.0s | 0.0 | 0.0 | 65.0% | 100 |
| uart | mock | PASS | 42.0s | 0.0 | 0.0 | 65.0% | 100 |
| gcd | mock | PASS | 42.0s | 0.0 | 0.0 | 65.0% | 100 |

These are mock-mode smoke checks, not signoff evidence.
