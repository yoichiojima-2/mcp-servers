FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/browser /app/src/browser

WORKDIR /app

# Install using workspace dependencies
RUN uv sync --frozen --package browser

EXPOSE 8001

CMD ["uv", "run", "python", "-m", "browser"]
