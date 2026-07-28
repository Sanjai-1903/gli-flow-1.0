# CLI Output Consistency Report

**Date:** 2026-06-17
**Standard:** ℹ INFO / ✓ SUCCESS / ⚠ WARNING / ✗ ERROR (unified globally)

---

## Unified Icon System

| Icon | Meaning | Function | Color |
|------|---------|----------|-------|
| ℹ | Info | `info()` | Cyan |
| ✓ | Success | `success()` | Green |
| ⚠ | Warning | `warn()` | Yellow |
| ✗ | Error | `error()` | Red |

---

## Command-by-Command Output Audit

### ✅ `run`
| Before | After |
|--------|-------|
| `Running GLI-FLOW` banner | `GLI-FLOW` banner (unchanged) |
| `[bold green]✓ Flow completed successfully[/bold green]` | `✓ Run completed successfully` |
| `[bold red]✗ Flow failed[/bold red]` | `✗ Flow failed` |
| `Unexpected error: ...` + traceback | `❌ Unexpected error` + 💡 + 🔧 |
| No next-step guidance | `Next: gli-flow dashboard` (on success) |
| | `Next: gli-flow diagnose <run>` (on failure) |

### ✅ `doctor`
| Before | After |
|--------|-------|
| `PASS` | `READY` |
| `FAIL` | `ERROR` |
| `WARN` | `WARNING` |
| `READY FOR TAPEOUT FLOW` | `✓ Environment is READY` |
| `NOT READY (1 failure(s))` | `✗ Environment has ERRORS` |
| `READY WITH WARNINGS` | `⚠ Environment has WARNINGS` |
| No next-step | `Next: gli-flow run counter --mock` |

### ✅ `install`
| Before | After |
|--------|-------|
| `PASS` label | `✓` success icon |
| `FAIL` label | `✗` error icon |
| `SKIP` label | `─ (already installed)` |
| `[FAIL] tool: error` | `✗ tool: error` |

### ✅ `ci`
| Before | After |
|--------|-------|
| `[bold green]CI PASS[/bold green]` | `✓ CI PASS` |
| `[bold red]CI FAIL[/bold red]` | `✗ CI FAIL` |
| `[red]![/red]` regression | `✗` regression |
| No next-step | `Next: gli-flow report <design>` |

### ✅ `history`
| Before | After |
|--------|-------|
| `Run History` (bold text) | `Run History` (section header) |
| No next-step | `Next: gli-flow run <design>` |

### ✅ `status`
| Before | After |
|--------|-------|
| `Recent Runs` (bold text) | `Recent Runs` (section header) |
| No next-step | `Next: gli-flow run <design>` |

### ✅ `batch`
| Before | After |
|--------|-------|
| `[dim]Queued:[/dim]` | `ℹ Queued:` |
| `OK` / `FAIL` on progress | `✓` / `✗` on progress |
| `Batch Complete: X succeeded, Y failed` | `✓ Batch Complete` |

### ✅ `diagnose`
| Before | After |
|--------|-------|
| `[red]Run not found[/red]` | `✗ Run not found` |
| `[yellow]No pattern detected[/yellow]` | `⚠ No pattern detected` |
| `[green]Analysis complete[/green]` | `✓ Analysis complete` |
| No next-step | `Next: gli-flow investigate <run>` |

### ✅ `investigate`
| Before | After |
|--------|-------|
| `[red]unavailable[/red]` | `❌ Investigation unavailable` |
| `[green]✓ Investigation complete[/green]` | `✓ Investigation complete` |
| `[red]Investigation failed[/red]` | `✗ Investigation failed` |
| Internal paths (saved_path, history) | Behind `--verbose` |
| No next-step | `Next: gli-flow diagnose <run_id>` |

### ✅ `db`
| Before | After |
|--------|-------|
| `[green]v1[/green] applied` | `✓ v1 applied` |
| `[bold green]Migrated[/bold green]` | `✓ Migrated` |
| `[bold red]Migration failed[/bold red]` | `✗ Migration failed` |
| `[green]Schema is up to date[/green]` | `✓ Schema is up to date` |

