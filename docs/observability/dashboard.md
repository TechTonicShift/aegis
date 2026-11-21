# Real-Time Control Plane Dashboard

Aegis includes an interactive visual control plane served at `/dashboard`.

---

## Key Features

1. **Live Financial Telemetry:**
   * Dynamic dollar cost savings based on benchmarked token pricing (\$2.50 per 1M tokens).
   * Total intercepted tokens count updated in real time.
2. **Hit Ratio & Latency Tickers:**
   * Dynamic hit ratio percentage ($H = \frac{\text{Hits}}{\text{Total Queries}}$).
   * Millisecond latency comparisons for cache hits vs cache misses.
3. **Interactive Semantic Sandbox:**
   * Send test prompts directly from your browser.
   * Observe `CACHE MISS` on initial calls, rephrase the prompt, and verify instant `CACHE HIT` with sub-millisecond latencies.
4. **Provider Health Grid:**
   * Real-time circuit breaker status cards (`CLOSED`, `OPEN`, `HALF_OPEN`) across Google Gemini, OpenAI, and local mock providers.
5. **Rolling Activity Stream:**
   * Live traffic feed tracking the last 50 queries with timestamps, execution durations, and provider tags.
6. **One-Click Cache Flush:**
   * Instantly clear the in-memory vector store on demand.
