.PHONY: run help test clean install serve lint pre-commit

help:
	@echo "Available commands:"
	@echo "  make install     - install dependencies and package in development mode"
	@echo "  make run         - run the MCP server"
	@echo "  make serve       - run the MCP server (alias for run)"
	@echo "  make test        - run the test suite with pytest"
	@echo "  make lint        - format and lint code with isort and ruff"
	@echo "  make clean       - clean up temporary and cache files"
	@echo "  make pre-commit  - run lint and clean before committing"

install:
	uv sync
	uv pip install -e .
	uv run playwright install chromium

run:
	uv run python -m browser

serve: run

clean:
	-rm .DS_Store
	find . -name .venv -type d -exec rm -rf {} +
	find . -name __pycache__ -type d -exec rm -rf {} +
	find . -name .vscode -type d -exec rm -rf {} +
	find . -name .pytest_cache -type d -exec rm -rf {} +
	find . -name .ruff_cache -type d -exec rm -rf {} +
	find . -name .mypy_cache -type d -exec rm -rf {} +
	find . -name .cache -type f -exec rm {} +
	find . -name uv.lock -type f -exec rm {} +
	find . -name "*.egg-info" -type d -exec rm -rf {} +

lint:
	uv run isort .
	uv run ruff check --fix .
	uv run ruff format .

pre-commit: lint clean

test: install
	uv run pytest -vvv
