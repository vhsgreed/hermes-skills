---
name: model-tier-routing
description: "Use when choosing which model or worker runs a task."
version: 1.1.0
author: Karl Sundström + Hermes
license: MIT
metadata:
  hermes:
    tags: [models, routing, cost, delegation, fallback, benchmark, compression, effort]
    related_skills: [claude-code, hermes-agent]
---

# Model tier routing

## When to Use

Choosing which model, worker, delegation target, summarizer (compression/aux) or fallback runs a task; evaluating a new model or a "router" setup someone posted; rerouting after a provider failure or policy block; explaining why a model was picked.

Cheapest tier that can do the job. Never a pay-per-use model that duplicates a subscription (never PAYG Claude on OpenRouter).

## The ladder (current wiring)

1. **Opus 5.5 via `claude-subscription-directsdk-experimental`** (Pro subscription, spawns the `claude` CLI): main chat model. Haiku 5.5 on the same provider is the subscription's quick/mechanical rung (switch per session, not per turn).
2. **mimo** (`xiaomi/mimo-v2.6-pro`, OpenRouter, ~$30/mo measured): fallback on Pro 429s, delegation, cron, aux. Karl likes it; replace only for a measured clear win (faster at marginal cost, no quality loss).
3. **gemma** (local Ollama `gemma4:26b-agentic`, $0, ~350 s/task): last-resort fallback and anything that must stay on the machine.
- **Mechanical OpenRouter rung** (short structured tasks: extract, classify, convert): `openai/gpt-6-luna` scored 0.995 on the 12-task code-graded benchmark at $0.08 per 1k tasks, 2.6 s p50. Luna is NOT a good compression summarizer (low AA index at low effort, loses ~a third of facts on long transcripts); judge summarizers with the compression bench instead.

## Procedure: evaluating a model or routing idea

1. **Map it onto the real wiring first.** Read `~/.hermes/config.yaml` (model, `fallback_providers`, `auxiliary`, `reasoning_effort`, `compression`) and the provider plugin. A proxy/router can only see HTTP rungs; the directsdk rung is a CLI subprocess.
2. **Measure current spend/burn, never estimate** (see Cost discipline + Cap economics). Reprice the real token stream from agent.log on candidate prices rather than comparing list prices.
3. **Pull public numbers in full**: AA leaderboard via embedded RSC payload, not the rendered table (recipe in `references/model-evaluation.md`).
4. **Run our own benchmark on our own task shape** before switching anything: `~/projects/gemma-benchmark/run_openrouter.py` (mechanical, ~$0.05) or `compression_bench.py` (summarizer recall on real transcripts). Validate graders against known hand scores or reference answers before spending.
5. **Apply config with `hermes config set`, then verify at the wire**, not in the file (verification commands in the reference). Re-pin any model whose effort a global change would silently raise.
6. Record findings here and update `~/STATUS.md`.

## Routing rules

- Route per task on agentic sessions, never per turn: per-turn model switching breaks provider prompt-cache prefixes, and a per-turn classifier only sees the last message (context-blind: "yes"/"go on" after hard work gets mis-scored). Social-media "50% saved with a complexity router" claims are stateless API traffic, not long cached agent sessions.
- litellm cannot front claude-subscription-directsdk (no HTTP endpoint; ANTHROPIC_BASE_URL guard fail-closed by policy). Do not add litellm.
- `jev-tier-router` plugin (~/.hermes/plugins/jev-tier-router) exists but is DISABLED for the reasons above; keep it off unless the design changes to per-task.
- Haiku 5.5 / Opus 5.5 reject thinking-off (MANDATORY_THINKING), so effort, not thinking-off, is the lever on those rungs.
- Effort beats model swapping for cap preservation; context hygiene beats both.

**Compression summarizer (benchmarked 2026-10-10, ~/projects/gemma-benchmark/RESULTS-compression.md):** recall on real 150K-char windows was deepseek-v4.1-flash 0.89 at 42 s, mimo-v2.6-flash 0.85 (too slow: 130 to 297 s), glm-5.3 0.75, mimo-v2.6-pro 0.71 (2 of 6 runs were truncated by the GMICloud and Novita providers), luna 0.61 to 0.65, flash-lite 0.47 with 17 fabrications. Do not use luna or flash-lite as the summarizer. Run the bench with ~/src/hermes-pr-test/.venv/bin/python, because the tools python lacks ruamel.

