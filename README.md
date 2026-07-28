# GLI-FLOW

Open-source RTL-to-GDS digital design flow — one command from Verilog to GDSII.

GLI-FLOW orchestrates Yosys, OpenROAD, Magic, Netgen, and KLayout through synthesis,
floorplanning, placement, CTS, routing, DRC/LVS, STA, and GDS export. Mock mode
validates your design config in seconds without any EDA tools installed.

## Why GLI-FLOW?

- **One command.** `gli-flow run <design>` runs the complete flow end-to-end.
- **Mock mode.** Develop and validate manifests without the EDA toolchain.
- **Built-in diagnostics.** Automated failure detection, root-cause analysis, and support bundles.
- **Dashboard.** Web UI for run history, timing/area/power, DRC/LVS, and telemetry.
- **Privacy-first.** Default local-only telemetry. RTL, GDS, and netlists are never collected.

## Quick Install

```bash
git clone https://github.com/Jegadiswar-SM/gli-flow-asic.git
cd gli-flow-asic
python3 -m venv venv
source venv/bin/activate
pip install -e .
gli-flow install
```

Python 3.9+. Linux (Ubuntu 22.04+ / Debian 12+ / WSL2).

## Quick Start

```bash
# Verify installation
gli-flow doctor

# First run (mock mode, no EDA tools required)
gli-flow run examples/counter --mock

# Launch dashboard
gli-flow dashboard
```

## Dashboard

```bash
gli-flow dashboard
```

Opens at `http://127.0.0.1:5173`. The backend starts automatically.
Use `--backend-only` for API at `http://127.0.0.1:8000`.

## Features

- Full RTL-to-GDS pipeline — synthesis, placement, routing, DRC, LVS, STA
- Mock mode — validate config without tools
- Web dashboard — run history, metrics, telemetry
- Automated failure detection with fix recommendations
- AI-assisted investigation (experimental — requires external API key)
- CI mode with JUnit/Markdown output
- Support bundles for issue reports

## Documentation

| Link | Contents |
|------|----------|
| [Getting Started](docs/user_guide/getting_started.md) | Clone to dashboard step-by-step |
| [User Manual](docs/user_guide/user_manual.md) | Install, run, diagnose, telemetry |
| [Dashboard Guide](docs/user_guide/dashboard.md) | Dashboard pages reference |
| [CLI Reference](docs/reference/cli_reference.md) | Every command and flag |
| [Troubleshooting](docs/reference/troubleshooting.md) | Common issues |
| [Telemetry & Privacy](docs/privacy/telemetry_and_privacy.md) | Data handling and consent |

## Current Beta Scope

**Included:**
- Open-source ASIC implementation flow (Yosys + OpenROAD + Magic + KLayout)
- Mock mode for config validation
- Execution observability and Failure Atlas
- Opt-in telemetry collection (RTL/IP never collected)
- Web dashboard

**Not included:**
- Commercial EDA tools (Synopsys, Cadence, Siemens)
- Tapeout certification or guaranteed tapeout outcomes
- Production signoff guarantees
- Enterprise collaboration features
- Multi-user cloud platform

GLI-FLOW is v1.1.0-beta. Report issues at https://github.com/Jegadiswar-SM/gli-flow-asic/issues.

## License

Apache 2.0 — see [LICENSE](LICENSE).
