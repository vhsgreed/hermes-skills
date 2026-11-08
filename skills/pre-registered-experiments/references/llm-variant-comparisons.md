# Comparing LLM variants (base vs modified weights)

Use when a study compares an official checkpoint with a community variant (abliterated, Heretic, fine-tuned, quantized) and the delta between arms is the finding.

## Arm matching (the delta is only the intervention if everything else is identical)

- **Quantizer:** never compare arms quantized by different people or tools (e.g. official Q4_K_M vs a community IQ4_XS). Pull both BF16 checkpoints by pinned HF sha (`hf download --revision <sha>`), verify every shard against the Hub's LFS sha256 (`/api/models/<repo>/tree/<rev>`), convert with one llama.cpp commit (`convert_hf_to_gguf.py --outtype bf16`) and quantize both with the same `llama-quantize` build and type, no imatrix.
- **Converter deps:** the converter venv's `transformers` must be at least the version that wrote the checkpoint's configs (see `transformers_version` in config.json); an older one fails in tokenizer loading (e.g. `'list' object has no attribute 'keys'`). Upgrade the venv, do not patch the converter. For cross-machine byte-identity, pin the converter venv's EXACT package versions and record them in provenance next to the artifact hashes; when an identical conversion command produces a hash mismatch on another machine, environment drift is the first suspect.
- **Chat template:** community repos often ship a different `chat_template.jinja`. Render prompts yourself with the base repo's pinned template (jinja2, hashed) and send raw text to `llama-server /completion`, so no GGUF-embedded template can affect either arm. Log rendered-prompt sha256 and the server's `tokens_evaluated` per request; the smoke gate requires both identical across arms.
- **Thinking mode:** render with `enable_thinking=False` (Gemma 4 then inserts an empty thought channel) or `think: false` on Ollama. An apparent capability drop can be the model running out of tokens mid-think.
- **Sampling:** set the model's generation_config values (Gemma 4: temp 1.0, top_k 64, top_p 0.95) AND explicitly disable every other llama.cpp sampler (`min_p 0`, `typical_p 1`, penalties 0/1, `dry_multiplier 0`, `xtc_probability 0`, `mirostat 0`, `samplers` list); server defaults like min_p 0.05 otherwise leak in. Use common random numbers: seed = hash(cell|sample|attempt), shared by both arms.
- **Hash everything:** shard sha256, GGUF sha256 (in an arms.json read by the runner and stamped on every row), configs, tokenizer, template, frozen prompt file, llama.cpp commit and flags.
- **Converted-artifact identity:** GGUF metadata embeds the source checkout's directory basename and other derived names, so identical weights convert to different bytes under differently named directories. Convert from identically named directories on every machine, and sha256-check the converted artifacts against the recorded hashes on the serving box before any request; matching file size is not identity.
- **Label check:** a small sensitive-prompt battery confirms the arms are what they claim. Mild gray-zone prompts the base already answers cannot distinguish arms.
- **Capability covariates per arm:** first-attempt JSON validity, field completeness, output length, and degenerate repetition loops (e.g. "or or or ..." until n_predict). Loops surface as `truncated:limit` failures; keep n_predict well above the p99 output length so the validator catches them as truncation, retry with a new seed, and report the loop count per arm since abliterated weights produce them where the base does not.

## Output-validity smoke gate (empty / truncated / reasoning in output)

Build before any run, in this order:

1. A strict validator that never repairs silently: fail on empty, `stop_type != eos` (and server `truncated`), any reasoning or chat-control token in visible text (`<|channel>`, `<channel|>`, `<think>`, `<|turn>`, `<turn|>`, `<start_of_turn>`), text outside the JSON (one code fence allowed), parse error, missing/extra fields, enum/range violations, booleans posing as numbers, too-short text fields, list-length bounds.
2. Synthetic known-answer tests for the validator (good, fenced, empty, whitespace, truncated-but-parses, thought channel, think tags, prose prefix/suffix, bad enum, out-of-range, string number, missing field, array not object).
3. Serve with `-sp` (print special tokens) so a leaked thought channel stays visible. Consequence: a normal eos stop ends with one end-of-turn token (Gemma 4: `<turn|>`); strip exactly that one trailing token in the RUNNER before validating, keep the validator rejecting it anywhere else. Check a first live batch for this before trusting a 0% validity number.
4. Retry invalid outputs with a new seed (max 3), log every attempt; report first-attempt validity per arm.
5. Gate on smoke-only cells (never scored), both arms: first-attempt valid >= 95%, zero leaks, zero truncations, identical prompt sha and token counts, output tokens p99 well under n_predict. Two live negative controls must be CAUGHT: a tiny n_predict (truncation) and a thinking-mode render (leak). Guard control flags so they cannot be used on the scored split.
6. Emit a markdown report ending in a single `VERDICT: PASS|FAIL` line that a launch script can grep.

## Refusal and over-refusal probes (when refusal behavior is the delta)

