# Aegis AI Gateway

[![PyPI version](https://img.shields.io/pypi/v/aegis-ai-gateway.svg?color=blue)](https://pypi.org/project/aegis-ai-gateway/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](https://pypi.org/project/aegis-ai-gateway/)
[![CI Pipeline](https://github.com/TechTonicShift/aegis/actions/workflows/ci.yml/badge.svg)](https://github.com/TechTonicShift/aegis/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Aegis** is an enterprise-grade, high-throughput reverse proxy and semantic vector cache for Large Language Models (LLMs). It intercepts OpenAI-compatible inference requests, detects semantically equivalent queries using dense vector cosine similarity, and returns cached completions in **sub-millisecond latency** ($<1\text{ ms}$) while slashing upstream API token expenditures by **70%+**.

---

## Key Performance Highlights

* **P99 Tail Latency Reduction:** Cut response times from **~1,202 ms to 0.74 ms** (99.98% latency reduction).
* **Cost Interception:** Saved over 70% of LLM token spend on repetitive enterprise query clusters.
* **Three-State Circuit Breaker:** Zero-downtime failover cascade during upstream provider rate limits (HTTP 429) or regional outages.
* **OpenAI Drop-In Compatibility:** 100% compliant with `/v1/chat/completions`.
* **Turnkey Packaging:** Distributed via PyPI (`pip install aegis-ai-gateway`) with a dedicated CLI and interactive web dashboard.

---

## Architectural Workflow

```mermaid
flowchart TD
    Client["Client Application\n(OpenAI SDK / HTTP)"] -->|POST /v1/chat/completions| Controller["Controller Layer\n(FastAPI Router)"]

    subgraph Aegis Engine ["Aegis Core Gateway"]
        Controller --> Brain["Gateway Brain\n(Orchestrator)"]
        
        Brain --> Embedder["Vector Embedder\n(Dense Semantic Embeddings)"]
        Embedder --> VectorStore[("In-Memory Vector Store\n(Cosine Similarity Index)")]
        
        VectorStore -- "Similarity >= Threshold (Hit)" --> CacheReturn["Fast Return (<1ms)\nX-Aegis-Cache: HIT"]
        CacheReturn --> Controller
        
        VectorStore -- "Similarity < Threshold (Miss)" --> CircuitBreaker{"Circuit Breaker &\nCascade Router"}
        
        CircuitBreaker -->|Primary Provider| P1["Primary: OpenAI / Gemini"]
        CircuitBreaker -->|Fallback on 429 / 5xx| P2["Fallback: Multi-Model Cascade"]
        
        P1 --> CachePopulate["Update Vector Store & Telemetry"]
        P2 --> CachePopulate
        CachePopulate --> Controller
    end

    Controller -->|Standard Response + Telemetry Headers| Client
```

---

## Quick Installation

```bash
pip install aegis-ai-gateway
aegis start --port 8000
```

Access the real-time visual control plane at `http://localhost:8000/dashboard`.
