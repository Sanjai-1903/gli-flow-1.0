import traceback
from rich.console import Console

console = Console()


def info(message: str):
    console.print(f"[bold cyan]ℹ[/bold cyan] {message}")


def success(message: str):
    console.print(f"[bold green]✓[/bold green] {message}")


def warn(message: str):
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def error(message: str):
    console.print(f"[bold red]✗[/bold red] {message}")


def error_and_exit(message: str, fix: str = None, verbose: bool = False):
    console.print(f"\n[bold red]✗ Error:[/bold red] {message}")
    if fix:
        console.print(f"\n[bold]🔧 Fix:[/bold] {fix}")
    if verbose:
        console.print_exception()
    exit(1)


def structured_error(what: str, why: str = None, fix: str = None, verbose: bool = False):
    console.print(f"\n[bold red]❌ {what}[/bold red]")
    if why:
        console.print(f"\n[bold yellow]💡 Why:[/bold yellow] {why}")
    if fix:
        console.print(f"\n[bold cyan]🔧 How GLI-FLOW will fix it:[/bold cyan] {fix}")
    console.print(f"\n[bold]User action required:[/bold] Run 'gli-flow doctor --fix' or see details above.")
    if verbose:
        console.print_exception()
    exit(1)


def section_header(title: str):
    console.print(f"\n[bold]{title}[/bold]")
