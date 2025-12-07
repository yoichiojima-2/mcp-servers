.PHONY: help test install run serve clean

help:
	@echo "Available commands:"
	@echo "  make install     - install dependencies"
	@echo "  make run         - run the composite MCP server"
	@echo "  make serve       - run the composite MCP server (alias for run)"
	@echo "  make test        - test tool registration"
	@echo "  make clean       - clean up temporary and cache files"

install:
	uv sync
	uv pip install -e .

run:
	uv run python -m composite

serve: run

test:
	uv run pytest -v

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
