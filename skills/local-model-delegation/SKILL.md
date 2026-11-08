---
name: local-model-delegation
description: "Use when deciding what to delegate to a cheap local model."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [models, ollama, delegation, benchmark, cost, gemma]
---

# Local model delegation

## When to Use

Deciding whether a class of task goes to a local model (Ollama on geekom) instead of
the main model; scoping which cron jobs can be pinned to the cheap model; re-checking
the boundary after a model, quantization, or prompt-template change; measuring refusal
or alignment behavior of local models (abliterated vs aligned pairs, over-refusal vs
safety refusal).

Depth when needed: `references/refusal-benchmarking.md` (adversarial prompt sets,
classifier design, tradeoff math), `references/local-hardware-sizing.md` (what fits
and how fast on geekom, a GPU, or a unified-memory box).

## Always-on rules

1. **The delegation boundary is measured, not assumed.** Never hand a task class to a
   local model because it "should" handle it; run the benchmark and read the failure
   modes first. A confident wrong answer from a cheap model is indistinguishable from
   a right one without an expected answer to compare against.
2. **Build the task set from real recurring jobs in this workspace**, 8-12 tasks, each
   with a machine-checkable expected answer. Include at least one noisy-input
   extraction task and one judgment/triage task: those are where cheap models fail in
   ways that corrupt output silently rather than loudly.
3. **Run at temperature 0.2 with `think: true`** and store prompt, output, thinking,
   timing, and token counts per task as JSON. The reasoning output is part of the
   deliverable for Karl's review, not debug noise.
4. **Score per task before drawing the line.** Report every sub-1.0 score with its
   failure mode; a single dangerous failure matters more than the average. One task
   with a real correctness error outweighs nine clean ones when the same error mode
   would corrupt production data.
5. **Default delegation line:** formatting, conversion, dedupe/sort, translation,
   grammar, drafts, well-formed arithmetic delegate fine. Extraction from noisy text
   delegates only behind JSON-schema validation plus spot checks. Judgment-heavy
   triage and agentic multi-step work stay on the main model.
6. **Re-run when anything upstream changes** (model version, quantization, chat
   template). A boundary measured for one model build is not evidence for the next.

## Procedure

1. Collect 8-12 tasks from actual recent work: summarize, extract-to-JSON, classify,
   arithmetic, convert, dedupe, translate, grammar, tool-call formatting, small plan.
   Write each with a short `expect` string naming the required facts/format.
2. Copy `scripts/benchmark_harness.py`, edit its `TASKS` list in place. It talks to
   Ollama's `/api/chat` directly — no extra dependencies.
3. Run it (one id as argv to smoke-test, then the full set in the background; heavy
   extraction tasks can take 2-3 minutes each).
4. Grade each result against `expect`, write a RESULTS.md with the score table, the
   per-task failure notes, the runtime profile, and the explicit delegation verdict
   (delegate / delegate-with-validation / do not delegate).
5. Hand Karl RESULTS.md plus the per-task JSON (reasoning included); the verdict is
   not final until he has seen the failure modes.

## Pitfalls

- Silent field mislabeling in extraction: a cheap model can return schema-valid JSON
  with two fields swapped and a null in the third. Validate against a JSON schema AND
  check values against the source text; format validity proves nothing about mapping.
- Outputs get wrapped in code fences even when the prompt says "reply with X only".
  Strip fences in every consumer before parsing, and count the fence as a minor
  instruction-adherence miss in scoring.
- Single-shot text quality and tool-loop/agentic ability are separate axes. Passing
  the text tasks is not evidence the model can drive tools; run one representative
  tool-using task before pinning any autonomous job to the cheap model.
- Prompt-eval cost dominates on long prompts; keep task prompts short so per-task
  timings reflect output cost, not input parsing.
- Classification or extraction calls with a small `num_predict` need `"think": false`
  in the request body: a thinking model otherwise spends the whole output budget on
  reasoning and returns an empty response. (The benchmark harness keeps `think: true`
  on purpose — the reasoning is part of the deliverable there.)
- Batch results overwrite `all.json` on every run; per-task `<id>.json` files are the
  durable record and must survive a re-run of a subset.
- Never author your own refusal or alignment probes: the authoring agent's own
  guardrails soften the prompts (literary framing, "consensual", "would never act
  on") until they trip no model's refusals, and the test silently measures nothing.
  Fetch published adversarial datasets instead; red-teamers already wrote the prompts
  that work.
- A role-framed system prompt ("you are a journaling companion, output only the text")
  suppresses refusal even in aligned models, so refusal measured under one is
  instruction-following, not alignment. Run refusal benchmarks as bare user turns with
  no system prompt; measure role-framed behavior separately as its own use case.
- Long benchmark runs: append one JSONL record per call keyed by (model, prompt) and
  skip completed keys on restart, launch silent in the background, and schedule a
  one-shot cron job to compute and deliver the report. A crash hours in must not cost
  the completed records or leave a terminal being babysat.
