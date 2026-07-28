# INSTALLATION_AUDIT.md

## Current Install Flow
Users are expected to clone the repository and install it in editable mode:
```bash
git clone <repo>
cd <repo>
pip install -e .
```

## Discovered Problems
1. **CLI command not found:** After `pip install -e .`, the `gli-flow` command is not available in the user's `PATH`.
2. **Missing PyPI package:** `pip install gli-flow` fails because the package is not published.
3. **Broken Installation Documentation:** Multiple URLs referenced in installation scripts or documentation return 404.
4. **Pathing Issues:** The installation directory (`~/.local/bin`) is often not on the user's `PATH` by default in fresh environments.

## Root Causes
1. **Entrypoint Misconfiguration/Pathing:** While `setup.py` defines `console_scripts`, the location where pip installs executables is not being added to the user's shell `PATH`.
2. **Lack of User-Friendly Validation:** The project lacks a simple "pre-flight" check or "doctor" command to verify the environment and PATH *before* the user tries to run the CLI.
3. **Documentation Stale:** The installation guide/scripts reference obsolete/broken resources.

## Risk Assessment
- **Severity: High.** New users cannot use the tool immediately after installation.
- **Impact:** Significant friction for onboarding beta testers, researchers, and ASIC engineers.
- **Urgency:** P0 - Fix onboarding immediately.
