"""Main modernizer agent - orchestrates the full pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from langchain_ollama import ChatOllama

from .analyze import AnalysisResult, analyze_file, list_python_files
from .patch import apply_patch, generate_patch, rollback
from .report import (
    ModernizationReport,
    create_failure_report,
    create_no_changes_report,
    create_success_report,
)
from .validate import validate_all

logger = logging.getLogger(__name__)


@dataclass
class ModernizationConfig:
    model_name: str = "qwen2.5-coder:7b"
    ollama_base_url: str = "http://localhost:11434"
    temperature: float = 0.1
    run_tests: bool = True
    max_diff_lines: int = 100
    dry_run: bool = False
    output_dir: Path = field(default_factory=lambda: Path("reports"))
    patches_dir: Path = field(default_factory=lambda: Path("patches"))


class ModernizerAgent:
    """AI agent that safely modernizes legacy Python code."""

    def __init__(self, config: ModernizationConfig | None = None):
        self.config = config or ModernizationConfig()
        self.llm = ChatOllama(
            model=self.config.model_name,
            base_url=self.config.ollama_base_url,
            temperature=self.config.temperature,
        )
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.patches_dir.mkdir(parents=True, exist_ok=True)

    def modernize_file(self, filepath: Path, test_dir: Path | None = None) -> ModernizationReport:
        """Modernize a single Python file with validation and rollback."""
        filename = filepath.name
        logger.info(f"Modernizing {filename}")

        # Step 1: Analyze
        try:
            analysis = analyze_file(filepath, self.llm)
        except Exception as e:
            return create_failure_report(
                filename, AnalysisResult(None, "error", str(e), "none", ""), None, str(e)
            )

        if not analysis.has_improvement:
            return create_no_changes_report(filename)

        # Step 2: Generate patch
        try:
            diff = generate_patch(filepath, analysis, self.llm)
        except Exception as e:
            return create_failure_report(filename, analysis, None, f"Patch generation failed: {e}")

        if len(diff.split("\n")) > self.config.max_diff_lines:
            return create_failure_report(filename, analysis, None, "Diff too large")

        if self.config.dry_run:
            (self.config.patches_dir / f"{filename}.patch").write_text(diff)
            return ModernizationReport(
                filename,
                analysis.target,
                analysis.improvement_type,
                analysis.description,
                analysis.risk_level,
                analysis.reasoning,
                True,
                None,
                diff,
            )

        # Step 3: Apply patch
        patch_result = apply_patch(filepath, diff)
        if not patch_result.success:
            return create_failure_report(filename, analysis, None, patch_result.error)

        # Step 4: Validate
        validation = validate_all(filepath, test_dir, self.config.run_tests)

        # Step 5: Rollback if failed
        if not validation.is_valid:
            rollback(filepath, patch_result.original_code)
            reason = (
                f"Syntax: {validation.syntax_error}"
                if not validation.syntax_valid
                else "Tests failed"
            )
            return create_failure_report(filename, analysis, validation, reason)

        # Success
        (self.config.patches_dir / f"{filename}.patch").write_text(diff)
        return create_success_report(filename, analysis, validation, diff)

    def modernize_directory(
        self, directory: Path, test_dir: Path | None = None, max_files: int = 1
    ) -> list[ModernizationReport]:
        """Modernize multiple files in a directory."""
        reports = []
        for filepath in list_python_files(directory)[:max_files]:
            report = self.modernize_file(filepath, test_dir)
            report.save(self.config.output_dir)
            reports.append(report)
        return reports


def create_agent(
    model: str = "qwen2.5-coder:7b", dry_run: bool = False, run_tests: bool = True
) -> ModernizerAgent:
    """Factory function to create a configured agent."""
    return ModernizerAgent(
        ModernizationConfig(model_name=model, dry_run=dry_run, run_tests=run_tests)
    )