### ✅ `setup`
| Before | After |
|--------|-------|
| `[green]✓[/green] PDK root` | `✓ PDK root` |
| `[yellow]⚠ PDK root does not exist[/yellow]` | `⚠ PDK root does not exist` |
| Panel with next steps | `Next: gli-flow doctor` |

### ✅ `init` / `quickstart`
| Before | After |
|--------|-------|
| `[OK] Created ...` | `✓ Created ...` |
| `Next steps:` bullet | `Next: ...` standardized |

### ✅ `reset-runs`
| Before | After |
|--------|-------|
| `[bold red]WARNING[/bold red]` | `⚠` |
| `[bold green]Reset complete[/bold green]` | `✓ Reset complete` |
| `[yellow]Reset cancelled[/yellow]` | `⚠ Reset cancelled` |

### ✅ `telemetry`
| Before | After |
|--------|-------|
| Bare `print()` | `info()`, `success()`, `warn()` |
| `[bold green]Enabled[/bold green]` | `✓ Telemetry enabled` |
| `[bold yellow]Disabled[/bold yellow]` | `⚠ Telemetry disabled` |

### ✅ `escalate`
| Before | After |
|--------|-------|
| `[red]ERROR:[/red]` | `✗ Error:` |
| `[green]✓ Failure recognized[/green]` | `✓ Failure recognized` |
| `[bold green]✓[/bold green] Escalation submitted` | `✓ Escalation submitted` |

### ✅ `config`
| Before | After |
|--------|-------|
| `[green]Telemetry set[/green]` | `✓ Telemetry set` |
| `Telemetry: on` | `ℹ Telemetry: on` |

### ✅ `cloud`
| Before | After |
|--------|-------|
| `[bold green]Uploaded[/bold green]` | `✓ Uploaded` |
| `[bold red]Upload failed[/bold red]` | `✗ Upload failed` |
| `[bold]Cloud Runs[/bold]` | `Cloud Runs` (section header) |

### ✅ `remote`
| Before | After |
|--------|-------|
| `[bold green]Connection OK[/bold green]` | `✓ Connection OK` |
| `[bold red]FAILED[/bold red]` | `✗ Connection FAILED` |
| `[bold green]SUCCESS[/bold green]` | `✓ Run completed` |

### ✅ `support-bundle`
| Before | After |
|--------|-------|
| `[cyan]Generating[/cyan]` | `ℹ Generating` |
| `[green]✓[/green] written` | `✓ Support bundle written` |
| No next-step | `Next: gli-flow doctor` |

### ✅ `upgrade-check`
| Before | After |
|--------|-------|
| `[dim]Current version[/dim]` | `ℹ Current version` |
| `[yellow]⚠ Newer version[/yellow]` | `⚠ Newer version` |
| `[green]✓ Up to date[/green]` | `✓ Up to date` |

### ✅ `ai-assist`
| Before | After |
|--------|-------|
| `[green]✓ Feedback recorded: Helpful[/green]` | `✓ Feedback recorded: Helpful` |
| `[yellow]No feedback found[/yellow]` | `⚠ No feedback found` |
| `[green]✓ Failure recognized[/green]` | `✓ Failure recognized` |

---

## Style Rules Enforced

1. **Capitalization:** Sentence case for all messages (first word capitalized, rest lowercase unless proper noun)
2. **Punctuation:** No trailing periods on short messages; periods on multi-sentence messages
3. **Spacing:** Single space after icon; consistent 2-space indentation for nested items
4. **Icons:** Only ℹ, ✓, ⚠, ✗ — no other status markers
5. **Format:** Icons are bold + colored; message text is default weight + default color
6. **Sections:** `section_header()` for bold section titles with newline before
7. **Next steps:** `print_next_step()` with green command suggestions, always at end of command
