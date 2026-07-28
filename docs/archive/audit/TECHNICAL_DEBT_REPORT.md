# Technical Debt Report

## Architectural Debt

| Severity | Type | Location | Risk | Recommended Fix |
|---|---|---|---|---|
| HIGH | design flaw | `backend/server.py` | Backend schema drift from migrations could break API startup or hide missing columns. | Fixed: backend now uses migration engine and runtime schema validation. |
| HIGH | technical debt | `failure_atlas/repository.py` | Repository API had drifted from tests/backend callers. | Fixed: restored public query/update methods and typed entry levels. |
| HIGH | technical debt | `gli_flow/backends/openroad_adapter.py` | Advanced signoff/stage methods mix production wrappers with speculative Tcl commands and regex parsers. | Split verified production paths from experimental stage helpers; require real report evidence for any “pass”. |
| MEDIUM | technical debt | `gli_flow/telemetry/parser.py`, `gli_flow/analytics/parse_openroad_reports.py`, root `analytics/*` | Multiple report parsers can disagree. | Consolidate on one parser contract and deprecate duplicate scripts. |
| MEDIUM | technical debt | `backend/server.py`, `failure_atlas/repository.py` | Similar analytics SQL exists in both API and repository. | Keep repository as source of truth or remove unused repository analytics methods. |
| MEDIUM | technical debt | `dashboard/dist/`, generated outputs | Built artifacts and run outputs in repo increase audit noise. | Keep generated outputs ignored or move golden artifacts to dedicated fixtures. |
| LOW | technical debt | `gli_flow/backends/librelane.py` | Secondary adapter appears less maintained than OpenROAD path. | Mark support level explicitly or remove from production surface until validated. |

## Dead/Stale/Temporary Code

| Severity | Type | Location | Risk | Recommended Fix |
|---|---|---|---|---|
| MEDIUM | technical debt | `gli_flow/testing/layout_images.py` used by real orchestrator path | Phantom screenshots could appear as real artifacts. | Fixed: real runs no longer generate placeholders. |
| MEDIUM | technical debt | `gli_flow/core/orchestrator.py` `_any_log_findings()` | Always returns false, so log-signature status is misleading. | Implement or remove after Failure Atlas log scan contract is finalized. |
| MEDIUM | technical debt | `dashboard/src/RunDesignPage.jsx` | Shows command snippets only; not a runnable backend flow. | Document as static help or remove from production dashboard navigation. |
| LOW | technical debt | Root scripts under `analytics/`, `scheduler/`, `release/` | Standalone script ecosystem duplicates package concepts. | Decide whether these are product commands, developer scripts, or archived prototypes. |

## Database Debt

Resolved:
- Backend schema duplication removed.
- Migration validation added.
- `entry_level` migration added.
- Default DB path resolver unified.

Remaining:
- API tests using `TestClient` hang in this container. Backend logic was verified by direct route calls, but CI needs a reliable ASGI test harness.
