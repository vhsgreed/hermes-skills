# Model evaluation recipes

## Artificial Analysis leaderboard: full data

The rendered/extracted table at artificialanalysis.ai/leaderboards/models is truncated and has empty cells, and `compare=` URL params are client-side only. The full data is in the Next.js RSC payload:

1. `curl -sL -A "Mozilla/5.0 ... Chrome/140" https://artificialanalysis.ai/leaderboards/models -o aa.html`
2. Join every `self.__next_f.push([1,"..."])` chunk, JSON-unescaping each (`json.loads('"'+c+'"')`).
3. For each match of `{"slug":"`, `json.JSONDecoder().raw_decode(payload, pos)`; keep dicts containing `intelligenceIndex`, dedupe by slug, drop `deprecated`.
4. Useful fields: `intelligenceIndex`, `intelligenceIndexCostPerTask`, `price1mInputTokens/OutputTokens`, `medianOutputTokensPerSecond`, `medianTimeToFirstAnswerTokenSeconds`, `medianEndToEndResponseTimeSeconds`, `terminalBench40` (agentic), `lcr` (long-context recall, relevant for summarizers), `omniscienceNonHallucination`.
5. Map to OpenRouter ids by normalized name against https://openrouter.ai/api/v1/models (strip effort suffixes like `(max)`). Last export: `~/projects/gemma-benchmark/aa-leaderboard-*.csv`.

Reasoning models' AA latency is end-to-end including thinking: luna at max is ~100 s, at low ~7 s. Compare at the effort you will actually run.

## Live provider latency

`GET https://openrouter.ai/api/v1/models/<id>/endpoints` (Bearer OPENROUTER_API_KEY) gives per-provider `latency_last_30m` / `throughput_last_30m` p50/p90 and price. Providers for one model vary 10x in price and speed; the cheapest endpoint is often fp4 and slower.

## Repricing real traffic

Parse agent.log `API call #N: model=... in= out= ... cache=hit/` lines for the role being replaced (e.g. mimo fallback calls), then cost them as (in-cache)*prompt + cache*input_cache_read + out*completion per candidate. Cache-read price dominates for agentic traffic (90%+ cache hits): models with expensive cache reads lose badly even at low list prices.

## Benchmarks (~/projects/gemma-benchmark)

- `run_openrouter.py [--models a,b] [--runs N] [--local]`: 12 short mechanical tasks, code-graded, parallel, appends `results-openrouter/raw.jsonl`. ~$0.05 per full run. Results: `RESULTS-openrouter.md`.
- `agentic_bench.py --models "m:effort,..." --runs 2`: 5 real `hermes chat` tool-loop tasks (bugfix vs hidden tests, CSV->VAT JSON, package rename, log root-cause, byte-exact STATUS edit), code-graded, ~$0.20 for 3 configs x 2 runs. Checks session_model_usage so a silent fallback to mimo cannot contaminate a run. Benchmark the fallback rung with this, not run_openrouter.py: short tasks don't exercise the tool loop. Tasks hit a ceiling (~1.0 for both 1017 and mimo); add harder long-horizon tasks before using it to claim one model is smarter.
- Benchmarks launched from a Hermes session run inside hermes-serve.service's cgroup: one runaway model tool call (an unbounded `^` tower in a fuzz test, 10 GB) triggers the OOM killer and systemd then kills the WHOLE unit (benchmark chain, live chat, desktop backend). agentic_bench.py wraps each `hermes chat` in `systemd-run --user --scope -p MemoryMax=2G -p MemorySwapMax=0`; keep that for any harness that runs model-written code.
- Applying a model swap: `hermes config set` for fallback_providers, agent.reasoning_overrides.<canonical-id>, provider_routing.models.<canonical-id>.ignore (warns 'not recognized' but chat_completion_helpers reads it), auxiliary.<task>.model + auxiliary.<task>.extra_body.provider.ignore (aux calls don't read provider_routing), delegation.model; cron pins via `hermes cron edit ID --model M --provider openrouter`. Verify with a real `hermes chat -m` call plus `hermes --run-module` on a script copied into ~/.hermes/hermes-agent (call_llm(task='compression')), then look up gen ids at /api/v1/generation?id= for provider_name.
- v2 harness lessons: validate every grader (broken < 1, reference == 1) AND compute gold two independent ways; my hand-written gold was wrong in 3/5 SQL items and one VAT total. Guard every hidden-test check individually: one unguarded case that the spec didn't require crashed a whole grader and zeroed a correct model. `fill_missing.py` resumes interrupted runs; chain jobs in one background command with notify, never via long foreground sleeps (interrupting the wait killed the chain). Budget guard: agentic_bench.spent() vs budget.json.
- `compression_bench.py`: builds Hermes' exact summarizer prompt (`ContextCompressor._serialize_for_summary` + `_build_summary_prompt`) from ~150K-char windows of real sessions in a COPY of `~/.hermes/state.db`, runs candidate summarizers with effort settings, then a fixed judge model scores recall on 12 cached gold questions per window plus fabrication count. Outputs `results-compression/`.
  - It imports Hermes internals, so run it with an interpreter that has Hermes' deps: `~/src/hermes-pr-test/.venv/bin/python` works against the live source (the launcher's bundled Python lacks ruamel).
  - Resolve output paths from `Path(__file__)` before any `os.chdir`.
  - Refresh the DB copy first via sqlite3 backup API (`state_copy.db` gets pruned to 0 bytes in scratch). Env overrides: `BENCH_CANDIDATES="model:effort,model:none" BENCH_RUNS=2`.
  - Run 2+ runs per window: the same model on identical prompts scored 0.889 on 10-10 and 0.757 on 10-27 (provider/run variance > most model gaps).
