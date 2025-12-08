# Multi-stage build for composite MCP server
# Uses Playwright base for browser support, with conditional heavy dependencies

FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    pandoc \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/ /app/src/

WORKDIR /app

# Install composite server and all available sub-servers
# This allows runtime configuration via composite-config.yaml
RUN uv sync --frozen \
    --package composite \
    --package browser \
    --package dify \
    --package pdf \
    --package xlsx \
    --package docx \
    --package pptx \
    --package vectorstore \
    --package langquery

EXPOSE 8000

# Default to SSE transport for Dify compatibility
ENV TRANSPORT=sse
ENV HOST=0.0.0.0
ENV PORT=8000

# Config file should be mounted at runtime
CMD ["uv", "run", "python", "-m", "composite"]
