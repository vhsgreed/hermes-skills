---
name: pre-registered-experiments
description: Use when running pre-registered dataset experiments.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, methodology, datasets, statistics, pipelines]
    related_skills: [spike, test-driven-development, reproducible-llm-panels, arxiv]
---

# Pre-registered experiments

Bars committed before data, canary-then-full-run, one-look locked tests, honest full-bar scoring, resumable multi-hour dataset pipelines.

Standard for every experiment (user's standing rule): results must be REPLICABLE, not just reproducible. Reproducible = a stranger reruns our code on our data and gets our numbers. Replicable = a stranger regenerates fresh data from public inputs (new samples, other hardware) and gets the same finding within registered criteria. Design for replication: every input public and hashed, one command to regenerate, replication criteria (sign, CI excludes zero, effect-size band) written into PLAN.md before data. A result that cannot be replicated is treated as false; label anything weaker a pilot. Every claim carries numbers (counts, dollar figures, ratios), never moods. Failures and self-corrections get reported alongside passes.

- Pitfall: when the user says reproducible/replicable/solid results, use their word exactly and confirm which one they mean before designing. The two lead to different studies (released-data reanalysis vs fresh generation).

## When to Use

Hypothesis testing against data where results must hold up: any experiment with a registered pass/fail bar, held-out evaluation, bootstrap CIs, or a multi-hour dataset run feeding a verdict. Covers cost/behavior predictors, dataset sweeps, and anything whose outcome becomes a published claim or a product decision. Skip for throwaway prototypes (see `spike`) and for pure engineering tests (see `test-driven-development`).

## Procedure

### 0. Novelty gate (Journal studies)

When the user wants impact on a research discourse, find the specific gap first: read the strongest recent paper's full method, clone its repo, and check whether its GENERATION step can be rerun from public inputs (data licences often say outputs are released but inputs are proprietary). A finding that nobody outside the authors can regenerate is the opening: an independent replication on an open task is the contribution. Ask the user for a measurable impact metric (citations, author reply, engagement count) before committing hours. When he turns the question back, propose ONE primary metric as named routes with a deadline (for a replication the author reply is the target: its feedback loop is months shorter than citations), and register the accepted metric in the plan's change log as a dated post-freeze addition that touches no bar.

Lane definitions (user's): the Journal is for closing information gaps with meaningful data, honest replication, and pushing a frontier; factual pieces (including "an agent audited X" framings) belong there or nowhere. Opinion is the user's light-hearted, human-centric personal journal. A review/report alone is related work, not a Journal article.

When the user asks whether to "pursue" a big open question (often one the agent itself called neglected in an earlier chat), run the incumbent search before answering, and retract the earlier "nobody is working on this" in one line if the search finds funded groups. Then test pre-registrability: no validated instrument or detector means no number to register, so it is not a Journal study; route it to an opinion piece (see `opinion-essays`) sized as a bet with stake cap, deadline and kill condition.

Before registering a study meant for the agentrecourse Journal, ask: would standard theory predict the answer's shape without the data? If yes (e.g. a risk premium falling with batch size is plain insurance pooling), it is a textbook exercise; the user does not want the Journal spent on those. Fold such results into an existing article as a short section and look for the open question instead: run a quick literature sweep (arXiv API by id for abstracts, a dozen web searches), state which direction the existing work covers, and register the gap or a reproduction of the main paper. Say plainly when an earlier framing of yours oversold a result.

### 1. Pre-register before touching results

Write hypothesis, bar, and method into the experiment repo's PLAN.md and commit BEFORE running scoring code on the data:

- dataset identity + revision (name, sha), and which units/splits are used for what
- split method + seed (e.g. shuffle unique repos with `random.Random(SEED)`, first 70% train)
- group definition exactly as the scorer will compute it
- every statistical clause: point-estimate threshold AND each CI requirement AND sample-size floor
- how many looks are permitted (usually: one)

Later changes go in as new dated entries marking the old bar superseded; never edit the old bar silently.

- Pitfall: before drafting a new registration, search the project ledger and existing experiment repos for a frozen plan on the same question. A pilot-to-confirmatory study may already exist mid-run; a second PLAN.md on one question creates competing bars and lets the bar move after data exists. Extend the existing plan's change log (new studies, metrics, packaging) instead of opening a rival registration.
- Pitfall: pilot runs feed the confirmatory DESIGN only (hypotheses, effect sizes, classifier failure modes, measured throughput), never its tests. Disclose every pilot in the change log and exclude it from scoring. When the pilot effect is near zero, register an equivalence margin instead of a difference test; "no difference" is only a finding with a margin committed before the data.

- Pitfall: push the freeze commit (tag `freeze-v1`) to a PUBLIC remote before the first scored-split datum is generated, and make any auto-launch script check that the tag exists on the remote. A local git timestamp is forgeable, so data generated before the public push can only be reported as a pilot or as a declared deviation; ask the user for the remote (default GitHub vhsgreed) while prep is still running, not after launch.

- Pitfall: implement EVERY clause of the bar in the scorer before the first scored run. A scorer that checks only the point estimate reports false passes that look like evidence — the registered CI clause is usually what decides. Fix the scorer and re-run before reporting anything; report the correction with the result.
- Pitfall: fit all transforms (cluster centroids, scalers, interval fits) on the train split only; assign held-out rows to train-fitted structures. Fitting on all rows leaks test data into the structure even without labels.
- Pitfall: bootstrap over the split unit (repos, users, projects), not over individual rows. Rows inside one unit are correlated; row-level resampling shrinks the CI and manufactures passes.
- Pitfall: register the cold-start rule (what happens to held-out rows whose group has no or too little fit history) before the run. Unit-held-out splits routinely produce test groups absent from fit; deciding the skip/fallback after a crash means results already printed are seen.
- Pitfall: with a fixed reference baseline in the bar, pick it once on the full fit/test and reuse that SAME baseline inside every bootstrap resample; taking `min(baseline_a, baseline_b)` per resample biases the ratio CI toward failure.
- Pitfall: the same applies to descriptive breakdowns (per turn, per bucket): accumulating `min(err_a, err_b)` per row is an oracle baseline that manufactures fake "baseline wins", and plausible-sounding mechanisms get invented to explain them. Fix the reference baseline in the pre-registration, never choose it on test data, and compute every descriptive table against that same fixed baseline.
- Pitfall: when a code review finds a bug in a published round, write the errata and the post-hoc re-tabulation spec into PLAN.md and commit BEFORE re-running; if the re-run overturns an explanation you gave (in PLAN.md, the article, or chat), retract it in place in each of those places rather than appending a softer one.
- Pitfall: smoke every new statistic and every hypothesis bar on SYNTHETIC data with a known answer (null case and strong-effect case) before the run. A bar that passes on pure noise is invalid by construction (e.g. a noisy buyer declines half the time with no private information, so "uptake < 50%" proves nothing); replace it in the change log before any real value is seen, and report results next to a permutation null. Ship it as `scorer --selftest` with one named check per hypothesis (`H1_null_not_pass`, `H1_strong_pass`, ...) and build the strong world from the claim's English sentence, not from the scorer code: sign and threshold-direction inversions (`rho <= -0.8` for a claim that gain grows with budget, `y_hat = gamma > th` for a claim that heavy tails win) only fail when the synthetic world is written independently of the code under test.
- Pitfall: raw LightGBM quantile regression (alpha .1/.9) under-covers on held-out units (R8: 62-76% for nominal 80%) even while its point error wins clearly. If the bar has a coverage clause, register a calibration step fit on out-of-fold fit data (e.g. split-conformal by group) up front; run a fit-internal smoke (fit units split 80/20, test never read) to catch this before the one look.
- Pitfall: when a richer forecaster is compared with a baseline, check that it keeps every conditioning variable the baseline has (e.g. the group); otherwise "adds X" is confounded with "drops Y".
- Pitfall: comparing outcomes across a policy's own choices (e.g. cheap-tier vs expensive-tier sessions under a router) is confounded, since the policy routes easy work to the cheap arm. For a causal answer, register a holdback: a deterministic hash of the decision key (`sha256(key) % 100 < PCT`) leaves PCT% of decisions unapplied, logs them with a holdback flag, and keeps the failure mode safe (holdback stays on the expensive/default arm). Make PCT an env setting defaulting to the registered value, and set it to 0 in the code's existing behavior tests so their contract still holds; give the holdback its own determinism and rate tests.
- Pitfall: when a scoring script is written ahead of a dated registered test, validate it first by running it on an already-published window and checking it reproduces the published numbers exactly; make a stale or partial export print NOT SCORABLE instead of scoring missing days as zero.

### 1b. Follow-up round on an already-used split

When a new round fixes a design flaw found by reading the previous round's output, reusing the same split is acceptable (paired comparison; every unit is already seen anyway) only if the registration says so explicitly: state that the design was motivated by the earlier test output, fix the reference baseline in advance, and write the expected verdict before running. Put the shared loader/split in one module (`traj_common.py` pattern) copied verbatim from the earlier script and assert the pooled numbers reproduce the earlier round exactly before trusting anything new.

- Pitfall: a clean FAIL is not a design flaw. Errata and re-runs are for broken implementation only (scorer bug, join bug, mis-parsed column). When the method ran as registered and the bar failed, a fix that would pass (calibration, extra features, a stronger model) is a NEW hypothesis for a future project, never the next round of the closed claim — re-registering it is moving the bar after seeing the result. Record the failure mode as a pitfall in this skill instead and let the decision rule stand.

- Pitfall: when a new study needs extra per-run fields from data an earlier round already cached, re-parse once and `assert` the new parse matches the old cache row for row on the shared fields before caching the extended rows. A silent parse drift would otherwise make "same split, same data" false. If the shared `split()` rebuilds tuples, rejoin extra fields by `id()` of an unchanged inner object (e.g. the per-run list), not by a value key that can collide.
- Pitfall: a bootstrapped ratio clause (A/B per resample) is undefined when any resample's denominator is <= 0. Register a NOT SCORABLE floor for the denominator and make the scorer return None for the CI and count the hypothesis as not passing, rather than crash or drop resamples silently.

### 2. Canary before any long run

Run the pipeline on a small slice of real data first. It validates parsing/joining/pricing plumbing AND gives the first read of the hypothesis. Decide explicitly:

- CI too wide to decide -> report point estimates with CIs, mark UNDERPOWERED, defer the verdict to the full run with the SAME bar.
- Effect cleanly absent -> close the hypothesis.
- Never weaken the bar to turn an underpowered canary into a pass.
- Metered rented compute (hourly GPU boxes): the full smoke gate, negative controls included, runs ON the metered hardware before the first scored request, and the reply states the projected total cost and the hard abort threshold before the launch command goes out. Every metered minute must buy scored data; an unvalidated pipeline on a running meter is where budgets die.

### 3. Locked test discipline

Freeze the test-unit list into a file committed before the run. Touch the locked test exactly once: no re-selection of units, no bar changes, no group cherry-picking after. Validation sets are for looking; the locked test is for the single registered verdict.

### 3b. New variables on already-scored data: explore/confirm split

When every unit's outcome has already been looked at, a NEW predictor can still be tested honestly: contamination is about the relationship tested, not the outcome column itself.

- Split units 50/50 with a fresh seed (EXPLORE / CONFIRM); inside CONFIRM split again fit/test by unit with another fresh seed. At large n the halves cost almost nothing in power.
- Explore freely (cutoffs, bucket counts, windows), pick by a selection rule written into the freeze commit, commit the frozen choices AND your predicted verdict before CONFIRM runs, then one look.
- Check joins to new metadata by match counts only, never by outcome, before pre-registering.
- Pitfall: per-user history features must use only rows strictly earlier in time than the predicted row; otherwise the feature sees the future and passes falsely. Held-out units plus time order are the non-negotiable parts; the explore/confirm split protects against analyst forking paths.
- Descriptive reference tables (n, p10/p50/p90, width per cell, small cells suppressed) need no hypothesis or split; publish the width alongside the typical value.
- Say plainly when you overstated a caveat (e.g. "no blind data left"); the user asks for the imperative behind methodology rules.

### 4. Smoke the chain, then run it long

Before launching a multi-hour job, run the whole chain end to end on 1–2 real units (download, parse, every downstream script). Give the runner an argv override to process named units only. Then run the full chain as one background command with `set -o pipefail`, each phase teed to its own output file.

- Unattended windows (user away or asleep): never leave the machine idle after a reply, since nothing wakes the agent between messages. Chain prep -> smoke gate -> run in one script launched as its own `systemd-run --user` unit with a hard deadline matching when the user wants the machine back; launch the main run automatically only on a PASS verdict line from the gate report, and log the launch decision to a file. On "I want to use the computer": stop the unit, verify every JSONL reads back, record the resume command in STATUS.md.
- On a status check mid-run: bucket per-request wall time by hour, not just the overall median. A slowdown hidden in the median (e.g. 25 s -> 60-80 s overnight) halves the night's output; find the cause (cgroup throttling, contention) and fix it live, then report decisions done vs total and the ETA from recent throughput.
- Health gate = plumbing only: row count, expected sub-units per unit, hashes present, no NaN/inf in registered fields, shapes and budgets within tolerance. Calibrate every tolerance to the method's OWN code before the first gate run (e.g. a rank rounded down to a multiple of 8 undershoots the bit budget ~6% at the lowest setting by design); a gate FAIL on the first row means read that row's fields and timings, and the timings often expose a second bug (redundant recomputation). Gate fixes are tooling-only change-log entries.
- On a status check, read state once (unit status, row counts, per-type median times, ETA from recent throughput) and answer. Never sleep-poll a multi-hour run inside a turn waiting for rows: the user sees minutes of silence, long sleeps hit the call timeout, and an interrupted call leaves state unknown.
- On "do the data look ok" mid-run: run a health-only script (counts, duplicates, validity, stop types, token ranges, hash/seed parity across arms, input completeness) and explicitly do NOT compare arms on registered outcomes before the stopping rule is met.
- Pitfall: check machine load (`ps --sort=-pcpu`, the project ledger) before launching a heavy CPU sweep; when another of the user's experiments is running, schedule after it, since contention slows it and skews any timings it records.
- Pitfall: when polling a background job with `sleep N` in a foreground terminal call, set the call timeout above N; equal values time out and lose the read.
- Pitfall: `cmd1 | tee log && cmd2` silently continues past failures because `&&` sees tee's exit code. Without pipefail a phase that crashed still feeds incomplete data to the next phase.
- Pitfall: make long jobs resumable at unit granularity before they start, not after they crash (see references/large-dataset-pipelines.md)
- Pitfall: a transient `systemd-run` unit's `RuntimeMaxSec` cannot be changed live (`set-property` refuses). To move a deadline: log it in the change log first, wait until the row count ticks over to a unit boundary, `systemctl --user stop`, check every JSONL parses, relaunch with the new limit computed as `deadline - now`; resume skips finished units. A deadline (or any run-parameter) change is clean only before any registered outcome is computed or viewed: state in the entry exactly what had been read (row counts, timings) and who decided.
- Hardware fault mid-run (abrupt freeze, failing memtest, MCE): every row computed on that machine since the fault could exist is untrusted even if it parses. Move rows, intermediates and logs UNREAD to `quarantine/<cause>-<date>/` (gitignored), log the cause and evidence in the change log, restart from zero with the same code and order, and add a post-run recheck phase to the chain: recompute a seeded random sample (~20 units) and require every registered field to match within the registered tolerance, else block publication. Test the recheck on one fresh unit (expect diff 0) before relaunch. Debug the machine first (see `linux-crash-diagnosis`); a silent hard freeze on a long CPU run is a hardware question, not an experiment bug.
- When the user attributes a stalled study to hardware ("not reproducible at this RAM"), check the ledger and the per-unit timings before agreeing. Slower hardware usually changes throughput, not any number; the real blocker is often a pause plus an expired deadline, and the options differ (close under the subset rule, register a new deadline, drop).
- Pitfall: quote a remaining-compute or close-out estimate from the rows' recorded per-unit times (`sum(t_total)` over the recheck sample, measured phase times), never from intuition. A recheck of 20 large units plus a synthetic grid is hours of CPU even when user time is near zero; say both numbers separately.
- Pitfall: precompute every per-cell quantile/median into a dict once; a quantile call inside a per-row, per-turn loop re-sorts the cell each time and turns minutes into hours. If a run must be killed for speed, kill it before any evaluation line prints, log the speed-only change in PLAN.md, and commit before re-running.

### 4b. Closing a study after its compute deadline passed

When the registered deadline expired with the run incomplete, close it under the registered partial-subset rule, never by a quiet extension. Order: plumbing-only read -> move partial units UNREAD to `out/notscored/` -> close-out change-log entry BEFORE the look (scored vs NOT SCORED; "k of N" bars are NOT SCORABLE below k and the entry supersedes the scorer's printed strings; scope limit of what remains; finishing = new registration) -> push -> remaining phases in a capped unit -> second unit runs the one look only on recheck PASS. Full recipe and commands: references/run-lifecycle.md.

### 5. Record and report

Append the outcome (including FAIL verdicts and script corrections) to PLAN.md's change log and commit with the output files. Every scorer emits a machine-readable `.json` beside the human `.out` (full keys, no truncation); later joins against console output break when display widths mangle group names. If a smoke test printed a verdict before the registered run, disclose it in PLAN.md and state that nothing in the scorer or bar changed after it.

Negative results are findings: when several hypotheses fail for the same mechanism (e.g. a ceiling test shows the tested inputs cannot narrow the range before the run), say so as the headline rather than hunting for a product angle. When the user asks whether anything is recoverable, rank options by evidence, measure the cheapest discriminating number first (minutes of compute on data on disk), and park speculative directions (e.g. RL) in the project's parking-lot note with the gated steps that would justify them, including the user's own reasoning. Report: the verdict, the numbers behind it, what is still open, and the next concrete step with an estimated cost in time/money.

Push back on scope (standing user request): when several rounds have produced solid findings, say that the next valuable step is publishing, not another experiment, and stop lines whose remaining fix costs user hours for n=1 evidence.

## Stats and clustering recipes

Width-ratio group tests, coverage CIs, bootstrap counts, batch break-even markup (risk premium for fixed-price products), adverse-selection (lemons) test with ICC and market equilibrium, k-means at scale: references/stats-test-recipes.md

## Publication figures

Figure/table budget, the `figures.py` pattern, matplotlib layout pitfalls, vision-check loop, and in-sample vs held-out number corrections: references/publication-figures.md

## Write-up, review response, repo publication

Drafting rules (every registered hypothesis reported, abstract matches verdicts, scoped claims, honest quantity names), handling LLM-generated reviews, and private-first repo publication checks: references/write-up-and-review.md

- Pitfall: never quote a number in an article or summary from an earlier chat message; re-read the committed `.out` file. Restated numbers drift.
- Pitfall: write the article draft to disk in the first minutes (skeleton + numbers from `.out`), then cite and polish in place. Sourcing first and writing at the end loses everything if the session or gateway dies mid-task.
- Pitfall: once the lab repo is public, keep drafts out of it (gitignore `journal/` or commit to a private branch) until the user has done the voice pass and approved publishing; a push for crash safety is a publication. The PLAN.md change log lives in that same public repo and is therefore published the moment it is pushed: verdict entries are the registration's record and belong there, but narrative, claims and draft prose do not.
- After a new round or correction changes a published number, grep every outreach draft AND every already-posted comment/issue for the old number and draft a follow-up correction for each live post (posted text goes stale silently; readers arriving later see the old claim).

## External replication

Reproducing a published paper from its released data (claim table, unit ambiguity, author contact, venues), surveying public datasets, tiering them by what they can test, independence (id-overlap) checks, task-unit hashing, schema-only freeze, reading wins against mixed baselines, outcome-tier (tail vs failure) rounds, backtesting a tail alarm on the user's own call logs (work vs carry tokens, conversation tax), and deriving success labels from the user's next message with a blind rating sheet: references/external-replication.md

- Pitfall: never compute an outcome on a new dataset before its grouping, split and eligibility are frozen in a commit. Group sizes are fair to inspect; cost values are not.
- Pitfall: gitignore every derived per-run file pattern (per-run reports, call rows) before the first commit of an extraction script; `git add -A` during a long extraction commits third-party rows, and removing them later means rewriting history before the repo can go public.

## Auditing a published ML method paper

Source sweep (paper versions, code forensics, OpenReview rebuttal-vs-camera-ready table, rivals' compute tables), headline-scope and bug-claim checks, CPU weight-level mechanism test via safetensors range requests, costing a reproduction, report shape, and the path from review to a Journal study: references/ml-paper-audit.md

## Comparing LLM variants (base vs abliterated/fine-tuned/quantized)

Arm-matching confounds (quantizer, chat template, thinking mode, sampling), refusal/over-refusal probe design, literature state on abliteration side effects, and design for local-CPU plus rented-BF16 arms: references/llm-variant-comparisons.md

## Large dataset pipelines

Resumable download/parse/delete pattern, per-unit atomic row files, prefetch threading, streaming tar.gz archives without saving them, parquet pitfalls: references/large-dataset-pipelines.md
