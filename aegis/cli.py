"""
Aegis AI Gateway - Command Line Interface (CLI)
Provides turnkey management: starting the reverse proxy, running automated
benchmarks, querying live telemetry, and flushing semantic caches.
"""

import sys
import os
import argparse
import asyncio
import httpx
import uvicorn

VERSION = "1.0.0"

BANNER = f"""
\033[1;34m    ___    ______ _____  ____ _____\033[0m
\033[1;34m   /   |  / ____// ___/ /  _// ___/\033[0m
\033[1;36m  / /| | / __/  / (_ /  / /  \\__ \\ \033[0m
\033[1;36m / ___ |/ /___  \\___ \\_/ /  ___/ / \033[0m
\033[1;32m/_/  |_/_____/ /____//___/ /____/  \033[0m
\033[1;37m   Aegis AI Gateway • v{VERSION}\033[0m
\033[90m   Semantic Caching & Fault-Tolerant Reverse Proxy\033[0m
"""

def cmd_start(args):
    """Start the Aegis Gateway proxy server."""
    print(BANNER)
    host = args.host
    port = args.port

    if args.threshold is not None:
        os.environ["SIMILARITY_THRESHOLD"] = str(args.threshold)
    if args.embedder is not None:
        os.environ["EMBEDDER_TYPE"] = args.embedder

    print(f"\033[1;32m[✓]\033[0m Starting Aegis Gateway on \033[1;37mhttp://{host}:{port}\033[0m")
    print(f"    ├─ \033[1;36mControl Plane / Web UI:\033[0m  http://{host}:{port}/dashboard")
    print(f"    ├─ \033[1;36mOpenAI Chat Endpoint:\033[0m   http://{host}:{port}/v1/chat/completions")
    print(f"    ├─ \033[1;36mOpenAPI Docs:\033[0m           http://{host}:{port}/docs")
    print(f"    └─ \033[1;36mReal-Time Telemetry:\033[0m    http://{host}:{port}/metrics\n")

    uvicorn.run("aegis.main:app", host=host, port=port, reload=args.reload)

def cmd_benchmark(args):
    """Run empirical latency & semantic hit benchmark."""
    print(BANNER)
    from scripts.benchmark import run_benchmark
    iterations = args.iterations or 3
    asyncio.run(run_benchmark(iterations=iterations))

def cmd_stats(args):
    """Query live metrics from a running Aegis gateway instance."""
    url = f"{args.url.rstrip('/')}/metrics"
    try:
        resp = httpx.get(url, timeout=5.0)
        resp.raise_for_status()
        data = resp.json()
        cache = data.get("cache", {})
        circuits = data.get("circuit_breakers", {})

        print(BANNER)
        print("\033[1;37m=== LIVE GATEWAY TELEMETRY ===\033[0m")
        print(f"Cached Vector Entries:  \033[1;33m{cache.get('total_cached_entries', 0)}\033[0m")
        print(f"Total Queries Handled:  \033[1;37m{cache.get('total_queries', 0)}\033[0m")
        print(f"Semantic Cache Hits:    \033[1;32m{cache.get('total_hits', 0)}\033[0m")
        print(f"Cache Hit Ratio:        \033[1;32m{cache.get('hit_ratio_percent', 0.0)}%\033[0m")
        print(f"Total Tokens Saved:     \033[1;36m{cache.get('total_tokens_saved', 0):,}\033[0m")
        print(f"Estimated Cost Saved:   \033[1;32m${cache.get('estimated_cost_saved_usd', 0.0):.4f}\033[0m\n")

        print("\033[1;37m=== CIRCUIT BREAKER STATUSES ===\033[0m")
        for prov, info in circuits.items():
            state = info.get("state", "UNKNOWN")
            color = "\033[1;32m" if state == "CLOSED" else ("\033[1;31m" if state == "OPEN" else "\033[1;33m")
            print(f" • {prov:20s}: {color}{state}\033[0m (Failures: {info.get('consecutive_failures', 0)})")
        print()

    except Exception as e:
        print(f"\033[1;31m[ERROR]\033[0m Could not connect to Aegis Gateway at {url}: {e}")
        sys.exit(1)

def cmd_flush(args):
    """Flush the in-memory semantic cache of a running instance."""
    url = f"{args.url.rstrip('/')}/cache/clear"
    try:
        resp = httpx.post(url, timeout=5.0)
        resp.raise_for_status()
        print(f"\033[1;32m[✓]\033[0m Semantic cache flushed successfully on {args.url}")
    except Exception as e:
        print(f"\033[1;31m[ERROR]\033[0m Failed to flush cache: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        prog="aegis",
        description="Aegis AI Gateway CLI - High-throughput reverse proxy with semantic vector caching.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"aegis {VERSION}")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: start / serve
    start_parser = subparsers.add_parser("start", aliases=["serve"], help="Launch the Aegis proxy server & dashboard")
    start_parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind (default: 0.0.0.0)")
    start_parser.add_argument("-p", "--port", type=int, default=8000, help="Port to bind (default: 8000)")
    start_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    start_parser.add_argument("--threshold", type=float, default=None, help="Cosine similarity threshold (e.g. 0.88)")
    start_parser.add_argument("--embedder", choices=["fast_local", "gemini"], default=None, help="Embedding engine")

    # Command: benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run local semantic caching benchmark")
    bench_parser.add_argument("-n", "--iterations", type=int, default=3, help="Number of benchmark iterations")

    # Command: stats
    stats_parser = subparsers.add_parser("stats", help="Fetch live metrics from a running Aegis gateway")
    stats_parser.add_argument("--url", default="http://127.0.0.1:8000", help="Aegis gateway base URL")

    # Command: flush / clear-cache
    flush_parser = subparsers.add_parser("flush", aliases=["clear-cache"], help="Flush the gateway's semantic cache")
    flush_parser.add_argument("--url", default="http://127.0.0.1:8000", help="Aegis gateway base URL")

    args = parser.parse_args()

    if args.command in ("start", "serve"):
        cmd_start(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command in ("flush", "clear-cache"):
        cmd_flush(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
