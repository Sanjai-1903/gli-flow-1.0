# GLI-FLOW Fresh Clone Certification Audit (v1)

**Audit Date:** 2026-06-17  
**Repository Commit:** 78181bc  
**Auditor:** Gemini CLI  
**Environment:** Linux (WSL2), Python 3.10.12  

---

## 1. Executive Summary

The GLI-FLOW installation and onboarding experience is generally smooth and functional. All core commands work as expected, and the "Manual Installation" path is reliable. However, there are minor friction points in usability and documentation accuracy that could confuse new users.

**Verdict: CERTIFIED** (with minor recommendations)

---

## 2. Success/Failure Matrix

| Step | Command | Status | Notes |
|------|---------|--------|-------|
| Clean Environment | `python3 -m venv venv` | PASS | |
| Installation | `pip install -e .` | PASS | Dependencies installed correctly. |
| Basic Help | `gli-flow --help` | PASS | |
| Environment Check | `gli-flow doctor` | PASS | Accurately detected tools and PDK. |
| Design Run | `gli-flow run examples/counter --mock` | PASS | Successful mock run. |
| Dashboard (Backend) | `gli-flow dashboard --backend-only` | PASS | Port 8000 active. |
| Dashboard (Full) | `gli-flow dashboard` | PASS | Port 5173 active (Vite). |
| Telemetry | `gli-flow telemetry status` | PASS | |
| Support Bundle | `gli-flow support-bundle` | PASS | Generated zip with 2 files. |

---

## 3. Issues and Observations

### [MEDIUM] `gli-flow run counter` Usability Friction
- **Issue:** Running `gli-flow run counter` fails if the user is not in the `examples/` directory.
- **Expected:** The tool should likely search for designs in common locations (like `./designs/` or `./examples/`) if a relative path is not found.
- **Impact:** First-time users might be confused when following a simplified command.

### [MEDIUM] `scripts/install.sh` Misleading Name
- **Issue:** The script only performs validation and does not install any software.
- **Expected:** A script named `install.sh` should handle dependency installation or environment setup.
- **Impact:** Users expecting an automated install will be disappointed.

### [LOW] Dashboard Port Mismatch
- **Issue:** Documentation (`docs/setup/installation.md`) states the dashboard opens at `http://127.0.0.1:8000`, but the full dashboard (Vite + FastAPI) starts the frontend at `http://127.0.0.1:5173`.
- **Impact:** Minor confusion for users trying to access the UI.

### [LOW] Support Bundle Content
- **Issue:** The support bundle only contains 2 files (`configs/config.json` and `bundle_data.json`).
- **Expected:** It should include `gli-flow doctor` output, recent logs, and environment metadata.
- **Impact:** Reduced utility for remote debugging.

### [LOW] Offline Mode Warning
- **Issue:** `gli-flow doctor` displays a `WARNING` for no internet connectivity.
- **Impact:** While accurate, it might be perceived as a failure by users in air-gapped or restricted environments.

---

## 4. Commands Executed & Actual Outputs

### Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e .
```
*Output: Successfully installed gli-flow-1.1.0b0 and 16 dependencies.*

### Environment Check
```bash
gli-flow doctor
```
*Output: ✓ Environment is READY. PDKs found: sky130A, sky130B. Tools found: yosys, openroad, magic, etc.*

### Mock Run
```bash
gli-flow run examples/counter --mock
```
*Output: ✓ Implementation: SUCCESS. ✓ Signoff: PASS. QoR Score: 0.6. Runtime: 42s.*

---

## 5. Undocumented Workarounds
- **Venv Activation:** The "Quick Install" instructions do not explicitly mention virtual environments, which are highly recommended to avoid system-wide conflicts.
- **Design Paths:** Users must provide the full relative path to examples (e.g., `examples/counter`) rather than just the design name.

---

---

## 7. Post-Audit Fixes (Implemented)

Following the inventory, the following fixes were applied:
1. **Shorthand Design Lookup:** `gli-flow run` now searches in `examples/` and `designs/` if the path is not found.
2. **Rename Script:** `scripts/install.sh` renamed to `scripts/validate.sh` and documentation updated.
3. **Support Bundle:** Enhanced to include `~/.gli-flow/logs/` and `EnvironmentValidator` report.
4. **Docs Correction:** Corrected dashboard port (5173) in installation guides.

**Status: CERTIFIED & HARDENED**