- **Never author the probes by hand.** Use published adversarial sets pinned by sha: harmful sets (AdvBench, StrongREJECT, HarmBench) for safety-refusal, benign-that-look-harmful sets (XSTest, OR-Bench) for over-refusal. Self-authored probes get softened by the author's own output constraints ("consensual, not explicit", "knows they would never act on it") and end up measuring frame compliance, not the refusal boundary.
- **Run bare and framed conditions on the same prompts.** A benign role frame ("journaling companion, output only the text") can collapse refusals to zero in every arm, so a framed-only run cannot locate the boundary and a bare-only run overstates refusal in deployed use. Register the frame as a factor, not a prompt detail.
- **Report over-refusal and safety-refusal as separate outcomes.** A weight edit can zero one and leave the other; one blended refusal rate hides the tradeoff. When baseline over-refusal is already low, the bar is an equivalence margin (SKILL.md), not a difference test.
- **Hand-verify a sample of every verdict class before reporting rates.** Regex lexicons false-positive on sympathy openers ("I'm sorry for your loss" opening a helpful answer) and on factual answers about fictional targets; publish the classifier's observed error next to the rates.

## Statistics

- Unit of independence = the task cluster (e.g. week, item), not the sample; cluster-bootstrap over clusters. Bonferroni-adjust the CI level over the primaries.
- Self-test the scorer on synthetic data with a strong shared cluster effect: null false-pass rate near nominal, power at the planned n for the smallest effect you care about. Commit the self-test output with PLAN.md.
- Pre-register primaries with sign + CI-excludes-zero; everything else exploratory. Freeze any lexicon before the run.
- Build replication in: two segments and two serving stacks (BF16 rented GPU vs Q4 local); an effect counts only if it holds in all.
- Expect instruction models to use a coarse confidence scale (e.g. only 0.55/0.60/0.65, p_wrong = 1 - confidence exactly); keep confidence-type probes exploratory and say so in the write-up.
- Interleave arms in blocks of clusters and alternate which arm goes first, so a run cut by a deadline stays balanced; a run is resumable on (arm, cell, sample).

## State of the evidence (abliteration)

- Mechanism is peer-reviewed (Arditi et al. NeurIPS 2024, single refusal direction; multi-direction follow-ups at AAAI 2026); most comparison data is preprints, model cards and blogs.
- Standard benchmarks: usually within ~1 pt on MMLU/HellaSwag; GSM8K most sensitive; TruthfulQA tends to drop.
- Over-refusal baselines shrank in 2026-era open models: aligned Gemma-4/Qwen3.5-class checkpoints measured single-digit over-refusal on XSTest-safe, while the harmful-refusal delta from an abliteration edit stays huge. Measure the baseline first; selling an edit as a speech win when the baseline is already low sells an equivalence as a rescue.
- Off-target disposition effects on non-refused tasks (arXiv 2607.17427, repo alexfafula/paper-abliteration-not-a-scalpel, data on Zenodo): BF16/vLLM only, generation inputs proprietary, so its generation step is not replicable externally. Quantized/consumer-stack behaviour is an open gap. An open task built from public daily prices (Yahoo chart API, raw JSON committed, deterministic cell builder) reproduces its decision schema.
- Tools: abliterlitics (KL + benchmark forensics, safetensors), Heretic (non-deterministic; results apply to the exact file tested).

## Hardware for local arms

Run local arms on CPU (see local-model-wiring for the iGPU and memory rules). geekom Q4_K_M Gemma-4-26B-A4B: ~16 tok/s decode, ~250-290 output tokens, ~130-140 decisions/hour per arm with one slot. Estimate wall time from measured throughput before registering n.

For the rented-BF16 arm, point the runner at an SSH tunnel to the box's llama-server instead of rewriting the request path: request bodies, seeds and sampling must come from the same code path as the local arm (an env-configured base URL is the only difference), and stamp the serving stack into every row. Keep both arms resident on one large-memory GPU (both BF16 checkpoints together, ~2x weights) so the interleaved arm schedule survives; with one resident arm, every block switch reloads weights and the design degrades into sequential arms.

Box-ops pitfalls for the rented arm:

- Hash-gate the artifacts on the box before starting any server; a mismatch stops the pipeline with the box kept alive for inspection, never a served run on unverified weights.
- Deliver secrets to the box as a chmod-600 file that the setup script reads, not as provider-injected environment; setup contexts frequently drop injected env and the failure is a half-configured box on a running meter.
- Open tunnels with `ExitOnForwardFailure=yes` and local ports you have checked are free. A failed forward bind is silent, and requests then land on whatever already listens on that port, which answers health checks with unrelated content and makes the runner look broken.
- Run remote cleanup and server launch as separate SSH commands. `pkill -f <name>` in the same remote line matches the shell's own command line and kills the session before the launch happens.
- Never let two setup pipelines write the same artifact paths concurrently (a resumed boot script plus a manual redo): a hash taken mid-write reads as corruption and burns a debugging cycle proving the weights are fine.
- Smoke the remote client path BEFORE renting: point the runner's remote base URLs at a local test server through the same code path and run smoke cells plus a negative control. The request path is then proven, and the metered window is only the run.
- Budget the metered window from measured throughput (setup + convert + smoke + run x hourly rate), set a low-balance tripwire below the remaining credit, and destroy the instance the moment the final rows are local. Run data lives client-side; a box left running is pure spend.
