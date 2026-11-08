# Run lifecycle: pauses, expired deadlines, close-out

Depth for SKILL.md sections 4 and 4b. Always-on rules stay in SKILL.md.

## Closing a study after its compute deadline passed

When the registered deadline expired with the run incomplete (paused, crashed, abandoned), close it under the registered partial-subset rule instead of quietly extending:

1. Read only plumbing: row counts, pilot/variance flags, per-unit timings, `scorer --selftest`. Do not run the scorer yet.
2. Move partial models/units UNREAD to `out/notscored/` (with any log that holds their rows) so the scorer's `*.jsonl` glob cannot pick them up. Restore any tracked log a relaunch overwrote (`git checkout <file>`) after copying the new version into `notscored/`.
3. Write a close-out change-log entry BEFORE the look:
   - what is scored, what is NOT SCORED, and why (deadline, who decided, what had been read);
   - per hypothesis, whether the subset can decide it. Bars that need "k of N" units/models are NOT SCORABLE below k. The scorer still prints a verdict string for them (it counts what exists), so the entry must say it supersedes those strings and the values are descriptive only;
   - the scope limit of what remains (e.g. the only scored model is the authors' own calibration model: a pass is a reproduction there and says nothing about unseen families);
   - registered outputs that were never implemented (say so rather than silently omitting them);
   - that finishing the rest is a new registration with its own freeze, not a continuation.
4. Commit and push the entry to the public remote. The close-out script refuses to run unless HEAD is on origin: `git fetch -q origin && git merge-base --is-ancestor HEAD origin/master || exit 1`.
5. Run the remaining registered phases (synthetic/H0, health gate, post-run recheck) as one `systemd-run --user` unit with `-p MemoryMax=... -p Nice=10 -p RuntimeMaxSec=...` so the user keeps the machine. Launch a second unit that loops `while systemctl --user is-active -q <first>; do sleep 60; done`, then runs the one look only if the recheck log contains `RECHECK: PASS` and a done-marker exists, else writes `out/analyze.blocked`. The verdict lands without the agent sleep-polling inside a turn.
6. Estimate wall time from recorded per-unit times (`sum(t_total)` over the seeded recheck sample + measured phase times) and report user time and machine time separately.
7. Update the ledger with unit names, ETA and the next decision (short Journal note vs ledger-only close). If a phase log line was seen while confirming the unit started, disclose it.

## Hardware blamed for a stalled study

Check the ledger and timings before agreeing that hardware blocks reproduction. Single-channel or smaller RAM on a one-unit-at-a-time pipeline changes throughput (~1.4x slower per matrix), not results; the registered recheck guard is what proves numbers are unaffected. The usual real blocker is a user pause that outlived the deadline. Offer: close under the subset rule, register a new deadline (clean only if no registered outcome was viewed), or drop.
