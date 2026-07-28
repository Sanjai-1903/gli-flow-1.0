# GLI-FLOW Security Review

## Audit Scope

**Target:** GLI-FLOW v1.0.0 (RTL-to-GDS silicon pipeline)
**Date:** 2026-06-15
**Scope:** Core library (`gli_flow/`), backend API (`backend/`), execution infrastructure, PDK handling, cloud integration, test suite.
**Out of scope:** Third-party vendor code under `examples/`, Docker base images, CI/CD runner environment.

---

## Findings

| ID | Severity | Category | Location | Finding | Status |
|----|----------|----------|----------|---------|--------|
| SEC-001 | **CRITICAL** | Subprocess Injection | `gli_flow/signoff.py:30-32` (historic) | `subprocess.run(cmd, shell=True)` — user-influenced path components interpolated into shell string. | **Fixed** — switched to `shlex.split()` + list form |
| SEC-002 | **HIGH** | Filesystem Access | `backend/server.py` (legacy) | Path traversal via `/runs/{run_id}/report/{path}`. | **Fixed** — `_safe_run_path()` added |
| SEC-003 | **HIGH** | No Privilege Separation | EDA adapters | Subprocesses run with full user permissions. EDA tool exploits could read/write any file the user can access. | **Open** |
| SEC-004 | **MEDIUM** | Path Traversal | CLI `run` command | User-supplied design argument is not validated for `../` components. | **Open** |
| SEC-005 | **MEDIUM** | Config Loading | YAML manifest loading | Historic concern: `yaml.load()` without safe loader. | **Fixed** — all YAML loading uses `yaml.safe_load()` |
| SEC-006 | **MEDIUM** | Secret Handling | `gli_flow/security/file_protection.py:83` | Historic concern: `GLI_ENCRYPTION_SECRET` would fall back to default. | **Fixed** — now raises `RuntimeError` if unset |
| SEC-007 | **MEDIUM** | Environment Inheritance | `gli_flow/core/subprocess_env.py` | `safe_env()` inherits all parent environment variables. Malicious `PATH`, `LD_PRELOAD` propagate to subprocesses. | **Open** |
| SEC-008 | **LOW** | Temp Files | `gli_flow/signoff.py:84-92` | Netgen Tcl setup script written to a predictable path with no cleanup. | **Open** |
| SEC-009 | **LOW** | Dependency Pinning | `setup.py` | No dependency pinning beyond `>=x.y.z` ranges. | **Open** |
| SEC-010 | **LOW** | No Security Scanning | CI pipeline | No SAST (Bandit, CodeQL), SCA (`pip-audit`), or secret scanning. | **Open** |

---

## Recommendations

| Priority | ID | Recommendation | Effort |
|----------|----|----------------|--------|
| P1 | SEC-004 | Add path containment validation to CLI `run` command design argument. | 1 day |
| P1 | SEC-007 | Strip dangerous env variables (`LD_PRELOAD`, `LD_LIBRARY_PATH`, `PYTHONPATH`) from `safe_env()`. | 1 day |
| P2 | SEC-003 | Add user-namespace sandboxing for EDA tools in multi-tenant deployments. | 2 weeks |
| P2 | SEC-008 | Write temp files to `tempfile.mkstemp()` directory; clean up after execution. | 1 day |
| P3 | SEC-009 | Pin dependencies with lock files and add `pip-audit` to CI. | 1-2 days |
| P3 | SEC-010 | Integrate Bandit, CodeQL, and Gitleaks into CI pipeline. | 2-3 days |

---

## Overall Security Score

| Category | Score | Notes |
|----------|-------|-------|
| Subprocess Safety | **7/10** | `shell=True` fixed. Remaining: no sandboxing, env inheritance. |
| Input Validation | **5/10** | Path traversal partially fixed. No systematic input validation. |
| Secrets Management | **7/10** | KMS integration exists. Production guardrail enforced. |
| Dependency Security | **3/10** | No pinning, no SCA scanning. |
| CI/CD Security | **2/10** | No SAST, SCA, or secret scanning in CI. |
| Configuration Safety | **8/10** | YAML safe loading enforced. |
| **Overall** | **5/10** | Critical shell injection fixed. Systematic hardening needed before production. |

## Fixed Issues

### SEC-001: shell=True in signoff.py

Replaced `subprocess.run(cmd, shell=True)` with `shlex.split()` + list form to prevent shell metacharacter injection.

### SEC-005: YAML safe loading

All YAML loading across the codebase now uses `yaml.safe_load()`:
- `gli_flow/config_validator.py`
- `gli_flow/cli/main.py`
- `gli_flow/core/orchestrator.py`
- `gli_flow/investigation/availability.py`
- `gli_flow/investigation/investigator.py`
- `gli_flow/config/__init__.py`

### SEC-006: Encryption secret guardrail

`GLI_ENCRYPTION_SECRET` now raises `RuntimeError` if not set, instead of falling back to a weak default. Requires explicit 32-byte hex key for production use.
