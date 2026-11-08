# External replication on public datasets

Use when a result has been confirmed on one dataset and the next question is whether it holds elsewhere, or when reproducing someone else's paper from their released data.

## 0. Reproducing a published paper (their data, your code)

Reproduction = same data, independent code; replication = new data. A study can do both (Part A reproduction, Part B new question).

1. Pin the paper version (arXiv vN) and the data revision sha. Extract the full HTML (`arxiv.org/html/<id>vN`, large char limit, save to scratch) and quote each claim verbatim with its section. Read the BODY, not just the abstract: abstracts overstate ("does not translate into higher accuracy" vs the body's "rises modestly, then saturates"); register the body's wording.
2. Pin the unit of every statistic before registering. Papers often omit it (one value per task averaged over models? per model x task? per run?). Read the authors' plotting/analysis scripts for definitions only (never reuse their code); if still ambiguous, register EACH plausible unit as a pre-declared variant and score the claim on the unit the scripts imply. Guessing one unit turns a matching result into a false NOT REPRODUCED.
3. Tolerances: papers give no CIs, so set a band per claim up front and say why. For "up to Nx" maxima, register the run filter too (e.g. drop runs that ended after <= K calls): crashed 1-call runs dominate any max/min ratio.
4. Overall rule (e.g. >= 5 of 6 claims), NOT EVALUABLE distinct from fail. Report the registered score as is; add an exploratory section (labelled post-hoc) explaining each miss, separating "our rule was wrong" from "their number does not come out of their data".
5. Release quirks: count archives vs models in the paper; check completeness per archive by counts only (tasks with all k runs) under a registered completeness rule; a release may mix layouts (e.g. OpenHands legacy `llm_completions/*.json` vs SDK `base_state.json` with `stats.usage_to_metrics.default.token_usages[]`/`costs[]`), so inspect one instance's schema per archive before extracting.
6. Before publishing: push code + aggregate tables only (raw rows stay local, check the data license; scan `git log --all --name-only` for derived per-run files and strip them from history before the first public push), open an issue on the authors' repo with the claim table and the specific open question; Karl approves the issue text first. Issue body: data revision used, link to the registration, our numbers next to theirs for what matches, then numbered questions each with the exact computation and the extreme case (task id, tokens, call counts). Check the repo's other issues: unanswered ones predict silence, so give a fixed reply window (about a week) and write the article either way with a placeholder for their answer.
7. Article order for a reproduction: registered score first, stated as is ("2 of 6, not reproduced"), then one bullet per miss classed as *our rule* (unit guess, abstract wording) or *their number* (does not come out of the data). Lead the takeaway with which findings that matter for the reader's question reproduce cleanly. Venues: own Journal; ReScience C (peer-reviewed reproductions, open GitHub review, no affiliation needed); Zenodo DOI for code; arXiv needs an endorsement for first-time independent posters.

## 1. Survey (minutes, no downloads)

- Search the HF hub API: `https://huggingface.co/api/datasets?search=<terms>&sort=downloads&limit=12`. Run many search terms (agent trajectories, traces, claude code, openhands, swe-agent, terminal-bench, token usage, llm cost) and dedupe by id.
- Probe each candidate through datasets-server without downloading:
  - `/size?dataset=X` gives rows and bytes
  - `/splits?dataset=X`, then `/first-rows?dataset=X&config=..&split=..` gives column names and a sample
  - `/rows?...&offset=&length=100` pages through small sets
  - `https://huggingface.co/api/datasets/X?blobs=true` gives the revision sha, file count, total size and card license
- Grep the sample for usage/cost keys, then read the context around each match. Keyword hits are often code text inside trajectories (`max_cost=`, `_log_api_usage_once`), not billing fields.
- Sort candidates into three tiers. This tier decides what a dataset can test:
  1. real billed cost + outcome
  2. outcome only, where tokens can be estimated from text (label as an estimate everywhere, no cache pricing)
  3. single API calls, which are not runs
- Datasets that replicate identical runs (same task x model x harness repeated) give the irreducible noise floor: the max/min cost spread across replicates. Report it as exploratory if you computed it during the survey.
- Note the license per dataset. Analysis is fine either way; check the terms before publishing tables built on 'other' or unlicensed sets.
- Download with `huggingface_hub.snapshot_download(repo, repo_type='dataset', revision=SHA, local_dir=..., max_workers=16-32)` into a gitignored `external/` dir. Datasets of thousands of tiny files download slowly and hit rate limits; fetch them last, or skip them once they are no longer needed.

## 2. Pre-register before any cost is computed

In PLAN.md, record:
- pinned revision shas
- any prior contact with outcome values (e.g. one sample row seen during the survey)
- the group definition that stands in for the original groups (e.g. model x benchmark x harness in place of model x trigger)
- the split unit and seed
- the bars, copied unchanged from the originals
- the replication rule: passes in every evaluable dataset AND at least 2 evaluable; a dataset with fewer than 3 eligible groups is 'not evaluable'

## 3. Schema-only inspection, then freeze

Read only column names, types, category counts and group sizes. Never read cost sums or distributions at this stage. Walk nested JSON for key paths and value TYPES only.

- **Independence:** before counting two datasets as independent, intersect their session/run ids. Datasets republished from the same runs (e.g. a leaderboard dump of another lab's traces) double-count; drop the overlapping one and log it.
- **Task unit:** when no task id exists, hash the first user text message of the run. Shared system/policy text is identical across tasks, so hash the user turn, not the whole input. Check how many configs land on each hash; that confirms it really is a task id.
- **Split design error:** if the split unit is also part of the group key (e.g. split by project, group includes project), held-out groups can never be fit. Use a chronological split within each unit instead (first 70% by timestamp = fit). That is also the realistic product case.
- **Eligibility:** count group sizes against the registered minimums before computing anything. If almost nothing is eligible, add a SECONDARY analysis with lower minimums. Keep the primary verdict as registered, label the secondary everywhere, and record that the amendment came from sizes only.
- Commit the amendments, then commit the scoring script itself, before its single run.

## 4. Run once, interpret against the baseline

- If the run computes all results and then crashes in reporting code, fix only the reporting code and re-run with the same seeds. Disclose this in PLAN.md and state that the numbers are identical.
- A run may be killed to make it faster only BEFORE any result has printed; log the kill and that no output was seen. If the fix touches scoring code (not just reporting), apply it uniformly to ALL datasets and rerun everything, not just the unfinished ones: partial results already printed are disclosed as seen, and fixed seeds make the rerun identical.
- When an evaluation skips runs it cannot score (e.g. a group with no fit history), that skip rule must come from the method's own support rule (the fallback chain's minimum), apply to every dataset alike, and be reported as a share of the test set.
- **Baseline mixing:** a model-only baseline that pools several task sources is very wide (100x+), so almost any task-specific group 'beats' it. Check pass rates separately for models whose baseline is already narrow. If passes vanish there, the finding is 'task source matters', not support for the general range claim.
- When replication ends up not evaluable for lack of data, report it as not evaluable. Then state the scarcity of public billed-cost data as a finding in its own right.

## 5. Outcome-tier rounds (no billed cost)

Use tier-2 datasets (trajectories with resolved/pass labels) to test whether cost tails fail more often. This is the gate before any tail alarm or stopping policy.

- **Fix the cost proxy in the pre-registration**, e.g. sum over assistant turns of the conversation length so far in characters / 4. Call it 'estimated tokens' everywhere and never convert it to dollars. Add a turn-count proxy as a secondary measure.
- **Compare within comparable groups:** dataset x model (x repo). Tail = above the group p90, body = at or below the group p50. Primary statistic = risk ratio of resolve rates, with a bootstrap CI over task instances.
- **State the confound in advance:** task difficulty drives both cost and failure, so the ratio can't show that stopping is free. Add a stopping backtest as an exploratory measure: stop at the group p90/p95/p99 and report estimated tokens saved against resolved runs lost.
- Use only datasets that have an outcome label. Download them with `allow_patterns=['*.parquet','README.md']` so you skip the bulk of per-instance artifacts.
- **Count rows vs distinct run ids per file set before freezing.** Multi-format releases ship the same runs under several file prefixes (`train`/`xml`/`tool`), and a single prefix can still contain duplicate rows. Freeze one prefix and dedupe by run id in the scorer; duplicates silently reweight the tail. If found after the run, re-run deduplicated and report both numbers.
- Report the decile curve (resolve rate cheapest to most expensive tenth) next to the risk ratio; a monotone fall is easier to read than a single ratio.
- **Runtime alarm test (turns an association into a deployable claim):** set thresholds on 70% of task instances (group p90 of FINAL size), then walk the held-out 30% turn by turn and fire at the first turn whose cumulative size crosses. Report per dataset: fire rate; fire rate among resolved runs (false alarms if auto-stopping); resolve rate fired vs not; median share of turns and tokens still ahead at firing (lead time); estimated tokens per resolved run with vs without stopping. The sign of the last number varies by setup, so present a warning (human decides) separately from auto-stop.
- The chars/4 divisor needs no sensitivity analysis when every threshold is a within-group percentile: a constant divisor leaves all ranks unchanged. Say so in one sentence.

## 6. Backtesting the tail alarm on the user's own logs

After an outcome round passes, test the alarm on the user's own numbers-only call logs before proposing it as a live feature.

- **Run = one user turn:** consecutive calls in a session until the call counter resets.
- **Threshold from the past only:** each run's line = p90 of EARLIER runs of the same model, with at least 20 prior runs; the alarm fires at the first call whose running total crosses it. Report fire rate, the call where it fired out of the total, and the share of tokens past the line (the upper bound on savings).
- **Pitfall: summing input tokens per call measures context length, not work.** Long conversations re-read 100k+ tokens of history on every call, so they cross the line while working normally. Split every call into **work** = output + (input - cache_read - cache_write) and **carry** = cache_read + cache_write, and size runs by work. Cache writes are carry too: a cache miss rewrites the whole context as one huge "new input" call and fires the alarm at call 1.
- Treat work and carry as separate research quantities. The user values work tokens as a metric independent of success, and conversation-style sessions (one long session kept for memory) are a usage population that public task-run datasets do not cover.
- **Conversation tax (descriptive):** per run, counterfactual fresh-session input = session's first-call input + (call input - run's first-call input), capped at actual. Report actual vs fresh totals, the multiplier per long session, and by turn position. State that some carry buys real memory, so this is an upper bound on waste.

