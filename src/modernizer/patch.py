"""Patch generation and application module."""
from __future__ import annotations
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage
from .prompts import PATCH_SYSTEM, PATCH_USER
from .analyze import AnalysisResult


@dataclass
class PatchResult:
    success: bool
    diff: str
    original_code: str
    modified_code: str | None
    error: str | None = None


def generate_patch(filepath: Path, analysis: AnalysisResult, llm: Any) -> str:
    """Generate unified diff for the proposed improvement."""
    code = filepath.read_text()
    messages = [
        SystemMessage(content=PATCH_SYSTEM),
        HumanMessage(content=PATCH_USER.format(
            target=analysis.target, improvement_type=analysis.improvement_type,
            description=analysis.description, filename=filepath.name, code=code)),
    ]
    response = llm.invoke(messages)
    diff = response.content if hasattr(response, 'content') else str(response)
    return _clean_diff(diff, filepath.name)


def _clean_diff(diff: str, filename: str) -> str:
    diff = re.sub(r'^```\w*\n?', '', diff, flags=re.MULTILINE)
    diff = re.sub(r'\n?```$', '', diff, flags=re.MULTILINE)
    diff = diff.strip()
    if not diff.startswith('---'):
        match = re.search(r'^---\s+a/', diff, re.MULTILINE)
        diff = diff[match.start():] if match else f"--- a/{filename}\n+++ b/{filename}\n{diff}"
    return diff


def apply_patch(filepath: Path, diff: str) -> PatchResult:
    """Apply unified diff to a file."""
    original = filepath.read_text()
    try:
        result = subprocess.run(['patch', '-p1', '--forward', '--no-backup-if-mismatch'],
                                input=diff, capture_output=True, text=True, cwd=filepath.parent.parent)
        if result.returncode == 0:
            return PatchResult(True, diff, original, filepath.read_text())
        filepath.write_text(original)
        return PatchResult(False, diff, original, None, f"Patch failed: {result.stderr}")
    except FileNotFoundError:
        return _apply_patch_python(filepath, diff, original)


def _apply_patch_python(filepath: Path, diff: str, original: str) -> PatchResult:
    """Pure Python patch fallback."""
    try:
        lines = original.split('\n')
        hunks = _parse_hunks(diff)
        if not hunks:
            return PatchResult(False, diff, original, None, "No hunks found")
        for hunk in reversed(hunks):
            lines = _apply_hunk(lines, hunk)
        modified = '\n'.join(lines)
        filepath.write_text(modified)
        return PatchResult(True, diff, original, modified)
    except Exception as e:
        filepath.write_text(original)
        return PatchResult(False, diff, original, None, str(e))


def _parse_hunks(diff: str) -> list[dict]:
    hunks = []
    for match in re.finditer(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$', diff, re.MULTILINE):
        start = match.end() + 1
        end = diff.find('\n@@', start)
        content = diff[start:end if end > 0 else len(diff)].strip()
        hunks.append({'start': int(match.group(1)), 'count': int(match.group(2) or 1), 'content': content})
    return hunks


def _apply_hunk(lines: list[str], hunk: dict) -> list[str]:
    result = lines[:hunk['start'] - 1]
    for line in hunk['content'].split('\n'):
        if line.startswith('+'):
            result.append(line[1:])
        elif line.startswith(' '):
            result.append(line[1:])
        elif not line.startswith('-'):
            result.append(line)
    result.extend(lines[hunk['start'] - 1 + hunk['count']:])
    return result


def rollback(filepath: Path, original: str) -> None:
    """Restore original file content."""
    filepath.write_text(original)
