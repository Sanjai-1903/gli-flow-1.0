# CLI Error Handling Audit

**Date:** 2026-06-17
**Scope:** All CLI commands in `gli_flow/cli/main.py`
**Standard:** Structured user-facing errors with ❌ What happened / 💡 Why it happened / 🔧 How to fix it

---

## Audit Summary

| Pattern | Location | Status |
|---------|----------|--------|
| `raise Exception(...)` | None found | ✅ Clean |
| `traceback.print_exc(...)` | `run_command` (old) | ✅ Migrated to `structured_error` |
| `print(traceback)` | None found | ✅ Clean |
| `print_error()` | Multiple commands | ✅ Migrated to `error()` / `structured_error()` |
| `print_warning()` | Multiple commands | ✅ Migrated to `warn()` |
| `friendly_error()` | `run_command` | ✅ Now uses structured format |

---

## Command-by-Command Audit

### `run`
- **Before:** `print_error("Unexpected error:"); traceback.print_exc()` only with `--verbose`
- **After:** `structured_error("Unexpected error", why=str(e), verbose=...)` — shows ❌ + 💡 + 🔧
- **Before:** `friendly_error("manifest")` used bare `print()` to stderr
- **After:** Uses `console.print()` with rich markup for consistent look

### `install`
- **Before:** `[FAIL]`, `[PASS]`, `SKIP` labels (inconsistent with rest of CLI)
- **After:** Uses `success()`, `error()`, `warn()` standardized functions

### `doctor`
- **Before:** `PASS`/`FAIL`/`WARN` status labels in doctor report
- **After:** `READY`/`ERROR`/`WARNING` — clearer semantics
- **Before:** `error_and_exit()` for magic repair failure
- **After:** `structured_error()` with ❌ 💡 🔧 format

### `ci`
- **Before:** `CI PASS` / `CI FAIL` text, `[red]![/red]` for regressions
- **After:** Uses `success()` / `error()` with standardized icons

### `diagnose`
- **Before:** Bare `[red]...[/red]` with local `Console()` instance
- **After:** Uses shared `console`, `error()`, `warn()`, `success()`

### `investigate`
- **Before:** Bare `[red]...[/red]` with local `Console()` instance
- **After:** Uses shared `console`, `structured_error()` for availability failures

### `db`
- **Before:** `[bold red]...[/bold red]` inline
- **After:** Uses `success()`, `error()`, `warn()`

### `cloud`
- **Before:** `[bold red]Upload failed[/bold red]`
- **After:** Uses `error("Upload failed")` with consistent icon

### `remote`
- **Before:** `Connection OK` / `FAILED` inline
- **After:** Uses `success()` / `error()` with consistent icons

### `init` / `quickstart`
- **Before:** `[OK] Created ...` with bare `print()`
- **After:** Uses `success()` with rich formatting

### `reset-runs`
- **Before:** `[bold red]WARNING[/bold red]` inline
- **After:** Uses `warn()` / `success()` / `error()` standardized functions

### `telemetry`
- **Before:** Bare `print()` in subcommands
- **After:** Uses `info()`, `success()`, `warn()`, `error()`

### `warehouse`
- **Before:** Bare `print()` 
- **After:** Uses `info()`, `section_header()`, `warn()`, `error()`

### `escalate`
- **Before:** `[red]ERROR:[/red]`
- **After:** Uses `error()` standardized

### `config`
- **Before:** `[green]...[/green]` inline
- **After:** Uses `success()` standardized

---

## Structured Error Format

All errors follow one of these patterns:

### `structured_error()` — Fatal errors
```
❌ What happened
💡 Why it happened
🔧 Fix: How to fix it
```

### `error()` — Non-fatal errors
```
✗ Message
```

### `warn()` — Warnings
```
⚠ Message
```

### `success()` — Success messages
```
✓ Message
```

### `info()` — Informational
```
ℹ Message
```

---

## Stack Trace Policy

- **Default mode:** No Python traceback visible to users
- **`--verbose` flag:** Shows full traceback via `console.print_exception()`
- Commands with `--verbose`: `run`, `install`, `doctor`, `diagnose`, `investigate`, `investigate-migrate`, `reset-runs`, `telemetry health`

---

## Common Failure Patterns Covered

| Failure | 🅧 What | 💡 Why | 🔧 Fix |
|---------|---------|--------|--------|
| Missing manifest | Directory/design not found | Design needs a manifest | `gli-flow init <design>` |
| Missing PDK_ROOT | PDK_ROOT not set | PDK tells tools how to build chip | `export PDK_ROOT=...` |
| Missing tool | Tool not found | Tool not installed | `gli-flow install` |
| Env validation | Env check failed | Missing system requirements | `gli-flow doctor --fix` |
| Run failed | Flow failed | Various per-stage causes | `gli-flow diagnose <run>` |
| Investigation unavailable | Cannot investigate | Missing API key or config | Set `GLI_FLOW_LLM_API_KEY` |
