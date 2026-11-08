# Large dataset pipelines

Resumable download -> parse -> delete pattern for multi-hour public-dataset runs (used by pre-registered-experiments step 4).

## Structure

- Done = a per-unit output row file exists (`full_rows/<unit>.jsonl`). Never a shared append log: a crash between parse and bookkeeping re-parses into the same append log and duplicates rows; per-unit files with atomic `os.rename(tmp, out)` cannot.
- Producer thread downloads the next unit into a `queue.Queue(maxsize=2)` while the main thread parses the current one; network and CPU overlap and peak disk stays at ~1-2 units.
- Delete each source parquet right after its row file lands. Peak disk = one unit + accumulated rows.
- Downloads: 3 attempts with backoff, explicit User-Agent, write to `.part` then rename. If a unit file already exists locally, skip the download (resumes mid-run).
- Runner accepts unit ids as argv for smoke tests (`sys.argv[1:] or ALL_UNITS`).
- Load metadata joins (session/task tables) ONCE at startup, not per unit.
- Fire the full chain as one background command: `set -o pipefail && phase1 | tee p1.log && phase2 | tee p2.log && phase3 | tee p3.log`.

## Streaming tar.gz archives (tens of GB, keep a few fields)

- Stream instead of downloading: `urllib.request.urlopen(resolve_url)` into `tarfile.open(fileobj=resp, mode="r|gz")`, iterate members, regex-match paths, `json.loads(tar.extractfile(m).read())`, write only needed fields to `data/<name>.jsonl.gz`, then a `<file>.done` marker with counts. 40+ GB extracts to ~20 MB with no disk peak.
- `tar tz` listing of the full archive takes as long as the download; list a `_mini` archive or `timeout 60 ... | head` instead.
- Run 3 archives in parallel via `xargs -P3` with a 3-try retry loop per archive, as one background command with notify.
- Nested archives inside the stream can be any format or corrupt: open with `mode="r:*"` inside try/except and count failures in the `.done` marker instead of crashing.
- Extractors print counts and timings only, never values, when the analysis is pre-registered but not yet frozen.

## Parquet pitfalls

- Inspect `pq.ParquetFile(p).schema_arrow` before assuming column names. Dataset exports often nest: `session.id`, `data.usage.prompt_tokens`, `data.choices[].message.tool_calls` are struct fields reached via `pc.struct_field`, not plain columns.
- Use `pq.ParquetFile(path).iter_batches(columns=[...])`, not `pq.ParquetReader(path)`: in some pyarrow versions the first positional argument of ParquetReader is memory_pool and gets the path string.
- Select only needed columns in `columns=[...]` and drop references (`del`) to wide tables as soon as their lists are extracted; these shards are ~200 MB each and full reads blow memory.

## Finding the source URLs

Query the host's file-tree API first (e.g. `https://huggingface.co/api/datasets/<repo>/tree/main/<dir>`) to confirm exact file names, sizes, and the resolve-URL pattern before writing the downloader. Guessing resolve URLs wastes a debugging cycle on 404s.

## Worked example: AgentLogs (HF `risenlab/agentlogs`)

- 276 step-log shards: `agent_session_logs/part_00000_of_00276.parquet` ... (~200 MB each); resolve URL = `https://huggingface.co/datasets/<repo>/resolve/main/<dir>/<file>`.
- Session tables: `agent_sessions/part_00000_of_00002.parquet` (+ second part) — carries `prompt` text, `model`, `state`, `event.type`, `created_at`, `task.id`.
- Task table maps `task.id` -> `repository.full_name` (needed for repo-held-out splits).
- Step-log schema is nested: `session.id`, `entry_index`, `data.usage.{prompt_tokens,completion_tokens,prompt_tokens_details.cached_tokens}`, `data.model`, `data.choices`. Usage rows are per model call; per-session cost = sum of per-call pricing by that call's own model, cached and uncached priced separately.
- Sessions with prompt text are a minority (~25-30%); power calculations must use the prompt-bearing subset, not total sessions.
- Venv without pip (uv-created): `uv pip install --python .venv/bin/python <pkg>`, or `.venv/bin/python -m ensurepip` first.
