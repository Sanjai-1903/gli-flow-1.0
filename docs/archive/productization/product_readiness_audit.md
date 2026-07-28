# Product Readiness Audit

> Generated: June 2026
> Target: External-user deployability of GLI-FLOW-ASIC

## Scoring Methodology

Each category is scored 0–10:
- **0–3**: Missing / non-functional
- **4–6**: Partial but requires expert knowledge
- **7–8**: Functional with minor gaps
- **9–10**: Production-ready, well-documented, automated

---

## 1. Installation (Score: 4/10)

### What exists
- `setup.py` with console_script `gli-flow=gli_flow.cli.main:main`
- `pip install -e .` works for development
- Two Dockerfiles (production + dev)
- `gli-flow install` CLI command that installs EDA tools via system packages
- `gli_flow/installer/` module with per-tool installers

### Findings

| ID | Severity | Finding |
|----|----------|---------|
| INST-001 | CRITICAL | **No `pip install gli-flow` support**. Package is not published to PyPI. No `requirements.txt`. No `pyproject.toml`. |
| INST-002 | CRITICAL | **No install script** (`scripts/install.sh` or `scripts/install.ps1`). User must know to clone, `cd`, `pip install`. |
| INST-003 | HIGH | **No OS detection or prerequisites check** in installation path. User may attempt on unsupported OS and get cryptic errors. |
| INST-004 | HIGH | **Dockerfile installs specific tool versions** that may be stale. Yosys from apt, not latest. OpenROAD pinned to a specific .deb release. |
| INST-005 | MEDIUM | **No automated doctor run after install**. User installs but has no feedback on whether the installation succeeded. |
| INST-006 | MEDIUM | **No install testing in CI**. CI runs tests but doesn't verify a fresh install produces a working environment. |
| INST-007 | LOW | **`scripts/` directory has outdated placeholder scripts** (`run_flow.sh` is echo/sleep mock). |

### Recommendations
1. Publish to PyPI, add `pyproject.toml`
2. Create `scripts/install.sh` and `scripts/install.ps1`
3. Run `doctor` automatically after install
4. Pin versions in install script, not just Dockerfile
5. Add fresh-install CI job

---

## 2. Configuration (Score: 3/10)

### What exists
- `configs/` directory with JSON configs for PDK, runtime, policies, toolchains
- Each design has `gli_manifest.yaml`
- `~/.gli-flow/config.json` is referenced at runtime
- `gli-flow config` CLI command (telemetry toggle only)
- `gli_flow/installer/` parses tool paths

### Findings

| ID | Severity | Finding |
|----|----------|---------|
| CFG-001 | CRITICAL | **No hierarchical configuration system**. Hardcoded paths and versions scattered across modules. No layered defaults/user/project/env override. |
| CFG-002 | CRITICAL | **No `~/.gli-flow/config.yaml` generated on install**. No PDK path, tool paths, or workspace config wizard. |
| CFG-003 | HIGH | **Configs are JSON and YAML mixed arbitrarily**. Some in `configs/`, some in individual design dirs. No single config loading entry point. |
| CFG-004 | HIGH | **Many hardcoded paths and versions remain**. Tool versions are baked into installer modules, not read from config. |
| CFG-005 | MEDIUM | **`config` CLI command only supports telemetry toggle**. Cannot set workspace, PDK path, tool paths via CLI. |
| CFG-006 | LOW | **Configuration validation is ad-hoc**. No schema validation for config files. Malformed configs produce runtime errors, not clear messages. |

### Recommendations
1. Build `gli_flow/config/` with layered resolution (defaults → user → project → env)
2. Add `gli-flow setup` interactive wizard for first-run config
3. Centralize all hardcoded values into defaults layer
4. Add JSON Schema validation for config files
5. Expand `config` CLI command to read/write all settings

---

## 3. Documentation (Score: 5/10)

### What exists
- `docs/` has 20+ files covering architecture, setup, reliability, reproducibility
- `README.md` has quickstart, commands table, manifest format
- Each design has `README.md` in some cases (gcd has one)
- `failure_atlas/README.md`

