# FIRST_TIME_USER_REPORT.md

## Experience Simulation
A user clones the repository and follows standard Python practices.

## Blockers
1. **Command Not Found:** Even after `pip install -e .`, the `gli-flow` command fails if `~/.local/bin` is not in the `PATH` or if the user hasn't sourced their shell profile after installation.
2. **Missing Dependencies:** The repository doesn't have a clear `requirements.txt` for *running* the tool (only `extras_require` in `setup.py`), leading to potential missing dependencies on a clean install.

## Confusion Points
1. **No "Doctor" check:** There's no initial validation step (`gli-flow doctor` must be run *after* successful installation, but how do they even know it's installed if the command isn't found?).
2. **Ambiguous Documentation:** The README does not specify that `~/.local/bin` might need to be added to `PATH` for the CLI to be accessible.

## Missing Documentation
1. **Getting Started Guide:** No comprehensive guide covering fresh Ubuntu/WSL environments.
2. **Environment Validation:** No instructions on how to verify the installation (other than running the command, which fails).

## Missing Validation
1. **Install Validator:** No script to check for required OS-level dependencies (like `magic`, `yosys`, `openroad`) *before* or *during* installation.
