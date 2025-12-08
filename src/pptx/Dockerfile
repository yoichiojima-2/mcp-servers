FROM python:3.12

RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/pptx /app/src/pptx

WORKDIR /app

# Install using workspace dependencies
RUN uv sync --locked --package pptx

EXPOSE 8003

CMD ["uv", "run", "python", "-m", "pptx_server"]
