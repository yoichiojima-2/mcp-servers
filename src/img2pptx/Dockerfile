FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/img2pptx /app/src/img2pptx

WORKDIR /app

RUN uv sync --frozen --package img2pptx

EXPOSE 8014

CMD ["uv", "run", "python", "-m", "img2pptx"]
