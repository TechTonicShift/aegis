FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package specifications
COPY requirements.txt pyproject.toml README.md ./
COPY aegis/ aegis/

# Install Aegis Gateway and dependencies
RUN pip install --no-cache-dir -e .

EXPOSE 8000

ENV PORT=8000 \
    HOST=0.0.0.0 \
    SIMILARITY_THRESHOLD=0.82 \
    EMBEDDER_TYPE=fast_local

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python3", "-m", "uvicorn", "aegis.main:app", "--host", "0.0.0.0", "--port", "8000"]
