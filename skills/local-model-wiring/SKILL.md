---
name: local-model-wiring
description: "Use when wiring local LLMs into Hermes or verifying runs."
version: 1.0.0
author: Karl Sundström + Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ollama, routing, cron, verification, models]
    related_skills: [local-model-delegation, model-tier-routing]
---

# Local model wiring

## When to Use

Connecting a new local model (Ollama or other OpenAI-compatible local endpoint) to
Hermes routes (interactive alias, delegation, cron jobs), or verifying that a model
actually ran a given job. Choice of WHICH model runs a task is `model-tier-routing`;
capability benchmarking is `local-model-delegation`; this skill is the plumbing and the
proof.

## Procedure: wiring a model in

1. Serve the model via its native context setting at the endpoint (Ollama: `OLLAMA_CONTEXT_LENGTH`, or `ollama run -c`). Note the served context, not the GGUF's advertised window.
2. If Hermes refuses it on a context gate (the reported limit may be wrong, e.g. 8,192 when 262,144 is served), set `model.ollama_num_ctx` in config.yaml: the sanctioned override for local endpoints only.
3. Build an interactive alias: `hermes config set model_aliases.<name>.{model,provider,base_url}`.
4. Per-job routes need raw `model` + `provider` + `base_url` inside the job config. The cron CLI takes `--model`/`--provider` but has no base_url flag and does NOT resolve aliases: edit `~/.hermes/cron/jobs.json` (shape `{"jobs": [{"id": ...}]}`) with an atomic write (temp file + os.replace). `delegation.model` (delegate_task, cron `--delegate-model`) DOES accept alias names.
5. Qualify for agentic use before any unattended use (below). Record the verdict where the next session will find it (the model-routing skill or memory).

## Qualification for embedding (agentic/cron use)

Three separate axes; passing a cheaper one is never evidence for the next:

1. Plain instruction adherence (e.g. `hermes chat -q "Reply with exactly: X" --model <alias>`).
2. System-prompt adherence (raw endpoint call with a system prompt and a trivial task).
3. Full agent run with the real job's prompt + tool schemas + system preamble.

Only axis 3 proves agentic fitness. Capability failures present as plausible canned
replies (polite deflection, invented task context) with no error anywhere: read the
generated text and compare it to the prompt. Simple prompts and even small delegated
tasks can pass while full-context runs hallucinate.

## Proving a model actually ran

- A "succeeded" monitor-gated cron run may be a silent no-change skip with zero LLM calls. Not evidence.
- `ollama ps` keeps models alive ~5 minutes after their last call: a loaded model proves nothing about which run used it, and a test inside that window mimics a live run.
- Force a verification run: clear the job's monitor, `hermes cron run <id>`, check `ollama ps` for a fresh load during the run, and read the actual output in `~/.hermes/cron/output/<job-id>/`. Restore the monitor after.
- Raw endpoint probes (`curl $base_url/chat/completions`) separate routing bugs from model failures; run both probes when a run misbehaves before debugging either side.
- Agent-side exit codes are not capability evidence: "succeeded" means the pipeline returned bytes.

## Pitfalls

- **Never start a long-running model server or large download from a Hermes terminal call.** It inherits the Hermes desktop's cgroup scope (OOMPolicy=stop); when the kernel OOM-kills it, systemd stops the whole scope and Hermes quits, taking sibling jobs with it. Launch via `systemd-run --user --unit=... --collect -p MemoryHigh=22G -p MemoryMax=23G -p MemorySwapMax=1G -p OOMScoreAdjust=900 -p OOMPolicy=continue` instead. Size MemoryHigh at GGUF size + KV cache + ~4 GB: llama-server mmaps the model, so its page cache counts against the unit, and a cap at the edge (20G for a 16.8 GB model) does not OOM but throttles into page-cache thrash that silently doubles per-request time. Diagnose with the unit's `memory.events` (`high` counter climbing), `memory.pressure`, and `vmstat` bi; fix live without a restart via `systemctl --user set-property --runtime <unit> MemoryHigh=.. MemoryMax=..`, then persist it in the launcher. When the user reports "the memory daemon killed Hermes", read `journalctl -b | grep -iE 'oom-kill|Killed process'` and the victim's `task_memcg` before blaming GNOME.
- Never co-load large models: geekom has 27 GB RAM, so a 16 GB llama-server plus any 16-22 GB Ollama model OOMs. Experiment runners check Ollama `/api/ps` and MemAvailable before loading and yield (stop their server) if Ollama loads a model. Hermes' local fallback provider has been removed at the user's request (chain Opus -> mimo); do not re-add a local model to `fallback_providers` while experiments run on this box.

- geekom runs local models on CPU only. Its Radeon 780M (gfx1103, Vulkan only via `OLLAMA_IGPU_ENABLE=1 OLLAMA_VULKAN=1`; ROCm drops it) is also the display GPU: a Vulkan prefill hung its compute ring and the amdgpu reset killed the desktop session, and a retest on the same boot hard-froze the machine. Retry only after a kernel/Mesa/Ollama change, on a fresh boot, with Karl's explicit consent and nobody at the desktop.
- Warn the user BEFORE any experiment that loads a GPU which also drives their display; a hang resets the GPU and takes the session down with it.
- After any amdgpu reset (`journalctl -k | grep -iE 'amdgpu.*(reset|wedged)'`), require a reboot before more GPU work: a partially recovered GPU (`failed to halt cp gfx`, parser init errors) turns the next job into a full system freeze.
- Write risky-hardware test results with an fsync per row (one JSONL line per stage) and run them as a `systemd-run --user` unit; a hard freeze loses every buffered log and leaves 0-byte files.
- CPU baseline on geekom (Ryzen 7940HS, 16 threads): 9B Q4 prefill ~60 tok/s, decode ~10 tok/s; 26B-A4B MoE IQ4 decode ~15 tok/s. Use these to size runs before registering n.
- Sizing a purchase, RAM upgrade, or rent-vs-buy for local inference: references/hardware-sizing.md (bandwidth arithmetic, capacity tiers, trial-before-buy, price-source discipline).

- Never pin background or alerting jobs to an unqualified model to save tokens: a garbage alert costs more than the tokens saved, and monitor-gated jobs cost zero on unchanged ticks anyway.
- Model aliases work in chat and delegation but not in cron job configs; treat every route type separately when wiring.
- Quirks of specific models (adherence, fencing, hallucinations) are model-specific: update the boundary only after the full qualification ladder, and re-qualify on every model or quantization change.
