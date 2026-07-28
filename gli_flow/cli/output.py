from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.columns import Columns
from rich import box

console = Console()

LVS_DISCLAIMER = (
    "LVS PASS verifies that the physical layout matches the schematic netlist.\n"
    "It does NOT verify functional correctness, timing, or that the RTL behaves as intended.\n"
    "Functional verification (simulation/formal) must be completed separately before tapeout."
)


def print_banner():
    console.print()
    console.print("[bold green]  GLI-FLOW  [/bold green] [dim]RTL-to-GDS Digital Design Flow[/dim]")
    console.print("[dim]Open-source ASIC implementation flow[/dim]")


def print_next_step(steps: list):
    if not steps:
        return
    console.print()
    console.print("[bold]Next:[/bold]")
    for s in steps:
        console.print(f"  [bold green]{s}[/bold green]")
    console.print()


def print_run_header(run_id, design_name, run_dir):
    layout = Layout()
    layout.split_row(
        Layout(Panel(f"[bold]Run ID[/bold]\n{run_id}", box=box.ROUNDED)),
        Layout(Panel(f"[bold]Design[/bold]\n{design_name}", box=box.ROUNDED)),
        Layout(Panel(f"[bold]Output[/bold]\n{run_dir}", box=box.ROUNDED)),
    )
    console.print(layout)
    console.print()


