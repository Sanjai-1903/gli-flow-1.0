# External Beta Readiness Audit — v1.0.0

**Date:** 2026-06-15
**Audit Scope:** Full product readiness for unsupervised external use
**Methodology:** Code review, documentation audit, install path simulation, security analysis, user journey simulation

---

## Executive Summary

**Verdict: NO-GO for unsupervised external beta.**

GLI-FLOW has strong engineering foundations — working pipeline, good architecture, real EDA integration, comprehensive telemetry transparency — but the install/setup path is broken for a stranger. A user who clones the repo today cannot complete a successful installation without debugging the install script, fixing `pip` package availability, discovering hidden dependencies, and inferring setup steps from aspirational documentation.

**Estimated time for a stranger to get first `--mock` run working: 45–90 minutes (with Python/PATH experience) or never (without).**

---

## Scorecard

| Category | Score | Key Issue |
|----------|:-----:|-----------|
| Installation | **2/10** | `scripts/install.sh` tries `pip install gli-flow[install]` — package **not on PyPI**. No `requirements.txt`. |
| First Run | **5/10** | `--mock` mode works after install. `quickstart` + `--mock` flow is clear. No real-EDA path validation. |
| Failure Experience | **7/10** | Failure Atlas, resolution intelligence, AI investigation all wired. Error messages are informative. |
| Documentation | **3/10** | Multiple docs reference non-existent commands, URLs, and package names. Critical docs are aspirational. |
| Trust & Privacy | **8/10** | Telemetry transparency center is excellent. Privacy guarantees are clear. Consent-gated uploads. |
| Observability | **7/10** | Dashboard, telemetry health, audit log, export all functional. Support bundle works. |
| Support Pipeline | **4/10** | `support-bundle` exists. No bug report templates. No `.github/ISSUE_TEMPLATE`. Escalation is experimental. |
| Security | **5/10** | Known issues (SEC-001 to SEC-010). Subprocess injection partially fixed. No SAST/SCA in CI. |
| **Overall** | **4.5/10** | **Not ready for unsupervised external beta.** |

---

## Critical Risks (Will Block a Stranger)

### CR-1: PyPI package does not exist

`scripts/install.sh` line 193 executes:
```bash
pip install "gli-flow[install]"
```

No package named `gli-flow` exists on PyPI. This command **always fails**. The script then suggests:
```
Try: pip install gli-flow
```
which also fails. The user must know to `git clone` and `pip install -e .` from source, which is not explained anywhere in the script.

**Impact:** Installation blocker for any user following the `scripts/install.sh` path.

### CR-2: Aspirational documentation

Three separate documentation files reference install paths that do not work:

| Document | Claim | Reality |
|----------|-------|---------|
| `docs/guides/installation_guide.md` | `pip install gli-flow` | Package not on PyPI |
| `docs/setup/installation.md` | `pip install -r requirements.txt` | `requirements.txt` does not exist |
| `README.md` Quick Start | `gli-flow quickstart` | Requires successful install first |

Additionally, `docs/guides/troubleshooting_guide.md` references commands that do not exist:
- `gli-flow pdk setup` — no such command
- `gli-flow support bundle` — actual command is `gli-flow support-bundle`
- `gli-flow debug lvs` — no such command
- `gli-flow db check/restore/reset` — no such commands

**Impact:** A user following documented instructions will hit dead ends and have no way to distinguish real docs from aspirational docs.

### CR-3: Unnecessary `click` dependency

`setup.py` lists `click>=8.1.0` as a core dependency. The CLI uses `argparse` exclusively. This adds an unnecessary 250KB+ dependency with no benefit.

**Impact:** Extra download time, potential version conflicts. Indicates the packaging dependencies are not validated.

### CR-4: No PATH guidance after install

After `pip install -e .`, the `gli-flow` command is only available if `~/.local/bin` (or the venv `bin/`) is in `PATH`. Neither the install script nor the README provides explicit PATH guidance for common shells.

**Impact:** A user who successfully installs will get `command not found` and may not know why.

---

## High Risks (Will Cause Significant Friction)

### HR-1: No bug report templates

The `.github/` directory has only `workflows/ci.yml`. No issue templates, no pull request template. A user experiencing issues has no structured way to report them.

### HR-2: Mock-mode discoverability

The `--mock` flag is mentioned only in passing in the README command table. The quickstart guide primarily shows non-mock usage. Users without EDA tools installed will run non-mock and get missing-tool errors.

### HR-3: Subprocess injection surface (SEC-001)

The security review confirms `shell=True` was used in `signoff.py`. While the fix is committed, there is no systematic audit of all `subprocess` calls across the codebase. User-controlled path components are interpolated into subprocess commands in multiple places.

### HR-4: `yaml.load()` history (SEC-005)

The security review claims `yaml.load()` is used, but the actual code uses `yaml.safe_load()` everywhere. This doc/reality mismatch erodes trust in the security review — if this finding is stale, others may be stale too.

