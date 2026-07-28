# GPL Compliance Report

**Date:** 2026-06-02
**Audited by:** Open-Source Compliance Auditor
**Repository:** GLI-FLOW-ASIC
**License:** Apache 2.0

---

## Summary

**Verdict: COMPLIANT** — No GPL code is linked, embedded, or derived from. All EDA tools are invoked as external subprocesses.

---

## Repository License

- **LICENSE file:** Apache License, Version 2.0
- **setup.py:** Explicitly declares `license="Apache-2.0"`
- **README.md:** States "Apache 2.0"
- **USER_MANUAL.md:** States "Apache 2.0 — Green Lantern Industries"

---

## Third-Party EDA Tools Audit

| Tool | License | Usage | GPL Risk |
|------|---------|-------|----------|
| **Yosys** | ISC (permissive) | Subprocess: `subprocess.run(["yosys", ...])` | None |
| **OpenROAD** | BSD-3-Clause | Subprocess: `subprocess.run(["openroad", ...])` | None |
| **OpenSTA** | GPL-3.0 | **Never invoked directly.** Listed only as APT conflict package removed during OpenROAD install. | None |
| **Magic** | BSD-3-Clause | Subprocess: `subprocess.run(["magic", ...])` | None |
| **Netgen** | BSD-3-Clause | Subprocess: `subprocess.run(["netgen", ...])` | None |
| **KLayout** | GPL-2.0+ (with toolkit exception) | Subprocess: `subprocess.run(["klayout", ...])` invoked for DRC via `_run_klayout_drc()` at `openroad_adapter.py:639`. Subprocess invocation (not linking) is the GPL compliance strategy — calling a GPL binary via subprocess does not create a derivative work under applicable legal interpretations. This interpretation should be confirmed by counsel. | None |

### Key Finding: OpenSTA

OpenSTA (GPL-3.0) is **not linked, imported, or invoked** by any gli-flow Python code. The single reference is:

- `gli_flow/installer/openroad.py:114`: `conflicts = ["opensta"]` — this is an apt package conflict list that removes `opensta` during OpenROAD installation to prevent package conflicts.

---

## Dependency License Audit (Python Packages)

| Package | License | Risk |
|---------|---------|------|
| click | BSD-3-Clause | None |
| rich | MIT | None |
| pyyaml | MIT | None |
| jinja2 | BSD-3-Clause | None |
| tabulate | MIT | None |
| pytest | MIT | None |
| fastapi | MIT | None |
| uvicorn | BSD-3-Clause | None |
| pydantic | MIT | None |
| boto3 | Apache-2.0 | None |
| google-cloud-storage | Apache-2.0 | None |

All dependencies are permissively licensed (MIT, BSD, Apache). **No GPL dependencies.**

---

## Vendored Code Audit

- **No GPL-licensed code** is vendored in `gli_flow/`.
- The `examples/mini_mac/rtl/core/ibex/` directory contains third-party IP (Apache 2.0, BSD, CC0) — these are example designs, not part of the gli-flow source.
- All third-party code in `examples/` maintains its own license files.

---

## Methodology

1. Grep for `GPL|LGPL|AGPL|General Public License` across all `.py`, `.md`, `.tcl`, and `.json` files in `gli_flow/`.
2. Grep for `import.*opensta\|from.*opensta\|import.*yosys\|from.*yosys` in `gli_flow/`.
3. Manual review of all `subprocess.*run` and `subprocess.*Popen` calls to verify subprocess-only usage.
4. Manual review of `setup.py` dependencies against [SPDX License List](https://spdx.org/licenses/).
5. File-by-file check of `examples/` vendored code licenses.

---

## Conclusion

**GLI-FLOW-ASIC is fully GPL-compliant.** No GPL code is linked, imported, statically embedded, or derived from. All EDA tools (Yosys, OpenROAD, Magic, Netgen, KLayout) are invoked as external subprocesses, which does not trigger GPL copyleft requirements.
