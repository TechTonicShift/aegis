import asyncio
import time
import statistics
import os
from typing import List, Dict, Any
from aegis.core.config import Settings
from aegis.core.models import ChatCompletionRequest, ChatMessage
from aegis.brain.gateway_engine import GatewayEngine
from aegis.providers.mock_provider import MockProvider

# Benchmark queries demonstrating real-world semantic overlap
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

async def run_benchmark(iterations: int = 5):
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
        # Simulate realistic frontier LLM API latency (~1,200ms)
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

    # Compute statistics
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
    print(f"{'METRIC':<30} | {'CACHE MISS (LIVE)':<18} | {'CACHE HIT (AEGIS)':<18}")
    print("-" * 70)
    print(f"{'Mean Latency':<30} | {miss_stats['mean']:>12.2f} ms | {hit_stats['mean']:>12.2f} ms")
    print(f"{'P50 Median Latency':<30} | {miss_stats['p50']:>12.2f} ms | {hit_stats['p50']:>12.2f} ms")
    print(f"{'P90 Latency':<30} | {miss_stats['p90']:>12.2f} ms | {hit_stats['p90']:>12.2f} ms")
    print(f"{'P99 Tail Latency':<30} | {miss_stats['p99']:>12.2f} ms | {hit_stats['p99']:>12.2f} ms")
    print("-" * 70)
    print(f"\n[+] Total Requests Processed : {len(miss_latencies) + len(hit_latencies)}")
    print(f"[+] Cache Hits               : {len(hit_latencies)} ({store_stats['hit_ratio_percent']}%)")
    print(f"[+] Total Tokens Intercepted : {store_stats['total_tokens_saved']:,}")
    print(f"[+] Latency Reduction        : {latency_reduction:.1f}%")
    print(f"[+] Throughput Speedup       : {speedup:.1f}x FASTER")
    print(f"[+] Est. API Spend Avoided   : ${store_stats['estimated_cost_saved_usd']:.5f} USD\n")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_benchmark(iterations=3))
