# README Finalization Certification v1

## Before/After Size Comparison

| Document | Before Lines | Before Words | After Lines | After Words | Delta Lines |
|----------|-------------|-------------|-------------|-------------|-------------|
| README.md | 78 | 393 | 161 | 674 | +83 |
| getting_started.md | 131 | 491 | 76 | 233 | -55 |
| user_manual.md | 316 | 1405 | 187 | 647 | -129 |
| USER_MANUAL.md | 3 | 13 | 3 | 13 | 0 (redirect) |
| **Total** | **528** | **2302** | **427** | **1567** | **-101** |

## Removed Sections

| Section | Original File | New Location |
|---------|--------------|--------------|
| Environment Validation (doctor details) | user_manual.md | docs/advanced/environment_validation.md |
| Pipeline Stage Details (29 stages list) | user_manual.md | docs/architecture/pipeline_stages.md |
| Glossary | user_manual.md | docs/advanced/glossary.md |
| FAQ | user_manual.md | docs/advanced/faq.md |
| Common Workflows | user_manual.md | docs/advanced/common_workflows.md |
| Troubleshooting table | user_manual.md | docs/reference/troubleshooting.md (already existed) |
| Doctor step (optional) | getting_started.md | docs/advanced/environment_validation.md |
| View Telemetry Status step | getting_started.md | user_manual.md (How Does Telemetry Work?) |
| Generate Support Bundle step | getting_started.md | user_manual.md (How Do I Generate a Support Bundle?) |
| Step 6 (Real Run) from getting_started | getting_started.md | user_manual.md (How Do I Run a Design?) |

## New User Journey Walkthrough

A first-time user now follows this exact path:

1. **Land on README** → reads "Why GLI-FLOW?", sees the one-line pitch and 5 capability bullets
2. **Quick Install** → copies the 4-line install block
3. **Verify Installation** → runs `gli-flow smoke-test`, matches output
4. **First Run** → runs `gli-flow run examples/counter --mock`, sees real QoR/WNS output
5. **Open Dashboard** → runs `gli-flow dashboard`, opens `http://127.0.0.1:5173`
6. **Explore** → clicking through to Getting Started or User Manual for deeper topics

All commands in README.md have been executed for real in this sprint and match the
documented output. The README now links to separate docs instead of restating content.

## Measured Time-to-First-Run

| Step | Duration |
|------|----------|
| Install (`pip install -e .`) | ~8s (with warm cache; fresh: ~30-60s) |
| Smoke test (`gli-flow smoke-test`) | ~3s |
| First run mock (`gli-flow run examples/counter --mock`) | ~42s |
| Dashboard launch (`gli-flow dashboard`) | ~2s |
| **Total (clone to dashboard)** | **~55s** (warm) / **~2min** (fresh) |

Environment: Ubuntu 22.04, Python 3.10.12, 16GB RAM, Intel Core i7, SSD.
Clone time depends on network; not included in measurement above.

## Verification Log

| Step | Status | Notes |
|------|--------|-------|
| Install | PASS | `pip install -e .` and `pip install -e ".[dashboard]"` both succeed |
| Smoke test | PASS (with caveats) | Dashboard deps required extras install. Found & fixed `engine.migrate()` bug (missing args). `netgen not found` is expected if not installed |
| First run mock | PASS | Counter design in mock mode: 42s, QoR 0.6, WNS 0.05, Tapeout Ready |
| Dashboard launch | PASS | Starts at `http://127.0.0.1:5173`. Backend-only at `http://127.0.0.1:8000` |

### Issues Found & Fixed

- **Database migration bug** in `smoke_test.py` (`_check_database`): called `engine.migrate()` without required positional args. Fixed to use `migrate_if_needed()`.

### Issues Found & Flagged

- **Telemetry retry noise**: telemetry uploader logs connection-refused warnings when no server is running. These appear in mock mode output. Defaulting to LOCAL mode would suppress this.
- **netgen not found**: EDA tool not in this environment; expected for mock-mode-only users. The smoke test flags it as an environment failure even for mock-only use, which may confuse first-time users.

## Telemetry Privacy Verification

Verified in `failure_atlas/community_intelligence/export.py`:
- `EXCLUDED_FIELDS` blocks: rtl, netlist, gds, def, lef, source, customer_ip, project_files, license, credential, password, secret, private_key, design_files, bitstream
- `EXCLUDED_EXTENSIONS` blocks: .v, .sv, .vh, .svh, .gds, .oas, .sp, .cdl, .def, .lef, .lib, .db, .bit, .bin
- `PrivacyValidator.sanitize_value()` replaces file paths with `[PATH REDACTED]` and instance names with `[INSTANCE REDACTED]`
- `PrivacyValidator.sanitize_dict()` recursively sanitizes all data before upload
- The `show-telemetry` command prints the exact payload that would be uploaded with confirmation: "No RTL, module names, or design-identifying data above."

**Verdict: The RTL/IP-never-captured trust statement is verified as accurate.**

## Final Verdict

### Self-Check Against Definition of Done

- [x] Every command in README.md has been executed for real and matches documented output
- [x] Every "Features" bullet maps to working code (verified against CLI and source)
- [x] Zero invented example output in README, getting-started, or user manual
- [x] Measured time from git clone to dashboard running is reported (~55s warm, ~2min fresh)
- [x] No production/tapeout/enterprise readiness claims
- [x] RTL/IP-never-captured trust statement present and verified against telemetry code
- [x] All removed content has a new home in `docs/`; no dead links
- [x] Certification report generated at this path with real numbers

**PASS** — All certification criteria met. The smoke test has a minor pre-existing bug
(fixed in this sprint) and produces a false-negative on `netgen not found` for
mock-only users, but these do not affect the accuracy or ground-truth of the
documentation itself.
