import shutil
import sys
import subprocess
import importlib.util
from pathlib import Path

from gli_flow.cli.utils import info, success, warn, error
from gli_flow.config_validator import validate_manifest


# Tool classification
MOCK_MODE_CHECKS = ["python"]  # Python is checked inline
REAL_FLOW_TOOLS = [
    ("yosys", "-V"),
    ("openroad", "-version"),
    ("magic", "--version"),
    ("netgen", ["-batch", "quit"]),
    ("klayout", "-v"),
    ("sv2v", "--version"),
]
OPTIONAL_CHECKS = ["dashboard_deps", "node", "npm"]


def run_smoke_test(args):
    info("Running smoke test...\n")

    mock_pass, mock_items = _check_mock_mode(args)
    real_tools = _check_real_flow_tools()
    optional_items = _check_optional(args)

    _print_redesign(mock_pass, mock_items, real_tools, optional_items)

    if not mock_pass:
        sys.exit(1)


def _check_mock_mode(args):
    """Check everything needed for mock mode. Returns (pass, items)."""
    items = []

    # Python
    py = sys.version_info
    py_ok = py.major >= 3 and py.minor >= 9
    ver_str = f"{py.major}.{py.minor}.{py.micro}"
    items.append(("Python", py_ok, ver_str if py_ok else f"{ver_str} (3.9+ required)"))

    # Database
    db_ok = False
    db_detail = ""
    try:
        from gli_flow.database.migrations import _get_db_path, migrate_if_needed

        db_path = getattr(args, 'db_path', None) or _get_db_path()
        if db_path and Path(db_path).exists():
            db_detail = f"Database at {db_path}"
        elif db_path:
            db_detail = "Database location configured (will be created on first run)"
        else:
            db_detail = "Database path configured"

        migrate_if_needed(db_path)
        db_ok = True
        from gli_flow.database.migrations import MigrationEngine, RUNS_MIGRATIONS, FAILURE_ATLAS_MIGRATIONS
        engine = MigrationEngine(db_path)
        db_ok = engine.validate_schema("runs", RUNS_MIGRATIONS) and engine.validate_schema("failure_atlas", FAILURE_ATLAS_MIGRATIONS)
        engine.close()
    except Exception:
        db_detail = "Database error: could not connect or migrate"

    items.append(("Database", db_ok, db_detail))

    # Telemetry config
    telemetry_ok = False
    telemetry_detail = ""
    try:
        from gli_flow.telemetry.settings import get_telemetry_settings
        settings = get_telemetry_settings()
        telemetry_detail = f"Config readable (mode: {settings.mode})"
        telemetry_ok = True
    except Exception:
        telemetry_detail = "Telemetry error: could not read configuration"
    items.append(("Telemetry", telemetry_ok, telemetry_detail))

    # Example design
    manifest_path = Path("examples/counter/gli_manifest.yaml")
    if not manifest_path.exists():
        manifest_path = Path(__file__).parent.parent.parent / "examples" / "counter" / "gli_manifest.yaml"

    design_ok = manifest_path.exists()
    design_detail = ""
    if design_ok:
        ok, msg = validate_manifest(manifest_path)
        design_ok = ok
        design_detail = "Manifest valid" if ok else f"Manifest invalid: {msg}"
    else:
        design_detail = "Example design not found"

    items.append(("Example Designs", design_ok, design_detail))

    all_pass = all(ok for _, ok, _ in items)
    return all_pass, items


def _check_real_flow_tools():
    """Check EDA tools for real ASIC flow. Never fails the smoke test."""
    results = []
    for name, flag in REAL_FLOW_TOOLS:
        version = _tool_version(name, flag)
        if version is not None:
            results.append((name, True, version))
        else:
            results.append((name, False, f"{name} not found — required only for real ASIC runs"))
    return results


def _check_optional(args):
    """Check optional dependencies. Never fails the smoke test."""
    results = []

    # Dashboard backend deps
    backend_deps = ["fastapi", "uvicorn"]
    missing = []
    for dep in backend_deps:
        if importlib.util.find_spec(dep) is not None:
            pass  # Found, no need to mention each
        else:
            missing.append(dep)
    if missing:
        results.append(("Dashboard deps", False, "Missing: " + ", ".join(missing) + " — pip install gli-flow[dashboard]"))
    else:
        results.append(("Dashboard deps", True, "Backend dependencies installed"))

    # Node.js
    node_v = _tool_version("node", "--version")
    if node_v is not None:
        results.append(("Node.js", True, node_v))
    else:
        results.append(("Node.js", False, "Not found — frontend dev server unavailable (use --backend-only)"))

    # npm
    npm_v = _tool_version("npm", "--version")
    if npm_v is not None:
        results.append(("npm", True, npm_v))
    else:
        results.append(("npm", False, "Not found — frontend dev server unavailable"))

    return results


def _print_redesign(mock_pass, mock_items, real_tools, optional_items):
    from rich.console import Console
    console = Console()

    console.print("[bold]Smoke Test — GLI-FLOW Environment Check[/bold]")
    console.print()

    # Section 1: Mock-Mode Ready
    mock_icon = "[green]✓[/green]" if mock_pass else "[red]✗[/red]"
    mock_color = "green" if mock_pass else "red"
    console.print(f"  [{mock_color}]{'Mock-Mode Ready' if mock_pass else 'Mock-Mode Issues'}[/{mock_color}]")
    for name, ok, detail in mock_items:
        icon = "[green]✓[/green]" if ok else "[red]✗[/red]"
        color = "green" if ok else "red"
        detail_str = f"  {icon} [{color}]{name}[/{color}] — {detail}"
        console.print(detail_str)

    console.print()
    console.print("  [bold]Real ASIC Flow:[/bold]")
    for name, ok, detail in real_tools:
        icon = "[green]✓[/green]" if ok else "[yellow]⚠[/yellow]"
        color = "green" if ok else "yellow"
        console.print(f"  {icon} [{color}]{name}[/{color}] — {detail}")

    console.print()
    console.print("  [bold]Optional:[/bold]")
    for name, ok, detail in optional_items:
        icon = "[green]✓[/green]" if ok else "[dim]—[/dim]"
        color = "green" if ok else "dim"
        console.print(f"  {icon} [{color}]{name}[/{color}] — {detail}")

    console.print()
    if mock_pass:
        console.print("[bold green]✓ Mock-mode ready.[/bold green] Add EDA tools for real ASIC runs.")
        console.print()
        console.print("Next:")
        console.print("  [bold green]gli-flow run examples/counter --mock[/bold green]  — Run a test design")
        console.print("  [bold green]gli-flow dashboard[/bold green]                     — Open the web dashboard")
        console.print("  [bold green]gli-flow doctor[/bold green]                        — Full environment details")
    else:
        console.print("[bold red]✗ Mock-mode requirements not met. See issues above.[/bold red]")
        console.print()
        console.print("Next:")
        console.print("  [bold green]gli-flow doctor[/bold green]        — Detailed environment report")
        console.print("  [bold green]gli-flow doctor --fix[/bold green]  — Auto-repair detected issues")


def _tool_version(tool_name, version_flags):
    path = shutil.which(tool_name)
    if not path:
        return None
    if isinstance(version_flags, str):
        version_flags = [version_flags]
    try:
        result = subprocess.run(
            [tool_name] + list(version_flags),
            capture_output=True, text=True, timeout=10,
        )
        version = (result.stdout or result.stderr or "").strip()
        parts = version.split("\n")[0].strip()
        return parts[:60] if parts else None
    except Exception:
        return None
