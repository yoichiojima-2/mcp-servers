FROM python:3.12

RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/core /app/src/core
COPY src/file-management /app/src/file-management

WORKDIR /app

# Install using workspace dependencies
RUN uv sync --frozen --package file-management

EXPOSE 8013

CMD ["uv", "run", "python", "-m", "file_management"]
