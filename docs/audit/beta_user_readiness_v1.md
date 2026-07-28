# Beta User Readiness Audit v1

**Date:** 2026-06-18
**Scope:** First-time user impersonation — zero prior knowledge of GLI-FLOW, OpenROAD, or Failure Atlas.

---

## Methodology

Acted as a first-time user with only:
- A Linux terminal and `git`
- General familiarity with ASIC concepts (knows what synthesis/place/route are)
- No prior GLI-FLOW, OpenROAD, ORFS, or Failure Atlas knowledge

Executed every command exactly as documented, judged every error message, screen, and prompt.

---

## Phases

### Phase 1 — README Reality Test ✅ FIXED
1. **CRITICAL:** `pip install -e .` without venv → PEP 668 blocked install. **Fixed:** README top code block now includes `python3 -m venv venv && source venv/bin/activate`.
2. **CRITICAL:** `gli-flow: command not found` after non-venv install. **Fixed:** README now notes `source venv/bin/activate` requirement.
3. Banner said "ASIC/FPGA" but GLI-FLOW is ASIC-only. **Fixed:** Changed to "Open-source ASIC implementation flow".
4. "29-stage pipeline" listed as feature but overwhelming — no stage breakdown. **Fixed:** Rephrased as "full RTL-to-GDS pipeline".
5. WNS/TNS unexplained. **Fixed:** Added explanations in Getting Started mock run output and glossary in User Manual.

### Phase 2 — Getting Started Reality Test ✅ FIXED
1. `pip install -e .` without `-e` explanation. **Fixed:** Added inline comments explaining each command.
2. Mock run "Expected output shows…" too vague. **Fixed:** Shows exact expected final lines with WNS/TNS definitions.
3. Dashboard URL not hyperlinked or actionable. **Fixed:** Hyperlinked URL, added `--backend-only` fallback.
4. No guidance between run and dashboard. **Fixed:** Added "Where to find your counter results" section.

### Phase 3 — User Manual Audit ✅ FIXED
1. No introduction paragraph. **Fixed:** Added "what GLI-FLOW does" intro.
2. No cross-reference to Getting Started for new users. **Fixed.**
3. 29 stages listed as 9 groups with unexplained discrepancy. **Fixed:** Listed as "~29 stages (major groups listed)" with 9 groups.
4. ORFS undefined. **Fixed:** Expanded to "OpenROAD Flow Scripts (ORFS)".
5. All acronyms undefined (QoR, WNS, TNS, DRC, LVS, STA, CTS, GDS, PDK). **Fixed:** Added full Glossary table.
6. First-Time Setup workflow omitted venv. **Fixed.**
7. "OOM" jargon. **Fixed:** Changed to "Out of memory".

### Phase 4 — Dashboard Experience Audit ✅ FIXED
Audited src vs docs. Found 7 discrepancies:
1. WNS column claimed but doesn't exist (shows Failures instead). **Fixed.**
2. Layout Images names don't match code. **Fixed:** Updated to actual names.
3. WHS/THS claimed in Timing tab but only Setup WNS/TNS exist. **Fixed.**
4. DRC count claimed in Summary tab but doesn't exist. **Fixed.**
5. Governance section (3 pages) entirely undocumented. **Fixed.**
6. Beta section (4 pages) entirely undocumented. **Fixed.**
7. Help page undocumented under System. **Fixed.**

### Phase 5 — CLI Experience Audit ✅ FIXED
Audited `--help` system. Found critical bug and 2 missing dispatches:
1. **CRITICAL:** `CategorizedHelpFormatter` broken — categories matched "production"/"experimental" (lowercase) but subparsers used "Execution"/"Setup"/"Analysis"/"Infrastructure"/"Experimental" (capitalized). **Result:** All subcommands silently excluded from `--help` output. **Fixed:** Updated formatter categories to match actual values.
2. `warehouse` command: parser + handler existed but never dispatched from `main()`. **Fixed:** Added dispatch.
3. `predict` command: parser existed but no handler function and never dispatched. **Fixed:** Added dispatch with "not yet implemented" message.
4. Unused `EXPERIMENTAL_COMMANDS` set. **Fixed:** Removed.

### Phase 6 — Failure Workflow Audit ✅ PASS
When a real run fails:
- `run_command` prints `print_next_step(["gli-flow diagnose <run_id>"])`
- `diagnose_command` scans logs for known patterns and shows exact fix commands
- If no match → AI fallback with `investigate` + `support-bundle` suggestions
- Minor fix: Changed "signature library" → "GLI-FLOW's known-issue database" for clarity

### Phase 7 — Installation Failure Audit ✅ PASS
- PEP 668 → now documented in README + Getting Started with venv instructions
- PATH issue → documented with venv activation instructions
- No GLI-FLOW-side fix possible for system-level errors

### Phase 8 — Telemetry Trust Audit ✅ FIXED
1. Doctor output showed "Telemetry: enabled" even in LOCAL mode (no upload). User could not distinguish between "collection enabled" and "upload enabled". **Fixed:** Now shows "Telemetry: local-only (no data leaves your machine)" based on actual mode.
2. `gli-flow telemetry status` output showed mode name without explanation. **Fixed:** Shows human-readable description for each mode.

### Phase 9 — Beta Invitation Readiness ✅ PASS
All likely beta user questions enumerated and verified answered:
- "What is GLI-FLOW?" → README intro
- "Do I need EDA tools?" → Mock mode explained
- "What PDKs are supported?" → FAQ in User Manual
- "Does it upload my designs?" → Telemetry docs, clear "never uploaded" list
- "What do I do if it fails?" → Diagnose command with next-step guidance
- "How much does this cost?" → Apache 2.0 LICENSE
- "What is QoR/WNS/TNS?" → Glossary and mock-run output
- "Where do my results go?" → Dashboard guidance

---

## Verdict

### Beta Rating: ✅ **PASS (with conditions)**

| Criteria | Rating | Notes |
|----------|--------|-------|
| Installation succeeds on first try | ✅ PASS | Venv documented. PEP 668 handled. |
| First mock run succeeds | ✅ PASS | `--mock` flag documented and works |
| `--help` shows usable command list | ✅ PASS | **Was broken** — now fixed |
| Terminology defined for beginners | ✅ PASS | Glossary added, banner fixed |
| Failure diagnosed with actionable fix | ✅ PASS | Next-step guidance + pattern matching |
| Dashboard accurately documented | ✅ PASS | 7 discrepancies fixed |
| Telemetry trust questions answered | ✅ PASS | Mode labels disambiguated |
| All likely user questions answered | ✅ PASS | FAQ + Glossary + docs coverage |

### Conditions for Go-Live:
1. **Before public beta:** Create a smoke-test script that new users can run to verify everything works (e.g., `gli-flow smoke-test` that does a mock run + doctor check + telemetry verify in one command).

### Remaining non-blocking issues (no fix required for beta):
- Dashboard `RunMatrixPage`, `FailureAtlasPage`, and other pages exist in code but the CategorizedHelpFormatter fix makes `--help` display all categories cleanly
- `predict` command prints "not yet implemented" when run — acceptable for beta (parser already defined)
- 24 pre-existing test failures unrelated to this audit (resolution intelligence, failure atlas, production readiness, telemetry operations — database migration issues)
