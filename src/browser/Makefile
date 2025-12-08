.PHONY: run help test clean install build serve lint pre-commit

help:
	@echo "Available commands:"
	@echo "  make install     - install dependencies and package in development mode"
	@echo "  make build       - build docker images"
	@echo "  make up          - start docker compose services"
	@echo "  make in          - run interactive bash shell in mcp container"
	@echo "  make serve       - run the MCP server with auto-reload"
	@echo "  make test        - run the test suite with pytest"
	@echo "  make lint        - format and lint code with isort and ruff"
	@echo "  make clean       - clean up temporary and cache files"
	@echo "  make pre-commit  - run lint and clean before committing"

install:
	cd ../.. && uv sync --locked --package browser
	uv run playwright install chromium

build:
	docker compose build

up:
	docker compose up

in:
	docker compose run -it mcp bash

serve:
	uv run python -m browser

clean:
	-rm .DS_Store
	find . -name .venv -type d -exec rm -rf {} +
	find . -name __pycache__ -type d -exec rm -rf {} +
	find . -name .vscode -type d -exec rm -rf {} +
	find . -name .pytest_cache -type d -exec rm -rf {} +
	find . -name .ruff_cache -type d -exec rm -rf {} +
	find . -name .mypy_cache -type d -exec rm -rf {} +
	find . -name .cache -type f -exec rm {} +
	find . -name "*.egg-info" -type d -exec rm -rf {} +

lint:
	uv run isort .
	uv run ruff check --fix .
	uv run ruff format .

pre-commit: lint clean

test: install
	uv run pytest -vvv