**v2 benchmark 2026-10-27 (RESULTS-v2-2026-10-27.md, pre-registered PLAN-v2.md, $6.54):** 18 tasks x 7 models, 244 runs. 1017 @ medium passed all 5 fallback bars vs mimo (hard 1.000 vs 0.997, 15 s vs 105 s, $0.0056 vs $0.0128/task); compression 1017-low passed all 3 bars (recall 0.885 vs 0.836, 8 windows). Our tasks ceiling at ~1.0 for 6/7 models, so AA Terminal-Bench does not predict them (rho 0.14); AA non-hallucination does track honesty traps (rho 0.75). minimax-m3.1-flash fails honesty traps; mimo-v2.6-flash viable cheap backup.

**Benchmarked 2026-10-27 (RESULTS-2026-10-27.md):** deepseek-v4.1-flash-1017 @ medium vs mimo @ medium on agentic_bench: 1.00 vs 0.99, 13 s vs 51 s p50 per task, same ~$0.0055/task, 0/30 runs contaminated. Mechanical 24/24 (mimo 11/24, fences). Compression 1017-low 0.80 / 0 fabrications vs old flash 0.76 / 2 (within noise; 1017 p50 54 s vs 22 s). Meets the "faster at marginal cost" bar for fallback; caveat AA non-hallucination 0.33 vs mimo 0.59.

**Applied 2026-10-10:** `auxiliary.compression` uses deepseek/deepseek-v4.1-flash with reasoning_effort low. Mimo is pinned to Xiaomi's own servers via `provider_routing.models.mimo-v2-6-pro.only: [xiaomi]`. Use the dot-free key: `hermes config set` splits a dot in `v2.6` into nested keys. The resolver accepts this spelling. The auxiliary tasks (titles, skills_hub) don't read provider_routing, so pin them with `auxiliary.<task>.extra_body.provider.only`. **Fast-fallback search:** no model reaches ~150 tok/s at mimo's price and intelligence. Only Haiku 5.5, Muse Spark 1.3 and Sonnet 5.5 reach 110+ tok/s at index 42+, and all cost 7x+ per task. glm-5.3 on fast hosts runs 166 to 190 tok/s for about $195 to $265 a month vs mimo's $31. Note that mimo's measured throughput on OpenRouter is only 28 to 35 tok/s, below AA's figure of 43.

## Resilience

- Main loop failure → `fallback_providers` (mimo → local gemma).
- `content_policy_blocked` is NOT retryable and does not trigger fallback. Route the step to gemma or split it instead of retrying.
- One pay-as-you-go key only (OpenRouter); Karl does not want to manage multiple PAYG keys. Resilience = gemma, not a second API.

## Cost discipline

OpenRouter spend via POST https://openrouter.ai/api/v1/analytics/query with the management key at ~/.secrets/OPENROUTER_MANAGEMENT_KEY (management keys only, never print it; file holds the raw key, not KEY=VAL). Schema: {"metrics":["total_usage","request_count","tokens_total"],"dimensions":["model"] (add "api_key" to attribute leaks),"order_by":{"field":"total_usage","direction":"desc"},"time_range":{"start","end"},"limit":N}. Zombie keys are the main leak: audit openrouter.ai/settings/keys when spend moves.

- **Per-day spend history:** `GET https://openrouter.ai/api/v1/activity` (same management key) returns rows `{date, model, usage, requests}` for roughly the last 30 days; `GET /api/v1/credits` gives total purchased vs used (balance = difference). For "how has the bill looked since X", sum `usage` per day, split at the change date, compare $/day and monthly pace, and name confounders (heavy build weeks vs quiet weeks) before claiming the saving. Today's date is usually absent from activity.
- **Cron cost audit (do it this way, it takes minutes):** `hermes cron list` shows Mode per job. `no-agent` script jobs cost $0 in models; `Monitor:` jobs run the agent only when the monitor output changes, so count actual agent runs via `ls ~/.hermes/cron/output/<job_id>/` filenames since the window start. Then compare against the activity per-day mimo spend: spikes on work-session days mean delegation, not cron, is the spend. Do not promise cron savings before this check. Jev via OpenRouter Decisions API (POST /api/alpha/decisions, `~typesafe/jev-latest`, question field `instructions`, answer `answers.<name>.noul`) costs noise.

## Subscriptions vs credit plans (Nous Portal, consumer AI plans)

