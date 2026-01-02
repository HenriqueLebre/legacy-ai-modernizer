"""Validation module - syntax checks and test execution."""

from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    syntax_valid: bool
    tests_passed: bool | None
    syntax_error: str | None = None
    test_output: str | None = None

    @property
    def is_valid(self) -> bool:
        return self.syntax_valid and self.tests_passed is not False


def validate_syntax(filepath: Path) -> tuple[bool, str | None]:
    """Validate Python syntax using AST and py_compile."""
    try:
        ast.parse(filepath.read_text())
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(filepath)], capture_output=True, text=True
    )
    return (True, None) if result.returncode == 0 else (False, result.stderr.strip())


def run_tests(test_dir: Path, verbose: bool = False) -> tuple[bool, str]:
    """Run pytest on test directory."""
    if not test_dir.exists() or not list(test_dir.glob("test_*.py")):
        return True, "No tests found (skipped)"

    cmd = [sys.executable, "-m", "pytest", str(test_dir), "-v" if verbose else "-q"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=test_dir.parent)
    return result.returncode == 0, result.stdout + result.stderr


def validate_all(
    filepath: Path, test_dir: Path | None = None, run_tests_flag: bool = True
) -> ValidationResult:
    """Run all validations on a file."""
    syntax_ok, syntax_error = validate_syntax(filepath)
    if not syntax_ok:
        return ValidationResult(False, None, syntax_error)

    if run_tests_flag and test_dir:
        tests_ok, test_output = run_tests(test_dir)
        return ValidationResult(True, tests_ok, test_output=test_output)

    return ValidationResult(True, None, test_output="Tests not run")
