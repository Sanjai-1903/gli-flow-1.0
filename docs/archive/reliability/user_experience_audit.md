# User Experience Audit — GLI-FLOW

> **Phase 10 of 10** — Final UX transformation report.
> Date: 2026-06-13

## Summary

GLI-FLOW underwent a 10-phase UX transformation focused on making the tool
**professional, trustworthy, intuitive, and enjoyable** for first-time users.
All changes were validated against the existing 540-test suite (0 failures).

---

## Phase 1 — First Run Experience

**Goal:** Make the first interaction with GLI-FLOW welcoming and guided.

| File | Change |
|------|--------|
| `gli_flow/cli/output.py` | Banner simplified from "Execution Intelligence Infrastructure" to "RTL-to-GDS Digital Design Flow" |
| `gli_flow/cli/output.py` | Added `print_first_run_guide()` — shows setup steps (setup → doctor → install → quickstart → run) |
| `gli_flow/cli/main.py` | First-run guide auto-displayed when `gli-flow` is invoked without a subcommand and no config exists |
| `gli_flow/cli/main.py` | Improved `_show_first_run_notice()` telemetry notice formatting |

**Result:** A new user running `gli-flow` sees a clear action plan, not just a command list.

---

## Phase 2 — Friendlier CLI

**Goal:** Every command should have clear help, examples, and actionable next steps.

| File | Change |
|------|--------|
| `gli_flow/cli/main.py` | `CategorizedHelpFormatter` groups commands into "Production" and "Experimental" categories |
| `gli_flow/cli/main.py` | All 25 subcommands now have `epilog` with 2-3 usage examples |
| `gli_flow/cli/main.py` | Top-level `epilog` includes issue tracker URL |
| `gli_flow/cli/main.py` | `FRIENDLY_ERRORS` dict provides human-readable explanations for PDK, ORFS, openroad, yosys, klayout, manifest errors |
| `gli_flow/cli/main.py` | `friendly_error()` function surfaces explanations with actionable next steps |

**Result:** `--help` on any command shows examples. Common errors explain *why* and *how to fix*.

---

## Phase 3 — User Confidence & Failure Handling

**Goal:** When something breaks, tell the user what happened, how confident you are, and what to do next.

| File | Change |
|------|--------|
| `gli_flow/cli/main.py` | `diagnose_command()` — full rewrite with AI explanation integration |
| `gli_flow/cli/main.py` | `investigate_command()` — new Tier 2 LLM investigation command |
| `gli_flow/cli/main.py` | `ai_assist_command()` — AI Investigation Assistant with trigger logic |
| `gli_flow/cli/main.py` | `escalate_command()` — Community Intelligence escalation workflow |
| `gli_flow/cli/output.py` | `print_ai_response()` — structured AI output with confidence, causes, steps, references |
| `gli_flow/core/orchestrator.py` | `_record_root_causes()` — persists root cause analysis to Failure Atlas |
| `gli_flow/core/orchestrator.py` | Root cause report included in `_write_run_summary()` |
| `gli_flow/core/orchestrator.py` | `_display_explanation()` — inline AI explanation display |

**Result:** Failed runs produce diagnosis with AI-generated hypotheses, confidence levels, and recommended next steps.

---

## Phase 4 — Dashboard & API Presentation

**Goal:** Dashboard and API responses should be complete, useful, and self-documenting.

| File | Change |
|------|--------|
| `backend/server.py` | `GET /runs` now returns `hold_wns`, `hold_tns`, `tapeout_ready`, `implementation_status`, `signoff_status`, `implementation_score`, `signoff_score`, `root_cause_summary`, `drc_violations`, `drc_is_clean`, `lvs_is_clean` |
| `backend/server.py` | `GET /runs/{id}` returns all signoff fields, DRC breakdown, LVS result |
| `backend/server.py` | Image serving supports `.webp`, `.webp.png`, `.svg` with correct MIME types |
| `backend/server.py` | NEW: `/ai/trigger`, `/ai/investigate`, `/ai/investigate/failure`, `/ai/feedback` endpoints |
| `backend/server.py` | Failure Atlas API extended with correlation, coverage, AI trigger data |
| `dashboard/src/FailureAtlasPage.jsx` | `AIInvestigationCard` component — inline AI investigation trigger + results |
| `dashboard/src/App.jsx` | "Engineering Dashboard" nav entry |
| `dashboard/src/RunDetail.jsx` | Richer run detail view with AI investigation integration |

**Result:** Dashboard is feature-complete with AI investigation, signoff tracking, and engineering overview.

---

## Phase 5 — Long-Run Progress & Heartbeat

**Goal:** Users running long flows should see progress, not silence.

| File | Change |
|------|--------|
| `gli_flow/core/orchestrator.py` | `_make_orfs_progress_callback()` — live routing progress bar with iteration % and violation count |
| `gli_flow/core/orchestrator.py` | `_write_run_summary()` — includes implementation status, signoff status, tapeout readiness |
| `gli_flow/cli/output.py` | `print_stage_progress()` — progress bar with stage name, percentage, color-coded status |
| `gli_flow/cli/output.py` | `print_run_header()` — laid out run ID, design, output dir |

**Result:** Long flows show stage transitions and routing progress in real time.

---

## Phase 6 — Achievement & Result Summaries

**Goal:** Completed runs should celebrate success and clearly communicate results.

| File | Change |
|------|--------|
| `gli_flow/cli/output.py` | NEW: `print_achievement_summary()` — success panel with QoR score, tapeout readiness, DRC/LVS status in green panel on success; red panel with next steps on failure |
| `gli_flow/cli/main.py` | `run_command()` calls `print_achievement_summary()` after orchestration completes |

