---
name: delegated-plan-execution
description: Use when executing a plan via delegated subagents.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [subagents, plans, code-review, delegation]
    related_skills: [superpowers:subagent-driven-development, superpowers:writing-plans, model-tier-routing]
---

# Delegated Plan Execution

The plugin skill `superpowers:subagent-driven-development` is the procedure:
fresh implementer per task, task review (spec + quality) after each, fix loops,
one whole-branch review at the end, a ledger as the recovery map. Read it first
with `skill_view`; it carries the prompt templates and the three scripts
(`scripts/sdd-workspace`, `scripts/task-brief`, `scripts/review-package`).

This skill is what that procedure does not say, and what breaks when the
harness is Hermes `delegate_task` rather than a session that can resume a live
child.

**Announce once:** "I'm executing the plan with delegated subagents; each task gets its own implementer and its own review."

## When to Use

- The user chose subagent-driven execution for an approved plan, or said
  "execute" / "proceed" on a plan with several reviewable tasks.
- A task is big enough that an independent reviewer gate is worth a fresh
  context (security boundary, data model, anything a wrong ship would cost).
- You are resuming a run: the plan's ledger under `<repo>/.superpowers/sdd/`
  names the completed tasks, so resume at the first without a `complete` line.

Not for: a single small edit, tightly coupled work that one context must hold
end to end, or a plan the user asked you to implement inline.

## Setup

1. `skill_view` the SDD skill, the plan, and the spec. The spec binds, the plan
   argues from it, and a conflict inside the plan resolves against the spec.
2. Work on a feature branch in place when no other work is in flight on the
   repo; use a worktree only when something else needs the tree. Record the
   base commit in the ledger.
3. Record the baseline test count before Task 1 (`pytest -q | tail -1`). Every
   later "N passed" is only meaningful against it.
4. Create the plan workspace with `scripts/sdd-workspace PLAN_FILE` and open
   `progress.md` with `# SDD ledger — plan: <path>` as line one. The workspace
   is git-ignored scratch and dies with `git clean -fdx`.

## Pre-flight scan

The SDD skill's scan looks for tasks contradicting each other and mandates the
rubric calls defects. Add two rows it does not ask for:

- **Steps whose effect leaves the repository.** Renaming the repo, rewriting
  the remote, moving the working directory, tagging a release, publishing,
  editing config outside the repo. Rule each to after the merge and ledger it.
  A directory move invalidates every later dispatch's brief path, and a tag cut
  from an unmerged branch ships code the main branch does not have.
- **Facts that appear twice with different values.** The same string, status
  code or field list written in the spec and again in a task's example will
  diverge, and the later task implements the stale one. Pick the value, ledger
  the ruling, and edit both documents before Task 1.

## Right-size before dispatching

- Several small same-shape edits: one batch dispatch, one review.
- One task bundling a security boundary or a new external surface with a large
  unrelated layer: split it at the boundary into `Task 4a`, `Task 4b`,
  dispatched in sequence. The guard, protocol edge or auth path gets its own
  brief, tests and review instead of being one clause in a review of a huge
  diff. Ledger the split as a ruling.
- A task whose plan text contains the complete code is transcription: cheapest
  usable model. Multi-file coordination written as prose: mid-tier. Security or
  concurrency: the strongest model available.

## Dispatch an implementer

Use `templates/dispatch-prompts.md`. The brief stays the single source of exact
values; the dispatch adds only what the brief cannot know: where the task fits,
the interfaces earlier tasks produced, your resolution of any ambiguity, the
report path, the commit convention.

Harness facts that shape the prompt:

- `delegate_task` has **no per-dispatch model parameter**. Children run at
  `delegation.model` from config. Escalating a fix round means a different tool
  (a CLI agent such as `claude -p --model ...` through terminal), not a
  dispatch argument. Know this before the loop needs it.
- Children are **one-shot and background**. Their result arrives as a message
  when they finish; nothing resumes them. A fix round is a fresh dispatch
  carrying brief path + report path + findings, with the report file as the
  child's memory across rounds.
- Never dispatch two implementers at once: one task, one tree, one review.
- Everything pasted into a dispatch stays in your context for the rest of the
  session. Hand artifacts over as file paths, always.

## Verify the child before you trust it

A child's summary is a self-report. After every DONE, run the cheap checks
before packaging the review:

```
git log --oneline -2 && git status --short && python -m pytest -q | tail -1
```

A commit that does not exist, a dirty tree, or a test count that does not match
brief + new tests is a finding you caught for free. "All tests pass" in a
report is worth exactly this much.

## Review gate

Package the diff with `scripts/review-package PLAN_FILE BASE HEAD` and hand the
reviewer: brief path, report path, diff path, the plan's Global Constraints
verbatim, the rulings that narrowed the task's scope, and a short list of named
risks.

- **Rulings are requirements, not verdicts.** "The repo rename was deferred to
  after merge" belongs in the prompt, or the reviewer reports a deliberately
  removed step as Missing. Named risks with the expected behaviour (the
  trailing 404 that must not count as incomplete; the credential that must not
  appear in an exception string) are the cheapest way to get the cases the
  tests miss actually executed.
- **Never tell the reviewer how to grade.** No "do not flag", no "at most
  Minor", no "the plan chose this". If you predict a false positive, let it
  surface and adjudicate it.
