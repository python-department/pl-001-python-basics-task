@echo off
rem Run the same checks locally as in CI (.github/workflows/ci.yml).
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo Error: uv is not installed. Install it: https://docs.astral.sh/uv/getting-started/installation/ 1>&2
    exit /b 1
)

echo ==^> Install dependencies
uv sync --locked || exit /b 1

echo ==^> Ruff lint
uv run ruff check src || exit /b 1

echo ==^> Ruff format check
uv run ruff format --check src || exit /b 1

echo ==^> MyPy
uv run mypy --strict src || exit /b 1

echo All checks passed.
