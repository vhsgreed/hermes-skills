---
name: niche-validation
description: "Use when choosing or validating a business niche or product."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Business, Research, Planning, Market]
    related_skills: [grounded-citations, pre-registered-experiments]
---

# Niche validation

Choose the next source of revenue with evidence, not mood. The deliverable is a decision
artifact that survives a review meeting and names one thing to do next. Pre-registered
criteria, parallel evidence workstreams, verified conclusion.

## When to Use

- "What should the product be / where does the first MRR come from / is there demand for X?"
- Choosing between candidate revenue lines, or deciding to kill or keep one.
- Picking a free/open-source or agent-tooling project to build (same incumbent check).
- The user sets a deadline for a decision (e.g. "conclusion for Sunday's review").

Do not use for: one-off competitor lookups (`competitor-news-monitor`) or pre-registered
software/ML experiments (`pre-registered-experiments`).

## Always-on rules

- Every goal carries a number and a date before planning starts. An undefined goal is
  unmeasurable; say so and get it defined instead of planning around it.
- Write the done-criteria BEFORE gathering evidence, date-stamped in the frame file.
  Criteria shaped after seeing results are rationalization.
- Done-criteria shape (pass/fail each): (1) paying demand: people already pay for this or
  an adjacent product at real prices, interest does not count; (2) a channel the user can
  actually use (see channel inventory, step 1); cold email has a 0-reply record for this
  user, so a candidate that only works by cold outreach fails; (3) a specific edge;
  (4) a short test (<= 4 weeks, <= $100) with a numeric pass bar; (5) fits 10-20 h/week
  beside studies; (6) a path to the MRR goal, or a bigger payoff with a first paid signal
  before the money gate; (7) recurring user-hours per output unit (video, game, post) are
  measured in the test and stay under a pre-registered cap, and the plan survives a month
  with zero output. Criterion 7 exists because this user quit a growing YouTube channel
  over hours of editing per video: reach does not rescue a format that costs hours per unit.
- Run an incumbent search BEFORE pitching or recommending any candidate, including in a
  quick chat menu: 3-4 queries (the idea in plain words, "github <idea>", the benchmark/
  leaderboard form, "<idea> 2026"). Agent-tooling niches fill within weeks, and a pick
  presented unchecked gets caught by the user. Lead with the incumbents table and the
  one angle none of them cover, labelled unverified until searched.
- "Fits assets already built" is a tiebreaker only, never pass/fail, when the user asks
  for a new area.
- Regulatory gate for health/medical candidates: anything that looks like treatment,
  symptom advice, or diagnosis triggers medical-device/patient-data law; reject unless the
  path is affordable for a sole trader.
- Required conclusion shape: 1 chosen candidate + 2 runners-up + every rejected idea with
  a one-line reason + dollar math to the MRR goal. "Nothing passes" is allowed;
  "both look promising" is not.
- The thread is closed only when the conclusion artifact exists and has been presented.
  End with a single decision request, not an open question list.

## Procedure

### 1. Frame

Before writing the frame, collect the user's context in ONE clarify round (skipping it
makes candidates die at step 0 after a full research run):
- Channel inventory: whom they can reach and are WILLING to contact (warm network,
  strangers, communities, public posting, face/name vs pseudonym). Get a count, not a yes.
- Craft and equipment: hobbies, gear, past creative or side projects and why they stopped
  (the stop reason usually becomes a criterion).
- Credentials/edge, and which standing rules still hold.
- For this user: never plan around his past network (former colleagues, old friends);
  strangers and new communities are fine. Do not probe why.

Then create `FRAME.md` in the work directory: the question, the context above, the
date-stamped done-criteria, and one workstream per candidate money source (template:
`templates/research-frame.md`). Commit it before dispatching. If the frame changes after a
failed step, write `FRAME-v2.md` and commit it rather than editing v1.

Pre-check platform rules yourself before dispatching content or game candidates (cheap,
and kills formats outright): see `references/creator-and-game-economics.md`.

### 2. Recon own data first

Mine the user's own data before any web research: platform APIs where products are already
listed, the product database (read-only, aggregates only, never personal data), repo and
analytics stats. It is free, it is the only first-party demand signal, and it reuses infra
that already exists. Web research comes after, for willingness to pay and competitor
pricing only.

### 3. Fan out evidence workstreams

Delegate one cheap subagent per candidate money source, all in parallel. Each writes
`<letter>-<name>.md` with fixed sections: Summary (5 lines max), evidence tables with URLs,
verdict against each criterion (pass/fail with evidence), proposed 2-week test with numeric
pass bar, or reject with reason. Also require in every file: the STRONGEST reason the idea
fails, incumbents named from a direct search, counter-evidence for every PASS, a 1-week
build probe when the candidate involves building, and "not found" instead of invented
numbers. Every child's context block must contain: the frame file
path to read first, the output path and section shape, and explicit read-only / no-post /
no-spend / no-contact rules. Children share nothing and will otherwise improvise external
actions.

### 4. Verify the decisive numbers yourself