### Findings

| ID | Severity | Finding |
|----|----------|---------|
| DOC-001 | HIGH | **No installation guide**. `docs/setup/installation.md` exists but may not cover all OS options. |
| DOC-002 | HIGH | **No troubleshooting guide**. User has no structured path to resolve common failures. |
| DOC-003 | HIGH | **Architecture docs duplicated** (`ARCHITECTURE.md` and `architecture.md` with different content). |
| DOC-004 | MEDIUM | **No migration guide** for upgrading between versions. |
| DOC-005 | MEDIUM | **No release notes / changelog**. |
| DOC-006 | MEDIUM | **Quickstart documents `gli-flow quickstart` but command output may not match docs**. |
| DOC-007 | LOW | **No deployment mode docs** (local vs WSL vs Docker vs CI/CD). |
| DOC-008 | LOW | **No security documentation**. No documented process for reporting vulnerabilities. |

### Recommendations
1. Create installation guide, quickstart, troubleshooting guide, migration guide
2. Deduplicate and reconcile architecture docs
3. Add release notes / CHANGELOG.md
4. Write deployment mode documentation
5. Document security model and vulnerability reporting

---

## 4. Packaging (Score: 3/10)

### What exists
- `setup.py` with dependencies, extras, entry point
- No `pyproject.toml`
- No `requirements.txt` or lockfile
- No `MANIFEST.in`

### Findings

| ID | Severity | Finding |
|----|----------|---------|
| PKG-001 | CRITICAL | **No `pyproject.toml`**. Modern Python packaging standard is not used. Cannot build wheels cleanly. |
| PKG-002 | HIGH | **No dependency lockfile**. Reproducible installs are not guaranteed. |
| PKG-003 | HIGH | **No `MANIFEST.in`**. `sdist` may miss required files (configs, examples, docs). |
| PKG-004 | MEDIUM | **Extras require manual discovery**. User must read `setup.py` to know `[install]`, `[cloud]`, `[dev]` extras exist. |
| PKG-005 | MEDIUM | **No Makefile or task runner** for common operations (install, test, lint, build, clean). |
| PKG-006 | LOW | **Package published checks** — no automated check that sdist/wheel are complete. |

### Recommendations
1. Create `pyproject.toml` with setuptools backend
2. Add `MANIFEST.in` to include non-Python files
3. Add `requirements.txt` / `requirements-dev.txt` or use pip-compile
4. Add `Makefile` for common dev tasks
5. Publish to TestPyPI and verify sdist contents

---

## 5. Logging (Score: 2/10)

### What exists
- 16+ modules create loggers via `logging.getLogger(__name__)`
- **No centralized logging configuration** (no `basicConfig`, no `dictConfig`)
- No log files, no log rotation, no structured logging
- Logging goes to `logging.lastResort` (stderr, WARNING+ only)

### Findings

| ID | Severity | Finding |
|----|----------|---------|
| LOG-001 | CRITICAL | **No log file output**. All logging is lost on terminal close. Cannot debug past runs. |
| LOG-002 | CRITICAL | **No structured logging**. Logs are free-text, not parseable by machines. No correlation IDs. |
| LOG-003 | HIGH | **No per-run or per-stage log files**. Cannot isolate a single run's logs. |
| LOG-004 | HIGH | **No log level configuration**. User cannot set `--verbose` to get DEBUG logs. |
| LOG-005 | MEDIUM | **No log rotation or size limits**. Would fill disk on long-running instances. |
| LOG-006 | LOW | **No support bundle generation** that includes logs. |

### Recommendations
1. Create `gli_flow/core/logging.py` with centralized config (file + console handlers)
2. Add structured logging with JSON format option
3. Create per-run and per-stage log files in `logs/`
4. Add log level CLI flags
5. Add log rotation

---

## 6. Telemetry (Score: 6/10)

