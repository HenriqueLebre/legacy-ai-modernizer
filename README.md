# Legacy AI Modernizer

[![CI](https://github.com/HenriqueLebre/legacy-ai-modernizer/actions/workflows/ci.yml/badge.svg)](https://github.com/HenriqueLebre/legacy-ai-modernizer/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green.svg)](https://ollama.ai/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🤖 AI-powered agent that safely modernizes legacy Python code with automatic validation and rollback

## 🎯 The Problem

Modernizing legacy code is **risky**. One wrong change can break everything. Developers spend hours manually refactoring, only to find out tests are failing.

## 💡 The Solution

Legacy AI Modernizer is an intelligent agent that:

1. **Analyzes** legacy Python code for safe improvements
2. **Generates** minimal, focused patches using LLM
3. **Validates** changes with syntax checks + pytest
4. **Rolls back automatically** if anything breaks

**One command. Safe changes. Zero broken builds.**

```bash
modernizer modernize legacy_code.py --tests tests/
```

## 🏆 Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Smart Analysis** | AI identifies safe improvements (type hints, docstrings, naming) |
| 🛡️ **Safety First** | Automatic rollback if validation fails |
| ✅ **Test Validation** | Runs pytest to ensure behavior is preserved |
| 📝 **Unified Diffs** | Generates clean, reviewable patches |
| 📊 **Reports** | Detailed markdown reports for each modernization |
| 🐳 **Docker Ready** | Containerized for consistent environments |

## 🚀 Quick Start

### Option 1: Local Installation

```bash
# Clone repository
git clone https://github.com/HenriqueLebre/legacy-ai-modernizer.git
cd legacy-ai-modernizer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install
pip install -e ".[dev]"

# Pull LLM model
ollama pull qwen2.5-coder:7b
```

### Option 2: Docker

```bash
# Build and run
docker build -t legacy-ai-modernizer .
docker run -it legacy-ai-modernizer

# Or with Docker Compose (includes Ollama)
docker-compose up -d
docker-compose exec modernizer bash
```

## 📖 Usage

### Analyze Code
```bash
modernizer analyze sample_legacy/erp/pricing.py
```

```
╭───────────────────────╮
│ Analyzing: pricing.py │
╰───────────────────────╯
  Code Statistics
┌────────────┬─────┐
│ Lines      │ 121 │
│ Functions  │ 11  │
│ Classes    │ 1   │
│ Type Hints │ No  │
└────────────┴─────┘

╭─────────────────── Improvement Found ───────────────────╮
│ Target: calc_price                                      │
│ Type: type_hints                                        │
│                                                         │
│ Add type hints to function parameters and return value. │
╰─────────────────────────────────────────────────────────╯
```

### Modernize with Validation
```bash
modernizer modernize sample_legacy/erp/pricing.py --tests sample_legacy/tests
```

### Dry Run (Preview Changes)
```bash
modernizer modernize sample_legacy/erp/pricing.py --dry-run
```

### Other Commands
```bash
modernizer list sample_legacy/erp     # List eligible files
modernizer validate file.py           # Check syntax
modernizer test tests/                # Run tests
```

## 🛡️ Safety Pipeline

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Analyze  │───▶│ Generate │───▶│  Apply   │───▶│ Validate │
│   Code   │    │  Patch   │    │  Patch   │    │  Code    │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                     │
                                    ┌────────────────┼────────────────┐
                                    ▼                ▼                ▼
                                 SUCCESS          FAILED          ROLLBACK
                                    │                │                │
                                    ▼                ▼                ▼
                               ┌────────┐      ┌──────────┐    ┌──────────┐
                               │ Report │      │  Report  │    │ Restore  │
                               │ Success│      │  Error   │    │ Original │
                               └────────┘      └──────────┘    └──────────┘
```

### Validation Steps

1. **Syntax Check** - AST parsing + py_compile
2. **Test Execution** - Full pytest suite
3. **Automatic Rollback** - Restores original on any failure

## 🔧 Improvement Types

| Type | Risk Level | Description |
|------|------------|-------------|
| `type_hints` | 🟢 Low | Add type annotations |
| `variable_names` | 🟢 Low | Improve unclear names |
| `docstring` | 🟢 Low | Add/improve documentation |
| `constants` | 🟢 Low | Replace magic numbers |
| `simplify` | 🟡 Medium | Simplify conditionals |
| `extract_function` | 🟡 Medium | Extract duplicated code |

## 📁 Project Structure

```
legacy-ai-modernizer/
├── src/modernizer/
│   ├── cli.py          # Typer CLI with Rich output
│   ├── agent.py        # Main orchestration pipeline
│   ├── analyze.py      # Code analysis with LLM
│   ├── patch.py        # Diff generation and application
│   ├── validate.py     # Syntax + pytest validation
│   ├── report.py       # Markdown report generation
│   └── prompts.py      # LLM prompts
├── sample_legacy/
│   ├── erp/            # Sample legacy ERP modules
│   │   ├── pricing.py  # Price calculations
│   │   ├── taxes.py    # Brazilian tax system
│   │   └── inventory.py# Stock management
│   └── tests/          # Comprehensive test suite
├── Dockerfile          # Container support
├── docker-compose.yml  # Orchestration with Ollama
└── .github/workflows/  # CI/CD pipeline
```

## 🧪 Sample Legacy Code

The project includes a sample Brazilian ERP system with intentional code smells:

- **pricing.py** - Price calculations without type hints
- **taxes.py** - ICMS, PIS, COFINS, IPI tax calculations
- **inventory.py** - Stock management with global state

Perfect for demonstrating modernization capabilities!

## ⚙️ Configuration

### Ollama Models

| Model | Size | Quality | Speed |
|-------|------|---------|-------|
| `qwen2.5-coder:7b` | 4.7GB | ⭐⭐⭐⭐ | Fast |
| `deepseek-coder-v2:16b` | 9GB | ⭐⭐⭐⭐⭐ | Medium |
| `codellama:13b` | 7GB | ⭐⭐⭐ | Medium |

```bash
# Use different model
modernizer modernize file.py --model deepseek-coder-v2:16b
```

## 🧪 Testing

```bash
# Run all tests
pytest sample_legacy/tests/ -v

# Run with coverage
pytest --cov=src/modernizer

# Lint check
ruff check src/

# Format code
ruff format src/
```

## 🗺️ Roadmap

- [x] Single file modernization
- [x] Syntax validation
- [x] Test validation
- [x] Automatic rollback
- [x] Report generation
- [x] Docker support
- [x] CI/CD pipeline
- [ ] Multi-file batch processing
- [ ] Custom rules engine
- [ ] VS Code extension
- [ ] Web UI dashboard

## 🤝 Tech Stack

- **Python 3.11+** - Modern Python features
- **LangChain + Ollama** - Local LLM integration
- **Typer + Rich** - Beautiful CLI
- **Pytest** - Test validation
- **Ruff** - Fast linting and formatting
- **Docker** - Containerization
- **GitHub Actions** - CI/CD

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Built for developers who maintain legacy code</b><br>
  <sub>Because refactoring shouldn't be scary 🛡️</sub>
</p>