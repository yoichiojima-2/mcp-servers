FROM python:3.12

RUN apt update && apt install -y make pandoc libreoffice
RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/docx /app/src/docx

WORKDIR /app

# Install using workspace dependencies
RUN uv sync --locked --package docx

CMD ["uv", "run", "python", "-m", "docx"]
