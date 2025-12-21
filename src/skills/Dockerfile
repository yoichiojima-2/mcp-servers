FROM python:3.12

RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install uv

# Copy monorepo configuration from root
COPY pyproject.toml uv.lock /app/
COPY src/skills /app/src/skills
COPY src/core /app/src/core

WORKDIR /app

# Install using workspace dependencies
RUN uv sync --frozen --package skills

EXPOSE 8005

CMD ["uv", "run", "python", "-m", "skills"]
