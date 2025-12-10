FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/file-management /app/src/file-management

WORKDIR /app

RUN uv sync --frozen --package file-management

EXPOSE 8010

CMD ["uv", "run", "python", "-m", "file_management"]