### HR-5: Encryption secret documentation (SEC-006)

The security review claims `GLI_ENCRYPTION_SECRET` defaults to `"default-change-in-production"`. The actual code has been fixed to raise `RuntimeError` when not set. The documentation is outdated.

---

## Medium Risks

### MR-1: Test gap for API routes
`RELEASE_READINESS.md` notes API test harness is a known blocker. 10 API route tests are disabled.

### MR-2: No real-flow reliability testing
No `counter x20` or `uart x20` real-flow reliability runs completed. Only mock-mode smoke tests exist.

### MR-3: Dependency pinning
`setup.py` uses loose version ranges (`>=x.y.z`). No lock file. Transitive dependency updates could break without notice.

### MR-4: No SAST/SCA in CI
No Bandit, CodeQL, pip-audit, or Gitleaks integrated. Vulnerabilities could be introduced without detection.

### MR-5: PATH shadowing repair is Magic-specific
`gli-flow doctor --repair-magic` only handles the magic binary. Other tool shadowing (yosys, openroad, netgen) is detected but not auto-repaired.

---

## Beta User Journey Simulation

### Student (Linux-proficient)
1. Clones repo ✅
2. Reads README → sees `gli-flow quickstart` ✅
3. Runs `gli-flow quickstart` → `command not found` ❌ (step 2 broken: no install instructions that work)
4. Tries `scripts/install.sh` → fails on `pip install gli-flow` ❌
5. Realizes must use `pip install -e .` → finds it by reading setup.py or experience ✅
6. Runs `gli-flow quickstart` → works in `--mock` mode ✅
7. Gets `command not found` for first run (PATH issue) → debug cycle ❌
8. Total time: ~45 min. Frustration: Moderate.

**Drop-off risk:** Moderate (requires Python packaging experience)

### Researcher (non-Python-expert, Linux)
1. Clones repo ✅
2. Follows README Quick Start → `gli-flow quickstart` → fails ❌
3. Tries `scripts/install.sh` → fails ❌
4. Tries `docs/guides/installation_guide.md` → `pip install gli-flow` → fails ❌
5. Tries `docs/setup/installation.md` → `pip install -r requirements.txt` → fails ❌
6. Gives up.

**Drop-off risk:** Very High

### ASIC Engineer (EDA background, maybe WSL)
1. Clones repo, reads docs, tries install → fails ❌
2. Debugs, finds `pip install -e .` ✅
3. Runs `gli-flow quickstart` → creates design ✅
4. Tries `gli-flow run <design>` (no `--mock`) → missing EDA tools ❌
5. Reads about `--mock` → runs with mock ✅
6. Wants real flow → needs ORFS, PDK, tools → no clear install path ❌
7. Total time: ~2 hours. Frustration: High.

**Drop-off risk:** High (will file issue or just switch to OpenROAD directly)

### FPGA Engineer (curious about ASIC)
1. Clones repo, tries install → hits same blockers ❌
2. If they get past install, `--mock` mode works ✅
3. No way to try real flow without installing ORFS + PDK (no Docker guidance in README) ❌
4. Loses interest.

**Drop-off risk:** Very High

---

## Documentation Audit

### Verified Accurate
- `docs/user_guide/USER_MANUAL.md` — Comprehensive 29-stage pipeline reference
- `docs/user_guide/TERMS_OF_SERVICE.md` — IP ownership, 90-day retention
- `docs/user_guide/KNOWN_LIMITATIONS.md` — Honest about CDC, Monte Carlo, analog gaps
- `docs/developer/telemetry_pipeline_audit.md` — Detailed telemetry flow
- `docs/developer/telemetry_sanitizer_audit.md` — Field-level classification
- `docs/developer/dataset_readiness_report.md` — Scoring for 7 dataset types
- All `examples/*/gli_manifest.yaml` — Valid manifests

### Outdated / Inaccurate
- `docs/security/security_review.md` — SEC-005 (yaml.load) and SEC-006 (default secret) are fixed in code but not in doc
- `docs/guides/installation_guide.md` — References `pip install gli-flow` (not on PyPI) and non-existent Docker image
- `docs/guides/troubleshooting_guide.md` — Multiple non-existent commands (`gli-flow pdk setup`, `gli-flow support bundle`, etc.)
- `docs/setup/installation.md` — References nonexistent `requirements.txt` and wrong file paths
- `docs/setup/quickstart.md` — Says "5-10 minutes" but install alone takes longer
- `docs/developer/ARCHITECTURE.md` — Now contains architecture summary
- `docs/developer/architecture.md` — Empty file (0 bytes)
- `docs/developer/reproducibility.md` — Now contains reproducibility overview

### Missing
- No `requirements.txt` for direct `pip install -r` usage
- No `.github/ISSUE_TEMPLATE/bug_report.md`
- No `.github/ISSUE_TEMPLATE/feature_request.md`
- No `CONTRIBUTING.md` that covers setup (the existing one covers PR process only)
- No getting-started guide for Docker deployment

