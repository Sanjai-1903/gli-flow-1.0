# Changelog

All notable changes to GLI-FLOW are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-06-09

### Added — Environment Resilience Program

- **Multi-candidate tool discovery** — `discover_magic_binaries()` returns all candidates, not just PATH-first
- **Candidate ranking engine** — `rank_tool_candidates()` uses functional validation > version > source priority
- **Functional tool validation** — `validate_magic_candidate()` tests execution, TCL, DRC per candidate
- **Doctor discovery report** — Shows all candidates with path, version, status, failure reason, evidence
- **Self-healing repair** — `gli-flow doctor --repair-magic` renames broken local binaries shadowing system installs
- **Generic repair framework** — `PathShadowingRepair`, `BrokenBinaryRepair` with detect/repair/verify lifecycle
- **Failure Atlas ENVIRONMENT domain** — New domain with PATH_SHADOWING, WRAPPER_MISSING, BROKEN_SYMLINK, TOOL_BROKEN categories
- **Adversarial environment tests** — 10 tests for broken wrappers, symlinks, permissions, PATH shadowing
- **PATH shadowing regression tests** — 7 tests ensuring broken candidates are never selected over valid ones
- **Install validation** — Detects PATH shadowing during install, warns with repair command
- **Telemetry** — Environment events recorded: tool_shadowing, broken_wrapper, repair_invocation, repair_success, repair_failure
- **Release gates** — 4 gates: multi-candidate discovery, regression tests, repair framework, adversarial tests
- **Documentation** — Updated README, USER_MANUAL, ARCHITECTURE, troubleshooting guide, MAGIC_ROOT_CAUSE

### Changed

- `tool_discovery.py`: `find_magic_binary()` now uses `discover_magic_binaries()` + `rank_tool_candidates()` internally
- `tool_discovery.py`: `validate_magic_functionality()` uses discovered binary path instead of hardcoded `/usr/bin/magic`
- `doctor.py`: Added `DiscoveryReport` and `run_magic_discovery()` for complete candidate visibility
- `repair_actions.py`: Added `PathShadowingRepair` and `BrokenBinaryRepair` classes
- `failure_atlas/taxonomy.py`: Added `ENVIRONMENT` domain and 8 environment-specific failure categories
- `telemetry_manager.py`: Added `record_environment_event()` and `export_environment_events()` methods

## [1.0.0] - 2026-06-08

### Added

- Initial public release
- RTL-to-GDS pipeline orchestration
- Failure Atlas failure detection and diagnosis
- QoR scoring and regression detection
- Golden design regression suite (counter, uart, gpio, fir)
- Doctor validation command
- Install certification (7 levels)
- Environment fingerprinting
- Execution intelligence data model
- QoR intelligence foundation
- Artifact validation framework
- Tool discovery with ToolInfo dataclass
- Support bundle generation
- Upgrade check command
- Interactive setup wizard
- Hierarchical configuration system
- Structured logging with log rotation
- Human-readable run summaries
- Security review and hardening
- Deployment mode documentation (local, WSL, Docker, CI/CD)
