# Extracting agent activity from Hermes' own state.db

Source of truth for "what did the agent do": `~/.hermes/state.db` (SQLite, per profile).
Every tool call is stored with its full JSON arguments, so file paths, diffs, commands and
queries are all recoverable without any instrumentation. Typical size after a month:
~300 MB, ~500 sessions, ~16 k tool calls per 30 days.

## Query

```python
con = sqlite3.connect(f"file:{STATE}?mode=ro", uri=True)   # read-only, WAL-safe
rows = con.execute(
  "select m.tool_calls, m.timestamp, s.cwd, s.title from messages m "
  "join sessions s on s.id = m.session_id "
  "where m.tool_calls is not null and m.tool_calls != '' "
  "and m.timestamp between ? and ? order by m.timestamp", (start, end)).fetchall()
```

- `messages.tool_calls` holds a **JSON array** — one assistant row can carry several calls.
  Iterate the array; never count rows.
- `sessions` carries `cwd`, `git_repo_root`, `git_branch`, `estimated_cost_usd`, token
  columns and `parent_session_id` (subagents), so cost and repo context come for free.
- `sqlite3` may not be on PATH; the Python module is always available.

## Tool → kind → attribution

| Tool | kind | magnitude / attribution |
|---|---|---|
| `read_file` | read | `args.path` |
| `write_file` | write | `args.path`; lines = `content.count("\n") + 1` (full overwrite) |
| `patch` | patch | `args.path`; **exact** LOC = new_string lines added, old_string lines removed |
| `search_files` | search | `args.path` + pattern |
| `terminal` | cmd | binary = first token of `command`; no path → session `cwd` |
| `execute_code` / `tool_call` | code | no path → session `cwd` |
| `web_search` / `web_extract` / `browser_exec` | web | query or host only |
| `skill_view` / `skill_manage` | skill | skill directory under `~/.hermes/skills` |

- `patch` arguments are the only place true churn exists; `write_file` counts a whole-file
  rewrite, so label it as such rather than summing it into "lines added".
- Shell commands are roughly half of all calls and carry no path field: attribute them to
  the session cwd as **weak attribution**, and parse absolute paths out of the command
  string before falling back or the focus marker parks on `~` all day.
- Bucket paths to 2-3 segments under `$HOME` for layout, but keep the full path on each
  mark for drill-in.

## Sanity checks

- Distinct files and directories per 7 days is the right scale to size a layout: expect
  ~350 files / ~135 dirs, i.e. grouping is mandatory.
- Subagent sessions appear as their own sessions with `Subagent:` titles; tag them so
  their work is visible but not merged into the parent.
- `~/.hermes/cache/scratch` accumulates real churn that produced nothing — render it faded
  rather than dropping it.
