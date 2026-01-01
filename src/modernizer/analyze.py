"""Code analysis module - identifies improvement opportunities."""
from __future__ import annotations
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage
from .prompts import ANALYSIS_SYSTEM, ANALYSIS_USER


@dataclass
class AnalysisResult:
    target: str | None
    improvement_type: str
    description: str
    risk_level: str
    reasoning: str

    @property
    def has_improvement(self) -> bool:
        return self.target is not None and self.improvement_type != "none"


def analyze_file(filepath: Path, llm: Any) -> AnalysisResult:
    """Analyze a Python file for improvement opportunities."""
    code = filepath.read_text()
    messages = [
        SystemMessage(content=ANALYSIS_SYSTEM),
        HumanMessage(content=ANALYSIS_USER.format(filename=filepath.name, code=code)),
    ]
    response = llm.invoke(messages)
    content = response.content if hasattr(response, 'content') else str(response)
    return _parse_response(content)


def _parse_response(content: str) -> AnalysisResult:
    match = re.search(r'\{[\s\S]*\}', content)
    if not match:
        return AnalysisResult(None, "error", "Failed to parse", "none", content[:200])
    try:
        data = json.loads(match.group())
        return AnalysisResult(
            target=data.get("target"),
            improvement_type=data.get("improvement_type", "unknown"),
            description=data.get("description", ""),
            risk_level=data.get("risk_level", "medium"),
            reasoning=data.get("reasoning", ""),
        )
    except json.JSONDecodeError:
        return AnalysisResult(None, "error", "Invalid JSON", "none", content[:200])


def get_code_stats(filepath: Path) -> dict[str, Any]:
    """Get basic statistics about a Python file."""
    code = filepath.read_text()
    lines = code.split('\n')
    return {
        "total_lines": len(lines),
        "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
        "function_count": len(re.findall(r'^\s*def\s+\w+', code, re.MULTILINE)),
        "class_count": len(re.findall(r'^\s*class\s+\w+', code, re.MULTILINE)),
        "has_type_hints": bool(re.search(r'def\s+\w+\([^)]*:\s*\w+', code)),
    }


def list_python_files(directory: Path) -> list[Path]:
    """List Python files eligible for modernization."""
    return sorted([p for p in directory.rglob("*.py")
                   if "test_" not in p.name and p.name != "__init__.py" and "__pycache__" not in str(p)])
