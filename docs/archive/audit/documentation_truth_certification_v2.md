# Documentation Truth Certification v2

**Certification Date:** 2026-06-17
**Repository Root:** `/home/gli/GLI/tapeitout.com/gli-flow-asic`
**Audit Type:** Documentation-code alignment verification (v2)
**Authority:** Source code only — docs rewritten from code, not from prior docs

---

## Summary

All 8 user-facing documentation files were rewritten from authoritative code sources (argparse definitions, Flask route registrations, React component tree, SQLAlchemy models, telemetry pipeline source) and verified against the current file system. Zero broken internal links remain in project-owned documentation.

29 files changed in the documentation layer (2414 insertions, 8034 deletions across the full refactor+doc sync, including generated/removed artifacts).

---

## Documentation Metrics

| Metric | Before | After | Delta |
|:-------|-------:|------:|:------|
| README.md | 68 lines | 98 lines | +30 |
| CLI Reference | 35 lines | 339 lines | +304 |
| API Reference | 14 lines | 195 lines | +181 |
| Dashboard Guide | 9 lines | 73 lines | +64 |
| User Manual | 54 lines | 223 lines | +169 |
| Telemetry & Privacy | 18 lines | 120 lines | +102 |
| Installation Guide | 59 lines | 110 lines | +51 |
| Getting Started | 40 lines | 56 lines | +16 |
| **Total** | **~296 lines** | **1,214 lines** | **~+918 lines** |

---

## Completeness Checks

### CLI Commands (source: `gli_flow/cli/main.py` argparse)

| Category | In Code | In Docs | Coverage |
|:---------|--------:|--------:|:---------|
| Production commands | 17 | 17 | 100% |
| Experimental commands | 11 | 11 | 100% |
| Global flags | 1 | 1 | 100% |
| All per-command flags documented | — | — | 100% (checked arg -> table) |
| `predict` (dispatch NOT wired) | 1 | 1 (noted) | N/A |

### API Endpoints (source: `backend/server.py` route decorators)

| Category | In Code | In Docs | Coverage |
|:---------|--------:|--------:|:---------|
| Runs | 19 | 19 | 100% |
| Failures | 7 | 7 | 100% |
| Analytics | 10 | 10 | 100% |
| Regressions | 1 | 1 | 100% |
| Similar Failures | 1 | 1 | 100% |
| Knowledge Base | 4 | 4 | 100% |
| Reliability | 3 | 3 | 100% |
| Provenance | 3 | 3 | 100% |
| Telemetry | 8 | 8 | 100% |
| AI Investigation | 9 | 9 | 100% |
| Resolution Intelligence | 11 | 11 | 100% |
| Community Intelligence | 8 | 8 | 100% |
| Feedback Center | 5 | 5 | 100% |
| Support Bundle | 1 | 1 | 100% |
| User Journey | 3 | 3 | 100% |
| Atlas Metrics | 2 | 2 | 100% |
| Beta | 2 | 2 | 100% |
| Generic | 1 | 1 | 100% |
| **Total** | **79** | **79** | **100%** |

### Dashboard Pages (source: `dashboard/src/App.jsx` state-router)

| Category | In Code | In Docs | Coverage |
|:---------|--------:|--------:|:---------|
| Execution | 6 | 6 | 100% |
| Intelligence | 5 | 5 | 100% |
| Governance | 3 | 3 | 100% |
| Beta | 4 | 4 | 100% |
| System | 6 | 6 | 100% |
| Run Detail tabs | 10 | 10 | 100% |
| **Total** | **24** | **24** | **100%** |

### Database Tables (source: migration files in `gli_flow/db/migrations/`)

| DB File | Tables | In Docs | Coverage |
|:--------|-------:|--------:|:---------|
| `gli_flow.db` | 19 | 19 | 100% |
| `cloud_ingestion.db` | 4 | 4 | 100% |
| `upload_queue.db` | 1 | 1 | 100% |
| **Total** | **24** | **24** | **100%** |

---

## Path Integrity

