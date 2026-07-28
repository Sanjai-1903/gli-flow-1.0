FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy just requirements first for docker cache
COPY requirements-ingest.txt ./
RUN pip install --no-cache-dir -r requirements-ingest.txt

# Copy the ingestion server code and its dependencies
COPY cloud_ingestion ./cloud_ingestion
COPY gli_flow/database ./gli_flow/database
COPY config ./config

# Render sets PORT env var
ENV PORT=8100
EXPOSE 8100

# Bind to 0.0.0.0 so Render can reach it (not just localhost)
CMD ["sh", "-c", "uvicorn cloud_ingestion.server:create_app --factory --host 0.0.0.0 --port ${PORT:-8100}"]
