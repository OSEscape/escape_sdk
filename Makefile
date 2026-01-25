SHELL := /usr/bin/env bash

.PHONY: test format clean build help

test:           ## Run all checks (ruff, basedpyright, skylos, pytest)
	uv run ruff check . && uv run ruff format --check . && uv run basedpyright escape/ && uv run skylos escape/_internal/ -c 80 --secrets && uv run pytest -q

format:         ## Auto-format code and fix linting issues
	uv run ruff format . && uv run ruff check --fix --unsafe-fixes . || true

clean:          ## Remove caches and build artifacts
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .ruff_cache -o -name htmlcov -o -name "*.egg-info" \) -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage 2>/dev/null || true

build:          ## Build distribution packages
	uv run python -m build

help:           ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
