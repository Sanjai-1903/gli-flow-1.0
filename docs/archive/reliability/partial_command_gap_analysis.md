# Partial Command Gap Analysis

**Date:** 2026-06-12  
**Goal:** Identify what each partial command needs to reach production readiness.

---

## 1. `remote` — Remote SSH Execution

### What Works
- SSH connection check via `--check` flag
- `RemoteWorkerConfig` with host, port, user, key path
- `RemoteWorker` SSH command construction
- `rsync`-based file transfer for design syncing
- Timeout handling in subprocess execution
- `RemoteWorkerResult` return type

### What's Missing
| Gap | Impact | Effort |
|-----|--------|--------|
| No `--mock` mode for testing without SSH | Cannot verify in CI/sandbox | Small |
| No error message if no SSH server on target | Confusing "Connection FAILED" with no details | Small |
| No SSH key auto-generation hint | First-time users may not have SSH keys configured | Small |
| No progress output during remote execution | Long runs appear hung | Medium |

### Blocks Production Readiness
- Requires live SSH server to test — not testable in isolation
- No mock/simulation mode for CI validation

### Estimated Effort to Complete
**Small-Medium (1-2 days):** Add mock mode, improve error messaging.

---

## 2. `cloud` — Cloud Storage (S3/GCS)

### What Works
- Full S3 upload/download/list implementations via `boto3`
- Full GCS upload/download/list implementations via `google.cloud.storage`
- Path traversal protection in download methods
- Run directory recursive upload
- Configurable provider, bucket, prefix

### What's Missing
| Gap | Impact | Effort |
|-----|--------|--------|
| `boto3`/`google-cloud-storage` marked optional — not installed by default | Command fails with "boto3 not installed" on first use | Small |
| No `pip install gli-flow[cloud]` hint in CLI error output | Users don't know how to enable cloud features | Trivial |
| No credentials configuration flow | Users must manually configure AWS/GCP credentials | Medium |
| No `--dry-run` flag to preview what would be uploaded | Users may accidentally upload sensitive data | Small |

### Blocks Production Readiness
- Missing error message guiding users to install extras
- No credential setup wizard

### Estimated Effort to Complete
**Small (0.5-1 day):** Add installation hints, credential verification.

---

## 3. `diagnose` — Run Failure Diagnosis

### What Works
- Database lookup by `run_id`
- Telemetry JSON parsing for failure stage
- 7 log pattern definitions with cause/fix/atlas references
- Recursive log file scanning with regex pattern matching
- Deduplication of findings
- Rich Panel output formatting

### What's Missing
| Gap | Impact | Effort |
|-----|--------|--------|
| Only 7 patterns defined | Many failure modes not covered | Medium |
| No pattern for "no results dir" (ORFS stage failure) | Most common failure not detected | Small |
| No suggestion to run with `--verbose` on next attempt | Users may not connect failure to missing info | Trivial |
| Only scans `.log` files — misses `.rpt` reports | Some tools write to non-.log extensions | Small |

### Blocks Production Readiness
- Limited pattern coverage means many failures yield "No specific failure pattern detected"
- Cannot diagnose runs that failed before telemetry.json was written

### Estimated Effort to Complete
**Medium (2-3 days):** Expand pattern library, support `.rpt` files, handle pre-telemetry failures.

---

## 4. `show-telemetry` — Telemetry Payload Inspector

### What Works
- Database lookup by `run_id`
- Read and display telemetry.json
- Sanitizes routing paths (removes `drc_report_path`, `lvs_report_path`)
- Syntax-highlighted JSON output via rich
- Privacy reassurance message about no RTL data

### What's Missing
| Gap | Impact | Effort |
|-----|--------|--------|
| No fallback if `run_dir` is missing from DB record | Silent failure | Small |
| No `--last` flag to show most recent run's telemetry | Requires knowing exact run_id | Trivial |
| No hint if telemetry is disabled | Users may wonder why file doesn't exist | Trivial |

### Blocks Production Readiness
- Requires existing run with telemetry.json — no standalone mode
- UX friction: users must know `run_id` (not discoverable from command output)

### Estimated Effort to Complete
**Small (0.5 day):** Add `--last` flag, better error messages.

---

## 5. `dashboard` — Web Dashboard

### What Works
- Starts uvicorn backend server on port 8000
- Starts frontend dev server via `npm run dev` on port 5173
- Falls back to backend-only mode if `npm` not found
- Opens browser automatically
- Handles WSL browser opening via `cmd.exe /c start`
- `--backend-only` flag for headless/API mode

### What's Missing
| Gap | Impact | Effort |
|-----|--------|--------|
| No check if uvicorn is installed | Subprocess will fail silently (stderr to DEVNULL) | Small |
| Hardcoded `backend.server:app` path | May not match all installations | Small |
| No health check after starting backend | Users may open browser before server is ready | Medium |
| Backend process not cleaned up on crash | Zombie process if main script dies | Medium |

### Blocks Production Readiness
- No uvicorn availability check
- No health check / ready signal
- Process management is fragile

### Estimated Effort to Complete
**Medium (2-3 days):** Add dependency checks, health polling, robust process lifecycle.

---

## 6. `upgrade-check` — Version Update Checker

### What Works
- Checks PyPI JSON API for latest version
- Checks GitHub releases API as fallback
- Graceful offline handling (URLError)
- Semantic version comparison (`latest > current`)
- Clear upgrade instructions when newer version found

### What's Missing
| Gap | Impact | Effort |
|-----|--------|--------|
| No `--json` output for programmatic use | Cannot integrate with CI/automation | Small |
| Hardcoded repo name `Jegadiswar-SM/gli-flow-asic` | Wrong if repo moves | Trivial |
| Version at `v1.0.0` — not published to PyPI/GitHub | Always shows "offline" — confusing | N/A (publishing) |

### Blocks Production Readiness
- Currently always shows "offline" because package isn't published
- Users see "Could not determine latest version" on first run

### Estimated Effort to Complete
**Trivial (after publishing):** No code changes needed. Currently works correctly if package were published.

---

## Summary

| Command | Gaps | Effort | Ready Blockers |
|---------|------|--------|----------------|
| `remote` | No mock mode, weak error messages | 1-2d | Cannot test without SSH |
| `cloud` | Missing dep hints, no credential flow | 0.5-1d | Requires optional deps |
| `diagnose` | Only 7 patterns, no `.rpt` support | 2-3d | Limited coverage |
| `show-telemetry` | No `--last` flag, UX friction | 0.5d | Requires existing run |
| `dashboard` | No dep check, zombie processes | 2-3d | Fragile lifecycle |
| `upgrade-check` | Package not published yet | Trivial | Publishing blocker |

### Recommendation for Beta

- **`upgrade-check`**: Mark as Experimental. Works correctly once package is published.
- **`remote`**: Mark as Experimental. Fully functional for users with SSH infrastructure.
- **`cloud`**: Mark as Experimental. Fully functional with `pip install gli-flow[cloud]`.
- **`diagnose`**: Keep as Production with caveat: "works best with failed runs."
- **`show-telemetry`**: Keep as Production with caveat: "requires completed run."
- **`dashboard`**: Mark as Experimental. Functional but process management needs hardening.
