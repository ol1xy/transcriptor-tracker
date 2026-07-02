FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/models_cache

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
COPY tests/ ./tests

RUN useradd -m appuser \
    && mkdir -p /app/models_cache \
    && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["python", "-m", "src.transcriptor_tracker.cli"]