# Security Audit

## Fixed

| Severity | Type | Location | Finding | Fix |
|---|---|---|---|---|
| HIGH | bug | `backend/server.py` `/runs/{run_id}/report/{path}` | Path traversal could read files outside a run directory. | Added `_safe_run_path()` containment check. |
| HIGH | bug | `backend/server.py` `/runs/{run_id}/image/{path}` | Path traversal risk through image path parameter. | Same containment check used before `FileResponse`. |
| MEDIUM | bug | SQLite initialization | Read-only user config dir could crash runtime instead of using writable path. | Common DB resolver verifies writability and falls back to local DB. |

## Audited Areas

- Subprocess calls use list arguments in most production paths.
- Remote worker builds an SSH command string with `shlex.quote()` for remote shell segments.
- Cloud download checks resolved destination remains under destination root.
- FastAPI SQL queries use parameter binding for user inputs.

## Remaining Risks

| Severity | Type | Location | Risk | Recommended Fix |
|---|---|---|---|---|
| HIGH | technical debt | `gli_flow/backends/openroad_adapter.py` generated Tcl | File paths are interpolated into Tcl scripts. Malicious design paths could affect Tcl parsing. | Quote/escape Tcl paths with a dedicated helper before real multi-user deployment. |
| MEDIUM | technical debt | `RemoteWorker.run()` | Remote command includes shell composition even with quoted segments. | Keep remote execution disabled by default; add integration tests before production use. |
| MEDIUM | technical debt | Dashboard/API CORS | Default CORS is localhost-only, but env can broaden it. | Document deployment CORS policy. |
| LOW | technical debt | File artifact serving | GDS/DEF artifacts are served to any API caller. | Put API behind authentication/reverse proxy for shared deployments. |

## Security Tests Added

- `tests/test_production_readiness.py::test_backend_rejects_report_path_traversal`
