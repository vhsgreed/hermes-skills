---
name: automation-pipelines
description: Use when building a scheduled fetch-and-deliver pipeline.
version: 1.0.0
author: Karl Sundström
license: MIT
metadata:
  hermes:
    tags: [cron, automation, pipelines, ollama, gemma, himalaya, fts5, rss]
    related_skills: [backup-and-recovery, agent-security-posture]
---
Build scheduled pipelines at zero API cost: stdlib fetching, the LOCAL Ollama model for text work, himalaya for delivery. Never let a background job call a paid endpoint.

## When to Use

- A recurring job that fetches, transforms, stores and delivers: digests, research sweeps, monitoring reports, price watches.
- Anything the user wants running unattended on a schedule.

Do not use for one-off foreground analysis, or for a job the user has explicitly pinned to a paid model (ask first).

## Always-on rules

- **Zero API spend by default.** Fetch with stdlib HTTP/RSS, write with the local Ollama model, deliver with himalaya over the existing mailbox. A cheap cloud writer is allowed only per job after the user approves it, and only with the local model as automatic fallback (see step 2c).
- **A stated cost constraint is a hard gate.** When the user says "run on gemma or free models", never fall back to a paid provider. Ship degraded or raw output instead.
- **Stages fail independently.** One dead feed or one failed summary must never abort the run. Log it, continue, and surface the problem list inside the delivered output so the user sees what is missing.
- **An exit code is not a delivery.** After the job reports success, confirm the artifact exists on disk and the message landed in Sent and not Spam.
- **Value gate before building or extending a digest.** Re-summarising public feeds that are already curated (Google News, outlet front pages) adds little for this user; he retired a daily news digest for exactly that reason. Before proposing one, name the input the user cannot get elsewhere: numbers (market data, APIs), primary sources, cross-source structure computed in code, or private data. If there is none, say so instead of building.
- **Retire, don't delete.** When the user stops a scheduled job, comment out its crontab line with a reason and back up the crontab first, so one edit turns it back on.

## Procedure

### 1. Fetch

Stdlib only: `urllib.request` for HTTP, `xml.etree.ElementTree` for syndication. Send a real User-Agent and a hard per-URL timeout.

- Strip XML namespaces (`tag.rsplit('}', 1)[-1]`) and handle both RSS 2.0 `<item>` and Atom `<entry>`, or half your feeds parse to zero items with no error raised.
- Bound items per feed and de-duplicate on normalised title before transforming, or the summary is dominated by one prolific source.
- A hanging feed must not consume the whole run: timeout per URL, not per job.
- **Vet a feed by freshness before adding it, not just by reachability.** A feed can return 200 with 300 items and none from the last week. Run `scripts/feedtest.py URL...`, which prints item count and items under 24h old, then add only feeds with a high fresh share. Candidate feeds by beat are in `references/news-feeds.md`.
- **Interleave feeds round-robin when the model sees only the first N items.** Appending feed by feed means the last feeds in the list never reach the prompt, so a newly added source silently changes nothing.
- When a feed dies, replace it in the same change and comment why in the config. Breadth comes cheapest from an aggregator (Google News topic RSS) plus one or two dense wire-grade feeds. Paywalled outlets still serve full headlines over RSS, and headlines are all a digest needs.
- For multi-outlet comparison ("same story, different angles"), store feeds as `(outlet label with country/ownership, url)` and tag every headline with its outlet in the prompt, or the model cannot attribute framing.

### 2. Transform with the local model

POST to `http://127.0.0.1:11434/api/chat` with `{"model": "gemma4:26b", "stream": false, ...}`.

- **Set `"think": false`.** With thinking left on, gemma spends its token budget in the `thinking` field and returns an EMPTY `content`, which reads as total model failure. Most expensive gotcha in this workflow. If content is empty anyway, salvage the `thinking` text rather than dropping the summary.
- **Set `"options": {"num_predict": 2048}`**. Ollama otherwise picks a small default and the reply truncates mid-sentence with `done_reason: "length"`.
- **Set `num_ctx` to cover the prompt you actually send.** A prompt overrunning the served context returns a very SHORT reply with `done_reason: "length"`, which reads as truncation and is not: raising `num_predict` does nothing. Read `eval_count` before tuning anything. `local-model-wiring` → `references/ollama-api-contract.md` separates the three failure signatures.
- **Cross-outlet comparison prompts need hard constraints.** Left open, the model picks obituaries and weather (where outlets cannot differ) and pairs outlets that cover different stories. Require political events, have it quote headline wording, and do the matching in code first (step 2d).
- Before swapping the model, A/B the candidate against the current one on the same items and prompt, scored on the task's actual failure mode. Capture the exact prompt by monkeypatching the pipeline's `urlopen` so both arms get identical input. Check quoted strings against the input headlines with quotes normalised (curly vs straight), or the check flags false fabrications. Note that a cloud model, even a free one, breaks the local-only rule; the user must OK that.
- **Enforce output structure in code when the prompt does not hold it.** Even told "never pad", models paired same-bloc outlets, kept one-outlet blocks saying "X does not cover this", and picked weather. Post-filter: keep a comparison block only if its bullets name at least one Western AND one non-Western outlet, drop "does not cover" lines, drop weather/obituary titles, and print an explicit "no cross-bloc story today" line when nothing survives. Filtering alone stops fake matches but can leave the section empty when the model misfiles a real match; keep it as a backstop behind code-side grouping (step 2d).
- Keep a raw-mode flag that writes the unsummarised item list. When the model leg fails you ship something useful instead of nothing.

