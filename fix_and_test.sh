#!/usr/bin/env bash
# Auto-fix imports/format, then run tests.
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
    echo "Error: uv is not installed. Install it: https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 1
fi

echo "==> Install dependencies"
uv sync --locked

echo "==> Ruff fix (imports, lint)"
uv run ruff check --fix src
uv run ruff format src

echo "==> Pytest"
uv run pytest src/tests

echo "All done."