### What exists
- Telemetry module (`gli_flow/telemetry.py`)
- Telemetry opt-out via `--telemetry off` or env var
- Privacy disclosure in README
- Telemetry payload inspection via `show-telemetry` command

### Findings

| ID | Severity | Finding |
|----|----------|---------|
| TEL-001 | MEDIUM | **No explicit telemetry consent prompt on first run**. README mentions it, but no interactive confirmation. |
| TEL-002 | MEDIUM | **Telemetry consent stored but no `config.yaml` integration**. Stored in an implementation-specific way. |
| TEL-003 | LOW | **No telemetry dashboard or transparency page**. User cannot see what was uploaded. |
| TEL-004 | LOW | **No documented data retention or deletion policy**. |

### Recommendations
1. Add explicit first-run telemetry consent during `setup` or `quickstart`
2. Store telemetry preference in `~/.gli-flow/config.yaml`
3. Add `gli-flow telemetry status` command
4. Document data retention and deletion in privacy notice

---

## 7. Release Process (Score: 1/10)

### What exists
- Version in `gli_flow/version.py` (`v1.0.0`)
- Dockerfile label references `v1.0.0-mvp`
- CI runs on push/PR to main

### Findings

| ID | Severity | Finding |
|----|----------|---------|
| REL-001 | CRITICAL | **No release checklist or process**. No documented steps for cutting a release. |
| REL-002 | CRITICAL | **No semantic versioning policy**. Version is `v1.0.0` but no documented policy for when to bump. |
| REL-003 | HIGH | **No release validation** (golden regression, failure corpus, doctor check) gating releases. |
| REL-004 | HIGH | **No CHANGELOG.md or release notes**. |
| REL-005 | MEDIUM | **No release automation** (GitHub Releases, tags, PyPI publish, Docker Hub publish). |
| REL-006 | MEDIUM | **No upgrade path documented**. Going from v0.x to v1.0.0 has no migration guide. |

### Recommendations
1. Document release checklist and process
2. Adopt strict semantic versioning policy
3. Create automated release validation pipeline
4. Create CHANGELOG.md following keepachangelog format
5. Automate GitHub Release + PyPI publish + Docker Hub publish

---

## 8. Supportability (Score: 2/10)

### What exists
- `doctor` command validates EDA tool installation
- `diagnose` command scans failed run logs
- Failure Atlas captures failure records
- Exception hierarchy with 12 custom classes

### Findings

| ID | Severity | Finding |
|----|----------|---------|
| SUP-001 | CRITICAL | **No support bundle command**. No way for user to generate a single archive with all diagnostic info. |
| SUP-002 | HIGH | **Error messages still expose raw stack traces** by default. No `--debug` flag separation in many commands. |
| SUP-003 | HIGH | **No structured error taxonomy**. Errors don't include error codes, documentation links, or resolution steps. |
| SUP-004 | MEDIUM | **Doctor command lacks fix mode documentation**. `--fix` flag exists but behavior is unclear. |
| SUP-005 | MEDIUM | **No health endpoint or status check** beyond `doctor`. |
| SUP-006 | LOW | **No metrics or SLIs exposed** for monitoring. |

### Recommendations
1. Create `gli-flow support-bundle` command
2. Add `--debug`/`--verbose` flag separation to all commands
3. Add error codes and documentation links to all errors
4. Improve doctor `--fix` mode documentation
5. Add health check endpoint for Docker deployments

---

## 9. Security (Score: 5/10)

### What exists
- `gli_flow/security/file_protection.py` with AES-256-GCM encryption
- `secure_run_directory()` sets 0o700/0o600 permissions
- `safe_env()` in `subprocess_env.py` strips dangerous env vars
- Exception hierarchy includes security-relevant errors

### Findings

