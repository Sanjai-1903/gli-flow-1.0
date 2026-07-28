# Installation Path Audit — v1.0.0

**Date:** 2026-06-15
**Scope:** Every documented installation method for GLI-FLOW validated from scratch

---

## Path 1: `pip install gli-flow`

**Status:** ❌ REMOVED — no longer documented

**Documented in (before fix):** `docs/guides/installation_guide.md`, `docs/setup/installation.md`

**What fails:** No package named `gli-flow` exists on PyPI.

**Error:**
```
ERROR: Could not find a version that satisfies the requirement gli-flow
ERROR: No matching distribution found for gli-flow
```

**Root cause:** Package has never been published to PyPI. This was an aspirational install path.

**Fix:** Removed from all documentation. Only source install is supported.

---

## Path 2: `scripts/install.sh`

**Status:** ✅ FIXED

**Documented in:** `README.md`, `docs/guides/installation_guide.md`

**Before fix:** Line 193 executed `pip install "gli-flow[install]"` which failed because the package is not on PyPI.

**Error (before fix):**
```
✗ gli-flow installation failed.
  Try: pip install gli-flow
```

**Root cause:** Script assumed PyPI availability.

**Fix applied:**
- Script now detects it's running from within the cloned repo
- Uses `pip install -e "$REPO_DIR"` to install from source
- Validates `setup.py` exists before attempting installation
- Provides clear PATH guidance if `gli-flow` command not found after install
- Verifies CLI works after installation

---

## Path 3: `pip install -e .`

**Status:** ✅ VERIFIED WORKING

**Steps:**
```bash
git clone https://github.com/Jegadiswar-SM/gli-flow-asic.git
cd gli-flow-asic
python3 -m venv venv
source venv/bin/activate
pip install -e .
gli-flow install
```

**Result:** Installs successfully. Dependencies pulled: `rich`, `pyyaml`, `jinja2`, `tabulate`.

**`click` dependency removed:** Previously `click` was listed in `setup.py` but the CLI uses `argparse`. Removed.

**Post-install verification:** `gli-flow --help` works immediately within the venv.

**PATH requirement:** If installed without a venv, `~/.local/bin` must be on PATH. Guidance added to README and install script.

---

## Path 4: Docker

**Status:** ⚠️ WORKS LOCALLY, image not published

**Steps:**
```bash
git clone https://github.com/Jegadiswar-SM/gli-flow-asic.git
cd gli-flow
docker build -t gli-flow:local .
docker run -it --rm -v "$(pwd):/workspace" gli-flow:local
```

**What works:** Dockerfile builds successfully. Includes EDA tools (Yosys, OpenROAD, KLayout, Magic, Netgen, sky130 PDK).

**What's missing:** No Docker image is published to GHCR or Docker Hub. The README referenced `ghcr.io/gli-flow/gli-flow:latest` which does not exist.

**Fix:** Removed references to non-existent Docker images from documentation. Users can build locally.

---

## Path 5: `docs/setup/installation.md`

**Status:** ❌ REMOVED — FIXED

**Before fix:** Referenced:
- `pip install -r requirements.txt` — `requirements.txt` does not exist
- `./install/install.sh` — references wrong path
- `python3 environment/validation/validate_environment.py` — script does not exist
- Docker as mandatory prerequisite — not required

**Fix applied:** Rewritten to match the source-install-only reality.

---

## Path 6: `docs/guides/installation_guide.md`

**Status:** ❌ REMOVED — FIXED

**Before fix:** Referenced:
- `pip install gli-flow` — not on PyPI
- `pip install gli-flow==1.2.0` — not on PyPI
- `curl -fsSL https://raw.githubusercontent.com/.../install.sh | bash` — script would fail on PyPI lookup
- Docker image at `ghcr.io/gli-flow/gli-flow:latest` — does not exist

**Fix applied:** Rewritten to match the source-install-only reality. Only two paths documented: source install and Docker build.

---

## Path 7: `README.md` Quick Start

**Status:** ❌ REMOVED — FIXED

**Before fix:** The Quick Start section showed `gli-flow quickstart` as the first step, which requires successful installation first — a circular dependency.

**Fix applied:** Quick Start now shows the correct order: clone → pip install → verify → run.

---

## Path 8: Aspirational Commands in Troubleshooting Guide

**Status:** ❌ REMOVED — FIXED

**Before fix:** The troubleshooting guide referenced these non-existent commands:
- `gli-flow pdk setup` — does not exist
- `gli-flow support bundle` — actual command is `gli-flow support-bundle`
- `gli-flow debug lvs` — does not exist
- `gli-flow db check` — does not exist
- `gli-flow db restore` — does not exist
- `gli-flow db reset` — does not exist
- `gli-flow db` — exists but with different subcommands

**Fix applied:** Troubleshooting guide rewritten — all commands verified against actual CLI help output.

---

## Path 9: Unused `click` Dependency

**Status:** ✅ FIXED

**Issue:** `setup.py` listed `click>=8.1.0` as a core dependency. The CLI uses `argparse` exclusively — `click` is never imported anywhere in the codebase.

**Impact:** Unnecessary 250KB+ download, potential version conflicts.

**Fix:** Removed `click` from `setup.py` `install_requires`.

---

## Summary

| Install Path | Before | After |
|---|---|---|
| `pip install gli-flow` | Documented but broken | Removed from docs |
| `scripts/install.sh` | Broken (PyPI dependency) | Fixed (source install) |
| `pip install -e .` | Undocumented but working | Now the primary documented path |
| Docker local build | Working but undocumented | Documented |
| Docker published image | Referenced but doesn't exist | Removed from docs |
| `docs/setup/installation.md` | Multiple dead ends | Rewritten to match reality |
| `docs/guides/installation_guide.md` | PyPI/curl/Docker aspirational | Rewritten |
| `README.md` Quick Start | Circular (requires install first) | Fixed (install-first order) |
| `setup.py click` dependency | Unused 250KB | Removed |
