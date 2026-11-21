# CLI Toolkit Reference

Aegis includes a dedicated command-line interface (`aegis`) installed automatically with the package.

---

## Command Overview

```text
usage: aegis [-h] [-v] {start,serve,benchmark,stats,flush,clear-cache} ...

Aegis AI Gateway CLI - High-throughput reverse proxy with semantic vector caching.

positional arguments:
  {start,serve,benchmark,stats,flush,clear-cache}
    start (serve)       Launch the Aegis proxy server & dashboard
    benchmark           Run local semantic caching benchmark
    stats               Fetch live metrics from a running Aegis gateway
    flush (clear-cache) Flush the gateway's semantic cache
```

---

## 1. `aegis start` (or `aegis serve`)

Launches the reverse proxy and control plane dashboard.

```bash
aegis start [OPTIONS]
```

### Options:
* `--host TEXT`: Host interface to bind (default: `0.0.0.0`).
* `-p, --port INTEGER`: Port to listen on (default: `8000`).
* `--reload`: Enable hot reloading for local development.
* `--threshold FLOAT`: Set minimum cosine similarity for cache hits (e.g. `0.85`).
* `--embedder [fast_local|gemini]`: Select the embedding engine.

---

## 2. `aegis benchmark`

Executes empirical micro-benchmarks against realistic semantic prompt clusters to evaluate latency reduction and hit rates.

```bash
aegis benchmark [-n ITERATIONS]
```

### Example Output:
```text
----------------------------------------------------------------------
Metric                           | Cache Miss (Live)  | Cache Hit (Aegis) 
----------------------------------------------------------------------
Mean Latency                     |         1202.04 ms |            0.35 ms
P50 Median Latency               |         1201.99 ms |            0.35 ms
P90 Latency                      |         1203.03 ms |            0.52 ms
P99 Tail Latency                 |         1203.15 ms |            0.52 ms
----------------------------------------------------------------------
[*] Overall Latency Reduction: 99.97%
[*] Throughput Acceleration:   3434.4x faster
```

---

## 3. `aegis stats`

Queries live telemetry from a running gateway instance and outputs metrics to terminal.

```bash
aegis stats [--url http://localhost:8000]
```

### Displays:
* Cached Vector Count
* Total Queries Processed
* Cache Hit Ratio (%)
* Total Tokens Saved
* Avoided API Costs ($ USD)
* Circuit Breaker Health Statuses

---

## 4. `aegis flush`

Clears the in-memory vector store on a running gateway instance without restarting the process.

```bash
aegis flush [--url http://localhost:8000]
```