- When Karl asks to compare a plan (Nous Portal Plus/Super/Ultra = $20/$100/$200 for $22/$110/$220 credits at ~API prices, rollover $10/$50/$100; or any credit gateway) against Claude Pro, reprice his MEASURED stream, not list prices: aggregate `~/projects/cost-predictor-spike/data/calls.jsonl` (token_logger output: ts, model, route, input, output, cache_read) by model+route over the window, then cost each rung at the candidate's per-token prices. Opus on the flat Pro subscription reprices to hundreds of dollars a month, so a credit plan can only ever replace the OpenRouter (mimo) rung; frame the saving against the OpenRouter bill (~5.5% top-up fee vs Portal's +10% credit bonus) and check the candidate actually serves the model in use.
- Consumer chat subscriptions (Google AI Pro, Gemini, ChatGPT Plus, Perplexity Pro) are NOT model rungs for Hermes: providers suspend accounts whose subscription OAuth is used by third-party agents, and they include no API credit. If Karl wants such a model in Hermes, it goes through a separate API key (e.g. AI Studio), never his personal subscription login.
- The real lever for the AI budget is context hygiene and cron/delegation volume on OpenRouter, since Pro extra usage is off; offer an audit of which crons call mimo and their monthly cost.

## Hardware vs rental vs API (buy a GPU / Spark / Strix Halo, rent, or OpenRouter)

1. **Measure the workload first**: 30-day spend AND prompt vs completion tokens from `/api/v1/activity` (rows include `prompt_tokens`, `completion_tokens`). Agent traffic is prompt-dominated (100x+ input over output), and local boxes are prefill-bound. That makes "can it even serve this volume" the deciding question, not price.
2. Price each option from live sources, then compute power at the all-in SE3 kWh price, payback against the *replaceable* open-weight spend, and days of prefill per month. Recipe, providers, and billing gotchas: `references/compute-buy-vs-rent.md`.
3. Frame the verdict against Karl's numbers: the $20 per-action cap, monthly burn, and the money-gate date. Say so plainly when nothing pays back before the gate.
4. Owning wins only for models no API serves (abliterated/Heretic fine-tunes, custom LoRAs), privacy, or round-the-clock batch utilisation. Point small models at geekom's existing Ollama first, and use per-second rental for occasional bigger-model tests.
5. If spend is the real complaint, name the actual lever (prompt caching, context trimming) and offer that audit.

**Hyped or unreleased models (e.g. creator fine-tunes):** before giving run advice, verify the weights exist: query `https://huggingface.co/api/models?search=<name>&sort=createdAt` and the official org's GitHub. Press often says "released" when the page says "coming soon". Warn against unofficial GitHub repos offering "Windows zip"/exe downloads of hyped models, because these are a common malware pattern. Use the base model's published VRAM figures as the sizing proxy.

## Cap economics and effort

- Pro subscription hits "session limit" HTTP 429 (resets same evening); extra usage OFF, so every 429 spills to mimo money (~11-16 fallbacks/day, ~$3.75/week measured).
- Cap burn is context-dominated: ~45% cache writes, 34% cache reads, 18% thinking, 3% uncached input. Cold re-caches after idle gaps (~256K each) were ~31% of burn; most burn sits in the longest-lived sessions. Compression at 150K on Opus (`compression.model_thresholds.claude-opus: 0.15`) targets this.
- Effort table (AA, Oct 2026): Opus 5.5 max 58/$5.98 per task, high 54/$1.82, medium 51/$1.34, low 42/$0.55; Sonnet 5.5 max 56/$7.67, high 47/$1.08, medium 41/$0.59; Haiku 5.5 43/$0.21; MiMo 46/~$0.13-0.27; GLM-5.3 max 45; DeepSeek V4.1 Flash 39 (fast but non-hallucination 0.04, avoid for summaries). Opus @ high is the quality-per-cap sweet spot and is the global default.
- **"Is it really serving Opus @ high?"** Answer from evidence: token_logger rows for the subscription route report the model id (Anthropic `msg_` ids, no reseller), `reasoning_effort` in config.yaml is what the plugin forwards, and cache_read share of input (~94% measured) explains why the flat plan is cheap. Say plainly what cannot be verified from inside (server-side effort/quality throttling), and flag ToS risk of subscription use in third-party harnesses as unverified unless checked.
- Effort wiring: directsdk passes `--effort` to `claude -p`; long-lived desktop sessions can carry a per-session override (reasoning pill beside the model picker) that a config change does not touch until restart.

## References

- `references/compute-buy-vs-rent.md`: GPU rental billing models per provider, buy-option shortlist, power and payback recipe with the prefill feasibility gate.
- `references/model-evaluation.md`: AA leaderboard extraction recipe, benchmark harnesses and how to run them, wire-level verification commands, fallback-candidate shortlist.
