# Destructive Reinstall Certification v1

**Date:** 2026-06-18
**Tester:** Automated Audit
**Repository:** https://github.com/Jegadiswar-SM/gli-flow-asic.git
**Commit:** 48481cf2e98f59c800d324297d686fe51e53d4cc

---

## Environment

| Attribute | Value |
|-----------|-------|
| OS | Ubuntu 26.04 LTS (Resolute Raccoon) |
| Kernel | Linux 6.18.33.1-microsoft-standard-WSL2 |
| Python | 3.14.4 |
| Node | v24.16.0 |
| npm | 11.13.0 |
| Architecture | x86_64 (WSL2) |

## Commands Executed

```bash
# Phase 1 — Inventory
cat /etc/os-release
python3 --version
node --version
which gli-flow
ls -la ~/.gli_flow
echo $PATH
pip3 list | grep -i gli
python3 -c "import gli_flow"
git log --oneline -5
du -sh /home/bolter/gli-flow

# Phase 2 — Destructive Cleanup
pip3 uninstall -y gli-flow --break-system-packages
rm -rf ~/.gli_flow
rm -rf /home/bolter/gli-flow/gli_flow.egg-info
pip3 cache purge
rm -rf /home/bolter/gli-flow/venv
rm -f /home/bolter/.local/lib/python3.14/site-packages/gli-flow.egg-link
rm -rf /home/bolter/gli-flow

# Phase 3 — Reboot Validation
which gli-flow  # → not found
python3 -c "import gli_flow"  # → ModuleNotFoundError
ls ~/.gli_flow  # → No such file or directory
pip3 show gli-flow  # → not installed

# Phase 4 — Fresh Clone
git clone https://github.com/Jegadiswar-SM/gli-flow-asic.git /home/bolter/gli-flow

# Phase 5 — Install Using Docs Only (README.md + docs/setup/installation.md)

# Phase 6 — Installation
python3 -m venv venv
pip install --upgrade pip setuptools wheel
pip install -e .

# Phase 7 — Database Validation
gli-flow doctor --fix <<< "3"

# Phase 8 — Core Workflow
gli-flow run examples/counter --mock

# Phase 9 — Dashboard Validation
gli-flow dashboard --backend-only
gli-flow dashboard

# Phase 10 — Telemetry Validation
gli-flow telemetry status

# Phase 11 — Support & Recovery
gli-flow support-bundle

# Phase 12 — Stress Reinstall Test
rm -f ~/.gli_flow/gli_flow.db
gli-flow doctor --fix <<< "3"
rm -f ~/.gli-flow/upload_queue.db
gli-flow telemetry status
gli-flow run examples/counter --mock
```

## Install Duration

| Step | Duration |
|------|----------|
| git clone | ~5s |
| python3 -m venv | ~2s |
| pip install --upgrade pip setuptools wheel | ~8s |
| pip install -e . (base) | ~15s |
| pip install -e ".[dashboard]" | ~20s |
| npm install (dashboard) | ~13s |
| **Total (base)** | **~30s** |
| **Total (with dashboard)** | **~63s** |

## Deleted Artifacts

| Artifact | Size | Location |
|----------|------|----------|
| Old repository clone | 235 MB | /home/bolter/gli-flow |
| Database | 278 KB | ~/.gli_flow/gli_flow.db |
| pip cache | 64 MB | /home/bolter/.cache/pip |
| Virtual environment | ~40 MB | /home/bolter/gli-flow/venv |
| egg-info | ~4 KB | /home/bolter/gli-flow/gli_flow.egg-info |
| egg-link | ~50 B | ~/.local/lib/python3.14/site-packages/gli-flow.egg-link |

## Issues Found

### Issue 1: `SchemaMigrationRepair.repair()` marks migrations as applied without executing SQL

**Severity:** HIGH
**File:** `gli_flow/infrastructure/repair_actions.py:50-63`
**Description:** `SchemaMigrationRepair.repair()` calls `MigrationEngine.repair()` which performs `INSERT OR IGNORE INTO schema_version` for all migrations without actually running the migration SQL. This records migrations as "applied" in `schema_version` without creating any tables. When `migrate_if_needed()` runs afterward, it sees all migrations are "applied" and skips all SQL execution. This results in a completely empty database with no tables.
**Impact:** `gli-flow doctor --fix` cannot recover from a deleted database. Fresh installations using `--fix` path also fail.
**Workaround:** Run `gli-flow doctor` (without `--fix`) after ensuring telemetry consent is configured, OR directly invoke `migrate_if_needed()`.

### Issue 2: `EXPECTED_COLUMNS` has columns that migrations don't create

**Severity:** MEDIUM
**File:** `gli_flow/database/migrations.py:423-437`
**Description:** The `EXPECTED_COLUMNS` dict for `resolution_patterns` expects 9 columns (`contradictory_reports`, `engineer_confirmations`, `tracked_design_names`, `tracked_run_ids`, `trust_level`, `trust_reason`, `trust_score`, `unique_designs`, `unique_runs`) that are not created by Migration 31 (which creates the table) or any subsequent migration. This causes `validate_runtime_schema()` to always fail for a freshly migrated database.
**Impact:** `gli-flow doctor` always shows `Schema ERROR` even after successful migration.
**Workaround:** Manually ALTER TABLE to add missing columns to `resolution_patterns`.

