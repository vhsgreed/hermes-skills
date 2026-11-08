# Final whole-branch review and doc-truth review

Per-task reviews judge each diff against its brief. They cannot see seams
between tasks: two modules that disagree about who catches an exception, who
paces, who reads the environment, or who may touch the network. Expect the
final review to find real Critical bugs even after every task review came back
clean; budget a fix wave for it.

## Final review prompt shape

Write the prompt to a file and run it on the strongest model, read-only.

1. **Judge against the product promises, not the task list.** Paste the
   headline promises (3-5 lines) and ask, for each, where the branch breaks it.
   The task list makes a reviewer re-grade tasks; the promises make it hunt.
2. **Integration walk.** Name the full pipeline (config load -> resolve ->
   retry/escalation -> pool/lease -> pacing -> runner -> outcome -> CLI exit ->
   report -> server response) and ask it to name every place two modules
   disagree about a contract.
3. **Adversarial local servers.** Ask for small 127.0.0.1 servers that
   misbehave on purpose (challenge then OK, 403 per proxy, 429 then OK, dead
   proxy, DNS failure) and that LOG EVERY HIT, so "never from the origin IP"
   style promises are checked from the server side, not from the client's
   self-report. Keep the servers in scratch: the fix rounds and the re-review
   reuse them to reproduce each bug before and after.
4. **Mutation check in a scratch copy.** Ask it to break 15-25 high-value
   behaviours one at a time in a copy outside the repo and report which the
   suite misses. Surviving mutations become required tests in the fix wave;
   assertion-free tests and stubs that raise `AssertionError` (which a
   catch-all converts into the expected result) show up here.
5. **"What would embarrass us in public":** the three bugs a stranger reports
   on day one. This ranks findings by user impact better than severity labels.
6. Output to a file in the ledger directory plus a short printed summary.

## Fix wave after the final review

- Rule every finding (ledger line with cost), then split: round A code
  (test-first, each test must FAIL at the reviewed HEAD and go through the
  integration path where the bug was proven), round B docs (code fixes make
  previously true sentences false, so docs go last).
- Require before/after reproductions with the reviewer's own probe servers in
  the report, and the mutation table re-run.
- Scoped re-review on the strongest model: re-run the original proofs, check
  that each amendment ruling did not reopen an earlier fixed bug (list the
  earlier behaviours explicitly), audit the test diff, and ask for the
  trade-off any ruling accepted (e.g. skipping a probe loses its hint).

## Doc-truth review (README, changelog, schema)

- The reviewer marks every factual claim TRUE / FALSE / UNVERIFIABLE by
  running the command or reading the code behind it, in a table. Reading the
  docs alone passes false claims.
- Validate any published schema against REAL output (a real report line, a
  real server response, the edge records such as zero-attempt pages), not
  against the examples in the schema.
- Check the first screen for what the spec requires there: a tall image above
  the setup block pushes it off the screen; measure rendered height, do not
  eyeball line numbers.
- Links, badges and `git clone` URLs that point at a not-yet-renamed repo are a
  release-order issue: record "merge, rename, then tag" rather than reverting
  the URLs.
- CI assertions such as `test $? -eq 0` after a pipeline are dead under
  `bash -eo pipefail` (GitHub's default `run:` shell): errexit fires first.
  Rely on pipefail and say so in a comment.
