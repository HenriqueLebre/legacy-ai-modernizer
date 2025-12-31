# Legacy AI Modernizer

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green.svg)](https://ollama.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🤖 AI agent that safely modernizes legacy Python code with validation and automatic rollback

## What It Does

```bash
modernizer modernize sample_legacy/erp/pricing.py --tests sample_legacy/tests
```

1. 📊 **Analyze** → Identifies ONE safe improvement
2. 📝 **Patch** → Generates unified diff
3. ✅ **Validate** → Syntax + pytest
4. ↩️ **Rollback** → Automatic if validation fails

## Quick Start

```bash
# Install
pip install -e .
ollama pull qwen2.5-coder:7b

# Use
modernizer analyze sample_legacy/erp/pricing.py
modernizer modernize sample_legacy/erp/pricing.py --tests sample_legacy/tests
modernizer modernize sample_legacy/erp/pricing.py --dry-run
```

## Safety Features

- ✅ Syntax validation (AST + compileall)
- ✅ Test execution (pytest)
- ✅ Automatic rollback on failure
- ✅ One file at a time
- ✅ Preserves behavior

## Improvement Types

| Type | Risk |
|------|------|
| `type_hints` | Low |
| `variable_names` | Low |
| `docstring` | Low |
| `constants` | Low |
| `simplify` | Medium |
| `extract_function` | Medium |

## Project Structure

```
src/modernizer/
├── cli.py        # Typer CLI
├── agent.py      # Main pipeline
├── analyze.py    # Code analysis
├── patch.py      # Diff generation
├── validate.py   # Syntax + tests
├── report.py     # Reports
└── prompts.py    # LLM prompts

sample_legacy/    # Demo ERP code
├── erp/          # Legacy modules
└── tests/        # Test suite
```

## License

MIT
