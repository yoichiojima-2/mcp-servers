FROM python:3.12-slim

WORKDIR /app

# Install uv for faster dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system --no-cache -e .

# Copy application code
COPY src ./src

# Expose port for SSE/HTTP transport
EXPOSE 8006

# Set environment variables
ENV TRANSPORT=sse \
    HOST=0.0.0.0 \
    PORT=8006

# Run the server
CMD ["python", "-m", "dify"]
