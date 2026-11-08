---
name: agent-skill-tooling
description: "Use when building scanners or lockfiles for agent skills."
version: 1.0.0
author: Karl Sundström + Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, supply-chain, skills, scanner, lockfile, testing, sarif]
    related_skills: [test-driven-development, requesting-code-review]
---

# Agent Skill Tooling

## When to Use

Building or extending security tooling for SKILL.md bundles: scanners, lockfiles, rule
corpora, CI gates. Also when tuning regex rules for agent-skill content — the FP checklist
below applies to any pattern matching over skill prose.

Building security tooling for SKILL.md bundles (scanners, lockfiles, rule corpora).
Proven on `skillguard` (scanner) and `skill-lock` (hash pinning) — repos at
`~/src/skillguard` and `~/src/skill-lock`.

## Corpus design: three bands, no pretending

Design every test corpus in three bands and enforce each with tests:

1. `samples/malicious/` — real attack primitives (exfil via a command substitution that cats the user's SSH private key,
   pipe-to-shell, base64 exec, silent nested installs, prompt injection, disguised update
   checks, staging-and-upload). **Every file must raise >= 1 high/critical finding.**
2. `samples/benign/` — realistic clean skills INCLUDING hard negatives from the FP checklist
   below. **Every file must raise ZERO findings of any severity.** This strong claim is
   what makes the tool credible; earn it with real-world samples, not toy ones.
3. `samples/needs-review/` — legitimate-but-risky patterns (official installers piped to
   shell). **Flagged on purpose: the review gate is the product.** Static analysis cannot
   tell `astral.sh/uv/install.sh | sh` from an attacker's pipe — say so instead of tuning it
   away. Claiming zero false positives there would be a lie.

Why: the band structure encodes exactly what line-based static analysis can and cannot know,
so every future rule change must keep all three promises simultaneously.

## False-positive classes (check every regex rule against these)

- **Negated policy language.** "never tell a user to put X in .env" (benign policy) vs
  a quoted instruction to keep a step secret from the user (malicious concealment). Distinguish by what
  follows: `tell the user TO <verb>` is usually benign instruction, `tell the user ABOUT/
  THAT/WHAT` is concealment. Test both phrasings as corpus samples.
- **Public keys.** Catting an SSH `.pub` public key is a benign display instruction. Exclude
  `.pub`, and beware backtracking defeating `(?<!\.pub)` — terminate the path match with a
  boundary class so shorter backtracked consumptions cannot succeed.
- **Existence checks.** A quiet probe like `-q "github.com" ~/.git-credentials` checks
  presence, it does not dump. Drop quiet-probe commands from dump rules (accept the FN) or
  split probing into a lower-severity rule.
- **Patterns quoted in docs/deny-lists.** `"deny": ["Bash(rm -rf *)"]` and tables of
  dangerous patterns trip the very rules they document. Fix with **line-anchored** command
  rules (`^\s*(?:sudo\s+)?curl\b...`) — NOT evadable ignore-lists on line text; anchoring
  misses prefixed commands (a curl-to-bash pipe after `cd /tmp &&`), which is the honest trade.
- **English-word commands.** `type`, `open`, `more` match prose near a path within the
  proximity window. Either anchor them or document the class.

When dogfooding produces FPs: fix the rule for the whole class, then ADD the offending real
line as a benign regression sample. Never delete the sample to make tests pass.

## Discipline

- Load `test-driven-development` and obey it: corpus/behavior tests first, watch them fail,
  then implement. Rules are data (rules.json) but engine changes are code — the corpus test
  that breaks is the failing test driving the change.
- Rules as JSON data, engine generic: contributors add detection without touching Python.
- Stdlib-only Python >= 3.10: zero install friction beats elegance.
- Emit SARIF 2.1.0 (`--format sarif`) — it IS the "detection category" gap (VentureBeat
  2026: SAST scanners have none for skill backdoors) and integrates GitHub code scanning.
- Severity bands: critical/high = CI gate (`--fail-on high` default), medium = review.
  Exit codes: 0 clean, 1 findings, 2 usage.

## Lockfile layer (skill-lock / skills-lock.json draft-01)

- Pin per-file sha256 + tree hash; verify statuses: verified/modified/missing/untracked.
- Per-skill update ONLY (re-pin one skill after showing changed files; never bulk without an
  explicit flag) — removes Orca's "blind bulk updates" primitive.
- Fail on duplicate skill names (shadowing) — removes the "silent override" precondition.
- Reserved `source` + `attestations` fields for provenance/signatures (Sigstore, skill.sig).
- Landscape as of 2026-09: Vercel's `skills` CLI has a global `~/.agents/.skill-lock.json`
  (sourceUrl + skillFolderHash) but it is an update-tracking DB — no install/sync semantics,
  no review step, no shadow detection (their issue #283 asks for it). HappySkills ships a
  product-tied lockfile. Claim for the RFC: no OPEN SPEC defines verify/update semantics.
- Trust model: TOFU — lockfiles prove stability, not benignity. Scan (skillguard) at lock time.

## Release flow

- Ship `skillguard` (detection) + `skill-lock` (pinning) + the RFC together.
- Verbatim attack phrases in skill prose (quoted concealment instructions)
  trip Hermes's cron prompt-injection scanner (pattern `deception_hide`) when the skill is
  attached to a cron job: documentation quotes read as payloads. Such skills cannot ride on
  cron jobs; keep cron prompts self-contained and attach nothing.
- Publish decision and repo placement (github.com/vhsgreed) are Karl's; commit locally, ask
  before pushing anywhere.
- Placement: agentskills maintainers keep the spec minimal (CONTRIBUTING: "when in doubt,
  leave it out"; jonathanhefner on #252: integrity belongs at the distribution layer).
  Lockfile semantics stay in vhsgreed/skill-lock; only artifact-level gaps (e.g. which files
  belong to a skill directory, which tree_hash needs) go to agentskills as narrow proposals.
  Check maintainer precedent before announcing any governance decision.
- Watch vercel-labs/skills#283: if Vercel ships install/sync or a format, reassess the
  neutral-spec window immediately.
