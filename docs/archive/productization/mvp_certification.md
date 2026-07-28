# MVP Certification Report

> **Project:** GLI-FLOW  
> **Date:** June 8, 2026  
> **Target:** External-user MVP readiness  
> **Methodology:** Each category scored 0–10. 0–3 = non-functional, 4–6 = partial/expert needed, 7–8 = functional with gaps, 9–10 = production-ready.

---

## 1. Can a stranger install it?

**Score: 7/10**

### What's working
- `scripts/install.sh` — full one-command installer with OS detection (Ubuntu 22.04+, Debian 12+, WSL2), Python version check, disk/RAM validation, system dependency install, virtual environment creation, `pip install gli-flow`, and post-install `doctor` run.
- `scripts/install.ps1` — equivalent PowerShell installer for Windows 10/11, WSL2.
- `docs/guides/installation_guide.md` — covers pip install, Docker, curl script, and dev install.
- `gli-flow install` CLI command installs EDA toolchain (Yosys, OpenROAD, KLayout, PDK).
- Dockerfiles (production + dev) in repo root.
- `gli-flow doctor` automatically validates the install post-setup.

### What's missing
- **No `pyproject.toml`** — still using `setup.py`; cannot build modern wheels.
- **Not published on PyPI** — `pip install gli-flow` will fail until the package is uploaded.
- **No dependency lockfile** (`requirements.txt` / lockfile) — reproducible installs not guaranteed.
- **No `MANIFEST.in`** — `sdist` may miss configs, examples, or docs.
- **No fresh-install CI job** verifying the install scripts work end-to-end.

### What needs improvement
- Publish to PyPI, add `pyproject.toml`, add lockfile.
- Add `MANIFEST.in` and verify `sdist` contents in CI.
- Add fresh-install CI job that runs `install.sh` in a clean container.

---

## 2. Can a stranger run it?

**Score: 8/10**

### What's working
- Clear README quickstart: `gli-flow run examples/counter --mock`.
- 18 documented CLI commands with descriptions (`run`, `init`, `quickstart`, `batch`, `ci`, `doctor`, `diagnose`, `report`, `history`, `status`, `config`, `install`, `show-telemetry`, `support-bundle`, `upgrade-check`, etc.).
- `gli-flow quickstart` interactive wizard creates manifest + skeleton RTL.
- `gli-flow init` auto-detects RTL files, top module, clock port.
- Manifest format fully documented in README with YAML example.
- 9 example designs ready to run, each with `gli_manifest.yaml`.
- Mock adapter for running without EDA tools (`--mock`).
- System requirements documented (Linux/macOS/WSL2, Python 3.9+, 8 GB RAM).
- FastAPI backend + React dashboard with real-time polling.
- `gli-flow doctor` validates environment before runs.

### What's missing
- **No `pyproject.toml`** means `pip install -e .` is the only dev install path.
- No Makefile or task runner for common operations (install, test, lint, build, clean).
- Configuration CLI commands limited — `config` only supports telemetry toggle.
- First-run config wizard not integrated with `config` system.

### What needs improvement
- Add `Makefile` for common dev tasks.
- Expand `gli-flow config` to manage all settings (PDK path, tool paths, workspace).
- Wire first-run setup into the hierarchical config system.

---

## 3. Can a stranger debug failures?

**Score: 7/10**

### What's working
- `gli-flow doctor` validates EDA toolchain and produces health report.
- `gli-flow diagnose <run_id>` scans stage logs from failed runs.
- `gli-flow support-bundle` generates a single archive with all diagnostic info.
- `gli-flow history` / `gli-flow status` for run overview.
- `docs/guides/troubleshooting_guide.md` (130 lines) — covers tool-not-found, PDK issues, DRC failures, Python/venv, Docker, network, and ORFS issues.
- Failure Atlas captures failure records with error classification.
- Exception hierarchy with 12 custom exception classes.
- Structured logging (JSON format support) with file output, rotation, and per-run log files.
- Log level configurable via env var (`GLI_FLOW_LOG_LEVEL`), config file, or programmatic override.
- Environment fingerprinting for reproducibility.

### What's missing
- **No error codes** on exceptions — errors lack machine-parseable identifiers and doc links.
- **Stack traces exposed by default** in many commands (no `--debug` flag separation).
- **Doctor `--fix` mode** behavior is undocumented.
- **No health endpoint** beyond `doctor` for Docker/CI deployments.
- **No metrics or SLIs** exposed for monitoring.

### What needs improvement
- Add error codes and documentation links to all exceptions.
- Separate `--debug` (verbose stack traces) from default user-facing output.
- Document doctor `--fix` mode.
- Add health check endpoint for Docker deployments.
- Add `--verbose`/`-v` flag to all commands for DEBUG-level logging.

---

## 4. Can a stranger understand results?

**Score: 8/10**

### What's working
- Output directory documented: `outputs/runs/<run_id>/` with `reports/`, `artifacts/`, `telemetry/`, `logs/`, `config.json`, `reproducibility.json`, `drc_lvs_summary.json`, `sta_corners.json`.
- QoR scoring and regression detection against previous runs.
- `gli-flow report <design>` for QoR report from ORFS output files.
- FastAPI backend + React dashboard with 5 metric cards, QoR trend chart, score breakdown, execution health gauge, recent runs table with 8 detail tabs.
- Dashboards poll every 2 seconds for live updates.
- Artifact validation framework validates GDS, netlists, reports.
- Telemetry payload inspection via `show-telemetry`.
- Per-run reproducibility data (SHA256 hashes, tool versions, system fingerprint).