### 2b. Dedupe against what was already delivered

A recurring digest repeats itself unless it compares today's items with its own sent archive. Slow feeds keep serving month-old entries, and the model rewrites the same themes day after day.
- Drop items older than N days by pubDate/updated/dc:date (RSS 2.0, Atom and RDF all differ).
- Drop items whose URL or normalised title appears in the archived reports from the last ~7 days.
- Give the model the last 2-3 delivered briefs as "already sent" so it avoids those themes. Restrict any "Update:" label to stories actually named in that text, or it puts "Update:" on unrelated items.
- Print the new vs skipped counts in the output, so the user can see the filter working.
- **Make `--dry-run` write to `<archive>/.dry-run/` and skip the indexer.** The archive IS the dedupe backlog, so a dry run that writes into it makes tomorrow's run judge itself against test output. Build this in from the start instead of backing up and restoring by hand.
- Record every fetched item in the backlog, not just the first N links listed in the report, or unlisted items return as "new".

### 2c. Cloud writer with local fallback (when approved)

Pattern: OpenRouter chat call first, gemma on any failure, per section.
- Read the API key from `$HERMES_HOME/.env` inside the script; cron has no shell env. Verify with `env -i HOME=... PATH=/usr/bin:/bin python3 -c ...`.
- Retry 429/5xx up to 3 times with backoff (that is upstream congestion). Fall back immediately on other 4xx, `finish_reason != "stop"`, or content under ~400 chars. Test the fallback with a bad key and with no key.
- **Keep reasoning OFF for digest writing.** Some providers leak the thinking into `content` even with `reasoning.exclude`, which fills `max_tokens` before the brief is written and would mail scratch work.
- Log provider and `usage.cost` per call. Name the writing model in each section header, and update the email footer and the crontab cost comment, so the archive shows which model wrote what.
- Check OpenRouter's live model list for pricing before promising "free". `:free` variants come and go.

### 2d. Cross-source comparison: group in code, not in the prompt

Asking a model to find "the same story across outlets" in a flat headline list fails both ways: it misses real matches and pairs unrelated items, even when the prompt says never to pad. Group the headlines in code first, and send the model only the groups that pass the cross-source rule.
- Local `nomic-embed-text` via Ollama `/api/embed`, prefix each text with `clustering: `, then normalise the vectors and run average-linkage clustering. Cosine 0.84 separated events cleanly on about 250 headlines. Single-link chains unrelated stories together.
- Pure Python is fine (~5 s for 250 items, no numpy needed).
- Fetch more items per feed (25) for this beat. Overlap between outlets grows with depth.
- If embedding fails, fall back to the flat prompt and log it as a problem.
- Send the model labelled `GROUP n` blocks (only cross-bloc groups, state media ranked first, cap ~8) plus a separate `SINGLE-BLOC` list for "only one side covers this".
- Bloc design decides the finding: a two-way Western/non-Western split mostly yields BBC vs The Hindu/Dawn. If adversarial state media is the point, use three blocs (Western, adversarial state, Global South/independent).
- Tune the threshold by printing the top ~60 cross-outlet pairs by cosine and cutting just below where unrelated pairs start; retune for a new embedder or language.

### 2e. Publishing a personal pipeline as OSS

When the user wants a tool open-sourced (code public, no promotion), follow `references/oss-sanitise.md`: config to env vars, strip personal and strategy comments, secret-scan, fresh single-commit repo, README with known weaknesses, reusable method as a `skills/<name>/SKILL.md` inside the repo. Creating the public repo is visible to anyone, so get the user's go-ahead first.

### 3. Store and index

Write dated artifacts to a stable home (`~/research/<beat>-YYYY-MM-DD.md`), then run the FTS indexer so the corpus stays queryable.

