---
name: session-handovers
description: "Use when handling session handovers or continuity documents."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sessions, handover, continuity, ledger, multi-session]
    related_skills: [backup-and-recovery]
---

# Session handovers and continuity

Karl keeps one long session on purpose, for memory continuity, and does not want it
split. Long sessions compact automatically; the durable state is the ~/STATUS.md
project ledger plus memory, not any handover document. A handover is a snapshot that
decays from the moment it is written, so it is a last resort, not the default.

## When to Use

Any decision about handing work between sessions: an incoming HANDOVER-*.md to follow,
a request to write one or to start a fresh session, parallel sessions splitting project
ownership, or a claim that something is blocked because it "needs login" or was "not
sent". Also when a session's topic ends and the question is what state survives. Skip
for session-history lookup (use session_search) and status reporting (status-report).

## Always-on rules

- Never push splitting a long-running session. When a session's topic ends, prefer
  letting it compact and keeping the STATUS.md ledger current over writing a handover.
- Never repeat a factual claim from an incoming handover as fact. The stale classes are
  "not sent / needs my login", deploy paths, unpushed state, and data availability.
  Check live state first: the platform itself, the credential store (~/.secrets and env —
  a token sitting there disproves "needs login" immediately), git, and row counts.
- When a handover claim proves wrong, correct it where it lives (the file, STATUS.md,
  memory) in the same session. A stale claim left in place is copied verbatim by the
  next session.
- Lane boundaries between parallel sessions (which session owns which project) belong in
  the project's STATUS.md block, not only in chat.

## Reading an incoming handover

1. Verify in cheapest-first order: outbound posts (open the thread), credentials (check
   the secret store before believing a blocker), repos and PRs (`gh` state), deploy
   config (the site's actual deploy command), data claims (query the source).
2. Treat every conclusion and number as re-checkable; re-run the verification the
   handover should have run rather than inheriting its confidence.
3. Fix what is wrong before acting on anything downstream of it.

## Writing a handover (only when asked)

1. Update every affected STATUS.md block first; the handover points at the ledger,
   never replaces it.
2. Each claim carries its verification basis (how you know, and when you checked).
   Unverified claims are labelled as such.
3. Point at artifacts — paths, commit hashes, URLs — instead of restating numbers in
   prose; restated numbers drift.

## Pitfalls

- Pitfall: "needs my login / cannot be done from here" is the most-repeated stale claim
  class; check the credential store and the target platform before relaying it — the
  session that wrote it usually never looked.
- Pitfall: deploy instructions in handovers describe the deploy as it was remembered,
  not as it is; the project's publishing skill or README is authoritative over any
  handover.
