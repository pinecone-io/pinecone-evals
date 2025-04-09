# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Build/Install: `uv pip install -e .`
- Run: `uv run python main.py`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Test: `uv run pytest`
- Single test: `uv run pytest tests/path_to_test.py::test_name`

## Code Style
- **Formatting**: Follow PEP 8, use ruff formatter
- **Imports**: Sort imports with standard library first, then third-party, then local
- **Types**: Use type hints for all functions and methods
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error handling**: Use specific exceptions, include context in error messages
- **Docstrings**: Google-style docstrings for public functions/classes
- **Line length**: Maximum 88 characters
- **Function length**: Keep functions focused and under 50 lines