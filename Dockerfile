FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates git \
    chromium chromium-driver fonts-liberation \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./

RUN pip install --no-cache-dir .

COPY . .

ENV HOST=0.0.0.0 \
    PORT=5000 \
    API_PREFIX=/api/v1 \
    DB_PATH=/app/data/main.db \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

RUN mkdir -p /app/data
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:create_app()"]
