# Docker Containerization

Aegis includes an optimized `Dockerfile` based on `python:3.11-slim` for zero-dependency containerized deployments.

---

## 1. Building the Docker Image

```bash
docker build -t aegis-gateway:latest .
```

---

## 2. Running the Container

Run the gateway exposing port `8000`:

```bash
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY="your-gemini-api-key" \
  -e SIMILARITY_THRESHOLD="0.85" \
  --name aegis \
  aegis-gateway:latest
```

---

## 3. Docker Compose Recipe

For persistent multi-container workflows, create a `docker-compose.yml`:

```yaml
version: "3.8"

services:
  aegis:
    image: aegis-gateway:latest
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SIMILARITY_THRESHOLD=0.85
      - EMBEDDER_TYPE=gemini
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

Start the stack:
```bash
docker-compose up -d
```
