#!/bin/bash
# Minimal 'just' runner wrapper
set -e

case "$1" in
  check)
    uv run ruff check . --fix
    uv run mypy src/
    uv run pytest tests/
    ;;
  setup)
    uv sync
    ;;
  *)
    echo "Usage: ./just {check|setup}"
    exit 1
    ;;
esac