**Result:** Every run ends with a clear, visually distinct summary panel.

---

## Phase 7 — Trust & Honest Language

**Goal:** Remove marketing puffery; be direct about what the tool does and doesn't do.

| File | Change |
|------|--------|
| `gli_flow/cli/output.py` | Banner: "Execution Intelligence Infrastructure" → "RTL-to-GDS Digital Design Flow" |
| `gli_flow/cli/output.py` | Subtitle: "RTL-to-GDS Silicon Pipeline" → "Open-source ASIC/FPGA implementation" |
| `gli_flow/cli/main.py` | Parser description: "GLI-FLOW — RTL-to-GDS Silicon Pipeline" → "GLI-FLOW — RTL-to-GDS Digital Design Flow" |
| `gli_flow/cli/main.py` | AI output always labeled "EXPERIMENTAL" and "NOT VERIFIED" |
| `gli_flow/cli/main.py` | AI disclaimer: "AI GENERATED — EXPERIMENTAL — NOT VERIFIED" displayed prominently |

**Result:** User-facing text describes what the tool *does*, not what it aspires to be.

---

## Phase 8 — Persona Walkthrough

Walkthrough performed for four target personas.

### Persona A: Student Learning ASIC Design
| Step | Experience |
|------|------------|
| `gli-flow` | Sees welcome guide with 5-step action plan |
| `gli-flow setup` | Interactive prompts with sensible defaults |
| `gli-flow doctor` | Rich table output, clear PASS/WARN/FAIL |
| `gli-flow quickstart` | Interactive wizard creates first design |
| `gli-flow run` | Live progress, ends with achievement summary |

### Persona B: Researcher Running Many Designs
| Step | Experience |
|------|------------|
| `gli-flow batch` | Parallel execution with per-job progress |
| `gli-flow history` | Table with run IDs, designs, status, QoR |
| `gli-flow diagnose` | Rich diagnosis with AI assistance |
| `gli-flow report` | Full QoR report grid |

### Persona C: ASIC Engineer in Production
| Step | Experience |
|------|------------|
| `gli-flow ci` | JUnit/Markdown output, baseline comparison |
| `gli-flow doctor --fix` | Auto-repair with re-verification |
| `gli-flow support-bundle` | Diagnostic archive generation |
| `gli-flow db migrate` | Database schema management |

### Persona D: FPGA Engineer Evaluating the Tool
| Step | Experience |
|------|------------|
| `gli-flow setup --non-interactive` | Headless configuration |
| `gli-flow install --dry-run` | Preview before changes |
| `gli-flow --help` | Categorized commands, examples on every subcommand |

---

## Phase 9 — Micro-Delights

| File | Change |
|------|--------|
| `gli_flow/cli/output.py` | `print_error()` / `print_warning()` — consistent error formatting |
| `gli_flow/cli/output.py` | `print_install_report()` — clear summary with completed/skipped/failed |
| `gli_flow/cli/output.py` | `print_results()` — color-coded QoR, hold WNS with tapeout blocker warnings |
| `gli_flow/cli/output.py` | `LVS_DISCLAIMER` — educates users on what LVS does/doesn't verify |
| `gli_flow/cli/main.py` | `friendly_error()` — explains *why* the error happened, not just *what* |
| `gli_flow/cli/main.py` | `print_ai_response()` — feedback prompt at end ("Was this helpful?") |
| `gli_flow/doctor.py` | Uses `rich` Console for all output (tables, panels, colored status) |
| `gli_flow/doctor.py` | `DoctorReport.print_summary()` — rich table with color-coded status column |

---

## Phase 10 — This Report

A comprehensive UX audit documenting all changes across 10 phases.

---

## Files Modified (UX Transformation)

| File | Phases |
|------|--------|
| `gli_flow/cli/output.py` | 1, 2, 5, 6, 7, 9 |
| `gli_flow/cli/main.py` | 1, 2, 3, 6, 7, 8 |
| `gli_flow/doctor.py` | 9 |
| `gli_flow/core/orchestrator.py` | 3, 5 |
| `gli_flow/core/error_experience.py` | 3 |
| `backend/server.py` | 4 |
| `dashboard/src/App.jsx` | 4 |
| `dashboard/src/FailureAtlasPage.jsx` | 4 |
| `dashboard/src/RunDetail.jsx` | 4 |
| `docs/reliability/user_experience_audit.md` | 10 (this file) |

---

## Impact Assessment

| Metric | Before | After |
|--------|--------|-------|
| Banner marketing language | "Execution Intelligence Infrastructure" | "RTL-to-GDS Digital Design Flow" |
| Commands with examples | 0 / 25 | 25 / 25 |
| Commands with categorized help | No | Yes (Production / Experimental) |
| Doctor output format | Raw `print()` | Rich tables with color status |
| Achievement summaries | None | Success/failure panels with key metrics |
| AI output confidence labels | None | Always shown ("LOW" / "MEDIUM") |
| AI disclaimer | None | "EXPERIMENTAL · NOT VERIFIED" on all AI output |
| Dashboard signoff fields | 0 fields | 10+ fields |
| Dashboard AI investigation | None | Full card with trigger, causes, steps |
| FRIENDLY_ERRORS coverage | 6 patterns | 6+ patterns with actionable next steps |
| First-run guide | None | Auto-displayed welcome panel |
| Tests | 540 passed, 0 failed | 540 passed, 0 failed (no regressions) |
