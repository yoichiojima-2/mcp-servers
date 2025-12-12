FROM python:3.12

RUN apt-get update && apt-get install -y --no-install-recommends make pandoc libreoffice && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/docx /app/src/docx

WORKDIR /app

# Install using workspace dependencies
RUN uv sync --frozen --package docx

EXPOSE 8004

CMD ["uv", "run", "python", "-m", "docx"]
