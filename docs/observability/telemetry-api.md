# Telemetry Headers & Metrics API

Aegis provides deep visibility into inference traffic, caching efficiency, and provider availability through standard HTTP response headers and dedicated telemetry endpoints.

---

## 1. Response Tracing Headers

Every response returned by `/v1/chat/completions` includes three granular headers:

| Header | Possible Values | Description |
| :--- | :--- | :--- |
| `X-Aegis-Cache` | `HIT`, `MISS` | Whether the request was fulfilled from semantic cache or routed upstream. |
| `X-Aegis-Provider` | `aegis_semantic_cache`, `gemini`, `openai`, `mock` | The exact provider or cache engine that fulfilled the completion. |
| `X-Aegis-Latency-Ms` | Numeric (e.g. `0.18`, `81.39`) | Total gateway execution duration in milliseconds. |

---

## 2. Telemetry Metrics Endpoint (`GET /metrics`)

The `/metrics` endpoint exposes real-time statistics covering cache efficiency, financial ROI, and circuit breaker statuses.

### Sample Response:
```json
{
  "cache": {
    "total_cached_entries": 142,
    "total_queries": 1050,
    "total_hits": 682,
    "hit_ratio_percent": 64.95,
    "total_tokens_saved": 418290,
    "estimated_cost_saved_usd": 1.04573,
    "recent_queries": [
      {
        "time": "13:28:45",
        "prompt": "user: How to configure Docker networking?",
        "cached": true,
        "provider": "aegis_semantic_cache",
        "latency_ms": 0.18,
        "tokens_saved": 22
      }
    ]
  },
  "circuit_breakers": {
    "gemini": {
      "name": "gemini",
      "state": "CLOSED",
      "failure_count": 0,
      "success_count": 368,
      "last_failure_time": 0.0,
      "cooldown_seconds": 30.0
    },
    "openai": {
      "name": "openai",
      "state": "CLOSED",
      "failure_count": 0,
      "success_count": 0,
      "last_failure_time": 0.0,
      "cooldown_seconds": 30.0
    }
  }
}
```

---

## 3. Health & Liveness Probe (`GET /health`)

Designed for Kubernetes liveness/readiness probes and load balancer health checks.

```bash
curl http://localhost:8000/health
```

### Response (`200 OK`):
```json
{
  "status": "healthy",
  "service": "aegis-ai-gateway",
  "active_providers": ["gemini", "openai", "mock"]
}
```

---

## 4. Cache Invalidation Endpoint (`POST /cache/clear`)

To programmatically invalidate the semantic vector store (for example, after deploying a prompt change or updated documentation):

```bash
curl -X POST http://localhost:8000/cache/clear
```

### Response (`200 OK`):
```json
{
  "status": "cache_flushed"
}
```
All in-memory vector entries and telemetry counters are cleanly reset.
