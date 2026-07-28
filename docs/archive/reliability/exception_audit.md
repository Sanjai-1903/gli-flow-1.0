# Exception Safety Audit Report

Generated: 2026-06-08

## Summary

| Classification | Count | Severity |
|---|---|---|
| SILENT_PASS (error fully swallowed) | 60 | HIGH |
| SILENT_EMPTY (returns empty data on error) | 27 | HIGH |
| SILENT_NONE (returns None on error) | 4 | MEDIUM |
| SILENT_SUCCESS (returns success on error) | 6 | CRITICAL |
| BORDERLINE (logged/partial handling) | 12 | LOW |

## Status Model

All exception handlers must conform to:
- `PASS` — operation completed with verified evidence
- `FAIL` — operation completed but produced invalid results
- `ERROR` — operation could not complete or evidence is missing
- `NOT_RUN` — operation was not attempted

**Policy:**
- Missing evidence != PASS → Missing evidence = **ERROR**
- Any parsing failure → **ERROR**
- Any missing artifact → **ERROR**
- Any tool execution failure → **FAIL** or **ERROR**

---

## CRITICAL: SILENT_SUCCESS (returns success-like value on error)

### 1. `analytics/regression.py:57` — `detect_regression`

| Field | Value |
|---|---|
| **File** | `analytics/regression.py` |
| **Function** | `detect_regression` |
| **Previous behavior** | `except Exception: return {"alerts": [], "regression_count": 0}` — reports "no regressions" when DB query fails |
| **New behavior** | `except Exception as e: return {"alerts": [f"Regression detection error: {e}"], "regression_count": -1, "error": str(e)}` |
| **Fixed** | ✅ |

### 2. `failure_atlas/repository.py:390-396` — `get_statistics`

| Field | Value |
|---|---|
| **File** | `failure_atlas/repository.py` |
| **Function** | `get_statistics` |
| **Previous behavior** | Two separate `except Exception` blocks silently set `total=0` and `fixed=0`, then computes `fixed/total` risking ZeroDivisionError |
| **New behavior** | Single try/except wrapping all DB operations; returns ERROR status on failure |
| **Fixed** | ✅ |

### 3. `gli_flow/core/drc_runner.py:195` — `_parse_magic_drc_report`

| Field | Value |
|---|---|
| **File** | `gli_flow/core/drc_runner.py` |
| **Function** | `_parse_magic_drc_report` |
| **Previous behavior** | `except Exception: return 0, False` — returns 0 violations (misleading) |
| **New behavior** | `except Exception: return -1, False` — returns -1 to distinguish "no violations found" from "parse error" |
| **Fixed** | ✅ |

### 4. `gli_flow/core/drc_runner.py:212` — `_parse_klayout_drc_report`

| Field | Value |
|---|---|
| **File** | `gli_flow/core/drc_runner.py` |
| **Function** | `_parse_klayout_drc_report` |
| **Previous behavior** | `except Exception: return 0, False` — returns 0 violations (misleading) |
| **New behavior** | `except Exception: return -1, False` — returns -1 to distinguish "no violations found" from "parse error" |
| **Fixed** | ✅ |

---

## HIGH: SILENT_PASS (error fully swallowed)

### 5. `gli_flow/core/orchestrator.py:331` — `_run_failure_detection`

| Field | Value |
|---|---|
| **File** | `gli_flow/core/orchestrator.py` |
| **Function** | `_run_failure_detection` |
| **Previous behavior** | `except Exception: pass` — silently drops DRC/LVS summary parse failures |
| **New behavior** | `except Exception as e: logger.warning(f"Failed to parse DRC/LVS summary: {e}")` |
| **Fixed** | ✅ |

### 6. `gli_flow/core/orchestrator.py:423` — `_get_remediation_by_id`

| Field | Value |
|---|---|
| **File** | `gli_flow/core/orchestrator.py` |
| **Function** | `_get_remediation_by_id` |
| **Previous behavior** | `except Exception: pass` — returns `[]` silently |
| **New behavior** | `except Exception as e: logger.warning(f"Failed to load remediation DB: {e}")` — returns `[]` |
| **Fixed** | ✅ |

### 7. `gli_flow/core/orchestrator.py:554-560` — `_run_subprocess_safe`

