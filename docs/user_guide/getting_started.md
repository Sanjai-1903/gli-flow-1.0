# Getting Started

Clone to dashboard. Mock mode requires no EDA tools.

**Prerequisites:** Python 3.9+, Linux (Ubuntu 22.04+ / Debian 12+ / WSL2), git

---

## 1. Clone and Install

```bash
git clone https://github.com/Jegadiswar-SM/gli-flow-asic.git
cd gli-flow-asic
python3 -m venv venv
source venv/bin/activate
pip install -e .
gli-flow install
```

`gli-flow install` installs the PDK (sky130A), OpenROAD-flow-scripts (ORFS), and dashboard
dependencies. EDA tools (Yosys, OpenROAD, Magic, Netgen, KLayout) must be pre-installed
— see `gli-flow doctor` to check. On Ubuntu: `apt install yosys openroad magic netgen klayout`.

## 2. Verify

```bash
gli-flow smoke-test
```

Checks Python version, EDA tools, database schema, telemetry config, and the example
design. All checks pass when GLI-FLOW is ready.

For detailed environment info: `gli-flow doctor`

## 3. Run Your First Design

```bash
gli-flow run examples/counter --mock
```

This runs the full pipeline in mock mode — no EDA tools needed. Expect:

```
  Metric        Value
─────────────────────
  QoR Score     0.6
  WNS           0.05
  TNS           0.0
  Utilization   65.0%
  Cell Count    100
  Runtime       42.0s

✓ Implementation: SUCCESS
✓ Signoff: PASS
✓ Tapeout Ready: YES
```

## 4. Open the Dashboard

```bash
gli-flow dashboard
```

Opens at `http://127.0.0.1:5173`. Browse run results, timing, area, DRC/LVS, and
telemetry. Use `gli-flow dashboard --backend-only` for the API server only at
`http://127.0.0.1:8000`.

---

**RTL/IP never collected:** GLI-FLOW's telemetry explicitly excludes RTL source code,
GDS, netlists, and constraints. Verified in the telemetry collection code. Default
mode is local-only. See [Telemetry & Privacy](../privacy/telemetry_and_privacy.md).

## Beta Scope

**Included:** Open-source ASIC implementation flow (Yosys + OpenROAD + Magic + KLayout),
mock mode, web dashboard, Failure Atlas, opt-in telemetry, Supabase cloud storage.

**Not included:** Commercial EDA tools, tapeout certification, guaranteed tapeout
outcomes, production signoff guarantees, enterprise features, multi-user platform.

## What's Next?

- [User Manual](user_manual.md) — install, run, diagnose, telemetry
- [Dashboard Guide](dashboard.md) — dashboard pages and features
- [CLI Reference](../reference/cli_reference.md) — every command
- [Troubleshooting](../reference/troubleshooting.md) — common issues
