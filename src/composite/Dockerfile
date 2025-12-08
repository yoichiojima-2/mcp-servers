# Lightweight composite server - no heavy dependencies
FROM python:3.12-slim

# Install uv
RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/ /app/src/

WORKDIR /app

# Install only composite package - minimal dependencies
RUN uv sync --frozen --package composite

EXPOSE 8000

# Default to SSE transport for Dify compatibility
ENV TRANSPORT=sse
ENV HOST=0.0.0.0
ENV PORT=8000

# Config file should be mounted at runtime
CMD ["uv", "run", "python", "-m", "composite"]