def print_stage_progress(stage, progress, status="RUNNING"):
    color = {"RUNNING": "yellow", "SUCCESS": "green", "FAILED": "red"}.get(status, "white")
    bar_len = 20
    filled = int(progress / 100 * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    console.print(f"  [{color}]{stage:<18}[/{color}] {bar} {progress:>3}%")


def print_results(record):
    table = Table(box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    qor_color = "green" if record.qor_score and record.qor_score >= 0.7 else "red"
    table.add_row("QoR Score", f"[{qor_color}]{record.qor_score}[/{qor_color}]")
    table.add_row("WNS", str(record.wns) if record.wns is not None else "N/A")
    table.add_row("TNS", str(record.tns) if record.tns is not None else "N/A")
    hold_wns = getattr(record, "hold_wns", None)
    if hold_wns is not None:
        hold_color = "green" if hold_wns >= 0 else "red"
        hold_label = "✓" if hold_wns >= 0 else "✗ TAPEOUT BLOCKER"
        table.add_row("Hold WNS", f"[{hold_color}]{hold_wns:.3f} ns {hold_label}[/{hold_color}]")
    table.add_row("Utilization", f"{record.utilization}%" if record.utilization is not None else "N/A")
    table.add_row("Cell Count", str(record.cell_count) if record.cell_count is not None else "N/A")
    table.add_row("Runtime", f"{record.runtime_sec}s" if record.runtime_sec is not None else "N/A")

    console.print(table)

    lvs_is_clean = getattr(record, "lvs_is_clean", None)
    if lvs_is_clean is True:
        console.print(f"  [green]✓ LVS PASS[/green]")
        console.print(f"\n  [dim]ℹ {LVS_DISCLAIMER}[/dim]")
    elif lvs_is_clean is False:
        console.print(f"  [red]✗ LVS FAIL[/red]")

    console.print()


def print_regression(regression):
    if not regression["regression_detected"]:
        return
    console.print("[bold yellow]⚠ REGRESSION ALERTS[/bold yellow]")
    for alert in regression["alerts"]:
        console.print(f"  [yellow]![/yellow] {alert}")
    console.print()


def print_run_history(runs):
    if not runs:
        console.print("[dim]No runs found.[/dim]")
        return

    table = Table(box=box.SIMPLE)
    table.add_column("Run ID", style="cyan", no_wrap=True)
    table.add_column("Design", style="green")
    table.add_column("Status", style="white")
    table.add_column("QoR", style="white")
    table.add_column("Timestamp")

    for run in runs:
        qor = f"{run['qor_score']:.2f}" if run.get("qor_score") is not None else "N/A"
        status_color = {
            "SUCCESS": "green",
            "FAILED": "red",
            "TIMEOUT": "yellow",
            "RUNNING": "cyan",
        }.get(run.get("status", ""), "white")

        table.add_row(
            run.get("run_id", "")[:20],
            run.get("design_name", ""),
            f"[{status_color}]{run.get('status', '')}[/{status_color}]",
            qor,
            run.get("timestamp", ""),
        )

    console.print(table)


def print_report(metrics):
    console.print("[bold]QoR Report[/bold]")
    console.print()

    grid = Table.grid(padding=(0, 2))
    grid.add_column()
    grid.add_column()

    left = Table(box=box.SIMPLE)
    left.add_column("Metric", style="cyan")
    left.add_column("Value", style="white")

    right = Table(box=box.SIMPLE)
    right.add_column("Metric", style="cyan")
    right.add_column("Value", style="white")

    def v(val, fmt=None):
        if val is None:
            return "N/A"
        if fmt:
            return fmt(val)
        return str(val)

    def color_slack(s):
        if s is None or s == "N/A":
            return "N/A"
        s = float(s)
        c = "green" if s >= 0 else "red"
        return f"[{c}]{s:.3f}[/{c}]"

    left.add_row("Design", metrics.get("design", "N/A"))
    left.add_row("Platform", metrics.get("platform", "N/A"))
    left.add_row("Die Area", v(metrics.get("die_area_um2"), lambda x: f"{x:,.0f} µm²"))
    left.add_row("Cell Area", v(metrics.get("cell_area_um2"), lambda x: f"{x:,.0f} µm²"))
    left.add_row("Utilization", v(metrics.get("utilization_pct"), lambda x: f"{x:.1f}%"))
    left.add_row("Cell Count", v(metrics.get("cell_count"), lambda x: f"{x:,}"))
    left.add_row("Port Bits (Pins)", v(metrics.get("pin_count")))
    left.add_row("---", "---")
    left.add_row("Worst Slack", v(metrics.get("worst_slack"), color_slack))
    left.add_row("WNS", v(metrics.get("wns"), color_slack))
    left.add_row("TNS", v(metrics.get("tns"), color_slack))
    left.add_row("Critical Path", v(metrics.get("critical_path_ns"), lambda x: f"{x:.2f} ns"))
    left.add_row("Fmax", v(metrics.get("fmax_mhz"), lambda x: f"{x:.0f} MHz"))

    right.add_row("Total Power", v(metrics.get("total_power_w"), lambda x: f"{x*1000:.1f} mW"))
    right.add_row("  Sequential", v(metrics.get("seq_power_w"), lambda x: f"{x*1000:.1f} mW"))
    right.add_row("  Combinational", v(metrics.get("comb_power_w"), lambda x: f"{x*1000:.1f} mW"))
    right.add_row("  Clock", v(metrics.get("clock_power_w"), lambda x: f"{x*1000:.1f} mW"))
    right.add_row("---", "---")
    right.add_row("Setup Violations", v(metrics.get("setup_violations")))
    right.add_row("Hold Violations", v(metrics.get("hold_violations")))
    right.add_row("Max Fanout Violations", v(metrics.get("fanout_violations")))
    right.add_row("Max Cap Violations", v(metrics.get("cap_violations")))
    right.add_row("Max Slew Violations", v(metrics.get("slew_violations")))
    right.add_row("---", "---")
    right.add_row("Clock Skew", v(metrics.get("clock_skew_ns"), lambda x: f"{x:.3f} ns"))
    right.add_row("Runtime", v(metrics.get("runtime_sec"), lambda x: f"{x:.0f}s"))

    grid.add_row(left, right)
    console.print(grid)
    console.print()

    if metrics.get("setup_violations") and int(metrics["setup_violations"]) > 0:
        console.print("[red]✗[/red] Setup violations present — design may not meet timing")
    if metrics.get("hold_violations") and int(metrics["hold_violations"]) > 0:
        console.print("[yellow]⚠[/yellow] Hold violations present — may require ECO fixes")
    if metrics.get("fanout_violations") and int(metrics["fanout_violations"]) > 0:
        console.print("[yellow]⚠[/yellow] Fanout violations present — clock tree may need tuning")


def print_install_report(report):
    console.print("[bold]Installation Summary[/bold]")
    console.print()

    for name in report.completed:
        console.print(f"  [green]✓[/green] {name}")
    for name in report.skipped:
        console.print(f"  [dim]─[/dim] {name} [dim](already installed)[/dim]")
    for name in report.failed:
        console.print(f"  [red]✗[/red] {name}")

    console.print()
    console.print("[bold]Validation Results[/bold]")

    table = Table(box=box.SIMPLE)
    table.add_column("Tool", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Version", style="white")

    for v in report.validations:
        status = "[green]✓[/green]" if v.ok else "[red]✗[/red]"
        table.add_row(v.tool, status, v.version or "—")

    console.print(table)
    console.print()

    if report.success:
        console.print("[bold green]✓ All components installed successfully[/bold green]")
    else:
        console.print(f"[bold red]✗ {len(report.failed)} component(s) failed[/bold red]")


def print_achievement_summary(record, elapsed=None):
    timing = ""
    if elapsed:
        timing = f" in [cyan]{elapsed:.0f}s[/cyan]"

    if getattr(record, "status", "") == "SUCCESS":
        qor = getattr(record, "qor_score", None)
        qor_str = f"  QoR Score: [bold green]{qor:.3f}[/bold green]" if qor is not None else ""

        tapeout = getattr(record, "tapeout_ready", False)
        tapeout_str = "  [bold green]✓ Tapeout Ready[/bold green]" if tapeout else ""

        drc_clean = getattr(record, "drc_is_clean", None)
        drc_str = "  [green]✓ DRC Clean[/green]" if drc_clean else ""

        lvs_clean = getattr(record, "lvs_is_clean", None)
        lvs_str = "  [green]✓ LVS Clean[/green]" if lvs_clean else ""

        body = f"[bold green]✓ Run completed successfully[/bold green]{timing}\n"
        if qor_str:
            body += f"\n{qor_str}"
        if tapeout_str:
            body += f"\n{tapeout_str}"
        if drc_str:
            body += f"\n{drc_str}"
        if lvs_str:
            body += f"\n{lvs_str}"

        console.print()
        console.print(Panel(body, border_style="green"))
    else:
        console.print()
        console.print(Panel(
            f"[bold red]✗ Flow failed[/bold red]{timing}\n\n"
            f"  Check diagnosis: [bold green]gli-flow diagnose {getattr(record, 'run_id', '<run_id>')}[/bold green]\n"
            f"  Generate support bundle: [bold green]gli-flow support-bundle --run-id {getattr(record, 'run_id', '<run_id>')}[/bold green]",
            border_style="red",
        ))
    console.print()


def print_first_run_guide():
    console.print()
    console.print(Panel(
        "[bold]Common Workflows[/bold]\n\n"
        "  First Time:\n"
        "    [bold green]gli-flow doctor[/bold green]\n"
        "    [bold green]gli-flow run counter[/bold green]\n\n"
        "  Investigate Failure:\n"
        "    [bold green]gli-flow diagnose <run>[/bold green]\n\n"
        "  Telemetry:\n"
        "    [bold green]gli-flow telemetry status[/bold green]\n\n"
        "  Support:\n"
        "    [bold green]gli-flow support-bundle[/bold green]\n\n"
        "  [dim]Run [bold]gli-flow --help[/bold] to see all available commands.[/dim]",
        title="Welcome to GLI-FLOW",
        border_style="cyan",
    ))
    console.print()


AI_BORDER_STYLE = "purple"


def print_ai_assistant_header():
    console.print()
    console.print(Panel(
        "[bold]AI Investigation Assistant[/bold]\n"
        "[dim]Experimental Feature[/dim]",
        border_style=AI_BORDER_STYLE,
    ))
    console.print()


def print_ai_response(response: dict):
    resp = response.get("response", response)
    trigger = response.get("trigger", {})

    if not resp:
        console.print("[yellow]No AI investigation response available.[/yellow]")
        return

    confidence = resp.get("confidence", "LOW")
    conf_color = {"LOW": "yellow", "MEDIUM": "blue"}.get(confidence, "yellow")
    console.print(Panel(
        f"[bold]Confidence: [{conf_color}]{confidence}[/{conf_color}][/bold]\n"
        f"[dim]AI GENERATED  ·  EXPERIMENTAL  ·  NOT VERIFIED[/dim]",
        border_style=AI_BORDER_STYLE,
    ))

    reasons = trigger.get("reasons", [])
    if reasons:
        console.print()
        console.print("[bold]Trigger:[/bold]")
        for r in reasons:
            icon = "✓" if "Known" in r or "historical" in r else " "
            console.print(f"  [{AI_BORDER_STYLE}]{icon}[/{AI_BORDER_STYLE}] {r}")

    summary = resp.get("summary", "")
    if summary:
        console.print()
        console.print(f"[bold]Summary:[/bold] {summary}")

    causes = resp.get("possible_causes", [])
    if causes:
        console.print()
        console.print("[bold]Possible Causes:[/bold]")
        for i, cause in enumerate(causes, 1):
            console.print(f"  [{AI_BORDER_STYLE}]{i}.[/{AI_BORDER_STYLE}] {cause}")

    steps = resp.get("investigation_steps", [])
    if steps:
        console.print()
        console.print("[bold]Suggested Investigation Steps:[/bold]")
        for i, step in enumerate(steps, 1):
            console.print(f"  [{AI_BORDER_STYLE}]{i}.[/{AI_BORDER_STYLE}] {step}")

    refs = resp.get("references", [])
    if refs:
        console.print()
        console.print("[bold]References:[/bold]")
        for ref in refs:
            console.print(f"  [{AI_BORDER_STYLE}]→[/{AI_BORDER_STYLE}] {ref}")

    console.print()
    console.print(Panel(
        "[yellow]This guidance is AI-generated and may be incorrect.\n"
        "Always verify findings with manual inspection.[/yellow]\n"
        "[dim]AI GENERATED  ·  EXPERIMENTAL  ·  NOT VERIFIED[/dim]",
        border_style=AI_BORDER_STYLE,
    ))

    console.print()
    console.print("[dim]Was this helpful? Provide feedback via:[/dim]")
    console.print(f"  [bold green]gli-flow ai-assist --feedback <investigation_id> --helpful[/bold green]")
    console.print(f"  [bold green]gli-flow ai-assist --feedback <investigation_id> --not-helpful[/bold green]")


def print_ai_diagnose_display(run_id: str, ai_result: dict):
    resp = ai_result.get("response", {})
    trigger = ai_result.get("trigger", {})

    if trigger.get("use_ai"):
        console.print()
        console.print(Panel(
            "[bold]Unknown Failure — AI Investigation Assistant[/bold]\n"
            "[dim]No signature or historical intelligence found.[/dim]\n"
            "[dim]AI GENERATED  ·  EXPERIMENTAL  ·  NOT VERIFIED[/dim]",
            border_style=AI_BORDER_STYLE,
        ))
        print_ai_response(ai_result)
    else:
        console.print(f"\n[green]✓ Failure recognized by Failure Atlas — no AI needed.[/green]")


def print_escalation_header():
    console.print()
    console.print(Panel(
        "[bold]Community Intelligence — Escalation[/bold]\n\n"
        "Unknown failures can be escalated to GLI engineers for analysis.\n"
        "This helps build the collective Failure Atlas knowledge base.",
        border_style="cyan",
    ))
    console.print()


def print_escalation_result(escalation: dict):
    esc_id = escalation.get("id", "—")
    status = escalation.get("status", "unknown")
    failure_type = escalation.get("failure_type", "—")
    tool = escalation.get("tool", "—")
    stage = escalation.get("stage", "—")
    bcid = escalation.get("bharatcode_submission_id", "")
    created = escalation.get("created_at", "—")

    color = "green" if status == "submitted" else "yellow"
    console.print(Panel(
        f"[bold]Escalation ID:[/bold] {esc_id}\n"
        f"[bold]Status:[/bold] [{color}]{status}[/{color}]\n"
        f"[bold]Failure:[/bold] {failure_type} ({tool}/{stage})\n"
        + (f"[bold]BharatCode ID:[/bold] {bcid}\n" if bcid else "")
        + f"[bold]Created:[/bold] {created}",
        title="Escalation",
        border_style="cyan",
    ))
    console.print()
