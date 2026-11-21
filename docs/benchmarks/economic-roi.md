# Enterprise Economic Analysis & ROI

Deploying an intelligent semantic cache delivers immediate, compounding financial returns by eliminating redundant token consumption on frontier models (e.g. OpenAI GPT-4o, Google Gemini 1.5 Pro).

---

## The Cost Equation

Let:
* $N$ = Total monthly inbound queries
* $H$ = Semantic cache hit ratio ($0.0 \le H \le 1.0$, typically $0.40 - 0.70$)
* $\bar{T}_{in}$ = Average prompt tokens per query (e.g. 500 tokens)
* $\bar{T}_{out}$ = Average completion tokens per response (e.g. 300 tokens)
* $P_{in}$ = Upstream price per 1M input tokens
* $P_{out}$ = Upstream price per 1M output tokens

The unoptimized monthly cost without Aegis is:
$$C_{\text{raw}} = N \times \left( \frac{\bar{T}_{in}}{10^6} P_{in} + \frac{\bar{T}_{out}}{10^6} P_{out} \right)$$

With Aegis intercepting redundant queries, the net cost becomes:
$$C_{\text{aegis}} = N(1 - H) \times \left( \frac{\bar{T}_{in}}{10^6} P_{in} + \frac{\bar{T}_{out}}{10^6} P_{out} \right) + N \cdot C_{\text{embed}}$$

Because embedding costs ($C_{\text{embed}} \approx \$0.00002\text{ / 1k}$) are orders of magnitude lower than generative inference, net monthly dollar savings scale directly with the cache hit ratio $H$:
$$\text{Savings} \approx H \times C_{\text{raw}}$$

---

## Financial Projections Across Enterprise Workloads

Assuming an average query workload of **500 prompt tokens** and **300 completion tokens** on `gpt-4o` (\$2.50 / 1M input, \$10.00 / 1M output) with a conservative **50% cache hit ratio ($H=0.50$)**:

| Monthly Query Volume | Unoptimized Monthly Spend | Spend with Aegis | **Monthly Dollar Savings** | **Annual Run-Rate Savings** |
| :---: | :---: | :---: | :---: | :---: |
| **100,000 queries** | \$425.00 | \$212.50 | **\$212.50** | **\$2,550.00** |
| **500,000 queries** | \$2,125.00 | \$1,062.50 | **\$1,062.50** | **\$12,750.00** |
| **1,000,000 queries** | \$4,250.00 | \$2,125.00 | **\$2,125.00** | **\$25,500.00** |
| **5,000,000 queries** | \$21,250.00 | \$10,625.00 | **\$10,625.00** | **\$127,500.00** |
| **10,000,000 queries** | \$42,500.00 | \$21,250.00 | **\$21,250.00** | **\$255,000.00** |

---

## Return on Investment (ROI)

For an enterprise running 1 million queries per month:
* **Infrastructure Cost:** Hosting Aegis on an internal Kubernetes pod or modest VM (\$20 - \$50/month).
* **Net Value Generated:** Over **\$25,000/year** in direct API billing reductions.
* **Effective ROI:** Exceeds **5,000%** within 60 days of deployment.
