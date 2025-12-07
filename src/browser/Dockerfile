FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "-m", "browser"]
