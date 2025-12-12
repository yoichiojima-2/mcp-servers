FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/frontend-design /app/src/frontend-design

WORKDIR /app

RUN uv sync --frozen --package frontend-design

EXPOSE 8005

CMD ["uv", "run", "python", "-m", "frontend_design"]
