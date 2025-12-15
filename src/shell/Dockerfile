FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/shell /app/src/shell

WORKDIR /app

RUN uv sync --frozen --package shell

EXPOSE 8015

CMD ["uv", "run", "python", "-m", "shell"]