## 7. During-run remaining-cost forecast

When the question is what a run will cost from here (not the total), test a cheap remaining-cost forecast before building anything learned.

- Table forecast: cell = (turns-elapsed bucket, cumulative size / fit-group median final bucket); point forecast = cell median final size, interval = cell p10-p90; fallback chain cell -> turns-only cell -> group table.
- Baselines: unconditional group median final and the turns-only table. Pick the reference from the pooled point estimates and keep that same reference in every bootstrap resample.
- Evidence-based expectation: cheap tables fail a 0.8 MAE bar against a turns-only baseline (cumulative size adds about 10% at best), while the 80% intervals do calibrate. The honest deliverable of the cheap version is bounds, not a point; learned compositional models (segment decomposition, e.g. TokenCast) are the citation for the learned ceiling, not something to reimplement.
- Cold start: runs in groups with no fit history cannot be forecast at all; count the skipped share of the test set (repo-grouped data can lose half). Runs with step caps make turns-only baselines strong near the cap.
- Evidence helps only late: report the MAE ratio by turn bucket; early turns are where every forecast is worst.

## 8. Validating the price model against billing

When dollars come from a price table, validate the pricing MODEL against real billing where a billed account exists (this validates tokens x price with the cache split; it does not validate price entries for models with no billing records).

