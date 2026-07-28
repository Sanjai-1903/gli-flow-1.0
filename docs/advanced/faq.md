# Frequently Asked Questions

**Do I need EDA tools to try GLI-FLOW?**
No. Mock mode runs the full pipeline without tools.

**What PDKs are supported?**
sky130A (tested), gf180mcuD (partial), IHP SG13G2 (planned).

**What designs have been tested?**
counter (~500 cells), uart (~2,000 cells), gcd (~500 cells), systolic array (~15,000 cells), PicoRV32 (~50,000 cells).

**Does GLI-FLOW upload my designs?**
No. RTL, netlists, GDS, and constraints are never uploaded regardless of telemetry mode.

**Can I use GLI-FLOW offline?**
Yes. Default telemetry mode is local-only.

**How do I report a bug?**
Run `gli-flow support-bundle` and attach the `.zip` to https://github.com/Jegadiswar-SM/gli-flow-asic/issues.
