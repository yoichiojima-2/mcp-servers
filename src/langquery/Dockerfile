FROM python:3.12

RUN apt update && apt install -y make
RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/langquery /app/src/langquery

WORKDIR /app

# Install using workspace dependencies
RUN uv sync --locked --package langquery

CMD ["uv", "run", "python", "-m", "langquery"]