### Telemetry Trust Documentation — Excellent
The telemetry docs are the best-documented area:
- `docs/developer/telemetry_pipeline_audit.md` — Full pipeline trace
- `docs/developer/telemetry_sanitizer_audit.md` — Every field classified (SAFE/REDACT/HASH/BLOCK/DERIVE)
- `dashboard/src/TelemetryPage.jsx` — Transparency Center with raw vs sanitized view
- README telemetry section — Clear what is/is not collected, opt-out instructions

---

## Security Audit Summary

| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| SEC-001 | **CRITICAL** | Subprocess injection via `shell=True` in signoff.py | **Fixed** (shlex.split + list form) |
| SEC-002 | HIGH | Path traversal in backend server endpoints | **Fixed** (`_safe_run_path()` added) |
| SEC-003 | HIGH | No privilege separation for EDA subprocesses | **Open** — no sandboxing |
| SEC-004 | MEDIUM | CLI `run` design argument path traversal | **Open** — no containment validation |
| SEC-005 | MEDIUM | YAML loading with `yaml.load()` | **Fixed in code**, doc outdated |
| SEC-006 | MEDIUM | Encryption secret default fallback | **Fixed in code**, doc outdated |
| SEC-007 | MEDIUM | Parent environment leaked to subprocesses | **Open** — `safe_env()` inherits everything |
| SEC-008 | LOW | Predictable temp file paths | **Open** — no cleanup |
| SEC-009 | LOW | No dependency pinning | **Open** — loose version ranges |
| SEC-010 | LOW | No SAST/SCA in CI | **Open** — not integrated |

---

## Observable vs Reality: What a Stranger Sees

```
What the docs PROMISE                    What actually happens
─────────────────────────────            ──────────────────────
pip install gli-flow                      ❌ Package not on PyPI
curl script | bash                        ❌ Script fails on missing package
gli-flow quickstart                       ❌ command not found (no install)
gli-flow run                              ❌ missing tools (needs --mock)
5-10 min to first run                     ❌ 45-90 min with debugging
Docker pull ghcr.io/...                   ❌ Image not published
```

---

## Recommended Actions Before External Beta

### P0 — Fix by Next Week
1. **Publish package to PyPI** (`gli-flow`) or update all docs for source-only install
2. **Fix `scripts/install.sh`** to `pip install -e .` from cloned repo instead of PyPI
3. **Delete or rewrite** `docs/guides/installation_guide.md` and `docs/setup/installation.md` to match reality
4. **Fix troubleshooting guide** — remove non-existent commands, add real commands

### P1 — Fix Before Beta Launch
5. **Add `.github/ISSUE_TEMPLATE/bug_report.md`** with structured format
6. **Add `--mock` discovery to quickstart** — auto-detect if real EDA tools exist, suggest mock if not
7. **Add PATH guidance** to install success message and README
8. **Update `docs/security/security_review.md`** to reflect current state (SEC-005, SEC-006 already fixed)
9. **Audit all `subprocess` calls** for `shell=True` or unsanitized user input
10. **Remove unused `click` dependency** from `setup.py`

### P2 — Before Production
11. **Add Bandit + pip-audit to CI** (SEC-010)
12. **Add path containment validation** to CLI `run` command (SEC-004)
13. **Strip dangerous env vars** from `safe_env()` (SEC-007)
14. **Publish Docker image** to GHCR (referenced in docs but doesn't exist)
15. **Run `counter x20` real-flow reliability test** and publish results
16. **Add `requirements.txt`** for direct install path

---

## Go / No-Go Decision

| Category | Score | Verdict |
|----------|:-----:|---------|
| Installation | 2/10 | ❌ **BLOCKING** |
| First Run | 5/10 | ⚠️ Weak |
| Failure Experience | 7/10 | ✅ Good |
| Documentation | 3/10 | ❌ **BLOCKING** |
| Trust & Privacy | 8/10 | ✅ Excellent |
| Observability | 7/10 | ✅ Good |
| Support Pipeline | 4/10 | ⚠️ Weak |
| Security | 5/10 | ⚠️ Acceptable for beta |

**Overall Verdict: NO-GO for unsupervised external beta.**

The product has strong technical foundations but the entry door is locked. A stranger cannot install GLI-FLOW by following the documented instructions. Two of the three install paths (`pip install gli-flow` and `pip install -r requirements.txt`) are dead ends, and the third (`scripts/install.sh`) crashes on a missing PyPI package.

Once past installation (requires manual `pip install -e .` or Docker), the product works well in mock mode and the telemetry transparency is best-in-class. The Failure Atlas, resolution intelligence, dashboard, and observability features are functional and well-designed.

**Recommendation:** Fix the P0 and P1 items (estimated 2-3 days of work), then re-score. Target: 7+/10 in Installation, 6+/10 in Documentation. At that point, GLI-FLOW is ready for a supervised external beta (with founder on standby) or an unsupervised beta with a comprehensive setup guide.
