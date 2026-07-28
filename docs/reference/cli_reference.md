# CLI Reference

Generated from `gli_flow/cli/main.py` — every documented command.

## Global Flags

| Flag | Description |
|------|-------------|
| `--non-interactive` | Run in non-interactive mode (telemetry defaults to LOCAL) |

## Production Commands

### `gli-flow run <design>`

Run a design through the full RTL-to-GDS pipeline.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `design` | positional | required | Path to design directory with `gli_manifest.yaml` |
| `--verbose`, `-v` | flag | false | Show full traceback on error |
| `--threads`, `-j` | int | — | Number of parallel threads |
| `--memory`, `-m` | int | — | Memory limit in MB |
| `--orfs-root` | str | — | OpenROAD-flow-scripts path |
| `--mock` | flag | false | Run with mock EDA adapter |
| `--db-path` | str | — | SQLite database path |

**Examples:**
```bash
gli-flow run examples/counter
gli-flow run designs/my_chip --threads 4
gli-flow run . --mock    # dry run without real tools
```

### `gli-flow history`

Show execution history.

| Flag | Default | Description |
|------|---------|-------------|
| `--limit` | 20 | Number of runs to show |
| `--db-path` | — | Database path |

### `gli-flow status`

Show recent run status (last 10 runs).

| Flag | Description |
|------|-------------|
| `--db-path` | Database path |

### `gli-flow batch <designs...>`

Run multiple designs in parallel.

| Flag | Default | Description |
|------|---------|-------------|
| `--parallel`, `-j` | 1 | Number of parallel workers |
| `--threads` | — | Threads per worker |
| `--memory` | — | Memory limit per worker (MB) |

### `gli-flow init <design_name>`

Create a new design manifest.

| Flag | Description |
|------|-------------|
| `--rtl-dir` | Path to RTL directory (auto-detect top, ports, files) |
| `--rtl` | Path to single RTL file (auto-detect top and ports) |

### `gli-flow quickstart`

Interactive setup wizard for new designs. No flags.

### `gli-flow install`

Install gli-flow and all EDA toolchain dependencies.

| Flag | Default | Choices | Description |
|------|---------|---------|-------------|
| `--pdk` | `sky130` | sky130, gf180mcu | PDK to install |
| `--pdk-root` | `~/.gli-flow/pdk` | | PDK install root |
| `--orfs-root` | `~/.gli-flow/orfs` | | ORFS install path |
| `--skip-orfs` | false | | Skip ORFS installation |
| `--force`, `-f` | false | | Reinstall if already present |
| `--dry-run`, `-n` | false | | Preview without changes |
| `--skip-system` | false | | Skip system package installation |
| `--skip-pdk` | false | | Skip PDK installation |
| `--verbose`, `-v` | false | | Show detailed info |

### `gli-flow doctor`

Validate installed EDA toolchain and produce health report.

| Flag | Description |
|------|-------------|
| `--fix` | Attempt to auto-repair detected issues |
| `--repair-magic` | Repair broken magic binary shadowing |
| `--db-path` | Database path |
| `--verbose`, `-v` | Show detailed discovery |

### `gli-flow diagnose <run_id>`

Diagnose a failed run by scanning stage logs.

| Flag | Description |
|------|-------------|
| `--db-path` | Database path |
| `--verbose`, `-v` | Show detailed diagnosis |

### `gli-flow report [design] [platform]`

Show QoR report for a completed ORFS run.

| Flag | Default | Description |
|------|---------|-------------|
| `--platform`, `-p` | — | Platform name |
| `--orfs-root` | — | ORFS flow root path |

### `gli-flow ci <design>`

Run a design in CI mode with JUnit/Markdown output.

| Flag | Description |
|------|-------------|
| `--junit` | Path to write JUnit XML report |
| `--markdown` | Path to write Markdown report |
| `--baseline` | Baseline run ID for comparison |
| `--qor-min` | Minimum acceptable QoR score |
| `--wns-max` | Maximum acceptable WNS (ns) |
| `--verbose`, `-v` | Show verbose output |
| `--db-path` | Database path |

### `gli-flow config`

View or change GLI-FLOW configuration.

| Flag | Choices | Description |
|------|---------|-------------|
| `--telemetry` | on, off | Enable or disable telemetry |

### `gli-flow db <subcommand>`

Database schema management.

| Subcommand | Description |
|------------|-------------|
| `status` | Show migration state |
| `migrate` | Apply pending migrations |
| `repair` | Repair schema version tracking |
| `path` | Show database file path and size |

All subcommands accept `--db-path`.

### `gli-flow reset-runs`

Permanently delete all run history, telemetry, and dashboard data.
Interactive — prompts for confirmation.

| Flag | Description |
|------|-------------|
| `--db-path` | Database path |
| `--verbose`, `-v` | Show detailed reset information |

### `gli-flow support-bundle`

Generate a support bundle archive for debugging.

| Flag | Description |
|------|-------------|
| `--output`, `-o` | Output path for the ZIP archive |
| `--run-id` | Include specific run ID's artifacts |
| `--db-path` | Database path |

### `gli-flow smoke-test`

Validate installation and environment readiness.

| Flag | Description |
|------|-------------|
| `--db-path` | Database path |

Checks: Python version, EDA tools (openroad, yosys, magic, netgen, klayout, sv2v), database schema, telemetry configuration, dashboard dependencies, and example design validity.