- Reviewers return "cannot verify from diff" items and findings flagged
  plan-mandated. Both are yours: resolve or rule, ledger it, then act.

## Fix rounds

- Minor findings never enter the loop. Ledger them as
  `Task <N>: minor (deferred): <one-liner>`; they are the final review's triage
  list. An unread roll-up is a silent discard.
- Critical, Important and spec-failure entries: one fresh dispatch with the
  findings verbatim and the covering test files named, then one scoped
  re-review over the fix range. Cap at five rounds per task, then adjudicate and
  ledger every open finding.
- Never fix findings in the controller session. Controller fixes skip review and
  fill the context you need for coordination.
- **Audit the test diff on every fix round.** Compare `git diff <fix-base> HEAD -- tests/`
  and demand justification for each changed assertion. An implementer under
  pressure relaxes the test that pins the bug instead of fixing the bug, and it
  reads as progress: the suite goes green, the count rises. Twice in one run a
  fix round rewrote a failing expectation and pinned the regression in a new
  test; both times the summary said "done". Put the question in the dispatch
  ("if an existing test's expectation must change, name it and say which ruling
  requires it") and again in the scoped re-review ("list every changed test with
  old and new text; was it ruling-required or relaxed").
- A fix can overshoot: a ruling meant to stop one failure mode (never fetch
  without a proxy) implemented as a blanket rule made the feature inert (no
  retry, no climb). Re-review the fixed range for behaviour the ruling never
  asked to remove, and keep the ruling's intent next to its cost so the next
  round can tell over-correction from correction.

## Rulings and the ledger

Every decision you take for the user is one ledger line:
`Ruling: <what> — <why> — <what it costs if wrong>`. Report them all, in order,
with their costs when you finish; they are the only channel by which the user
sees what you decided on their behalf.

- When a ruling settles a value the spec or plan states literally (a message
  format, a field name, a threshold), **edit that text in the same pass**. The
  next brief and the final reviewer both read it; a stale literal becomes a
  finding against correct code.
- A conflict you notice while writing a dispatch is a pre-flight finding too:
  rule and ledger it at that moment instead of letting the implementer choose.

## Finish

Final whole-branch review over `git merge-base main HEAD` on the strongest
model, pointed at the ledger's deferred-minor and parked lines. It will find
integration bugs every task review missed; judge it against the product's
promises, with adversarial local servers and a mutation check (recipe and
prompt shape: [references/final-review.md](references/final-review.md)). One
fix wave (code first, then docs), one scoped re-review, residuals surface to
the user.

Running the strongest-model reviewer through a CLI agent: write the prompt to
a file and pass it on **stdin** (`claude -p --model opus --allowedTools ... <
prompt.md`), never as a trailing positional argument. Variadic flags such as
`--allowedTools <tools...>` swallow the positional prompt and the CLI exits
with "Input must be provided". Run it as a background terminal process with
`notify=true`; if it reports a usage limit with a reset time, queue the same
command behind a wait-until-reset loop instead of downgrading the final gate
to the delegation model. Tags, publishes, pushes to
shared branches and repo renames are the user's call: ask once with the steps
numbered (a `clarify` with go / partial / hold choices), and on his go run them
all yourself in the ledgered order.

Release procedure (fresh CI-identical venv first, master CI green before the
tag, tag-triggered workflows, patch release instead of moving a tag, PyPI
trusted publishing): `github` skill, `references/python-package-release.md`.
The dev venv accumulates optional extras over a run, so the suite that passed
all reviews can still fail CI on an unconditional import.

A green plan run proves the plan, not the shipped artifact. Before announcing
or listing anything, run the PUBLISHED package the way a stranger installs it
against live targets; the packaging bug and the parsing bug that reached users
both passed every review and every test in the dev tree.

Update the project's block in `~/STATUS.md` (Current + Last touched) at task
boundaries and at the end; a long run otherwise leaves the ledger stale.

## Pitfalls

| Pitfall | Why it bites |
|---|---|
| A plan step renames the repo or moves the tree mid-run | Every later brief path points at the old location; the subagent fails on a path, not on the work |
| Trusting the child's "N passed" | Children report intent; only your own run proves the tree |
| Deferring a plan-mandated finding without a ruling | The next task builds on the defect and the final review cannot see why it exists |
| Asking the reviewer to ignore something | Pre-judging hides real defects; adjudicating after the fact is cheaper |
| One review per minor fix | Fix waves multiply context cost; batch the findings into one dispatch |
| A fix round turns the suite green by rewriting a test | The regression it hid returns in the next task, and the reviewer of a green diff has no reason to look |
| Letting a ruling die with the workspace | The user never learns what you decided for them |
| Docs written in the same task as late code fixes | A code fix makes a true README sentence false; re-run doc claims after the last code change |
| Tagging from a dev venv's green suite | Optional extras installed during the run hide an unconditional import; CI on the tag goes red after the release is public |
| Treating clean task reviews as merge-ready | Seams between tasks (who catches, who paces, who may fetch) are invisible per task; only the whole-branch review sees them |

Templates: [dispatch-prompts.md](templates/dispatch-prompts.md) — implementer
and reviewer prompt skeletons for this harness.
