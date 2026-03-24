.PHONY: help install test lint fmt check clean examples

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install package with dev dependencies
	pip install -e ".[dev]"
	pre-commit install

test: ## Run tests with coverage
	pytest --cov=td --cov-report=term-missing --cov-fail-under=85

lint: ## Run linter and type checker
	ruff check .
	ruff format --check .
	mypy td/

fmt: ## Auto-format code
	ruff format .
	ruff check --fix .

check: lint test ## Run all checks (lint + test)

examples: ## Regenerate command examples doc
	python scripts/generate_examples.py > docs/examples.md

clean: ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info .coverage coverage.xml htmlcov/ .mypy_cache/ .ruff_cache/ .pytest_cache/
