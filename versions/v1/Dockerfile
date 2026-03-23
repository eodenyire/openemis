FROM python:3.11-slim

LABEL maintainer="openEMIS <support@openemis.org>" \
      org.opencontainers.image.title="openEMIS" \
      org.opencontainers.image.description="Open Source Educational Management Information System – Standalone Python Edition" \
      org.opencontainers.image.url="https://github.com/eodenyire/openEMIS" \
      org.opencontainers.image.source="https://github.com/eodenyire/openEMIS" \
      org.opencontainers.image.licenses="LGPL-3.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose API port
EXPOSE 8000

# Run with uvicorn (production: no --reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
