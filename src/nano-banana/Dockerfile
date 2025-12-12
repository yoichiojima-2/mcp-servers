FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/nano-banana /app/src/nano-banana

WORKDIR /app

RUN uv sync --frozen --package nano-banana

EXPOSE 8006

CMD ["uv", "run", "python", "-m", "nano_banana"]
