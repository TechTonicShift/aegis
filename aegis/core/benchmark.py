"""
Aegis AI Gateway - Built-in Benchmark Engine
Runs empirical latency and cache hit benchmarks across semantic clusters.
"""

import time
import statistics
import os
from typing import List, Dict
from aegis.core.config import Settings
from aegis.core.models import ChatCompletionRequest, ChatMessage
from aegis.brain.gateway_engine import GatewayEngine
from aegis.providers.mock_provider import MockProvider

BENCHMARK_PROMPTS = [
    # Cluster A: Password reset
    ("How do I reset my password?", "A1"),
    ("Forgot my password, how do I reset it?", "A2"),
    ("Steps to change my account password", "A3"),
    ("I lost my password, how to regain access?", "A4"),

    # Cluster B: Docker networking
    ("How to configure bridge networking in Docker?", "B1"),
    ("Docker bridge network configuration guide", "B2"),
    ("Setting up bridge network for Docker containers", "B3"),

    # Cluster C: Python decorators
    ("What are decorators in Python and how do they work?", "C1"),
    ("Explain Python function decorators with examples", "C2"),
    ("How do decorators work in Python?", "C3"),

    # Cluster D: Database indexing
    ("Why should I use B-tree indexes in PostgreSQL?", "D1"),
    ("How do B-tree indexes improve database query speed?", "D2"),

    # Cluster E: REST vs GraphQL
    ("Differences between REST APIs and GraphQL?", "E1"),
    ("Compare GraphQL versus REST API architecture", "E2"),
]

async def run_benchmark(iterations: int = 3):
    print("=" * 70)
    print("  AEGIS AI GATEWAY: EMPIRICAL LATENCY & CACHE HIT BENCHMARK")
    print("=" * 70)

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    use_live_gemini = bool(gemini_key)

    settings = Settings(
        cache_enabled=True,
        similarity_threshold=0.82,
        embedder_type="gemini" if use_live_gemini else "fast_local",
        gemini_api_key=gemini_key,
        provider_cascade=["gemini" if use_live_gemini else "upstream_llm", "mock"],
    )

    gateway = GatewayEngine(settings)
    if not use_live_gemini:
        gateway.register_provider(MockProvider(name="upstream_llm", simulated_delay_ms=1200.0))

    miss_latencies: List[float] = []
    hit_latencies: List[float] = []

    print(f"\n[*] Embedder: {'Google Gemini Dense Vectors' if use_live_gemini else 'Aegis FastLocal Vectors'}")
    print(f"[*] Upstream Provider: {'Live Gemini API' if use_live_gemini else 'Upstream LLM (Simulated 1,200ms)'}")
    print(f"[*] Similarity Threshold: {settings.similarity_threshold}")
    print(f"[*] Running {len(BENCHMARK_PROMPTS) * iterations} total requests across semantic clusters...\n")

    for i in range(iterations):
        for prompt, cluster in BENCHMARK_PROMPTS:
            req = ChatCompletionRequest(
                messages=[ChatMessage(role="user", content=prompt)]
            )
            t0 = time.time()
            res = await gateway.execute(req)
            elapsed_ms = (time.time() - t0) * 1000.0

            if res.cached:
                hit_latencies.append(elapsed_ms)
            else:
                miss_latencies.append(elapsed_ms)

    def calc_percentiles(data: List[float]) -> Dict[str, float]:
        if not data:
            return {"p50": 0.0, "p90": 0.0, "p99": 0.0, "mean": 0.0}
        s = sorted(data)
        return {
            "p50": round(statistics.median(s), 2),
            "p90": round(s[int(len(s) * 0.90)], 2),
            "p99": round(s[min(int(len(s) * 0.99), len(s) - 1)], 2),
            "mean": round(statistics.mean(s), 2),
        }

    miss_stats = calc_percentiles(miss_latencies)
    hit_stats = calc_percentiles(hit_latencies)
    store_stats = gateway.vector_store.get_stats()

    speedup = (miss_stats['mean'] / hit_stats['mean']) if hit_stats['mean'] > 0 else 0.0
    latency_reduction = (1.0 - (hit_stats['mean'] / miss_stats['mean'])) * 100.0 if miss_stats['mean'] > 0 else 0.0

    print("-" * 70)
    print(f"{'Metric':<32} | {'Cache Miss (Live)':<18} | {'Cache Hit (Aegis)':<18}")
    print("-" * 70)
    print(f"{'Mean Latency':<32} | {miss_stats['mean']:>15.2f} ms | {hit_stats['mean']:>15.2f} ms")
    print(f"{'P50 Median Latency':<32} | {miss_stats['p50']:>15.2f} ms | {hit_stats['p50']:>15.2f} ms")
    print(f"{'P90 Latency':<32} | {miss_stats['p90']:>15.2f} ms | {hit_stats['p90']:>15.2f} ms")
    print(f"{'P99 Tail Latency':<32} | {miss_stats['p99']:>15.2f} ms | {hit_stats['p99']:>15.2f} ms")
    print("-" * 70)
    print(f"[*] Overall Latency Reduction: \033[1;32m{latency_reduction:.2f}%\033[0m")
    print(f"[*] Throughput Acceleration:   \033[1;32m{speedup:.1f}x faster\033[0m")
    print(f"[*] Cache Hit Ratio:          \033[1;36m{store_stats['hit_ratio_percent']}%\033[0m ({store_stats['total_hits']}/{store_stats['total_queries']})")
    print(f"[*] Intercepted Tokens:       \033[1;36m{store_stats['total_tokens_saved']:,} tokens\033[0m")
    print(f"[*] Estimated Cost Saved:     \033[1;32m${store_stats['estimated_cost_saved_usd']:.5f} USD\033[0m")
    print("=" * 70)
