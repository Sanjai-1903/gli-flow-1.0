# CLI Command Inventory

**Generated:** 2026-06-12  
**Version:** v1.0.0  
**Entrypoint:** `gli_flow.cli.main:main` (registered via `setup.py` console_scripts)  
**Parser:** `argparse` via `build_parser()` at `gli_flow/cli/main.py:1612`  
**Handler file:** All handlers in `gli_flow/cli/main.py`  

---

## Complete Command Table

| # | Command | Handler | Line | Subcommands | Args |
|---|---------|---------|------|-------------|------|
| 1 | `run` | `run_command` | 442 | — | `design`, `--verbose`, `--threads`, `--memory`, `--orfs-root`, `--mock`, `--db-path` |
| 2 | `history` | `history_command` | 519 | — | `--limit`, `--db-path` |
| 3 | `status` | `status_command` | 529 | — | `--db-path` |
| 4 | `batch` | `batch_command` | 539 | — | `designs` (nargs+), `--parallel`, `--threads`, `--memory` |
| 5 | `init` | `init_command` | 1084 | — | `design_name`, `--rtl-dir`, `--rtl` |
| 6 | `quickstart` | `quickstart_command` | 1138 | — | (none) |
| 7 | `report` | `report_command` | 734 | — | `design`, `platform`, `orfs_root`, `--platform`, `--orfs-root` |
| 8 | `install` | `install_command` | 587 | — | `--pdk`, `--pdk-root`, `--orfs-root`, `--skip-orfs`, `--force`, `--dry-run`, `--skip-system`, `--skip-pdk` |
| 9 | `ci` | `ci_command` | 773 | — | `design`, `--junit`, `--markdown`, `--baseline`, `--qor-min`, `--wns-max`, `--verbose` |
| 10 | `remote` | `remote_command` | 943 | — | `design`, `--host`, `--port`, `--user`, `--key`, `--gli-flow-path`, `--work-dir`, `--check` |
| 11 | `cloud` | `cloud_command` | 978 | `upload`, `download`, `list` | `run_id`, `--dir`, `--provider`, `--bucket`, `--prefix` |
| 12 | `doctor` | `doctor_command` | 904 | — | `--fix`, `--repair-magic`, `--db-path` |
| 13 | `reset-runs` | `reset_runs_command` | 185 | — | `--db-path` |
| 14 | `db` | `db_command` | 121 | `status`, `migrate`, `repair`, `path` | `--db-path` |
| 15 | `diagnose` | `diagnose_command` | 1208 | — | `run_id`, `--db-path` |
| 16 | `show-telemetry` | `show_telemetry_command` | 1309 | — | `run_id`, `--db-path` |
| 17 | `config` | `config_command` | 1601 | — | `--telemetry` |
| 18 | `dashboard` | `dashboard_command` | 396 | — | `--backend-only` |
| 19 | `setup` | `setup_command` | 1391 | — | `--pdk-root`, `--workspace`, `--telemetry`, `--non-interactive` |
| 20 | `support-bundle` | `support_bundle_command` | 1484 | — | `--output`, `--run-id`, `--db-path` |
| 21 | `upgrade-check` | `upgrade_check_command` | 1560 | — | (none) |

---

## Dispatch Architecture

```
main()  (line 1780)
  ├── build_parser()  (line 1612) — constructs argparse tree
  ├── parser.parse_args()
  └── if/elif chain (21 branches) routing args.command → handler
```

Subcommand dispatch for `cloud` uses `args.action` (upload/download/list).  
Subcommand dispatch for `db` uses `args.db_action` (status/migrate/repair/path).

---

## Output Layer

All display logic: `gli_flow/cli/output.py` (225 lines)  
Uses `rich` library (Console, Table, Panel, Layout, Columns).

---

## Core Dependencies

| Module | File | Lines | Role |
|--------|------|-------|------|
| `FlowOrchestrator` | `core/orchestrator.py` | 1274 | Run execution engine |
| `DatabaseManager` | `database/sqlite.py` | 301 | DB abstraction layer |
| `MigrationEngine` | `database/migrations.py` | 392 | Schema migration engine |
| `EnvironmentValidator` | `infrastructure/environment_validator.py` | 298 | System health checks |
| `Installer` | `installer/installer.py` | 292 | Tool/PDK installer |
| `JobQueue` | `scheduler/queue.py` | 142 | Threaded batch scheduler |
| `RemoteWorker` | `scheduler/remote.py` | 113 | SSH execution |
| `CloudStorageManager` | `cloud/storage.py` | 205 | S3/GCS abstraction |
| `CIRunner` | `ci/runner.py` | 148 | CI pipeline runner |
| `RepairActions` | `infrastructure/repair_actions.py` | 345 | Auto-repair system |
| `doctor` | `doctor.py` | 384 | Tool health verification |
| `rtl_parser` | `parser/rtl_parser.py` | 202 | Verilog/SV parsing |
| `config_validator` | `config_validator.py` | 85 | Manifest validation |
| `Runner` | `runner.py` | 69 | LibreLane runner |

Total implementation: **6,310 lines** across core modules, **1,832 lines** in CLI handler file.
