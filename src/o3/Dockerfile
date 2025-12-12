FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/o3 /app/src/o3

WORKDIR /app

RUN uv sync --frozen --package o3

EXPOSE 8007

CMD ["uv", "run", "python", "-m", "o3_search"]