- Before spending: check graders reproduce known hand scores and that reference answers score 1.0; confirm every candidate id exists in /api/v1/models.
- Strip code fences before grading if downstream code will; fence penalties dominate otherwise-correct JSON from mimo/glm/gemma/flash-lite.
- Write ambiguous-free prompts: a field named like a word in the source text (e.g. `lev` vs "Leveransdatum") makes every model "swap" fields.

## Verify config at the wire

- Compression threshold: `hermes chat -v -q 'Reply with just: ok' 2>&1 | grep 'Context compressor initialized'` (the line only logs in verbose mode; old log lines mislead).
- Effort: background `ps -eww -o args= | grep -- '--input-format stream-json'` sampling during a `hermes chat -q` run; look for `--effort <x> --model <y>`.
- Per-model effort pins: `agent.reasoning_overrides.<model-slug>`; check matching with `hermes_constants.resolve_per_model_reasoning_effort(model, overrides)` (slug `mimo-v2-6-pro` matches `xiaomi/mimo-v2.6-pro`). After raising the global effort, pin fallback/aux models that should not inherit it.
- `hermes config set` warns "Did you mean ..." for valid-but-unregistered keys like `agent.reasoning_effort`; verify the key landed with `hermes config get` and a diff against a backup.

## New-model sweep 2026-10-27 (OpenRouter models created since mimo-v2.6-pro, 2026-09-21)

List them with `/api/v1/models` filtered on `created >= mimo's created`, then AA RSC join. Repriced 30d mimo stream (calls.jsonl, 571M in / 94.6% cache / 5.4M out): mimo $20/mo, deepseek-v4.1-flash-1017 $19 list ($8 on cheap fp8 hosts), minimax-m3.1-flash $16, gpt-6.1-terra $85 (cache read $0.05 kills it), step-5 $100, gemini-4-argon $170, glm-5.3 $208, kimi-k3.1-pro $224. Only DeepSeek V4.1 Flash 1017 (AA 45.1, TB 0.34, non-halluc 0.33 up from 0.04, 130-226 tok/s) is a near-mimo-quality, faster, same-cost candidate; AA no longer lists the old v4.1-flash used for compression. Frontier leaders: Muse Wonder Full 55.8 (no price), Kimi K3.1 Pro 55.1 (TB 0.67, 24-31 tok/s on OR), Gemini 4 Argon 52.6 (non-halluc 0.85). MiniMax M3.1 Flash non-halluc 0.07: avoid.

## Fallback-candidate shortlist (vs mimo, Oct 2026)

From AA + repriced mimo traffic: GLM-5.3 max ~2x mimo throughput, idx 45, better terminal-bench and non-hallucination, ~1.7x monthly cost: the only serious "faster at marginal cost" swap. Step-5 ~3x cost; Gemini 3.8 Flash ~3.4x cost and weaker agentic; DeepSeek V4.1 Flash fast and cheap but hallucinates; MiMo-V2.6-Flash cheapest but idx 38.