### Issue 3: Dashboard dependencies not in base install

**Severity:** MEDIUM
**File:** `setup.py:48-53`
**Description:** `fastapi`, `uvicorn`, and `pydantic` are declared in `extras_require["dashboard"]` but the README and installation docs only document `pip install -e .`. Users must run `pip install -e ".[dashboard]"` separately. Additionally, the React frontend requires `npm install` in `dashboard/` which is completely undocumented.
**Impact:** `gli-flow dashboard` fails silently — uvicorn not found, process exits without error message.
**Workaround:** `pip install -e ".[dashboard]" && cd dashboard && npm install`

### Issue 4: Telemetry consent wizard blocks non-interactive use

**Severity:** MEDIUM
**File:** `gli_flow/cli/main.py:132-145`
**Description:** The telemetry consent wizard uses `input()` and blocks execution until the user selects a mode. There is no documented `--non-interactive` flag or environment variable to skip this. When run in CI or headless mode, it fails with `EOF when reading a line`.
**Impact:** All CLI commands fail on first run in non-interactive mode.
**Workaround:** Pipe telemetry mode selection: `echo "3" | gli-flow doctor`

### Issue 5: Repository URL mismatch in documentation

**Severity:** LOW
**File:** `README.md:12`, `docs/setup/installation.md:15,24,61`
**Description:** Documentation references `https://github.com/green-lantern-industries/gli-flow.git` but the actual repository is at `https://github.com/Jegadiswar-SM/gli-flow-asic.git`.
**Impact:** Users following docs exactly will clone the wrong repository.

### Issue 6: PEP 668 / externally-managed-environment

**Severity:** LOW
**Description:** Ubuntu 26.04 ships with PEP 668 protection that blocks `pip install` outside a virtual environment. The docs mention venv as an alternative approach, but the "Quick Install" section still shows bare `pip install -e .` which will fail on modern systems.
**Impact:** Installation fails with `error: externally-managed-environment` on affected systems.
**Workaround:** Use documented venv approach: `python3 -m venv venv && source venv/bin/activate && pip install -e .`

## Issues Fixed

No source code was modified during this audit. All workarounds were applied at the system/configuration level (manual SQL ALTER TABLE, pip install of extras, npm install).

## Dashboard Status

| Component | Status | Detail |
|-----------|--------|--------|
| Backend (port 8000) | OK | FastAPI responds on /health |
| Frontend (port 5173) | OK | React dev server responds |
| /health endpoint | OK | `{"status":"ok","database":true,"tools":{...}}` |

## Telemetry Status

| Check | Status |
|-------|--------|
| Mode | LOCAL |
| Consent | Given |
| Events Collected | 0 |
| Upload Queue DB | Initialized |
| Upload Success Rate | 100% |

## Support Bundle Status

| Check | Status |
|-------|--------|
| Archive created | OK |
| Files included | 5 (config, logs, bundle_data) |
| Logs included | OK |
| Doctor report included | OK (in bundle_data.json as `doctor` key) |

## Database Recovery Status

| Test | Result |
|------|--------|
| Delete gli_flow.db + doctor --fix | FAILED — repair marks migrations as applied without creating tables |
| Delete gli_flow.db + direct migrate_if_needed() | PARTIAL — tables created but schema validation fails (Issue 2) |
| Delete upload_queue.db | PASS — auto-recreated on next `gli-flow run` |

## Success Criteria

| Criterion | Status | Notes |
|-----------|--------|-------|
| Complete uninstall successful | PASS | All artifacts removed |
| Fresh install successful | PASS | Editable install works |
| Doctor passes | FAIL | Schema validation fails (Issue 1 + Issue 2) |
| Database migrates | PARTIAL | Migration runs but schema validation fails |
| Mock run passes | PASS | 42s, QoR 0.6, tapeout ready |
| Dashboard works | PASS | Both backend and frontend (after extras) |
| Telemetry initializes | PASS | Queue, consent, mode all OK |
| Support bundle generates | PASS | 5 files, logs + doctor report |
| Database self-recovers | FAIL | doctor --fix cannot recover from deleted DB |
| No undocumented workarounds | FAIL | Multiple undocumented steps required |

## Verdict

**PARTIAL**

GLI-FLOW passes core workflow tests (install, mock run, dashboard, support bundle, telemetry) but has two blocking issues:

1. **`SchemaMigrationRepair` is broken** — it marks migrations as applied without creating tables, making `doctor --fix` a no-op for database recovery.
2. **Schema validation is over-constrained** — `EXPECTED_COLUMNS` expects columns that migrations never create.

These issues prevent clean first-time setup and disaster recovery from succeeding without manual intervention. The system is functional once these are worked around, but cannot claim "install and run from zero" readiness.