### What's missing
- **No structured error taxonomy** — results don't include error codes or resolution hints.
- Dashboard requires manual startup (`uvicorn` + `npm run dev`) — no single-command launch.
- No deployment mode docs for non-local setups (covered in `docs/guides/deployment_modes.md` but not referenced from README).

### What needs improvement
- Add error codes to run results so users can cross-reference documentation.
- Add `gli-flow dashboard` single-command launcher.
- Cross-link deployment modes doc from README.

---

## 5. Can a stranger generate GDS?

**Score: 7/10**

### What's working
- Core RTL-to-GDS pipeline via ORFS: Yosys synthesis → OpenROAD P&R → GDS.
- `gli-flow run <design>` runs the full pipeline.
- GDS validation in `artifact_validator.py` (binary header check, size check, presence check).
- DRC/LVS verification on generated GDS (Magic DRC, KLayout DRC, Magic extraction for LVS).
- GDS presence, size, and staleness checks in `orchestrator.py` and `openroad_adapter.py`.
- Mock adapter generates fake GDS for CI/testing without EDA tools.
- Output artifacts include `6_final.gds` with manifest.
- Supported PDKs: sky130 (sky130A/sky130hd, tested), gf180mcu (defined).
- Maximum tested complexity: ~50,000 cells (ibex RISC-V).

### What's missing
- **Requires external EDA tools** — Yosys, OpenROAD, KLayout, and a PDK must be installed separately (or via `gli-flow install`).
- **No built-in GDS viewer** — user must have KLayout or equivalent.
- Only sky130 is verified; gf180mcu is defined but untested.
- No CDC analysis — mandatory disclaimer for multi-clock designs.
- No Monte Carlo timing — deterministic corner analysis only.
- SystemVerilog requires sv2v preprocessing.
- No hierarchical or analog/mixed-signal flow support.

### What needs improvement
- Add `gli-flow gds-view` that wraps KLayout or provides a web-based viewer.
- Verify and document gf180mcu support.
- Document GDS output expectations (layer map, cell naming conventions).

---

## 6. Can a stranger reproduce examples?

**Score: 8/10**

### What's working
- 9 example designs: `counter`, `fir`, `gcd`, `gpio`, `mini_mac`, `mini_mac_soc`, `systolic_array`, `tiny_or`, `uart`.
- Each design has `gli_manifest.yaml` with proper configuration.
- `counter/README.md` — complete with description, top module, PDK, clock, expected QoR table, expected runtime breakdown (per-stage), run command, and output description.
- `gcd/README.md` — designated as primary onboarding design for MVP validation.
- Golden regression suite (counter, uart, gpio, fir) run in CI.
- Some designs include run scripts (`scripts/run_systolic.py`, `examples/uart/run_uart.py`).
- Mock mode works for all examples without EDA tools.
- `pytest tests/ -v` runs the full test suite including golden designs.
- CI runs tests on push/PR to main.

### What's missing
- Not all examples have READMEs (only counter, gcd have them).
- gcd README says "placeholder onboarding design" — RTL/config integration not yet complete.
- gcd is the intended golden validation design but not yet fully wired.
- No expected output hashes or golden GDS checksums for result verification.
- No single `examples/README.md` index listing all examples and their purposes.

### What needs improvement
- Complete gcd example as the golden validation design (RTL, config, expected outputs).
- Add READMEs to remaining examples (fir, gpio, mini_mac, etc.).
- Add expected output checksums or golden reference data for self-verification.
- Create `examples/README.md` index.

---

## Overall MVP Readiness

| Category | Score (0–10) |
|----------|:--------:|
| 1. Installation | **7** |
| 2. Run-ability | **8** |
| 3. Debuggability | **7** |
| 4. Result Comprehension | **8** |
| 5. GDS Generation | **7** |
| 6. Example Reproducibility | **8** |
| **Average** | **7.5 / 10** |

### Blocker Summary

| Blocker | Area | Impact |
|---------|------|--------|
| **Not on PyPI** | Installation | Users cannot `pip install gli-flow`. Must clone repo or use Docker. |
| **No `pyproject.toml`** | Installation/Packaging | Cannot build modern wheels; Python packaging best practice gap. |
| **GCD example incomplete** | Reproducibility | Intended golden validation design is still a placeholder. |
| **Only sky130 verified** | GDS Generation | gf180mcu defined but untested; limits PDK choice. |
| **No error codes** | Debuggability/Results | Errors lack machine-parseable identifiers and resolution links. |
| **No dependency lockfile** | Installation | Unpredictable dependency resolution across installs. |

### Assessment

GLI-FLOW achieves a **7.5/10 average** across all 6 MVP certification categories. The tool is **functional and usable by a technically proficient stranger** for RTL-to-GDS flows on sky130 using the provided examples. The install scripts, documentation, dashboard, and example suite provide a solid onboarding experience.

The single critical blocker is **PyPI publishing** — without it, the one-command install scripts (`install.sh` / `install.ps1`) will fail at `pip install gli-flow`. The remaining blockers are important but do not prevent a stranger from evaluating the tool (they can clone + `pip install -e .`).

**Verdict:** MVP-ready with one critical action item (publish to PyPI) and several high-priority improvements (pyproject.toml, gcd completeness, error codes).
