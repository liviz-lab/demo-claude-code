# CLAUDE.md

## 🔨 最重要ルール - 新しいルールの追加プロセス

ユーザーから今回限りではなく常に対応が必要だと思われる指示を受けた場合：

1. 「これを標準のルールにしますか？」と質問する
2. YESの回答を得た場合、CLAUDE.mdに追加ルールとして記載する
3. 以降は標準ルールとして常に適用する

このプロセスにより、プロジェクトのルールを継続的に改善していきます。

## チャットの出力について
日本語で出力してください

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI project using uv for dependency management.

**Dependencies:**
- FastAPI: Modern, fast web framework for building APIs
- Uvicorn: ASGI server for running FastAPI applications
- Pydantic: Data validation and settings management

**Project Structure:**
- `pyproject.toml`: Project configuration and dependencies
- `main.py`: Main application entry point
- `.venv/`: Virtual environment (managed by uv)

## Development Setup

This project uses uv for dependency management. The virtual environment is automatically created and managed.

## Common Commands

**Development:**
- Install dependencies: `uv sync`
- Add new dependency: `uv add <package>`
- Remove dependency: `uv remove <package>`
- Run in development mode: `uv run uvicorn main:app --reload`
- Run Python scripts: `uv run python main.py`
- Shell into virtual environment: `uv shell`

**FastAPI Specific:**
- Start development server: `uv run uvicorn main:app --reload`
- Start production server: `uv run uvicorn main:app --host 0.0.0.0 --port 8000`
- View API documentation: http://localhost:8000/docs (Swagger UI)
- View alternative documentation: http://localhost:8000/redoc (ReDoc)

**Testing:**
- Run all tests: `uv run pytest`
- Run tests with coverage: `uv run pytest --cov`
- Run specific test file: `uv run pytest tests/api/test_endpoints.py`
- Run tests by marker: `uv run pytest -m unit` or `uv run pytest -m api`
- Run tests with verbose output: `uv run pytest -v`
- Generate HTML coverage report: `uv run pytest --cov --cov-report=html`
- Run tests in parallel: `uv run pytest -n auto` (requires pytest-xdist)

**Test Categories:**
- `@pytest.mark.unit`: Unit tests for individual functions/classes
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.api`: API endpoint tests
- `@pytest.mark.slow`: Tests that take longer to run