- When you introduce a new report naming scheme, add its glob to the indexer's GLOBS list in the same change. A report written but not globbed is silently unsearchable forever.
- **Sanitise model output before rendering.** The model emits its own top-level `#` heading regardless of what you asked for, so a rendered document ends up with two stacked titles; demote everything beneath the heading the pipeline owns. Escape every text node before applying markup — a headline containing `<` or `&` otherwise breaks the document or injects markup.

### 4. Deliver

Pipe a fully formed RFC822 message to `himalaya message send` on stdin.

- **Absolute paths for every binary.** A cron `PATH` does not include `~/.local/bin` or a project venv, so `himalaya` and `python` resolve to "not found". The job then logs a clean run while delivering nothing, and can do so for days. Most common cause of a pipeline that works interactively and mails nobody. Resolve paths once inside the script and test through cron's own shell, never the interactive one.
- himalaya v2 takes `-m/--mailbox` for a folder; `-f` is a hard error. `attachment list/download` and `message read` take the ENVELOPE id (the `id` field of `envelope search --json`), not the RFC Message-ID header. Passing the header fails with an empty result, not an error. Use Message-ID only as a dedupe key.
- api.riksbank.se (SWEA) rate-limits bursts of narrow date lookups: the first 2-3 calls succeed and later ones fail empty. Fetch one wide date range per series (e.g. 730 days) and look dates up in the returned table instead.
- Mailbox names here are Swedish (`[Gmail]/Skickat`, `[Gmail]/Skräppost`). After the first send, confirm the message is in Sent and NOT in Spam.
- **Send formatted mail as `multipart/alternative`** — a `text/plain` part plus a `text/html` part. A `text/markdown` body renders in most clients as an opaque blob or a stray attachment rather than as mail. Derive the plain part from the same source so the fallback is never empty.
- `himalaya send` and `himalaya message send` are both in the wild across versions. Try both before declaring the send broken.
- **Read the delivered message back before reporting success.** The send's exit code is not proof, which is how a broken MIME structure ships unnoticed. The reader can also fail on a message that is fine: it reports "no body" for a well-formed `multipart/alternative` while `message read --raw` returns the entire thing. Judge structure from the raw bytes, never from the reader's verdict.
- **Stripe-hosted receipt links expire** (older mails print a "Receipt URL Expired" form that saves fine and parses to nothing). After printing a fetched page to PDF, check its extracted text for a dead end and fall back to the mail body, which still carries the amount.

### 5. Schedule and log

System crontab on geekom, output appended to `~/logs/<job>.log`, one job per line with a comment naming its cost model.

- Prefer a system cron over an agent cron for this class. The pipeline is self-contained and must still run when the agent is down.

### 6. Change watchers (no_agent variant)

For thread/activity watching, the job is a no_agent script whose stdout is delivered verbatim: print only when something changed, empty stdout otherwise.
- Watermark on a monotonic ID (comment ids), not timestamps or hashes of the whole payload.
- Run the script once manually BEFORE the first scheduled run to seed the state file. Without a baseline run, every historical event arrives as "new" on the first tick and the watchdog wakes on noise.
- Detect state transitions (open/merged/closed) separately from new comments; a merged PR with no new comment is the event worth delivering.
- **Verify the data source actually surfaces the events being watched, or silence proves nothing.** Many platform APIs return only the caller's own rows in per-object listings while third-party activity appears only in aggregate counters, so an owner-id filter never matches and the watcher quietly reports "nothing new" forever. Cross-check the watcher's claim of silence against an aggregate stat before trusting it.
- **Make errors loud in a quiet-by-default watcher.** A failed fetch or parse must print an error line and exit non-zero; a broken check that looks like "nothing happened" gets believed, which is the one failure mode this delivery style cannot express.
- **Alert only on genuine human events; record the rest.** Autoresponders, ticket acknowledgements, and the user's own test sends match any naive "new reply" filter and wake the user on noise until they stop reading the alerts. Match and drop them by pattern, but still write them to the seen-state so they cannot resurface later as new.

## Verification checklist

- [ ] `--dry-run` completed before the first live send.
- [ ] Binaries resolve from the cron environment, not only from an interactive shell.
- [ ] Model leg returned non-empty content and `done_reason: "stop"` (or `finish_reason: "stop"` for the cloud writer).
- [ ] With a cloud writer: fallback to the local model verified with a bad key and with no key.
- [ ] Artifact on disk at the expected size.
- [ ] Message in Sent and not in Spam, with the intended MIME structure in the raw message.
- [ ] Source-problem list, if any, present in the delivered output.
