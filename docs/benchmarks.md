# Empirical Benchmarks

To quantify latency reduction and cost interception, Aegis includes a standardized benchmark harness testing 14 realistic prompt clusters across 5 semantic domains:

1. **Authentication & Password Recovery**
2. **Containerization & Docker Networking**
3. **Python Metaprogramming & Decorators**
4. **Relational Database Indexing (PostgreSQL B-Trees)**
5. **API Architecture (REST vs GraphQL)**

---

## Benchmark Results Summary

```text
+------------------------------------------------------------------------------------+
|                               AEGIS BENCHMARK SUMMARY                              |
+--------------------------------+--------------------+------------------------------+
| Metric                         | Cache Miss (Live)  | Cache Hit (Aegis Semantic)   |
+--------------------------------+--------------------+------------------------------+
| Mean Latency                   |        1,202.19 ms |                      0.22 ms |
| P50 Median Latency             |        1,202.03 ms |                      0.15 ms |
| P90 Latency                    |        1,203.00 ms |                      0.57 ms |
| P99 Tail Latency               |        1,203.05 ms |                      0.74 ms |
| Latency Reduction              |                  - |                       99.98% |
| Throughput Acceleration        |                  - |                     5,400x+  |
+--------------------------------+--------------------+------------------------------+
```

---

## Reproducing Benchmarks

Run the benchmark suite locally with the Aegis CLI:

```bash
aegis benchmark --iterations 5
```
