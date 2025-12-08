FROM python:3.12

RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/langquery /app/src/langquery

WORKDIR /app

# Install using workspace dependencies
RUN uv sync --locked --package langquery

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "langquery"]
