# CLI Help Quality Audit

**Date:** 2026-06-12  
**Scope:** Every command's `--help` output

---

## Rating Scale

| Rating | Meaning |
|--------|---------|
| ✅ GOOD | Clear, beginner-friendly, includes context |
| ⚠️ FAIR | Understandable but missing examples or uses jargon |
| ❌ POOR | Confusing, missing critical info, internal terminology |

---

## Command-by-Command Audit

### 1. `run`

| Aspect | Verdict |
|--------|---------|
| ⚠️ FAIR | Describes arguments but no examples, `--mock` flag is hidden at bottom |

**Issues:**
- No usage example (e.g., `gli-flow run my_design --mock`)
- `--orfs-root` references ORFS (jargon — not explained)
- `--db-path` mentions `$GLI_FLOW_DB_PATH` (internal env var)

**Fix:** Add examples section, describe ORFS as "OpenROAD Flow Scripts."

---

### 2. `history`

| Verdict | Issues |
|---------|--------|
| ✅ GOOD | Simple, clear. No internal terminology. |

---

### 3. `status`

| Verdict | Issues |
|---------|--------|
| ✅ GOOD | Simple, clear. |

---

### 4. `batch`

| Verdict | Issues |
|---------|--------|
| ⚠️ FAIR | Missing example of usage. "Design directories with gli_manifest.yaml" is clear. |

---

### 5. `init`

| Verdict | Issues |
|---------|--------|
| ✅ GOOD | Clear description, well-named flags. |

---

### 6. `quickstart`

| Verdict | Issues |
|---------|--------|
| ❌ POOR | No description, no help text, no examples. Only shows `usage: gli-flow quickstart [-h]` |

**Fix:** Add description text explaining interactive wizard.

---

### 7. `report`

| Verdict | Issues |
|---------|--------|
| ❌ POOR | Confusing dual positional/optional args (`design`/`platform`/`orfs_root` + `--platform`/`--orfs-root`). References "ORFS" without explanation. |

**Fix:** Remove duplicated positional args, add examples.

---

### 8. `install`

| Verdict | Issues |
|---------|--------|
| ✅ GOOD | Well-structured, all flags explained, defaults shown. |

---

### 9. `ci`

| Verdict | Issues |
|---------|--------|
| ❌ POOR | Uses internal jargon: "JUnit XML," "QoR," "WNS," "baseline." No examples. Currently broken. |

**Fix:** Add examples, define acronyms, fix the bug.

---

### 10. `remote`

| Verdict | Issues |
|---------|--------|
| ⚠️ FAIR | Clear flags but no usage example. SSH jargon assumed. |

---

### 11. `cloud`

| Verdict | Issues |
|---------|--------|
| ⚠️ FAIR | Subcommands (`upload`/`download`/`list`) have no individual help description for their args. |

---

### 12. `doctor`

| Verdict | Issues |
|---------|--------|
| ✅ GOOD | `--fix` and `--repair-magic` are well described. |

---

### 13. `reset-runs`

| Verdict | Issues |
|---------|--------|
| ✅ GOOD | Clear description. Destructive nature is obvious. |

---

### 14. `db`

| Verdict | Issues |
|---------|--------|
| ✅ GOOD | Subcommands are clearly named and described. |

---

### 15. `diagnose`

| Verdict | Issues |
|---------|--------|
| ⚠️ FAIR | No example. Run ID format not explained. |

---

### 16. `show-telemetry`

| Verdict | Issues |
|---------|--------|
| ⚠️ FAIR | No example. Run ID format not explained. The help text is very long (one line). |

---

### 17. `config`

| Verdict | Issues |
|---------|--------|
| ✅ GOOD | Simple, clear. |

---

### 18. `dashboard`

| Verdict | Issues |
|---------|--------|
| ⚠️ FAIR | No explanation of prerequisites (uvicorn, npm). `--backend-only` is clear but undocumented in terms of when to use. |

---

### 19. `setup`

| Verdict | Issues |
|---------|--------|
| ✅ GOOD | All flags well-described. |

---

### 20. `support-bundle`

| Verdict | Issues |
|---------|--------|
| ✅ GOOD | Clear flags, good descriptions. |

---

### 21. `upgrade-check`

| Verdict | Issues |
|---------|--------|
| ⚠️ FAIR | No explanation of what sources it checks. |

---

## Summary

| Rating | Count | Commands |
|--------|-------|----------|
| ✅ GOOD | 10 | history, status, init, install, doctor, reset-runs, db, config, setup, support-bundle |
| ⚠️ FAIR | 7 | run, batch, remote, cloud, diagnose, show-telemetry, dashboard, upgrade-check |
| ❌ POOR | 3 | quickstart, report, ci |

---

## Key Issues

1. **No usage examples** — Most commands lack example invocations, which are critical for new users.
2. **Jargon** — "ORFS," "QoR," "WNS," "TNS," "PDK" are used without explanation.
3. **`quickstart` has no help** — Shows only usage line with no description.
4. **`report` has confusing args** — Duplicate positional and optional arguments.
5. **`ci` is broken and poorly documented** — Hidden from help listing but `--help` still works.

---

## Fix Plan

| Priority | Command | Fix |
|----------|---------|-----|
| High | `quickstart` | Add `description` parameter to `add_parser` |
| High | `ci` | Fix bug (done), add docs, add examples |
| Medium | `report` | Remove redundant positional args, simplify |
| Medium | All | Add `epilog` with usage examples to each subparser |
| Low | All | Define acronyms in help text (ORFS, PDK, QoR, etc.) |
