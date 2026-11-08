# hermes-skills

28 skills for [Hermes Agent](https://github.com/NousResearch/hermes-agent), written
by one user and his agent over about six weeks of daily use (Sep-Nov 2026). Each one
records a procedure that worked plus the pitfalls found along the way, rather than
general advice. They follow the
[agentskills](https://agentskills.io) `SKILL.md` format, so other agents that read that
format can use them too.

## Install

```bash
hermes skills tap add vhsgreed/hermes-skills      # browse them in the hub
hermes skills install vhsgreed/hermes-skills/skills/linux-crash-diagnosis
```

Or copy a folder into `~/.hermes/skills/<category>/`.

## What's here

### Linux and machines

| Skill | Use when |
|---|---|
| [`linux-crash-diagnosis`](skills/linux-crash-diagnosis) | a Linux machine freezes, glitches, or misbehaves |
| [`linux-package-management`](skills/linux-package-management) | managing Ubuntu apps across apt, snap, Flatpak |
| [`linux-printer-setup`](skills/linux-printer-setup) | a printer won't work on Linux (CUPS, mDNS) |
| [`backup-and-recovery`](skills/backup-and-recovery) | backing up machines or recovering lost data |
| [`retro-emulation`](skills/retro-emulation) | setting up or fixing game emulation (RetroArch) |
| [`retro-game-emulation`](skills/retro-game-emulation) | setting up emulators or gamepads on Linux |

### Agents and models

| Skill | Use when |
|---|---|
| [`agent-security-posture`](skills/agent-security-posture) | agents run with real keys or untrusted input |
| [`agent-skill-tooling`](skills/agent-skill-tooling) | building scanners or lockfiles for agent skills |
| [`delegated-plan-execution`](skills/delegated-plan-execution) | executing a plan via delegated subagents |
| [`design-conventions`](skills/design-conventions) | brainstorming or planning a new project or feature |
| [`session-handovers`](skills/session-handovers) | handling session handovers or continuity documents |
| [`hermes-multi-machine`](skills/hermes-multi-machine) | linking machines to one Hermes brain or state sync |
| [`local-model-delegation`](skills/local-model-delegation) | deciding what to delegate to a cheap local model |
| [`local-model-wiring`](skills/local-model-wiring) | wiring local LLMs into Hermes or verifying runs |
| [`model-tier-routing`](skills/model-tier-routing) | choosing which model or worker runs a task |
| [`reproducible-llm-panels`](skills/reproducible-llm-panels) | running multi-model LLM juries or sweeps |
| [`upstream-bug-reporting`](skills/upstream-bug-reporting) | judging if an upstream bug is known or reportable, or when asked to test or report vulnerabilities in a system the user does not own |

### Building and publishing

| Skill | Use when |
|---|---|
| [`automation-pipelines`](skills/automation-pipelines) | building a scheduled fetch-and-deliver pipeline |
| [`browser-automation`](skills/browser-automation) | code must drive a real browser (Playwright, CDP) |
| [`interactive-data-visualization`](skills/interactive-data-visualization) | Build animated data visualizations as one HTML file |
| [`static-site-publishing`](skills/static-site-publishing) | building or previewing static websites |
| [`indie-game-development`](skills/indie-game-development) | designing or building small indie games |
| [`niche-validation`](skills/niche-validation) | choosing or validating a business niche or product |

### Research and writing

| Skill | Use when |
|---|---|
| [`pre-registered-experiments`](skills/pre-registered-experiments) | running pre-registered dataset experiments |
| [`practical-protocol-design`](skills/practical-protocol-design) | turning research into a dosed hands-on protocol |
| [`opinion-essays`](skills/opinion-essays) | co-authoring a researched, cited opinion article |

### Sweden

| Skill | Use when |
|---|---|
| [`swedish-consumer-disputes`](skills/swedish-consumer-disputes) | a Swedish purchase, return, or refund is disputed |
| [`swedish-small-business-finance`](skills/swedish-small-business-finance) | advising on Swedish tax, moms, or entity choice |

## Read before you use them

- **Written for one setup.** The measurements (tokens/s, RAM ceilings, timings)
  come from one Ryzen 7940HS mini-PC on Ubuntu 26.04, and some skills describe that
  machine's layout (RetroArch keybinds, a 6-button pad, flatpak timers). Re-measure
  before relying on a number. Mentions of "Karl" mean the author. Where a skill
  points at a ledger file (`~/STATUS.md`) or a sibling skill that isn't in this repo,
  skip that step or map it to your own setup.
- **Sweden-specific skills are not legal or tax advice.** They cite sources, so check
  the current year's rules against those sources.
- **Scanned, not audited.** The pack passes
  [skillguard](https://github.com/vhsgreed/skillguard) except for four findings, all
  quoted attack strings in prose that documents them (`agent-skill-tooling`) or a
  verification checklist (`session-handovers`). Pin with
  [skill-lock](https://github.com/vhsgreed/skill-lock) if you install them, and read a
  skill before you let an agent act on it.

This is a snapshot. Fixes are welcome as PRs, but the author's working copies keep
changing and are synced here by hand.

## License

MIT (see `LICENSE`).
