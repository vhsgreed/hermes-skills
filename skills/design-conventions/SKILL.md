---
name: design-conventions
description: "Use when brainstorming or planning a new project or feature."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [brainstorming, design, naming, spec]
    related_skills: [spike, niche-validation]
---
# Design dialogue conventions (Karl)

Companion deltas to superpowers:brainstorming (plugin-bundled and not
patchable via skill_manage; its process still governs). Where these rules
conflict with the plugin skill, these win.

## When to Use

- A request to build, create, or change something enters design or
  brainstorming (the superpowers:brainstorming process), for any project of
  Karl's.
- Not for pure questions, status reports, or work with no design decision.

## Questions during ideation

- Ask one question per message, in plain chat text, open-ended. Menus
  (multiple choice or a multi-question clarify form) fit only bounded
  pick-one decisions: in ideation Karl answers free-text and reframes past
  the offered options, and batched question forms get cancelled outright.
  Open questions about purpose converge faster than options that pre-frame
  the space.

## Naming is design, not polish

- Before recommending a project, package, or repo name, batch-check
  availability live instead of guessing. Use scripts/check-names.sh (PyPI
  JSON endpoint: 404 = free; GitHub search API for collisions), present the
  field with trade-offs, and recommend one. The script's unauthenticated
  GitHub search rate-limits after ~10 names (prints `gh:?`); re-check those
  with `gh api "search/repositories?q=NAME+in:name"`. For a public project the name is
  half the reach, so settle it during design, before the spec is written.
- Karl often coins his own name instead of picking from the field. Check his
  name with the same script right away (PyPI incl. -/_ variants, GitHub
  repos, github.com/<name> user/org) and report free/taken plus at most one
  practical caveat (e.g. typing length, suggest a short CLI alias in the
  spec); do not re-pitch your own recommendation.
- Rename an existing repo/package only after the written spec is approved;
  GitHub redirects a renamed repo, so renaming in place keeps stars and links.
- For a v-next of an existing project, re-check the current name the same
  way: a GitHub repo name does not mean the PyPI name is Karl's. Read the
  PyPI JSON `info.home_page`/`project_urls` before citing pypistats
  downloads as reach, since a same-named package by someone else counts
  their installs, not his.

## Opening a new project

- Before the first design question, read the ~/STATUS.md anchor block's
  betting rule and apply it: propose concrete bet terms (stake cap in hours
  or money, deadline before the next exam checkpoint, a measurable kill
  condition) for Karl to correct, and ask which ACTIVE block it displaces
  if the slot is full. Proposing terms beats asking him to invent them.
- Add the project's STATUS.md block as [IDEATION] in the same turn.
- When the subject is his own machine or data, run a read-only inventory
  (sizes, unit counts: repos, projects, skills; separate tool/cache noise
  such as Steam, browser data, toolchains from what he made) and lead with
  it. Sprawl feels smaller once noise is separated, and the counts size the
  cost estimate. Read-only exploration is allowed before spec approval.
- If he answers a different question than the one asked, take the answer,
  record it, and do not re-ask the original; it was not the one that mattered.
- He often brainstorms between other commitments ("leaving in 20 min").
  Keep each design reply short, end with one question marked no-rush, and
  close with a one-line reminder of the commitment if one is pending.

## Starting a v-next of an existing project

- Before the first question, gather the reach evidence (stars, forks,
  real downloads), the feature surface from the README, and recent commit
  history, and state them in a few lines. "Improved" needs a direction,
  and the evidence frames the purpose question.
- Add or update the project's block in ~/STATUS.md when ideation starts,
  with Next = the open question. Record each decision as it lands (goal,
  target number + date, name, approach), so an interrupted design resumes
  at the right stage.

## Turning a stated benefit into design

- When Karl names a feature by its benefit ("proxy rotation for faster
  extraction"), trace the mechanism and say which prerequisite the benefit
  silently needs, before designing the feature. Example rule: rotation only
  speeds a scrape if fetches run concurrently, and a next-link chain cannot
  be parallelised, only URL patterns, URL lists, or multi-site jobs can.
  A missed prerequisite surfaces later as a feature that ships and does not
  deliver the benefit.
- Push back when the new aim contradicts a promise the project already makes
  (README "what it will not do"): name the contradiction and let Karl decide
  it deliberately; the README wording becomes part of the design.
- Short replies ("ok", "go for A") approve exactly the stage presented. Move
  to the next stage; do not treat them as approval of later artifacts.
- When Karl rewrites a headline, tagline, or name, check whether the new
  wording promises behaviour the design does not have yet ("escalating
  effort" implies per-page escalation, not a one-time pick). Add the implied
  feature to the spec as its own section and flag it as needing his OK: a
  wording change that silently adds scope ships a README that lies.
- When Karl proposes a "novel" or experimental layer, check prior art before
  agreeing it is novel (name the existing tools), and state the risk it puts
  on the project's users (account bans, terms of service) and any README
  promise it breaks. If he wants it after the current spec, park it in the
  spec's Parked section with the constraints it must keep, so its own spec
  later starts from them instead of re-deriving them.

- Feature requests from unsolicited or AI-generated email are zero demand
  (bulk outreach, often vendors selling the thing requested). Say so once,
  keep that feature minimal, and build the differentiating parts first. Do
  not ship integrations (provider presets, third-party APIs) nobody can test
  without paid accounts; add one when a real user asks, with their test.
- When adding a new status or exit code, Karl checks whether it will become
  the normal result and so turn into noise. Answer with a narrow definition
  (what counts, what explicitly does not), retries before it counts, an
  opt-out flag for old scripts, and a measured check (e.g. the live check
  must show it zero times on healthy targets).

## Approaches and design sections

- Present 2-3 approaches with a rough effort estimate each and what each
  keeps or throws away (tests, history, live checks, existing stars), lead
  with the recommendation. For an existing working codebase, evolving in
  place usually wins; a rewrite must justify the weeks spent reaching parity.
- Announce the design sections up front (numbered), present one per message,
  and end each with one concrete question. Include a YAGNI line naming what
  is deliberately left out.

## Spec scope

- The spec and plan cover the working product only. Demo videos, launch
  posts, and marketing polish are a later phase gated on the product meeting
  its viability criteria; record them as parked and keep them out of design
  sections, the spec, and the plan.
- End the spec with a section listing decisions taken without explicit
  sign-off (unanswered questions where the recommendation was used, names
  picked during writing). On approval, rename it to "Decisions confirmed",
  set the spec's status line to approved with the date, and commit that
  before writing the plan, so the plan never builds on an unratified choice.
- Before writing the plan's interfaces for a new dependency, install it in
  the project venv and introspect the real API (import paths, class names,
  test client, result shape) with a ten-line smoke script. Major versions
  rename entry points, and a plan written from memory sends every task's
  first test at a symbol that does not exist.
- Viability criteria in a spec are numbers, not moods. If the goal is stated
  as a mood ("viral", "dopamine", "usable"), propose a falsifiable number and
  a date before it enters the spec.
- Plan shape: repo rename, remote rewrite, version tag, publish, moving the
  working directory, and edits to config outside the repo go in a closing
  "After merge" section, never inside a task. An implementer working task 3
  cannot follow a brief that names a path task 1 moved, and a tag cut from an
  unmerged branch ships code the main branch does not have. Hand the user
  those commands instead of running them.
- Split any task that bundles a security boundary (an SSRF guard, an auth path,
  a credential store) or a new external surface with a large unrelated layer:
  each half then gets its own brief, its own tests and its own review, instead
  of the boundary being one clause inside a review of a huge diff.
