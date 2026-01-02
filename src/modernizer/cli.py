"""CLI interface using Typer and Rich."""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from . import __version__
from .agent import ModernizerAgent, ModernizationConfig
from .analyze import analyze_file, get_code_stats, list_python_files
from .validate import validate_syntax, run_tests

app = typer.Typer(name="modernizer", help="AI-powered legacy Python code modernizer", add_completion=False)
console = Console()
logging.basicConfig(level=logging.WARNING)


def version_callback(value: bool):
    if value:
        console.print(f"[bold blue]Legacy AI Modernizer[/] v{__version__}")
        raise typer.Exit()


@app.callback()
def main(version: bool = typer.Option(False, "--version", "-v", callback=version_callback, is_eager=True)):
    """Legacy AI Modernizer - Safely modernize Python code with AI."""


@app.command()
def analyze(filepath: Path = typer.Argument(..., exists=True),
            model: str = typer.Option("qwen2.5-coder:7b", "--model", "-m")):
    """Analyze a file for improvement opportunities."""
    console.print(Panel.fit(f"[bold]Analyzing:[/] {filepath.name}", style="blue"))

    stats = get_code_stats(filepath)
    table = Table(title="Code Statistics", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    for k, v in [("Lines", stats["total_lines"]), ("Functions", stats["function_count"]),
                 ("Classes", stats["class_count"]), ("Type Hints", "Yes" if stats["has_type_hints"] else "No")]:
        table.add_row(k, str(v))
    console.print(table)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as p:
        p.add_task("Analyzing with AI...", total=None)
        from langchain_ollama import ChatOllama
        result = analyze_file(filepath, ChatOllama(model=model, temperature=0.1))

    if result.has_improvement:
        console.print(Panel(f"[bold]Target:[/] {result.target}\n[bold]Type:[/] {result.improvement_type}\n\n{result.description}",
                            title="Improvement Found", style="green"))
    else:
        console.print("[yellow]No safe improvements identified.[/]")


@app.command()
def modernize(filepath: Path = typer.Argument(..., exists=True),
              model: str = typer.Option("qwen2.5-coder:7b", "--model", "-m"),
              test_dir: Optional[Path] = typer.Option(None, "--tests", "-t"),
              dry_run: bool = typer.Option(False, "--dry-run", "-n"),
              no_tests: bool = typer.Option(False, "--no-tests")):
    """Modernize a Python file with AI."""
    console.print(Panel.fit(f"[bold]Modernizing:[/] {filepath.name}" + (" [dim](dry run)[/]" if dry_run else ""), style="blue"))

    config = ModernizationConfig(model_name=model, dry_run=dry_run, run_tests=not no_tests)
    agent = ModernizerAgent(config)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as p:
        p.add_task("Working...", total=None)
        report = agent.modernize_file(filepath, test_dir)

    if report.success:
        console.print(Panel(f"[bold green]SUCCESS[/]\n\n[bold]Target:[/] {report.target or 'N/A'}\n[bold]Type:[/] {report.improvement_type}",
                            title="Complete", style="green"))
        if report.diff:
            console.print(Syntax(report.diff, "diff", theme="monokai", line_numbers=True))
        console.print(f"[dim]Report saved to:[/] {report.save(config.output_dir)}")
    else:
        console.print(Panel(f"[bold red]FAILED[/]\n\n{report.failure_reason}", title="Failed", style="red"))
        raise typer.Exit(1)


@app.command()
def validate(filepath: Path = typer.Argument(..., exists=True)):
    """Validate Python file syntax."""
    ok, error = validate_syntax(filepath)
    console.print(f"[green]✓[/] {filepath.name}" if ok else f"[red]✗[/] {filepath.name} - {error}")
    if not ok:
        raise typer.Exit(1)


@app.command()
def test(test_dir: Path = typer.Argument(..., exists=True)):
    """Run tests in a directory."""
    passed, output = run_tests(test_dir, verbose=True)
    console.print(output)
    console.print("[green]All tests passed![/]" if passed else "[red]Tests failed.[/]")
    if not passed:
        raise typer.Exit(1)


@app.command("list")
def list_files(directory: Path = typer.Argument(..., exists=True)):
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
        table.add_row(str(f.relative_to(directory)), str(s["total_lines"]), str(s["function_count"]))
    console.print(table)


if __name__ == "__main__":
    app()