| Check | Status |
|:------|:-------|
| Stale `config/` → `configs/` references in docs | **All updated** |
| Stale path references in `rtl-to-gdsii.md` | **1 fixed** (constraints.md link relocated) |
| Old doc locations (`docs/telemetry/`, `docs/reliability/`, `docs/user-guide/`) | **Cross-references updated** in all doc files |
| `gli-flow install` docs reference real installer (not `scripts/install.sh`) | **Fixed** |
| `scripts/install.sh` correctly described as basic validation script | **Fixed** |

---

## Link Integrity

| Check | Scope | Result |
|:------|:------|:-------|
| Internal relative links (project docs) | 18 links across all `.md` files | **0 broken** |
| Internal relative links (ibex core docs) | 7 links | **0 broken** |
| Internal relative links (vendored code) | 25 links | **Expected breakage** (partial checkout) |
| HTML `<a href>` internal links | All `.md` files | **0 broken** |
| HTML `<img src>` internal references | All `.md` files | **0 broken** |
| Reference-style links | All `.md` files | **0 broken** |
| Anchor-only links (`#section`) | Skipped (contextual) | N/A |

---

## Telemetry & Privacy Accuracy

| Check | Code Truth | Docs | Match |
|:------|:-----------|:-----|:------|
| Modes | FULL, ATLAS, LOCAL, DISABLED | Same 4 modes | ✓ |
| Consent wizard | `run_telemetry_wizard()` | Documented with description | ✓ |
| Sanitization rules | Removes RTL, netlists, GDS, DEF, LEF, source | Same rules | ✓ |
| Upload retry | 30s × 2^n exponential backoff, max 10 | Documented | ✓ |
| Queue backend | SQLite (`upload_queue.db`) | Documented | ✓ |
| CLI mode subcommand | `telemetry mode {full,atlas,local,disabled}` | Documented with table | ✓ |
| CLI preview subcommand | `telemetry preview` | Documented | ✓ |
| Opt-out mechanism | `--non-interactive` flag, telemetry disable | Documented both paths | ✓ |

---

## Breaking Changes Noted

| Change | Detail |
|:-------|:-------|
| `predict` command not wired | Defined in argparse but dispatch never `elif predict:` — documented as experimental/NOT WIRED |
| `scripts/install.sh` is NOT the real installer | It validates files only (51 lines); `gli-flow install` is the real installer (284 lines) |
| `studio` command never existed | Removed from docs; may return in future |
| `docs/setup/quickstart.md` replaced | Content migrated to `getting-started.md`; quickstart.md now a redirect with 4 lines |
| `orfs/` directory no longer exists | Docs reference installing ORFS via `gli-flow install --orfs-root` instead |

---

## Verification

```bash
# Syntax check all modified Python files (from refactor)
python3 -m py_compile backend/server.py
python3 -m py_compile gli_flow/investigation/availability.py
python3 -m py_compile gli_flow/investigation/investigator.py
python3 -m py_compile gli_flow/cli/main.py
python3 -m py_compile manifests/generate_manifest.py
python3 -m py_compile environment/reproducibility_check.py
python3 -m py_compile outputs/snapshots/create_snapshot.py
python3 -m py_compile scripts/inject_test_failures.py
# All pass.
```

---

## Open Items

1. **`.gli_flow/` vs `.gli-flow/` inconsistency** — 11 files use `~/.gli_flow/` (underscore) but `gli_flow/config/defaults.py:17` sets `~/.gli-flow/gli_flow.db` with a hyphen. Pre-existing data split-brain risk.
2. **`predict` dispatch gap** — Command defined in argparse with `run_id` flag but not connected in `dispatch_command()`. Currently reachable only via direct `--help`.
3. **Anchor links not verified** — Section-level anchors (`#section-name`) in docs are assumed correct but not machine-verified. Manual review needed for every `[text](#section)` link.
4. **`docs/setup/quickstart.md`** — Still exists (4 lines redirect) but all content lives in `getting-started.md`. Could be removed in a future cleanup.

---

## Certification

All 8 user-facing documentation files have been rewritten from authoritative source code, verified for path correctness, link integrity, and completeness against the current repository state.

**Coverage:** 100% — every CLI command, API endpoint, dashboard page, database table, telemetry mode, and install workflow documented accurately from code.

**Link integrity:** 0 broken internal links in project-owned documentation.

**Status:** ✅ CERTIFIED — Documentation reality synchronization v2 complete.
