"""
Example: Drop-in usage of Aegis AI Gateway with standard OpenAI SDK or HTTP requests.
Simply point `base_url` to Aegis Gateway (http://localhost:8000/v1).
"""

import httpx
import time

GATEWAY_URL = "http://localhost:8000/v1/chat/completions"

def query_gateway(prompt: str):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    t0 = time.time()
    resp = httpx.post(GATEWAY_URL, json=payload, timeout=30.0)
    latency_ms = (time.time() - t0) * 1000.0

    data = resp.json()
    cache_header = resp.headers.get("X-Aegis-Cache", "UNKNOWN")
    provider = resp.headers.get("X-Aegis-Provider", "UNKNOWN")

    print(f"\nQuery: '{prompt}'")
    print(f"Status: {resp.status_code} | Cache: {cache_header} | Provider: {provider} | Latency: {latency_ms:.2f}ms")
    print(f"Answer: {data['choices'][0]['message']['content'][:120]}...\n")

if __name__ == "__main__":
    print("Testing Aegis Gateway Semantic Interception...")

    # First Query (Cache Miss)
    query_gateway("How do I reset my password?")

    # Second Query with different wording (Semantic Cache HIT!)
    query_gateway("Forgot my password, what is the procedure to reset it?")
