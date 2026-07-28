# GLI-FLOW Documentation Execution Audit v1

## 1. Broken Commands/Workflows
- **Installation:**
  - `bash scripts/install.sh` fails on the final step because it triggers an interactive telemetry wizard (`EOFError`) which cannot be bypassed via CLI arguments.
  - Required manual intervention (`pip install httpx`) to fix a `ModuleNotFoundError` during the post-install verification step (`gli-flow doctor`).

## 2. Missing Prerequisites
- **Dependencies:** The installation script does not correctly install all required Python dependencies (specifically `httpx`), causing runtime errors immediately after installation.

## 3. Ambiguous Instructions
- **Telemetry Configuration:** The documentation claims `gli-flow config --telemetry off` can change settings, but the interactive telemetry wizard is mandatory at first run, and there is no non-interactive way to bypass it during the initial `gli-flow doctor` execution.

## 4. Other Issues
- **Installation Path:** The script installs into `/root/.gli-flow/venv` when run with sudo, which may not be accessible/expected by a normal user attempting to run `gli-flow` later.
