FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/browser /app/src/browser

WORKDIR /app

# Install using workspace dependencies
RUN uv sync --locked --package browser

EXPOSE 8007

CMD ["uv", "run", "python", "-m", "browser"]
