FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/o3-search /app/src/o3-search

WORKDIR /app

RUN uv sync --frozen --package o3-search

EXPOSE 8012

CMD ["uv", "run", "python", "-m", "o3_search"]