**Examples:**
```bash
gli-flow smoke-test
gli-flow smoke-test --db-path /custom/path/gli_flow.db
```

### `gli-flow setup`

Interactive first-time setup — configure PDK, tools, workspace.

| Flag | Choices | Description |
|------|---------|-------------|
| `--pdk-root` | | PDK install root directory |
| `--workspace` | | Workspace directory for designs and runs |
| `--telemetry` | on, off | Telemetry consent |
| `--non-interactive` | | Skip prompts, use defaults or flags |

### `gli-flow show-telemetry <run_id>`

Show exact telemetry payload that would be uploaded (no data sent).

| Flag | Description |
|------|-------------|
| `--db-path` | Database path |

## Experimental Commands

### `gli-flow remote [design]`

Run a design on a remote machine via SSH.

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--host` | ✅ | | Remote hostname or IP |
| `--port` | | 22 | SSH port |
| `--user` | | | SSH user |
| `--key` | | | SSH private key path |
| `--gli-flow-path` | | `gli-flow` | Path on remote |
| `--work-dir` | | | Working directory on remote |
| `--check` | | false | Test SSH connection only |

### `gli-flow cloud <action>`

Upload/download/list run artifacts to/from cloud storage.

| Action | Description |
|--------|-------------|
| `upload <run_id>` | Upload run artifacts |
| `download <run_id>` | Download run artifacts |
| `list` | List cloud artifacts |

Flags: `--dir`, `--provider` (s3/gcs), `--bucket`, `--prefix`

### `gli-flow dashboard`

Start the GLI-FLOW dashboard (backend + frontend).

| Flag | Description |
|------|-------------|
| `--backend-only` | Start backend only, skip frontend |

### `gli-flow upgrade-check`

Check for newer versions of GLI-FLOW on PyPI and GitHub. No flags.

### `gli-flow investigate <run_id>`

Run LLM investigation on a failed run (Tier 2 — Experimental).

| Flag | Description |
|------|-------------|
| `--db-path` | Database path |
| `--verbose`, `-v` | Show detailed investigation |

### `gli-flow investigate-migrate [run_id]`

Restore failed investigations from backup.

### `gli-flow ai-assist`

AI Investigation Assistant — analyze unknown failures.

| Flag | Description |
|------|-------------|
| `--failure-type` | Failure type classification |
| `--signature` | Failure signature string |
| `--severity` | Failure severity (default: MEDIUM) |
| `--confidence` | Classification confidence (0.0-1.0) |
| `--tool` | EDA tool that failed |
| `--stage` | Pipeline stage at failure |
| `--error-text` | Error text from the run |
| `--log-snippet` | Log snippet |
| `--run-id` | Run ID for context |
| `--db-path` | Database path |
| `--feedback <id>` | Record or view feedback |
| `--helpful` | Mark feedback as helpful |
| `--not-helpful` | Mark feedback as not helpful |
| `--resolved` | Mark issue as resolved |
| `--did-not-resolve` | Mark issue as not resolved |

### `gli-flow escalate`

Community Intelligence — escalate unknown failure to GLI engineers.

| Flag | Description |
|------|-------------|
| `--failure-type` | Failure type classification |
| `--signature` | Failure signature string |
| `--severity` | Failure severity (default: MEDIUM) |
| `--confidence` | Classification confidence (0.0-1.0) |
| `--tool` | EDA tool that failed |
| `--stage` | Pipeline stage |
| `--error-text` | Error text |
| `--run-id` | Run ID for context |
| `--db-path` | Database path |
| `--consent` | Confirm consent to share sanitized data |
| `--submit` | Submit the escalation (requires --consent) |
| `--notes` | Additional notes for engineers |
| `--feedback <id>` | View an escalation by ID |

### `gli-flow telemetry <subcommand>`

Telemetry Operations Center.

| Subcommand | Description |
|------------|-------------|
| `status` | Show telemetry mode, consent, events collected |
| `enable` | Set mode to FULL, consent to True |
| `disable` | Set mode to LOCAL, consent to False |
| `mode [full\|atlas\|local\|disabled]` | Show or set telemetry mode |
| `preview` | Show next upload payload as formatted JSON |
| `export` | Export sanitized telemetry (JSON or CSV) |
| `replay <file>` | Replay a telemetry export file |
| `health` | Show telemetry pipeline health |
| `snapshot` | Create dataset snapshot for AI training |
| `audit-log` | Show telemetry audit log entries |

### `gli-flow warehouse <subcommand>`

Telemetry Intelligence Warehouse.

| Subcommand | Description |
|------------|-------------|
| `status` | Warehouse entries count and fix rate |
| `coverage` | Failure Atlas coverage by domain |
| `quality` | Intelligence quality score |
| `correlations` | Discovered failure→root-cause→resolution chains |
| `snapshot` | Create knowledge graph snapshot |

### `gli-flow predict <run_id>`

Predict execution risk and tapeout readiness.
**Note:** Defined in parser but not wired in dispatch.

## Custom Help Epilog

Common Workflows:
```
First Time:
  gli-flow smoke-test          Verify installation
  gli-flow doctor              Detailed environment check
  gli-flow run counter         Run your first design

Investigate Failure:
  gli-flow diagnose <run>      Analyze a failed run
  gli-flow investigate <run>   Deep AI investigation

Telemetry:
  gli-flow telemetry status    View telemetry status

Support:
  gli-flow support-bundle      Generate debug archive
```
