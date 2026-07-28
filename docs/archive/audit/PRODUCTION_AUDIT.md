# GLI-FLOW Production Audit

Date: 2026-06-07

Scope audited: `gli_flow/`, `failure_atlas/`, `backend/`, `dashboard/src/`, `tests/`.

## Executive Verdict

GLI-FLOW is not yet fully production-ready for real tapeout signoff. It is substantially closer after this audit: schema drift, mock-run startup failure, Failure Atlas repository/API drift, pytest collection, path traversal, and telemetry WNS/TNS lineage blockers were fixed and regression-tested.

Remaining blockers are mostly real-flow validation gaps: full benchmark suite, repeated reliability runs, fresh OS installs, and real signoff evidence across Magic/Netgen/OpenROAD versions.

## Fixed Production Blockers

| Severity | Type | Finding | Evidence | Fix |
|---|---|---|---|---|
| CRITICAL | bug | Pytest collected vendored Ibex scripts under `examples/`, causing `SystemExit` during collection. | `python3 -m pytest --collect-only -q` failed in `examples/mini_mac/.../gen_csr_test.py`. | Added `pytest.ini` restricting discovery to `tests/`. |
| CRITICAL | design flaw | Backend had duplicated SQLite schema instead of using migrations. | `backend/server.py` had local `CREATE TABLE` definitions that omitted migrated columns. | Backend now calls migration/schema validation and local schema strings were removed. |
| HIGH | bug | Mock CLI runs failed when user DB directory was not writable or WAL could not be enabled. | `gli-flow run examples/tiny_or --mock` failed with `sqlite3.OperationalError`. | Common DB path resolver verifies writability; WAL is best-effort with reconnect fallback. |
| HIGH | bug | `--mock` still ran local tool/PDK validation. | E2E CLI mock test failed on permissions/PDK environment. | CLI and orchestrator skip local environment validation in mock mode. |
| HIGH | bug | Orchestrator dropped parsed WNS/TNS because parser emits `setup_wns_ns`/`setup_tns_ns`. | Integration test found telemetry `metrics.wns is None`. | Orchestrator now maps canonical setup/hold keys. |
| HIGH | bug | Failure Atlas repository did not implement its tested/public methods consistently. | `TestFailureRepository` failed on missing methods/signature drift. | Restored repository query/update APIs and JSON decoding. |
| HIGH | design flaw | Successful runs could retain Failure Atlas entries. | Orchestrator records entries before final success status; log signatures can be recorded on otherwise successful runs. | Added `INFO/WARNING/FAILURE` entry level and purge FAILURE-level entries on successful run completion. |
| HIGH | bug | Backend artifact/report endpoints allowed path traversal. | Routes accepted `{path}` and joined paths without containment check. | Added `_safe_run_path()` and regression test. |
| MEDIUM | technical debt | Real runs always generated placeholder layout images. | `generate_placeholder_images()` called unconditionally. | Placeholder images are now mock-only. |

## Remaining Findings

| Severity | Type | Location | Finding | Recommended Fix |
|---|---|---|---|---|
| CRITICAL | technical debt | Real regression suite | Requested `fifo`, `spi`, `i2c`, `picorv32`, standalone `ibex` manifests do not exist. | Add curated benchmark manifests before claiming benchmark coverage. |
| CRITICAL | technical debt | Fresh installs | Ubuntu 22.04, Ubuntu 24.04, and WSL2 clean-machine validation were not executable in this workspace. | Run scripted install audits in clean VMs/WSL images. |
| HIGH | technical debt | API tests | `fastapi.testclient.TestClient` hangs in this container, although direct endpoint calls return. | Pin/validate FastAPI-Starlette-httpx stack and add API tests that run reliably in CI. |
| HIGH | technical debt | `OpenRoadAdapter` | Many advanced stage Tcl scripts parse optimistic or placeholder output. | Gate stage claims on real report existence and real tool support. |
| HIGH | technical debt | Signoff | LVS SPICE wrapping, VSUBS insertion, and net tolerance are workarounds requiring PDK/tool-version qualification. | Keep but label as compatibility workarounds until cross-PDK regression evidence exists. |
| MEDIUM | enhancement | Dashboard | Some pages show command/help placeholders rather than executable flows. | Document as observability-only until intentionally implemented. |

## Verification Performed

- `python3 -m pytest --collect-only -q`: 287 tests collected.
- `python3 -m pytest tests -q -k 'not TestAPIRoutes'`: 277 passed, 10 deselected.
- Targeted regression: `tests/test_production_readiness.py`, mock CLI, counter mock pipeline: 5 passed.
- `npm run build`: passed.
- Mock smoke runs: `examples/counter`, `examples/uart`, `examples/gcd`: passed.

## Verification Not Performed

- Full real OpenROAD/ORFS benchmark suite.
- `counter x20` and `uart x20` real-flow reliability.
- Fresh Ubuntu/WSL install testing.
- Numeric coverage measurement: `pytest-cov`/`coverage` are not installed.

## Signoff Hardening Classification

| Area | Classification | Rationale |
|---|---|---|
| Magic invocation through subprocess | PRODUCTION FIX | Maintains GPL isolation and uses external tool boundary. Needs more environment coverage, but architecture is correct. |
| Netgen invocation through subprocess | PRODUCTION FIX | Correct license/process boundary and report parsing path. |
| Magic `magicdnull` discovery and fallback paths | WORKAROUND | Required for headless environments; path list must be validated per distro/package. |
| SPICE top-cell wrapping | WORKAROUND | Addresses Magic/Netgen format mismatch, but is format-sensitive. Needs golden LVS fixtures. |
| Verilog LVS preprocessing | WORKAROUND | Fixes Yosys/SKY130 naming and power pin conventions; not yet generalized by parser/AST. |
| VSUBS insertion for power pins | TECHNICAL DEBT | Can make LVS pass by normalizing substrate/power naming, but risks hiding real power connectivity issues if not tightly qualified. |
| LVS unmatched-net tolerance | TECHNICAL DEBT | Tolerating up to five net mismatches needs documented evidence; otherwise it can mask real LVS failures. |
| Signoff gate requiring DRC/LVS/timing/artifacts | PRODUCTION FIX | Correct production behavior: missing or failing signoff blocks success. |
