PYTHON_FILES = `(find . -iname "*.py" -not -path "./.venv/*")`
TOML_FILES = `(find . -iname "*.toml" -not -path "**/.venv/**")`

setup: ## Install developper experience
	rm -f .git/hooks/commit-msg
	rm -f .git/hooks/pre-commit
	ln -s ../../.scripts/commit-msg .git/hooks/commit-msg
	ln -s ../../.scripts/pre-commit .git/hooks/pre-commit
	git config pull.rebase false

setup-hard: ## Install developper experience with no cache
	rm -f .git/hooks/commit-msg
	rm -f .git/hooks/pre-commit
	make setup

install: ## Install package dependencies
	poetry install --sync --with dev

install-hard: ## Install package dependencies from scratch
	rm -rf .venv/
	make install

poetry-update: ## Upgrade poetry and dependencies
	poetry self update
	poetry run pip install --upgrade pip wheel setuptools
	poetry update

toml-sort: ## Upgrade poetry and dependencies
	poetry run toml-sort --all --in-place $(TOML_FILES)

format: ## Format python code using Ruff Format
	poetry run ruff format $(PYTHON_FILES)

format-check: ## Format python code using Ruff Format
	poetry run ruff format --check $(PYTHON_FILES)

lint-check: ## Run all linters
	poetry run ruff $(PYTHON_FILES)

lint: ## Run all linters with automated fix
	poetry run ruff --fix $(PYTHON_FILES)

pytest: ## Run Pytest
	poetry run pytest tests/

pytest-coverage: ## Run coverage report
	poetry run coverage run -m pytest tests/
	poetry run coverage report --skip-covered --show-missing --sort=cover

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
