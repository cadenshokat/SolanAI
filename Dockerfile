# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps + Chromium for Selenium
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates git \
    chromium chromium-driver fonts-liberation \
  && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Default env inside container
ENV HOST=0.0.0.0 \
    PORT=5000 \
    API_PREFIX=/api/v1 \
    DB_PATH=/app/data/main.db \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Persisted data directory
RUN mkdir -p /app/data

# Expose API port
EXPOSE 5000

# Default command = API web server (Gunicorn)
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:create_app()"]
