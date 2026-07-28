# Telemetry and Privacy Guide

GLI-FLOW collects anonymized execution telemetry to improve failure detection, resolution intelligence, and toolchain reliability.

## Telemetry Modes

| Mode | Collection | Upload | Use Case |
|------|-----------|--------|----------|
| `FULL` | ✅ All events | ✅ Upload | Contribute to GLI intelligence |
| `ATLAS` | ✅ Failure events only | ✅ Upload | Share only failure data |
| `LOCAL` | ✅ All events | ❌ No upload | Full insights, no data sent |
| `DISABLED` | ❌ No collection | ❌ No upload | Zero telemetry |

Default: `LOCAL` (non-interactive), user chooses during first run (interactive).

## Consent Workflow

1. First CLI command triggers the telemetry wizard
2. Interactive: prompts "Enable telemetry?" (Y/n)
3. Non-interactive (`--non-interactive`): defaults to LOCAL
4. Saved to `~/.gli-flow/config.yaml`

## Managing Telemetry

```bash
# View current status
gli-flow telemetry status

# Enable collection + upload
gli-flow telemetry enable

# Disable upload (local only)
gli-flow telemetry disable

# Set specific mode
gli-flow telemetry mode full
gli-flow telemetry mode local
gli-flow telemetry mode atlas
gli-flow telemetry mode disabled

# Preview what would be uploaded
gli-flow telemetry preview

# Show payload for a specific run
gli-flow show-telemetry <run_id>

# Export sanitized data
gli-flow telemetry export --format csv

# Via config command
gli-flow config --telemetry on
gli-flow config --telemetry off
```

## Collected Data

- Command invocations (command name, flags, exit code)
- Run metadata (design name, PDK, QoR metrics, WNS, TNS, cell count, utilization, runtime)
- Stage completion status and duration
- Failure classifications (failure type, severity, tool, stage)
- Tool versions (yosys, openroad, magic, netgen, klayout)
- Resolution outcomes

## Data NOT Collected

- RTL source code or Verilog/SystemVerilog files
- Design-identifying information (design name is hashed)
- GDS, DEF, LEF geometry data
- Netlists or gate-level representations
- User environment variables or file paths (sanitized)
- Any proprietary or confidential design data

## Sanitization

All telemetry data passes through a sanitizer that strips:
- RTL, netlists, GDS, DEF, LEF references
- Source code snippets
- User-identifying information
- Absolute file paths

Only safe keys (SAFE/REDACT/HASH classification) are included in uploads.

## Upload Behavior

- Retry: exponential backoff (30s × 2^n), max 10 retries
- Queue: SQLite-backed persistent queue at `~/.gli-flow/upload_queue.db`
- Failed uploads remain queued for retry
- Privacy validation available via API: `GET /telemetry/privacy-validate`

## Viewing Uploaded Data

```bash
# See what will be uploaded
gli-flow telemetry preview

# Export all telemetry
gli-flow telemetry export

# View in dashboard
# Navigate to Telemetry → Upload Preview tab
```

## Opt-out

```bash
gli-flow config --telemetry off
# or
gli-flow telemetry disable
# or
gli-flow telemetry mode disabled
```

## Auditing

All telemetry events are logged to the audit log:

```bash
gli-flow telemetry audit-log
# or via API: GET /telemetry/audit-log
```
