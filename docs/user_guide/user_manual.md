# User Manual

If you haven't run anything yet, start with [Getting Started](getting_started.md).
This manual covers how to install, run designs, open the dashboard, diagnose failures,
generate support bundles, and how telemetry works.

---

## How Do I Install?

```bash
git clone https://github.com/Jegadiswar-SM/gli-flow-asic.git
cd gli-flow-asic
python3 -m venv venv
source venv/bin/activate
pip install -e .
gli-flow install
```

Dashboard dependencies are installed automatically by `gli-flow install`.

EDA toolchain + PDK installation (for real ASIC runs, not mock mode):

```bash
gli-flow install
```

This installs the sky130 PDK and OpenROAD Flow Scripts. Supported PDKs: `sky130`
(fully tested), `gf180mcu` (partial). See `gli-flow install --help` for options.

**Smoke test** after install to verify everything works:

```bash
gli-flow smoke-test
```

---

## How Do I Run a Design?

Every design needs a directory with RTL files and a `gli_manifest.yaml`.

Create a new design:

```bash
gli-flow init my_chip
# Or with auto-detection from existing RTL:
gli-flow init my_chip --rtl-dir src/rtl
```

Run in mock mode (no tools needed) to validate:

```bash
gli-flow run my_chip --mock
```

Run with real EDA tools:

```bash
gli-flow run my_chip
```

The manifest (gli_manifest.yaml) specifies RTL files, top module, clock, PDK, and
constraints. See `examples/counter/gli_manifest.yaml` as a reference.

### Common Run Options

| Flag | Description |
|------|-------------|
| `--mock` | Run without EDA tools |
| `--threads, -j N` | Parallel thread count |
| `--memory, -m N` | Memory limit in MB |

### Run History

```bash
gli-flow history              # Show recent 20 runs
gli-flow history --limit 50   # Show more
```

---

## How Do I Open the Dashboard?

```bash
gli-flow dashboard
```

Opens the full web UI at `http://127.0.0.1:5173`. If npm is unavailable or you only
need the API:

```bash
gli-flow dashboard --backend-only
```

The backend API is at `http://127.0.0.1:8000`.

The dashboard shows: run history, timing/area/power results, DRC/LVS violations,
Failure Atlas, telemetry, and settings.

See the [Dashboard Guide](dashboard.md) for page-by-page documentation.

---

## How Do I Diagnose a Failure?

```bash
gli-flow diagnose <run_id>
```

Scans run logs for known failure patterns (DRC violations, LVS mismatches, timing
violations, OOM kills, missing modules) and prints the likely cause and fix.

For deeper investigation (requires an AI provider):

```bash
gli-flow investigate <run_id>
```

Find run IDs via `gli-flow history`.

---

## How Do I Generate a Support Bundle?

```bash
gli-flow support-bundle
```

Creates `gli-flow-support-bundle-<timestamp>.zip` containing: GLI-FLOW version,
last 20 runs, system info, config, tool versions, and doctor output. Attach this
file when reporting issues.

Include a specific run's logs (RTL/netlists/GDS excluded):

```bash
gli-flow support-bundle --run-id run_abc123
```

---

## How Does Telemetry Work?

### Modes

| Mode | Collection | Upload | Use Case |
|------|-----------|--------|----------|
| `FULL` | All events | Uploaded | Contribute to GLI intelligence |
| `ATLAS` | Failure events only | Uploaded | Share only failure data |
| `LOCAL` (default) | All events | Never uploaded | Full insights, no data sent |
| `DISABLED` | None | Never uploaded | Zero telemetry |

### Commands

```bash
gli-flow telemetry status       # View current settings
gli-flow telemetry enable       # Enable full collection + upload
gli-flow telemetry disable      # Disable uploads
gli-flow telemetry mode local   # Keep everything local
gli-flow telemetry preview      # View what would be uploaded
gli-flow show-telemetry <id>    # Payload for a specific run
```

### Privacy Commitment

**RTL source code, Verilog/SystemVerilog files, GDS, DEF, LEF, netlists, SDC
constraints, and design-identifying data are never collected** — regardless of
telemetry mode. This has been verified in the telemetry collection code
(`failure_atlas/community_intelligence/export.py`), which explicitly blocks all
IP-bearing file extensions and fields before any data leaves the machine.

All telemetry passes through a privacy validator. Preview the exact payload before
any upload with `gli-flow telemetry preview`.

Default mode is LOCAL — no data leaves your machine without explicit consent.

See the [Telemetry & Privacy guide](../privacy/telemetry_and_privacy.md) for full
details.

---

## See Also

- [Getting Started](getting_started.md)
- [Dashboard Guide](dashboard.md)
- [CLI Reference](../reference/cli_reference.md)
- [Troubleshooting](../reference/troubleshooting.md)
- [Known Limitations](KNOWN_LIMITATIONS.md)