Re-execute the 2-3 queries or API calls the conclusion rests on before presenting.
Subagent summaries are self-reports, and research children grade their own candidate PASS
on nearly every criterion. Run your own search against each "nobody sells X" gap claim
(one search often finds several incumbents) and check every claimed user asset
(communities, contacts, audience) against what the user actually said; children invent
these. Record the checks as a table (claim, file, check, TRUE/FALSE/WEAKENED) in the
conclusion and rescore.

### 5. Conclusion

Write `CONCLUSION.md`: chosen candidate, 2 runners-up, one-line rejections, dollar math,
risks stated plainly (including what could not be measured), and what the review must
decide. Present it briefly and ask for one decision.

## Pitfalls

- Keep the existing-asset list out of candidate generation when the user asks for a NEW
  area: a frame with one workstream per existing asset can only return what already exists.
  Generate candidates demand-first (where people already pay, through which channel), then
  score fit afterwards.
- When a candidate depends on a warm channel, make "user lists N contacts" a pre-registered
  step 0 with a kill rule (fewer than N = channel fails, run the named fallback). When it
  fails, log it and move on; never reframe the same offer as outreach to strangers to rescue it.
- When nothing passes 1-7 but the user has free time and wants to build, a $0 one-week
  build probe that measures criterion 7 (hours per unit) and stranger pickup is a valid
  conclusion. Say plainly that it tests production and discovery, not income.
- When the user's own history (health, past crises) comes up, do not ask for more detail
  or records than the decision needs, and do not save it to memory; note only the
  constraint it creates (e.g. "past network excluded").

- Date-stamp the done-criteria in the frame file before evidence collection; unstamped
criteria can be rewritten to fit whatever the evidence turned out to be.
- Re-run decisive queries yourself before concluding; a subagent's summary and its actual
tool output diverge often enough to change a decision.
- Usage is not revenue: separate runs/users from paying users before claiming demand.
Free-tier users pay nothing and inflate every count.
- Count the warm channel before building on it. Query the user table; an uncounted warm
user base is a hypothesis, and freemium math on a base of 2 accounts is a rounding error.
- Keep the channel criterion as pass/fail; a product buyers cannot find without cold
outreach fails regardless of how loud the pain is.
- "Nobody sells X" is ambiguous: check whether free tools already do X. Adjacent free
alternatives are a rejection signal, not an open market.
- List rejected ideas in the conclusion with one-line reasons; rejections never presented
get re-proposed in a later session as if new.
- When a test is pre-registered with a pass bar and a date, name the fallback move at the
  same time, so a miss produces a decision instead of another search.
- Ask for the platform's own revenue export before scoring a marketplace candidate on
  usage counts. Usage-based dollar estimates can miss by 10x; when measured numbers
  arrive, rewrite the conclusion's math with them and recalibrate any pass bar set from
  the estimate before its window opens, saying the old bar was too weak or too strong.
- Rank a lane with measured revenue above an unbuilt product with weeks of build ahead
  and estimated odds, even when the unbuilt one has richer research. Park the runner-up
  with a dated revisit trigger instead of killing it.
- When the user calls a lane "proven", agree with the ranking but state what the data
  does not cover: days of data, revenue concentrated in a few users or days (a batch job
  looks like a spike), how much of the product line actually earns, and the realized
  amount versus the run rate.
- Concentration is the first risk to name once a lane earns: few paying users on one
  item means the next build is the one that widens the paying base, not a new search.
- Before fixing pass-bar dates, check the platform's change constraints (effective-date
  lead time, per-item change quotas). A change that takes effect in 2 weeks starts the
  measurement window then, not at the decision date, and a quota can push stragglers
  past the window. Pre-register the fallback script/cron so delayed items land unattended.
- A pre-registered revert is a proposal, not an automatic action, when the platform
  charges a quota for reverting (e.g. one price change per month): state what a revert
  costs and let the user decide.
- When a hypothesis claims demand is price-driven, answer with the break-even multiple
  (a Px price change keeps revenue up while volume falls by less than (1 - 1/P)x), the
  cross-section (rivals priced higher with equal or more users contradicts it), and a
  direct retention read of existing users through the change. Test the hypothesis, do
  not just disagree with it.
- Gate a build on a pre-registered spike pass bar measured on BOTH precision and recall:
  a resolver returning only correct rows at 15% coverage fails a 50% bar even though
  every row is right, and precision-only eyeballing will wrongly green-light it.
- Separate market ceiling from tooling failure before declaring a data product unbuildable:
  measure the ceiling with an identity-exact source (e.g. a directory card matched by
  registration number) and count how often the field exists at all. If the market does not
  hold the data, no tooling fixes it; change the shape so the buyer supplies the hard
  field and you enrich around it.
- Before proposing another clone of the one earning item for another country/site,
  count the user's existing clones and their users: copies that already sit at 1-2
  users show the earning item's demand is specific, not a template to repeat.
- Competitor user counts validate the competitor's input/output shape, not a related one
  you considered: before counting a leader's users as demand for your variant, name the
  input they accept and the fields they return and check both against what you would ship.