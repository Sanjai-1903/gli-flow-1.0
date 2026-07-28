from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from gli_flow.telemetry.settings import get_telemetry_settings, TelemetryMode

console = Console()

def run_telemetry_wizard():
    console.print()
    console.print(Panel(
        "[bold cyan]Welcome to GLI-FLOW Telemetry[/bold cyan]\n\n"
        "GLI-FLOW collects sanitized execution telemetry to improve:\n"
        "  • [bold]Failure Atlas[/bold] (community failure knowledge)\n"
        "  • [bold]Resolution Intelligence[/bold] (AI-driven fixes)\n"
        "  • [bold]Trust Scoring[/bold] (verifying tool results)\n"
        "  • [bold]Product Quality[/bold]\n\n"
        "[bold green]Privacy Guarantee:[/bold green]\n"
        "GLI-FLOW [underline]NEVER[/underline] uploads RTL, Verilog, SystemVerilog, VHDL, Netlists,\n"
        "DEF, LEF, GDS, Bitstreams, Liberty Files, or Constraint Contents.",
        border_style="cyan",
    ))
    console.print()

    console.print("[bold]Choose your Telemetry Mode:[/bold]")
    console.print("  [bold green]1. Full Sanitized Telemetry[/bold green] [Recommended]")
    console.print("     Uploads runtime metrics, failure signatures, root causes,\n"
                  "     resolution outcomes, and design fingerprints.")
    console.print("  [bold yellow]2. Failure Atlas Only[/bold yellow]")
    console.print("     Uploads only failure fingerprints and root causes.")
    console.print("  [bold white]3. Local Only[/bold white]")
    console.print("     Nothing ever leaves your machine.")
    console.print()

    choice = Prompt.ask(
        "Select a mode",
        choices=["1", "2", "3"],
        default="1"
    )

    settings = get_telemetry_settings()
    
    if choice == "1":
        settings.mode = TelemetryMode.FULL
        console.print("[green]Full Telemetry enabled.[/green]")
    elif choice == "2":
        settings.mode = TelemetryMode.ATLAS
        console.print("[yellow]Failure Atlas Only mode enabled.[/yellow]")
    else:
        settings.mode = TelemetryMode.LOCAL
        console.print("Local Only mode enabled. No data will be uploaded.")

    settings.consent_given = True
    settings.save()

    console.print("\n[bold green]✓ Settings saved.[/bold green] You can change this anytime with [bold]gli-flow telemetry mode[/bold].\n")
