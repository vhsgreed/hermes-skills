# Sizing local-inference hardware (buy, upgrade, or rent)

Use when the user asks what a machine, an upgrade, or a purchase would net for running
LLMs locally. Convert the wish into a measured gap list before pricing anything. Money
verdicts and budget lines belong to life-and-money-planning; this file is the arithmetic
and the hardware decision procedure.

## Procedure

1. **Measure the machine as it stands** (RAM total/available, swap in use, models on
   disk, one timed generation on the model already loaded). Then run the intended use
   case on existing hardware for days before any purchase verdict. Existing hardware
   often covers most of the want; the trial converts a mood goal into a gap list.
2. **Build the gap list:** which models at what context length, interactive decode vs
   overnight bulk, inference-only vs weight-editing. Each gap maps to one row below.
3. **Price the tiers** from live listings (new AND used; GPU and DDR5 prices swing 2x on
   AI demand, so "hardware holds value" is a bet, not a floor) and compare against
   renting: daily interactive use with private data favors ownership; sporadic burst
   work and edit runs favor rented hours (check slot count and documented max before
   ordering RAM).
4. **Deliver keep / park / drop per tier with numbers**, naming which gap each tier
   closes and what stays impossible (e.g. fp16 editing of 70B on any desktop tier).

## The arithmetic that decides everything

- **Decode is memory-bandwidth-bound:** tok/s ≈ effective bandwidth / weight bytes read
  per token. Q4 weights cost ~0.55-0.6 bytes/param. MoE reads only activated experts, so
  a 26B-A4B can decode faster than a 9B dense. Prefill is compute-bound and runs 3-10x
  faster than decode on the same box.
- **Use the real bandwidth, not the spec number:** dual-channel DDR5-5600 is 89.6 GB/s
  theoretical and ~55-65 GB/s effective for llama.cpp. Compute the estimate, then
  confirm with a short timed run before promising anything.
- **Capacity tiers at Q4:** 24 GB holds 27-35B dense; 2x24 or 1x48 GB holds 70B dense;
  128 GB unified holds 200B-class quantized. Weight-editing tools need fp16 (2
  bytes/param): a 27B edit ≈ 54 GB, a 70B edit ≈ 140 GB. Always say which of run-vs-edit
  the box enables; they have different thresholds.
- **Unified-memory "AI box" class** (128 GB at ~270 GB/s) buys capacity, not speed:
  expect single-digit tok/s at 70B and low single digits at 200B. GDDR cards decode
  5-10x faster per token on the same weights. Match the machine to the workload:
  interactive co-writing needs decode; evals and overnight drafts need capacity.

## Current baselines (verify; hardware drifts)

- geekom (A7 Max, Ryzen 9 7940HS, CPU only): 9B Q4 ~10 tok/s decode, 26B-A4B MoE
  IQ4 ~15 tok/s, 27B dense Q4 ~3-5 tok/s, 70B Q4 ~1.2-2 tok/s at 64 GB RAM.
