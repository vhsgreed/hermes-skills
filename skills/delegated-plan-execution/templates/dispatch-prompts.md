# Dispatch prompts for Hermes delegate_task

Two skeletons. The brief file is always the single source of exact values;
these prompts carry only context the brief cannot know.

## Implementer

```
context: |
  Task N of M. <one line on where this fits in the project>.

  READ THIS FIRST — it is your requirements, with the exact values to use verbatim:
  <workspace>/task-N-brief.md

  Repo: <path> (branch <branch> already checked out; do NOT switch branches, do not push).
  Venv: <path>/bin/python. Baseline: <N> passed.

  Interfaces from earlier tasks: <exact names/signatures the brief cannot know>

  Controller rulings (decisions the brief leaves open — follow them):
  - <ruling>: <why, one clause>

  Rules:
  - TDD: write the tests first, run them, capture the RED output, then implement.
  - Keep existing tests passing unmodified.
  - Commit: git -c user.name=<identity> -c user.email=<email> commit, subject
    "<type>: <subject>", trailer "Co-authored-by: <name> <noreply>"
  - Do not spawn subagents. Self-review your diff before reporting.

  Write your full report to <workspace>/task-N-report.md: what you implemented,
  TDD evidence (RED and GREEN commands with output), files changed, self-review,
  concerns.

  Final reply under 15 lines: Status DONE | DONE_WITH_CONCERNS | BLOCKED |
  NEEDS_CONTEXT; commit SHA + subject; one-line test summary; concerns; report path.
goal: |
  Implement Task N (<name>) of the <plan> plan, test-first, and commit on the
  current branch.
```

Why each piece: the status vocabulary makes the report machine-readable; the
report path keeps long prose out of the controller's context; the explicit
no-push and no-subagent rules are the two that cost most when omitted.

## Reviewer

```
context: |
  You are a task reviewer. Your full instructions are the prompt block in
  <sdd-skill-dir>/task-reviewer-prompt.md — read it first and follow it exactly.

  Placeholder values:
  - BRIEF_FILE: <workspace>/task-N-brief.md
  - REPORT_FILE: <workspace>/task-N-report.md
  - BASE_SHA: <base>   HEAD_SHA: <head>
  - DIFF_FILE: <workspace>/review-<base>..<head>.diff
  - Repo: <path>

  Controller rulings that changed the brief (the implementer was told these;
  judge against brief + rulings):
  - <deferred scope rulings>

  GLOBAL CONSTRAINTS (verbatim from the plan):
  - <exact values, formats, exit codes, interfaces>

  Named risks worth one focused check each:
  1. <condition> must <expected behaviour> — confirm what actually happens.

  Do not spawn subagents. Your final message is the review report.
goal: |
  Review Task N of the <plan> plan (spec compliance + code quality) and return a
  review report. Read-only: do not modify files, index, HEAD or branches.
```

## Scoped re-review

Same shape, using `<sdd-skill-dir>/re-review-prompt.md`, with `FIX_BASE` set to
the head the previous review saw, the diff restricted to the fix range, and the
findings pasted verbatim, each to be marked ADDRESSED or NOT ADDRESSED with
file:line evidence.
