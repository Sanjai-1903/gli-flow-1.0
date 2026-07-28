# Beta Command Matrix

**Date:** 2026-06-12  
**Category definitions:**

| Category | Meaning |
|----------|---------|
| ✅ **READY** | Fully functional, tested, help is adequate, no known blockers |
| 🔶 **EXPERIMENTAL** | Functional but requires external setup (SSH keys, cloud credentials, etc.) |
| ❌ **BROKEN** | Known bug prevents normal use |

---

## Command Status

| # | Command | Category | Help Quality | Tested | Notes |
|---|---------|----------|-------------|--------|-------|
| 1 | `setup` | ✅ READY | ✅ GOOD | ✅ | Interactive and `--non-interactive` modes work |
| 2 | `doctor` | ✅ READY | ✅ GOOD | ✅ | 10+ tool checks, `--fix` works |
| 3 | `run` | ✅ READY | ⚠️ FAIR | ✅ | Full pipeline executes with `--mock` |
| 4 | `history` | ✅ READY | ✅ GOOD | ✅ | Shows formatted table |
| 5 | `status` | ✅ READY | ✅ GOOD | ✅ | Simple, clear output |
| 6 | `batch` | 🔶 EXPERIMENTAL | ⚠️ FAIR | ⚠️ | Needs `--mock` passthrough support |
| 7 | `init` | ✅ READY | ✅ GOOD | ✅ | Creates manifest + RTL dir |
| 8 | `quickstart` | ✅ READY | ❌ POOR | ✅ | Works interactively, has no help text |
| 9 | `install` | ✅ READY | ✅ GOOD | ✅ | All flags work, dry-run supported |
| 10 | `report` | 🔶 EXPERIMENTAL | ❌ POOR | ⚠️ | Duplicate positional/optional args; needs ORFS |
| 11 | `reset-runs` | ✅ READY | ✅ GOOD | ✅ | Clears run history |
| 12 | `db` | ✅ READY | ✅ GOOD | ✅ | Status/migrate/repair/path subcommands work |
| 13 | `diagnose` | ✅ READY | ⚠️ FAIR | ✅ | Takes run_id, output format TBD |
| 14 | `show-telemetry` | ✅ READY | ⚠️ FAIR | ✅ | Takes run_id, shows telemetry |
| 15 | `config` | ✅ READY | ✅ GOOD | ✅ | Toggle telemetry on/off |
| 16 | `support-bundle` | ✅ READY | ✅ GOOD | ✅ | Creates diagnostic zip |
| 17 | `ci` | ❌ BROKEN | ❌ POOR | ❌ | Needs `--mock` passthrough; `_extract_metrics` fixed but still no EDA tools without real install |
| 18 | `remote` | 🔶 EXPERIMENTAL | ⚠️ FAIR | ⚠️ | Requires SSH host + key; cannot test without target |
| 19 | `cloud` | 🔶 EXPERIMENTAL | ⚠️ FAIR | ⚠️ | Requires boto3/s3 credentials; upload/download/list parsed correctly but fail without provider config |
| 20 | `dashboard` | 🔶 EXPERIMENTAL | ⚠️ FAIR | ⚠️ | Requires uvicorn + npm; untested in headless env |
| 21 | `upgrade-check` | 🔶 EXPERIMENTAL | ⚠️ FAIR | ✅ | Works offline but can't reach PyPI/GitHub |

---

## Summary

| Status | Count | Commands |
|--------|-------|----------|
| ✅ **READY** | 12 | setup, doctor, run, history, status, init, quickstart, install, reset-runs, db, diagnose, show-telemetry, config, support-bundle |
| 🔶 **EXPERIMENTAL** | 6 | batch, report, remote, cloud, dashboard, upgrade-check |
| ❌ **BROKEN** | 1 | ci |

---

## Beta Release Recommendation

**Ship v1.0.0-beta with the experimental framework in place.**

- 12 of 19 commands (63%) are READY
- The experimental framework clearly marks the 7 non-production commands
- The one BROKEN command (`ci`) is hidden from `--help`
- Two high-priority help text fixes (quickstart, run examples) should be applied before tagging beta

### Pre-Beta Must-Fix

1. **`quickstart` help** — Add `description=` to subparser (trivial, 1 line)
2. **Add `--mock` support to `batch`** — So users can test batch in CI
3. **`run --help` examples** — Add epilog with `--mock` usage example

### Post-Beta Backlog

1. Fix `ci --mock` passthrough (blocked on full EDA test)
2. Simplify `report` duplicated arguments
3. Add dependency pre-checks to `dashboard`
4. Add acronym glossary (ORFS, PDK, QoR, WNS, TNS)
