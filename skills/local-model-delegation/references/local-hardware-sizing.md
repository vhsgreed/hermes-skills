# Local inference hardware sizing

## The math

CPU and unified-memory inference is bandwidth-bound: tok/s ≈ effective memory
bandwidth / weight bytes per token (≈ 0.55-0.6 B/param at Q4). Compute the ceiling
before promising any speed.

- DDR5-5600 dual channel: ≈ 90 GB/s theoretical, ~55-65 GB/s effective in llama.cpp.
- Measured geekom (A7 Max, Ryzen 9 7940HS, 32 GB): 9B dense Q4 ≈ 10 tok/s; 26B-A4B
  MoE Q4 ≈ 14.5 tok/s (only ~4B active per token, so mid-size MoE beats smaller dense
  models on CPU); prefill 45-112 tok/s. An 18 GB model barely fits and pushes into
  swap.
- DGX Spark / ASUS GX10 class (128 GB LPDDR5x, 273 GB/s): 70B at 2.7-3.4 tok/s, 32B
  ≈ 7 tok/s. Capacity machines, not decode machines; GDDR cards decode 5-10x faster
  at the same model size.

## Capacity rules

- Quantized inference: Q4 ≈ 0.55-0.6 GB per B params, plus 2-8 GB KV cache for
  16-100k context. 24 GB runs 27-35B Q4; 48 GB runs 70B Q4; 128 GB runs ~200B Q4.
- Weight editing (abliteration, merges, direction edits) needs fp16/bf16 weights in
  memory: 9B ≈ 18 GB, 27B ≈ 54 GB, 70B ≈ 140 GB, 235B ≈ 438 GB. Editing 70B+ is a
  rent-a-cluster job even when running the edited model quantized is local.
- MoE models price by active parameters for decode speed, by total parameters for
  storage and editing.

## Rent vs buy

- Interactive daily use over private data (journal, client material): own the
  hardware; the data staying home is the product.
- Occasional editing runs or frontier-class models (100B+ total, e.g. 1T-param MoE
  checkpoints): rent by the hour; one cluster run costs hundreds of SEK against a
  70k+ SEK box that cannot load the model anyway.
- Used GPU prices ride AI demand spikes (3090-class traded +47% y/y in 2026). Re-check
  current Prisjakt/Blocket prices before quoting any card in a plan; a price from an
  article is a mood.
