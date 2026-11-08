# Compute: buy hardware vs rent GPUs vs API tokens

Depth for the "Hardware vs rental vs API" section in SKILL.md. Prices go stale fast: DRAM shortages doubled unified-memory box prices within months, so re-fetch before quoting. The numbers below are a starting point for the search, not values to quote.

## Billing models (check the provider's docs page, not blog tables)

| Provider | Billing unit | Gotchas |
|---|---|---|
| Runpod Pods | per second, compute + storage, no egress fees | 1 h of credit required to start; stopped-pod volume disk billed at 2x; $0 balance terminates pods without a network volume (data lost). Per-GPU prices only in the console. |
| Vast.ai | per second; on-demand / interruptible (50%+ cheaper, reclaimable) / reserved 1-6 mo | marketplace prices; third-party hosts. |
| Lambda | hourly rate billed per minute | bills while idle; datacenter GPUs only (A6000 48GB is the cheapest useful tier). |
| Modal | per second, serverless scale-to-zero; Starter plan includes $30/mo compute | needs Python deploy code, not an SSH box. Good for a rarely-hit private endpoint. |
| HF Spaces / Inference Endpoints | hourly | priciest per hour; ZeroGPU free tier, PRO $9/mo raises quota. |
| JarvisLabs | per minute | single node only. |

Pages that extract cleanly: docs.runpod.io/pods/pricing, vast.ai/pricing, docs.lambda.ai/public-cloud/billing/, lambda.ai/pricing, modal.com/pricing (per-second rates; multiply by 3600), huggingface.co/pricing.

## Buy options to price

- **eGPU**: used RTX 3090 24 GB (track bestvaluegpu.com price history) + OCuLink/USB4 dock ($40-350). geekom (GEEKOM A7 Max, Ryzen 9 7940HS) has two USB4 controllers and no OCuLink. Published LLM penalty figures are for OCuLink (~7-8%); treat USB4 as somewhat worse, unmeasured.
- **Strix Halo 128 GB** (Framework Desktop, GMKtec EVO-X2, Beelink GTR9): same chip, differences are cooling/firmware. Prefill ~340 tok/s.
- **DGX Spark** 64 GB / 128 GB (GB10): CUDA, prefill ~1,700 tok/s, ~5x Strix. Check pi3g.com (EU) and ServeTheHome for current prices.

## Power cost

Use the all-in SE3 apartment price (spot + grid fee + energy tax + VAT, ~2.9 SEK/kWh), not spot alone (elpris-idag.se shows monthly spot averages). Model monthly kWh as (load_W x load_h + idle_W x (24 - load_h)) x 30 / 1000 for both 4 h/day and 24/7 scenarios.

## Calculation recipe

1. Spend + token mix from `GET /api/v1/activity`: rows also carry `prompt_tokens` and `completion_tokens`, so sum both alongside `usage`. Split the subscription-duplicate models (Claude) out; only open-weight spend is replaceable by local hardware.
2. Payback months = capex / (replaceable monthly API spend - monthly power). Label it optimistic.
3. Feasibility gate before payback: monthly prompt tokens / box prefill tok/s / 86400 = days of prefill per month. If that is over ~30, the box cannot serve the workload at any price. Also check that the models in use fit in the box's memory.
4. Rental equivalent: $/h x 120 (4 h/day) and x 730 (24/7).
5. Compare against OpenRouter per-token prices for the same model (`GET /api/v1/models`, pricing fields are $/token; x1e6 for $/M).