| ID | Severity | Finding |
|----|----------|---------|
| SEC-001 | HIGH | **1 `shell=True` instance in `signoff.py`** (line 30-32). Allows shell injection via crafted input. |
| SEC-002 | HIGH | **No subprocess sandboxing**. All subprocesses inherit full user permissions. No privilege separation. |
| SEC-003 | MEDIUM | **No input validation for user-supplied paths**. Path traversal possible in `run` command design arg. |
| SEC-004 | MEDIUM | **No automated security scanning** (SAST/SCA) in CI. |
| SEC-005 | MEDIUM | **Encryption secret falls back to default** (`GLI_ENCRYPTION_SECRET` not set → hardcoded default). |
| SEC-006 | LOW | **No dependency vulnerability scanning**. |
| SEC-007 | LOW | **No documented security policy** (no SECURITY.md, no vulnerability reporting process). |

### Recommendations
1. Remove `shell=True` usage, replace with `shlex` + list form
2. Add SAST scanning (Bandit, CodeQL) to CI
3. Validate all user-supplied paths against traversal
4. Require `GLI_ENCRYPTION_SECRET` in production, fail if unset
5. Create SECURITY.md with reporting process

---

## 10. Upgradeability (Score: 1/10)

### What exists
- Version number in single file `gli_flow/version.py`

### Findings

| ID | Severity | Finding |
|----|----------|---------|
| UPG-001 | CRITICAL | **No upgrade command** (`gli-flow upgrade` or `gli-flow upgrade-check`). User cannot check for newer versions. |
| UPG-002 | HIGH | **No migration mechanism** for config format changes. Version bumps may silently break previous configs. |
| UPG-003 | HIGH | **No version comparison logic**. No way to determine if a version is newer or has breaking changes. |
| UPG-004 | MEDIUM | **No database schema version check on startup**. DB migrations may not run automatically. |
| UPG-005 | LOW | **No documented breaking changes policy**. |

### Recommendations
1. Create `gli-flow upgrade-check` comparing installed vs latest version
2. Add migration system for config format changes
3. Check for pending DB migrations on startup and run them
4. Document breaking changes policy in SEMVER.md

---

## Overall Product Readiness Score

| Category | Score (0–10) | Priority |
|----------|:--------:|----------|
| Installation | **4** | Immediate |
| Configuration | **3** | Immediate |
| Documentation | **5** | High |
| Packaging | **3** | Immediate |
| Logging | **2** | Immediate |
| Telemetry | **6** | Medium |
| Release Process | **1** | Immediate |
| Supportability | **2** | Immediate |
| Security | **5** | High |
| Upgradeability | **1** | Immediate |
| **Average** | **3.2 / 10** | |

### Critical (Must Fix Before v1.0)

| ID | Area | Finding |
|----|------|---------|
| INST-001 | Installation | No PyPI package, no pip install |
| INST-002 | Installation | No install script |
| CFG-001 | Configuration | No hierarchical config system |
| CFG-002 | Configuration | No first-run config generation |
| LOG-001 | Logging | No log file output |
| LOG-002 | Logging | No structured logging |
| PKG-001 | Packaging | No pyproject.toml |
| REL-001 | Release | No release checklist |
| REL-002 | Release | No semantic versioning policy |
| SUP-001 | Supportability | No support bundle |
| UPG-001 | Upgradeability | No upgrade command |

### High Priority (Must Fix Before Public Launch)

| ID | Area | Finding |
|----|------|---------|
| INST-003 | Installation | No OS detection |
| CFG-003 | Configuration | Config format inconsistency |
| CFG-004 | Configuration | Hardcoded paths/versions |
| DOC-001 | Documentation | No installation guide |
| DOC-002 | Documentation | No troubleshooting guide |
| LOG-003 | Logging | No per-run/per-stage logs |
| LOG-004 | Logging | No log level configuration |
| PKG-002 | Packaging | No dependency lockfile |
| PKG-003 | Packaging | No MANIFEST.in |
| REL-003 | Release | No release validation |
| SUP-002 | Supportability | Stack traces exposed by default |
| SUP-003 | Supportability | No error codes |
| SEC-001 | Security | shell=True in signoff.py |
| SEC-002 | Security | No subprocess sandboxing |
| UPG-002 | Upgradeability | No migration mechanism |
| UPG-003 | Upgradeability | No version comparison |
