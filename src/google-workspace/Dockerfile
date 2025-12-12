FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/google-workspace /app/src/google-workspace

WORKDIR /app

RUN uv sync --frozen --package google-workspace

EXPOSE 8016

CMD ["uv", "run", "python", "-m", "google_workspace"]
