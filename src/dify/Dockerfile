FROM python:3.12-slim

# Install uv for faster dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/dify /app/src/dify

WORKDIR /app

# Install using workspace dependencies
RUN uv sync --frozen --package dify

# Expose port for SSE/HTTP transport
EXPOSE 8003

# Set environment variables
ENV TRANSPORT=sse \
    HOST=0.0.0.0 \
    PORT=8003

# Run the server
CMD ["uv", "run", "python", "-m", "dify"]
