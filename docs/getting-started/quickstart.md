# Quickstart Guide

This guide walks you through installing and launching Aegis AI Gateway, configuring provider credentials, and pointing your existing client applications to the proxy.

---

## 1. Installation

### From PyPI (Recommended)

```bash
pip install aegis-ai-gateway
```

### From Source

```bash
git clone https://github.com/TechTonicShift/aegis.git
cd aegis
pip install -e .
```

---

## 2. Setting Up Environment Variables

Aegis supports both Google Gemini and OpenAI as upstream LLM providers. Export your API keys:

```bash
# For Google Gemini (Recommended for embeddings and completions)
export GEMINI_API_KEY="your-gemini-api-key"

# Optional: For OpenAI fallback
export OPENAI_API_KEY="your-openai-api-key"

# Optional: Configure semantic cache sensitivity (default: 0.85)
export SIMILARITY_THRESHOLD="0.82"
```

---

## 3. Launching the Gateway

Start the proxy server using the built-in CLI:

```bash
aegis start --port 8000
```

Once started, the following services are active:
* **Proxy Chat Endpoint:** `http://localhost:8000/v1/chat/completions`
* **Visual Control Plane:** `http://localhost:8000/dashboard`
* **Interactive OpenAPI Specs:** `http://localhost:8000/docs`
* **Real-Time Telemetry JSON:** `http://localhost:8000/metrics`

---

## 4. Connecting Client Applications (1-Line Drop-In)

Because Aegis complies with the OpenAI REST specification, you can redirect any standard OpenAI SDK client by modifying the `base_url`:

=== "Python (OpenAI SDK)"

    ```python
    from openai import OpenAI

    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="not-needed-handled-by-aegis"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "How do I configure Docker networking?"}]
    )

    print(response.choices[0].message.content)
    ```

=== "cURL / HTTP"

    ```bash
    curl -X POST http://localhost:8000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "How do I configure Docker networking?"}]
      }'
    ```

---

## 5. Observing Telemetry Headers

Every HTTP response returned by Aegis includes observability headers:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Aegis-Cache: HIT
X-Aegis-Provider: aegis_semantic_cache
X-Aegis-Latency-Ms: 0.18
```
