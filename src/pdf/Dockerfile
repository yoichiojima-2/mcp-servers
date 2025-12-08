FROM python:3.12

RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/pdf /app/src/pdf

WORKDIR /app

# Install using workspace dependencies with OCR support
RUN uv sync --locked --package pdf --extra ocr

EXPOSE 8001

CMD ["uv", "run", "python", "-m", "pdf"]