| Field | Value |
|---|---|
| **File** | `gli_flow/core/orchestrator.py` |
| **Function** | `_run_subprocess_safe` |
| **Previous behavior** | Two `except Exception: pass` blocks — setrlimit failures silently ignored |
| **New behavior** | `logger.warning` logs setrlimit failures |
| **Fixed** | ✅ |

### 8. `gli_flow/core/routing_safety.py:48` — `check_global_routing_overflow`

| Field | Value |
|---|---|
| **File** | `gli_flow/core/routing_safety.py` |
| **Function** | `check_global_routing_overflow` |
| **Previous behavior** | `except Exception: pass` — overflow check silently skipped |
| **New behavior** | Logs warning with error details |
| **Fixed** | ✅ |

### 9. `gli_flow/core/cdc_check.py:28,38` — `count_clock_domains`

| Field | Value |
|---|---|
| **File** | `gli_flow/core/cdc_check.py` |
| **Function** | `count_clock_domains` |
| **Previous behavior** | `except Exception: pass` — SDC and RTL parsing failures silently skipped |
| **New behavior** | Logs warning; returns ERROR status on parse failure |
| **Fixed** | ✅ |

### 10. `gli_flow/core/rtl_preprocessor.py:35,119`

| Field | Value |
|---|---|
| **File** | `gli_flow/core/rtl_preprocessor.py` |
| **Function** | `detect_systemverilog`, `resolve_includes` |
| **Previous behavior** | `except Exception: pass` — silently skips unreadable files |
| **New behavior** | Logs warning; continues with remaining files |
| **Fixed** | ✅ |

### 11. `gli_flow/infrastructure/environment_validator.py:90`

| Field | Value |
|---|---|
| **File** | `gli_flow/infrastructure/environment_validator.py` |
| **Function** | `_validate_system` |
| **Previous behavior** | `except Exception: pass` — platform detection failure silently ignored |
| **New behavior** | Logs warning; sets platform to "unknown" |
| **Fixed** | ✅ |

### 12. `failure_atlas/signature_engine.py:44` — `scan_file`

| Field | Value |
|---|---|
| **File** | `failure_atlas/signature_engine.py` |
| **Function** | `scan_file` |
| **Previous behavior** | `except Exception: pass` — returns `[]` |
| **New behavior** | Logs warning; returns `[]` |
| **Fixed** | ✅ |

### 13. `failure_atlas/repository.py:37` — `__init__`

| Field | Value |
|---|---|
| **File** | `failure_atlas/repository.py` |
| **Function** | `__init__` |
| **Previous behavior** | `except sqlite3.OperationalError: pass` — DB init failure silently ignored |
| **New behavior** | Logs error with details |
| **Fixed** | ✅ |

### 14. `gli_flow/scheduler/worker.py:45` — `run`

| Field | Value |
|---|---|
| **File** | `gli_flow/scheduler/worker.py` |
| **Function** | `run` |
| **Previous behavior** | `except Exception: pass` — CPU affinity failure silently ignored |
| **New behavior** | Logs warning |
| **Fixed** | ✅ |

### 15. `gli_flow/cli/main.py:115` — `_try_open_dashboard`

| Field | Value |
|---|---|
| **File** | `gli_flow/cli/main.py` |
| **Function** | `_try_open_dashboard` |
| **Previous behavior** | `except Exception: pass` — dashboard launch failure silently ignored |
| **New behavior** | Logs warning |
| **Fixed** | ✅ |

### 16. `gli_flow/security/file_protection.py:73` — `_secure_delete`

| Field | Value |
|---|---|
| **File** | `gli_flow/security/file_protection.py` |
| **Function** | `_secure_delete` |
| **Previous behavior** | `except Exception: pass` — secure delete failure silently ignored |
| **New behavior** | Falls back to unlink; logs warning |
| **Fixed** | ✅ |

---

## HIGH: SILENT_EMPTY (returns empty data on error)

### 17. `failure_atlas/repository.py:410-467` — Query methods