- OpenRouter management key: `/api/v1/generation?id=<gen-id>` returns billed `usage` and `native_tokens_*`; there is NO listing endpoint — join by generation ids harvested from local call logs (`id=gen-...` fields) or response bodies. `/api/v1/credits` and `/api/v1/keys` work for account checks.
- Estimate per call: uncached input x prompt price + cached input x cache-read price + output x completion price, from `/api/v1/models` pricing fields; note the fetch date (price drift is the main deviation source).
- Join integrity first: logged native tokens must equal the billing record exactly; report the mismatch count and drop mismatches.
- Report: median ratio billed/estimated, p10-p90, share within +/-5% and +/-10%, split by high vs low cache share (this is what validates the cache split). Bar: median in [0.95, 1.05] and >= 90% within +/-10%.
- Per-call rows stay local; only aggregates go into PLAN.md and any article.

## 9. Success labels for the user's own runs

Own logs carry no outcome, so derive one without storing message text:

1. Read the FIRST user message after the run's last call from `~/.hermes/state.db` (`messages` table, read-only `file:...?mode=ro` URI), classify it, store only the label in a gitignored-free numbers file (`data/run_labels.jsonl`).
2. Labels: `corrected` (wrong, re-ask, pushback), `accepted` (continue, thanks, go-ahead, new topic). System-injected text (background-process notices, cron output, out-of-band or compaction markers) -> `no_human_reply`. No reply yet -> skip and retry later; still none after ~6 h -> `unknown`. Cron/oneshot/subagent sessions are almost all `unknown`; report labels by session source.
3. Classifier = local Ollama model, temperature 0, `format: json`, **`"think": false`** — thinking models otherwise spend the whole `num_predict` budget on reasoning and return an empty response. Sanity-check on ~7 hand-written replies first.
4. Validate before trusting: build a blind sheet of all `corrected` plus random `accepted` up to 30, shuffled, labels in a separate key file; sheet shows the end of the agent's answer and the user's next message. Give it radio buttons (accepted/corrected/unsure), localStorage autosave, an answered counter, and Download / Copy JSON / Send-to-Hermes (`window.hermes.send`, shown only when present) export so the user can rate inside the chat via `::preview`. Keep the sheet gitignored (it holds text) and delete it after scoring.
5. Only wire the labeler into the hourly logger cron after the hand-check shows the error rate; then try a smaller local model on the same sheet before choosing the cron model.
6. Score as a 2x2 (labeler vs rater): agreement, recall and precision on `corrected`, and the correction rate among labeler-`accepted` runs (the real base rate is usually higher than the labeler reports, since quiet pushback is missed). If recall is poor AND the rater calls the cases hard, drop the line rather than tune the labeler: one rater on ambiguous cases is a weak reference, and benchmark datasets with test-verified outcomes already answer the outcome question better than guessed labels on n=1.
