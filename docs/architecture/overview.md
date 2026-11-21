# Architecture & Systems Design Overview

Aegis is architected following the **Deep Module** and **Vertical Slice** design principles popularized by John Ousterhout (*A Philosophy of Software Design*). Each module exposes a simple, cohesive interface while encapsulating sophisticated internal algorithms and state machines.

---

## High-Level Architectural Diagram

```mermaid
flowchart TD
    Client["Client Application\n(OpenAI SDK, LangChain, cURL)"] 
    -->|HTTP POST /v1/chat/completions| Controller["Controller Layer\n(FastAPI Router & Observability)"]

    subgraph Aegis Core Gateway ["Aegis Gateway Engine"]
        Controller --> Engine["Gateway Orchestrator\n(aegis/brain/gateway_engine.py)"]
        
        Engine --> Embedder["Vector Embedder\n(Google Gemini / FastLocal)"]
        Embedder --> VectorStore[("In-Memory Vector Store\n(Cosine Similarity Index)")]
        
        VectorStore -- "Similarity >= Threshold\n[CACHE HIT]" --> CacheReturn["Instant Response (<1ms)\nX-Aegis-Cache: HIT\nX-Aegis-Latency-Ms: 0.18"]
        CacheReturn --> Controller
        
        VectorStore -- "Similarity < Threshold\n[CACHE MISS]" --> Breaker{"Circuit Breaker Manager\n(State Machine)"}
        
        Breaker -->|State: CLOSED| P1["Primary: Google Gemini / OpenAI"]
        Breaker -->|State: OPEN (Trip on 429)| P2["Fallback: Secondary Provider"]
        Breaker -->|All Upstreams Failed| P3["Local Mock / Offline Provider"]
        
        P1 --> CacheWrite["Populate Vector Cache & Telemetry Ring-Buffer"]
        P2 --> CacheWrite
        P3 --> CacheWrite
        CacheWrite --> Controller
    end

    Controller -->|Standard OpenAI Response + Tracing Headers| Client
```

---

## Core Module Anatomy

The repository follows a clean, highly modular layout:

```text
aegis/
├── aegis/
│   ├── core/                    # Foundation & Shared Contracts
│   │   ├── config.py            # Typed dataclass settings and environment defaults
│   │   ├── models.py            # OpenAI-compliant Pydantic request/response schemas
│   │   └── benchmark.py         # Self-contained empirical benchmark harness
│   ├── storage/                 # Data Persistence & Vector Indexing
│   │   └── vector_store.py      # Normalized cosine similarity index & ring-buffer
│   ├── brain/                   # Orchestration & Intelligence Layer
│   │   ├── embedder.py          # Gemini 3,072d dense & FastLocal subword vectorizers
│   │   ├── circuit_breaker.py   # Three-state finite state machine per provider
│   │   └── gateway_engine.py    # Main request pipeline and cascade orchestrator
│   ├── providers/               # Upstream Model Adapters
│   │   ├── base.py              # Abstract BaseProvider contract
│   │   ├── gemini_provider.py   # Google Gemini API adapter
│   │   ├── openai_provider.py   # OpenAI API adapter
│   │   └── mock_provider.py     # Fault-injection mock adapter for testing
│   ├── controller/              # HTTP Transport & Visual Presentation
│   │   ├── router.py            # FastAPI REST endpoints & observability headers
│   │   └── dashboard.py         # Embedded dark-mode Tailwind telemetry control plane
│   ├── cli.py                   # Global system command-line interface
│   └── main.py                  # ASGI entry point, CORS middleware & factory
```

---

## Design Principles

### 1. Zero Extra External Infrastructure Required
Many modern semantic caches force developers to deploy, configure, and maintain separate vector database clusters (Pinecone, Weaviate, Milvus). Aegis includes an **optimized in-memory cosine similarity engine** with $O(1)$ dot-product evaluations, enabling single-binary or single-container deployments that run with **zero external database dependencies**.

### 2. Strict OpenAI REST Conformance
Aegis adheres 100% to the OpenAI Chat Completions API specification:
* Request payload: `{"model": "...", "messages": [{"role": "user", "content": "..."}]}`
* Response payload: `ChatCompletionResponse` with `id`, `object="chat.completion"`, `choices`, and `usage`.
* Any application or agent built with LangChain, LlamaIndex, AutoGen, CrewAI, or the OpenAI SDK integrates with Aegis by changing a single parameter: `base_url="http://localhost:8000/v1"`.

### 3. Fail-Safe Cascading
If upstream providers experience rate limits (HTTP 429), server errors (500/503), or network dropouts, Aegis guarantees client resilience through its multi-model circuit breaker cascade, preventing downstream application crashes.