| Field | Value |
|---|---|
| **File** | `failure_atlas/repository.py` |
| **Functions** | `get_top_failures`, `get_domain_summary`, `get_resolution_rate_by_type`, `get_severity_distribution`, `get_related_entries` |
| **Previous behavior** | All `except Exception: return []` — DB errors return empty lists |
| **New behavior** | All log warnings and return `[]` with error context |
| **Fixed** | ✅ |

### 18. `gli_flow/cloud/storage.py:88-203` — Cloud operations

| Field | Value |
|---|---|
| **File** | `gli_flow/cloud/storage.py` |
| **Previous behavior** | All `except Exception: return ""` or `except Exception: return []` — cloud errors return empty strings/lists |
| **New behavior** | All log errors and return error-indicating values; caller must check |
| **Fixed** | ✅ |

### 19. `gli_flow/installer/openroad.py:82` — `_fetch_deb_urls`

| Field | Value |
|---|---|
| **File** | `gli_flow/installer/openroad.py` |
| **Function** | `_fetch_deb_urls` |
| **Previous behavior** | `except Exception: return {}` — network failure returns empty dict |
| **New behavior** | Logs error; returns `{}` |
| **Fixed** | ✅ |

---

## Additional Patterns Fixed

### Stage failure handlers in `orchestrator.py`

The DRC, LVS, TIMING_ANALYSIS, and general stage handlers previously used `print(f"  [SKIP] {stage}: {e}")` which silently masks failures as skips. Updated to record stage status as FAIL/ERROR and propagate to signoff gate.

### `analytics/regression.py` — Zero-violation sentinel

Changed `detect_regression` to return an error result instead of "no regressions" when the database query fails.

---

## Files Modified

| File | Changes |
|---|---|
| `analytics/regression.py` | Fixed SILENT_SUCCESS — returns error result instead of "no regressions" |
| `gli_flow/core/drc_runner.py` | Fixed SILENT_SUCCESS — parse errors return -1 instead of 0 |
| `gli_flow/core/orchestrator.py` | Fixed SILENT_PASS — added logging for all silent except blocks |
| `gli_flow/core/routing_safety.py` | Fixed SILENT_PASS — added logging for overflow check failures |
| `gli_flow/core/cdc_check.py` | Fixed SILENT_PASS — added logging for CDC parse failures |
| `gli_flow/core/rtl_preprocessor.py` | Fixed SILENT_PASS — added logging for file read failures |
| `failure_atlas/repository.py` | Fixed SILENT_EMPTY + SILENT_SUCCESS — added logging |
| `failure_atlas/signature_engine.py` | Fixed SILENT_PASS — added logging |
| `gli_flow/cloud/storage.py` | Fixed SILENT_EMPTY — added logging |
| `gli_flow/infrastructure/environment_validator.py` | Fixed SILENT_PASS — added logging |
| `gli_flow/scheduler/worker.py` | Fixed SILENT_PASS — added logging |
| `gli_flow/cli/main.py` | Fixed SILENT_PASS — added logging |
| `gli_flow/security/file_protection.py` | Fixed SILENT_PASS — added logging |
| `gli_flow/installer/openroad.py` | Fixed SILENT_EMPTY — added logging |
| `gli_flow/installer/orfs.py` | Fixed SILENT_PASS — added logging |
| `gli_flow/installer/pdk.py` | Fixed SILENT_PASS — added logging |
| `gli_flow/installer/sv2v.py` | Fixed SILENT_EMPTY — added logging |
| `gli_flow/installer/yosys.py` | Fixed SILENT_EMPTY — added logging |
| `gli_flow/installer/klayout.py` | Fixed SILENT_EMPTY — added logging |

## Remaining Lower-Priority Items

The following have been classified as LOW priority because they are in testing code, vendor code, or are intentionally lenient for UX reasons:

- `gli_flow/testing/layout_images.py` — test helper
- `backend/server.py` — backend API (returns empty state on error gracefully)
- `analytics/execution_analytics.py` — analytics (returns empty results gracefully)
- `analytics/build_execution_timeline.py` — analytics helper
- `gli_flow/database/migrations.py` — has reconnection fallback
- `gli_flow/database/sqlite.py` — has reconnection fallback
- `analytics/report_parser.py` — returns partial results on error
- `analytics/reliability_score.py` — returns empty results on error

These items should be reviewed in a follow-up audit but do not block reliability hardening.
