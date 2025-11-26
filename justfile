set shell := ["bash", "-c"]

# 0. SETUP
setup:
\t@echo "🚀 Hydrating Environment (uv)..."
\tuv sync
\tuv run pre-commit install

# 1. QUALITY
check: format lint type test

format:
\tuv run ruff format .

lint:
\tuv run ruff check . --fix

type:
\tuv run mypy .

test:
\tuv run pytest tests/ -v

# 2. STATE HYGIENE
audit-db:
\tuv run python scripts/audit_redis.py
