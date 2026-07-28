# Test Coverage Report

## Measurement Status

Numeric coverage could not be measured in this environment:

- `python3 -m pytest ... --cov`: failed because `pytest-cov` is not installed.
- `python3 -m coverage --version`: failed because `coverage` is not installed.

## Executed Tests

- `python3 -m pytest --collect-only -q`: 287 tests collected.
- `python3 -m pytest tests -q -k 'not TestAPIRoutes'`: 277 passed, 10 deselected.
- `python3 -m pytest tests/test_production_readiness.py tests/e2e/test_mock_pipeline.py::test_mock_pipeline_via_cli tests/integration/test_e2e_counter.py::test_counter_sky130_full_pipeline -q`: 5 passed.
- `npm run build`: passed.

`TestAPIRoutes` was excluded because `fastapi.testclient.TestClient` hangs on first request in this container. Direct endpoint calls for `/health`, `/runs/count`, `/failures`, and `/similar-failures` returned correctly.

## Covered Well

- Dataclasses and parsers for power, EM, SI, density, signoff, antenna, ATPG, scan, formal, top-floorplan, yield.
- Failure Atlas repository and rule detector.
- Database migrations and environment validation.
- Mock adapter stage coverage.
- Mock CLI/e2e pipeline.
- QoR and regression scoring.

## Critical Untested Paths

| Severity | Type | Path | Gap |
|---|---|---|---|
| HIGH | technical debt | Real `OpenRoadAdapter.run()` | No automated real ORFS execution in this environment. |
| HIGH | technical debt | Magic DRC / Netgen LVS | Real tool invocation not covered by current unit tests. |
| HIGH | technical debt | Backend ASGI requests | `TestClient` hangs; direct calls are not a full HTTP test. |
| HIGH | technical debt | Fresh installer | No clean Ubuntu/WSL VM validation here. |
| MEDIUM | technical debt | Dashboard runtime | Build is tested; browser interaction is not. |

## New Regression Tests

- Schema migration/runtime validation includes `entry_level`.
- Successful-run cleanup removes only FAILURE-level atlas entries.
- Backend path containment rejects traversal.

## Priority

1. Pin/install `pytest-cov` and `coverage`; enforce a coverage floor.
2. Fix or replace the ASGI test harness.
3. Add real ORFS smoke tests gated by tool availability.
4. Add Magic/Netgen fixture tests using captured real reports.
