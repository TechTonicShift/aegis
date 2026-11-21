# API Reference & Endpoints

Aegis provides full REST endpoints compliant with the OpenAI specification, alongside custom endpoints for observability and cache management.

---

## 1. `POST /v1/chat/completions`

Generates a model completion with semantic vector cache lookup and automated circuit breaker failover.

### Request Headers
| Header | Type | Description |
| :--- | :--- | :--- |
| `Content-Type` | `string` | Must be `application/json` |

### Request Body Schema
```json
{
  "model": "string (e.g. 'gpt-4o-mini', 'gemini-3.5-flash-lite')",
  "messages": [
    {
      "role": "user | assistant | system",
      "content": "string"
    }
  ],
  "temperature": "float (optional, default: 0.7)",
  "max_tokens": "integer (optional)",
  "stream": "boolean (optional, default: false)"
}
```

### Response Headers
| Header | Value | Description |
| :--- | :--- | :--- |
| `X-Aegis-Cache` | `HIT` or `MISS` | Cache interception status |
| `X-Aegis-Provider` | Provider ID | Which provider fulfilled the request |
| `X-Aegis-Latency-Ms` | Float (ms) | Execution latency |

### Response Body (`200 OK`)
```json
{
  "id": "chatcmpl-aegis-9a4f21b",
  "object": "chat.completion",
  "created": 1732185600,
  "model": "gpt-4o-mini",
  "provider_used": "aegis_semantic_cache",
  "cached": true,
  "latency_ms": 0.18,
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "To configure bridge networking in Docker..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 45,
    "total_tokens": 57
  }
}
```

---

## 2. `GET /v1/models`

Lists available models across registered provider cascades.

### Response (`200 OK`)
```json
{
  "object": "list",
  "data": [
    {"id": "gpt-4o-mini", "object": "model", "owned_by": "openai"},
    {"id": "gemini-3.5-flash-lite", "object": "model", "owned_by": "google"},
    {"id": "aegis-auto", "object": "model", "owned_by": "aegis"}
  ]
}
```

---

## 3. `GET /health`

Liveness and readiness health probe.

### Response (`200 OK`)
```json
{
  "status": "healthy",
  "service": "aegis-ai-gateway",
  "active_providers": ["gemini", "openai", "mock"]
}
```

---

## 4. `GET /metrics`

Returns live telemetry and circuit breaker state machines.

### Response (`200 OK`)
```json
{
  "cache": {
    "total_cached_entries": 24,
    "total_queries": 100,
    "total_hits": 52,
    "hit_ratio_percent": 52.0,
    "total_tokens_saved": 1420,
    "estimated_cost_saved_usd": 0.00355,
    "recent_queries": []
  },
  "circuit_breakers": {
    "gemini": {
      "name": "gemini",
      "state": "CLOSED",
      "failure_count": 0,
      "success_count": 48
    }
  }
}
```

---

## 5. `POST /cache/clear`

Flushes all vector embeddings and telemetry logs from memory.

### Response (`200 OK`)
```json
{
  "status": "cache_flushed"
}
```
