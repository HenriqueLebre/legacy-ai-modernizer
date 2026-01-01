"""LLM Prompts for code analysis and patch generation."""

ANALYSIS_SYSTEM = """You are a Python code reviewer. Identify ONE safe improvement:
1. Add type hints  2. Improve variable names  3. Add docstrings
4. Extract functions  5. Replace magic numbers  6. Simplify conditionals

DO NOT change logic, public APIs, or add dependencies."""

ANALYSIS_USER = """Analyze this file and identify ONE improvement.

File: {filename}
```python
{code}
```

Respond in JSON:
{{"target": "function_name", "improvement_type": "type_hints|variable_names|docstring|extract_function|constants|simplify", "description": "what to change", "risk_level": "low|medium", "reasoning": "why"}}

If no safe improvement, respond: {{"target": null, "improvement_type": "none", "description": "Code is well-structured", "risk_level": "none", "reasoning": "No safe improvements"}}"""

PATCH_SYSTEM = """Generate a unified diff. Rules:
1. Output ONLY the diff  2. Don't change logic  3. Keep changes minimal
4. Preserve all behavior  5. Valid unified diff format"""

PATCH_USER = """Generate unified diff for:
Target: {target}
Improvement: {improvement_type}
Description: {description}

File ({filename}):
```python
{code}
```

Output ONLY the diff starting with:
--- a/{filename}
+++ b/{filename}"""

REPORT_TEMPLATE = """# Modernization Report
- **File**: `{filename}`
- **Target**: `{target}`
- **Type**: `{improvement_type}`
- **Status**: {status}

## Description
{description}

## Validation
- Syntax: {syntax_status}
- Tests: {test_status}
"""