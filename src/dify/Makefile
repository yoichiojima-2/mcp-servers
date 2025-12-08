.PHONY: install test run docker-build docker-run clean

# Install dependencies
install:
	cd ../.. && uv sync --locked --package dify

# Run tests
test:
	uv run pytest -v

# Run the server locally
run:
	uv run python -m dify

# Run with SSE transport
run-sse:
	TRANSPORT=sse uv run python -m dify

# Build Docker image
docker-build:
	docker build -t mcp-dify .

# Run Docker container
docker-run:
	docker run -p 8006:8006 \
		-e DIFY_API_KEY="${DIFY_API_KEY}" \
		-e DIFY_CONSOLE_API_KEY="${DIFY_CONSOLE_API_KEY}" \
		mcp-dify

# Clean up
clean:
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Format code
format:
	uv run ruff format .
	uv run isort .

# Lint code
lint:
	uv run ruff check .
