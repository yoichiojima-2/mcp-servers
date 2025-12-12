FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/data-analysis /app/src/data-analysis

WORKDIR /app

RUN uv sync --frozen --package data-analysis

EXPOSE 8002

CMD ["uv", "run", "python", "-m", "data_analysis"]
