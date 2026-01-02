"""CLI interface using Typer and Rich."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

from . import __version__
from .agent import ModernizationConfig, ModernizerAgent
from .analyze import analyze_file, get_code_stats, list_python_files
from .validate import run_tests, validate_syntax

app = typer.Typer(
    name="modernizer",
    help="AI-powered legacy Python code modernizer",
    add_completion=False,
)
console = Console()
logging.basicConfig(level=logging.WARNING)


def version_callback(value: bool):
    if value:
        console.print(f"[bold blue]Legacy AI Modernizer[/] v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool, typer.Option("--version", "-v", callback=version_callback, is_eager=True)
    ] = False,
):
    """Legacy AI Modernizer - Safely modernize Python code with AI."""


@app.command()
def analyze(
    filepath: Annotated[Path, typer.Argument(exists=True)],
    model: Annotated[str, typer.Option("--model", "-m")] = "qwen2.5-coder:7b",
):
    """Analyze a file for improvement opportunities."""
    console.print(Panel.fit(f"[bold]Analyzing:[/] {filepath.name}", style="blue"))

    stats = get_code_stats(filepath)
    table = Table(title="Code Statistics", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    for k, v in [
        ("Lines", stats["total_lines"]),
        ("Functions", stats["function_count"]),
        ("Classes", stats["class_count"]),
        ("Type Hints", "Yes" if stats["has_type_hints"] else "No"),
    ]:
        table.add_row(k, str(v))
    console.print(table)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as p:
        p.add_task("Analyzing with AI...", total=None)
        from langchain_ollama import ChatOllama

        result = analyze_file(filepath, ChatOllama(model=model, temperature=0.1))

    if result.has_improvement:
        msg = (
            f"[bold]Target:[/] {result.target}\n"
            f"[bold]Type:[/] {result.improvement_type}\n\n"
            f"{result.description}"
        )
        console.print(Panel(msg, title="Improvement Found", style="green"))
    else:
        console.print("[yellow]No safe improvements identified.[/]")


@app.command()
def modernize(
    filepath: Annotated[Path, typer.Argument(exists=True)],
    model: Annotated[str, typer.Option("--model", "-m")] = "qwen2.5-coder:7b",
    test_dir: Annotated[Path | None, typer.Option("--tests", "-t")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", "-n")] = False,
    no_tests: Annotated[bool, typer.Option("--no-tests")] = False,
):
    """Modernize a Python file with AI."""
    label = f"[bold]Modernizing:[/] {filepath.name}"
    if dry_run:
        label += " [dim](dry run)[/]"
    console.print(Panel.fit(label, style="blue"))

    config = ModernizationConfig(model_name=model, dry_run=dry_run, run_tests=not no_tests)
    agent = ModernizerAgent(config)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as p:
        p.add_task("Working...", total=None)
        report = agent.modernize_file(filepath, test_dir)

    if report.success:
        msg = (
            f"[bold green]SUCCESS[/]\n\n"
            f"[bold]Target:[/] {report.target or 'N/A'}\n"
            f"[bold]Type:[/] {report.improvement_type}"
        )
        console.print(Panel(msg, title="Complete", style="green"))
        if report.diff:
            console.print(Syntax(report.diff, "diff", theme="monokai", line_numbers=True))
        console.print(f"[dim]Report saved to:[/] {report.save(config.output_dir)}")
    else:
        console.print(
            Panel(
                f"[bold red]FAILED[/]\n\n{report.failure_reason}",
                title="Failed",
                style="red",
            )
        )
        raise typer.Exit(1)


@app.command()
def validate(filepath: Annotated[Path, typer.Argument(exists=True)]):
    """Validate Python file syntax."""
    ok, error = validate_syntax(filepath)
    if ok:
        console.print(f"[green]✓[/] {filepath.name}")
    else:
        console.print(f"[red]✗[/] {filepath.name} - {error}")
        raise typer.Exit(1)


@app.command()
def test(test_dir: Annotated[Path, typer.Argument(exists=True)]):
    """Run tests in a directory."""
    passed, output = run_tests(test_dir, verbose=True)
    console.print(output)
    if passed:
        console.print("[green]All tests passed![/]")
    else:
        console.print("[red]Tests failed.[/]")
        raise typer.Exit(1)


@app.command("list")
def list_files(directory: Annotated[Path, typer.Argument(exists=True)]):
    """List Python files eligible for modernization."""
    files = list_python_files(directory)
    if not files:
        console.print("[yellow]No eligible files.[/]")
        return
    table = Table(title=f"Python Files in {directory}")
    table.add_column("File", style="cyan")
    table.add_column("Lines", justify="right")
    table.add_column("Functions", justify="right")
    for f in files:
        s = get_code_stats(f)
        table.add_row(
            str(f.relative_to(directory)),
            str(s["total_lines"]),
            str(s["function_count"]),
        )
    console.print(table)


if __name__ == "__main__":
    app()
