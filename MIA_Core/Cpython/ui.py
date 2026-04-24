# Cpython/ui.py
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel

console = Console()


def info(msg):
    console.print(f"[cyan]ℹ️[/cyan] {msg}")


def success(msg):
    console.print(f"[green]✅[/green] {msg}")


def warning(msg):
    console.print(f"[yellow]⚠️[/yellow] {msg}")


def error(msg):
    console.print(f"[red]❌[/red] {msg}")


def step(msg):
    console.print(f"[bold blue]▶[/bold blue] {msg}")


def header(title):
    console.print(Panel(f"[bold white]{title}[/bold white]", border_style="blue"))


def create_progress():
    return Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    )
