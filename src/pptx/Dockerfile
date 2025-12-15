FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/frontend-design /app/src/frontend-design
COPY src/pptx /app/src/pptx

WORKDIR /app

RUN uv sync --frozen --package pptx

EXPOSE 8010

CMD ["uv", "run", "python", "-m", "pptx_mcp"]
