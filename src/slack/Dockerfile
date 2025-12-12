FROM python:3.12-slim

# Install Node.js for npx (required to run @ubie-oss/slack-mcp-server)
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Pre-cache the npm package to avoid download on first request
RUN npx -y @ubie-oss/slack-mcp-server --version || true

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/slack /app/src/slack

WORKDIR /app

RUN uv sync --frozen --package slack

EXPOSE 8013

CMD ["uv", "run", "python", "-m", "slack"]
