.PHONY: help install test lint fmt check clean examples release

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
	mypy src/td/

fmt: ## Auto-format code
	ruff format .
	ruff check --fix .

check: lint test ## Run all checks (lint + test)

examples: ## Regenerate command examples doc
	python scripts/generate_examples.py > docs/examples.md

clean: ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info .coverage coverage.xml htmlcov/ .mypy_cache/ .ruff_cache/ .pytest_cache/

release: check ## Release a new version (make release VERSION=x.y.z)
ifndef VERSION
	$(error VERSION is required. Usage: make release VERSION=0.2.0)
endif
	@echo "Releasing v$(VERSION)..."
	git checkout -b release/v$(VERSION)
	@sed -i 's/__version__ = ".*"/__version__ = "$(VERSION)"/' src/td/__init__.py
	@sed -i 's/## \[Unreleased\]/## [Unreleased]\n\n## [$(VERSION)] - $(shell date +%Y-%m-%d)/' CHANGELOG.md
	git add src/td/__init__.py CHANGELOG.md
	git commit -m "chore(release): v$(VERSION)"
	git push -u origin release/v$(VERSION)
	gh pr create --title "chore(release): v$(VERSION)" --body "Version bump and changelog for v$(VERSION)."
	@echo ""
	@echo "PR created. After CI passes and PR is merged, run:"
	@echo "  git checkout main && git pull"
	@echo "  git tag -a v$(VERSION) -m \"v$(VERSION)\""
	@echo "  git push origin v$(VERSION)"
