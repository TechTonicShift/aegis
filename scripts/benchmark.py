"""
Aegis AI Gateway - Standalone Benchmark Script
Wraps the core benchmark engine for direct terminal execution.
"""

import asyncio
from aegis.core.benchmark import run_benchmark, BENCHMARK_PROMPTS

if __name__ == "__main__":
    asyncio.run(run_benchmark(iterations=3))
