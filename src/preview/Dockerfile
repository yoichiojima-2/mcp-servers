FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/preview /app/src/preview

WORKDIR /app

# Install using workspace dependencies
RUN uv sync --frozen --package preview

# Expose ports (MCP: 8010, HTTP: 3000)
EXPOSE 8010 3000

CMD ["uv", "run", "python", "-m", "preview"]
