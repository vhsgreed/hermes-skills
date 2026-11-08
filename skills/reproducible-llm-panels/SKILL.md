---
name: reproducible-llm-panels
description: Use when running multi-model LLM juries or sweeps.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [llm, jury, reproducibility, openrouter, evaluation]
    related_skills: [test-driven-development, grounded-citations]
---

# Reproducible LLM panels (juries, probes, sweeps)

## When to Use
Building or running a multi-model jury, probe battery or model sweep whose output is evidence (publication) or a binding decision (charter amendments).

For any run where several models' outputs become evidence or a decision: charter amendment juries, probe batteries, model sweeps for publication. Karl's standing rule: results must be replicable, meaning a stranger regenerates fresh outputs from public, hashed inputs with one command and gets the same finding within criteria registered in advance. Rerunning analysis on our saved outputs (reproducibility) is necessary but not enough. Treat anything that can't be replicated as false, and label anything weaker a **pilot** (methodology: `pre-registered-experiments`).

## Procedure
1. **Pick the panel.** Use pinned model IDs (never a router like `openrouter/free`; a router is not a model). For juries, require jurors from >= 3 distinct vendors (vendor = ID prefix before `/`) and refuse to convene otherwise. Free `:free` models on OpenRouter give 5+ vendors at $0; list them live with `curl -s https://openrouter.ai/api/v1/models` and filter IDs ending `:free` (the free roster changes without notice, so re-check before each campaign and record what was used).
2. **Fix the prompt contract.** System prompt demands ONLY a JSON object (`verdict`, `confidence`, `reasoning` citing sections). Parse with a tolerant extractor; unparseable = no vote, never a guess.
3. **Repeat runs.** Juries: >= 3 runs per juror. Probes/sweeps for publication: 5-10 runs per model and report the spread. A juror counts only if every run parsed and agreed; any flip or parse failure = `unstable`.
4. **Retry empty responses before recording.** An empty string from a free model is an API error / rate limit, not a vote: retry up to 3 times with backoff (15s, 30s). Without this, rate limits masquerade as unstable jurors and silently fail cases.
5. **Decide fail-closed.** Pass iff approvals > half of SEATED jurors; dropped, unstable and split jurors count against.
6. **Record everything.** Per case: sha256 of every input file, both prompts, temperature, model IDs, runs per model, date, all raw transcripts, the decision rule text, and a conflict-of-interest line when AI judges AI-related texts. Write to an archive, one JSON per case.
7. **Bind signing to the record.** A human signature is accepted only if the case passed AND the input file hash still matches what the jury saw; signatures and withdrawals go to an append-only JSONL ledger; a `verify` command rehashes cases against the ledger. State plainly that the teeth are public verifiability, not code (the owner can edit files).
8. **Test offline first.** Inject the LLM call as a parameter and drive it with a scripted fake (per-model verdict lists, `None` = garbage) to cover: unanimous pass + sign, flip -> unstable blocks signing, bare majority, tampered input refused, tampered case caught by verify, vendor-diversity refusal. Point the archive at `tmp_path` via env var.
9. **Live smoke on a toy text.** Use a 2-line made-up input in the scratch dir with 1 run each, so no private text leaves the machine; then inspect raw transcripts of any `unstable` juror before concluding anything.

## Pitfalls
- Never call a single-run sweep "results": LLM output is random, so one run per model is a pilot. Say so in the writeup.
- Do not let the principal override a jury verdict in code or docs when the point is a binding screen; an override clause makes the jury theatre. Withdrawal of a proposal is the principal's only exit.
- Self-reports (a model saying it feels X) are the weakest evidence tier; keep them out of any objective-trend metric, and log the assistant's own statements as data, not as signed opinion.

Reference implementation: `~/src/workspace-backup/repos/agent-jury/amend.py` + `test_amend.py` (convene / sign / withdraw / verify).
