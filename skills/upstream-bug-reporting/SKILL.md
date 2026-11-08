---
name: upstream-bug-reporting
description: "Use when judging if an upstream bug is known or reportable, or when asked to test or report vulnerabilities in a system the user does not own."
license: MIT
version: 1.0.0
metadata:
  hermes:
    tags: [github, issues, upstream, bug-report, oss]
    related_skills: [github, systematic-debugging]
---

# Upstream Bug Reporting

Use this after you have found the root cause of a bug in someone else's project (Hermes, a library, a CLI) and the user asks whether it is known or worth reporting. The output is a recommendation: file a new issue, add a comment, add a +1, or skip. When a post is warranted, also produce a draft the user approves before anything is posted.

## Procedure

0. **Rule out designed behavior and local config first.** Before searching trackers, find the component's documented rule for the failing path (README, man page, `/usr/share/doc/<pkg>/`) and test whether a local input triggers it (router, DNS, config file). A system that disables itself on a documented heuristic is not a bug; answer "known, works as intended, fix is X" and skip reporting. Also rule out your own reproduction: when the bug was observed only through a debug CLI or test harness (e.g. `gnome-software-cmd`), confirm that it runs the same pipeline as the real client (refine steps, flags, default options). Also check that the layer underneath (daemon socket, library call) returns the expected data. A harness that skips a step the GUI always runs will produce a convincing fake bug. For distro packages (no GitHub repo), the trackers are Launchpad (`bugs.launchpad.net/ubuntu/+source/<pkg>`), the upstream project, and the ArchWiki troubleshooting section, which usually documents known traps.
1. **Confirm the bug is still in the current code.** Record the installed commit (`git log -1 --oneline` in the source checkout) and the file:line of the faulty logic. A report pinned to a commit can be checked. "Happens to me" cannot.
2. **Search with exact strings, not prose.** Run one query per specific token: the exact log line, the config key, the function name.
   ```bash
   gh search issues "<exact log text>" --repo OWNER/REPO --limit 8 --json number,title,state -q '.[]|"\(.number) [\(.state)] \(.title)"'
   gh search prs   "<config_key>"      --repo OWNER/REPO --limit 8 --json number,title,state -q '.[]|"\(.number) [\(.state)] \(.title)"'
   ```
   Log strings and config keys find duplicates that a plain-English title search misses. Run the issue and PR searches as separate commands with timeout 60+. Large repos make each `gh search` slow, and chaining many in one call times out.
3. **Read the state of the work.**
   - An open issue plus several open, unmerged fix PRs means maintainers acknowledge the bug but haven't picked an approach. Recommend a comment or a +1, not a new issue.
   - A closed issue on the same topic was probably closed as a duplicate. Check it before assuming the bug was fixed.
   - If the user's local workaround already fixes their problem, say so. They don't need the upstream fix.
4. **Read the full thread before drafting.** If `gh issue view N --comments` errors on the GraphQL Projects-classic deprecation, use REST:
   ```bash
   gh api repos/O/R/issues/N/comments --paginate -q '.[].body' > thread.txt
   gh api repos/O/R/issues/N -q .body >> thread.txt
   ```
   Grep `thread.txt` for every point you plan to make, such as the provider name, "still on main", the symptom, or the workaround. Drop the points already covered.
5. **Draft only what the thread lacks:** a newly affected route or provider, the commit you reproduced on, the symptom the user actually sees and its cost (latency, money), a verified workaround with numbers, and pointers to the open fix PRs. Keep it short. Maintainers skim.
6. **Save the draft to a file and hand it over.** Write it to the scratch dir. Show the full text, then list:
   - every claim stronger than the evidence (for example "every turn" when the logs show "several per session");
   - every personal detail it exposes (model names, account or subscription setup, hostnames, paths).
   Give the exact post command (`gh issue comment N --repo O/R --body-file <file>`). Don't post until the user approves. Public posts under the user's account always need approval first.

## Salvaging a stale fix PR

When an open fix PR already targets the bug but has gone stale (far behind main, tests no longer collect) and the user asks to "fix and PR":
1. Check the PR's target code is unchanged on main (`git diff origin/main...pr-N -- <file>` plus read the same lines on main). If it moved, the fix needs rework, not a rebase.
2. `git checkout -B salvage origin/main && git cherry-pick pr-N`: the original author's commit keeps its authorship.
3. Run the touched test file. If the PR's new tests fail, read the error before touching the fix: typically main changed the call path the test mocks (e.g. a spawn helper replaced `subprocess.run`), so mock what the neighbouring tests on main mock.
4. Prove the test catches the bug: revert only the source file to main, rerun the new test, it must fail; restore.
5. Run the wider test slice on the branch AND on unmodified main; report collection errors that exist on main as pre-existing, not as yours.
6. Fork (`gh repo fork O/R --clone=false`), push a branch, open the PR titled `... (salvage #N)` with "Fixes #issue / Supersedes #N", the changes-on-top list, and the test evidence.
7. If a related issue has a maintainer needs-info request your evidence answers, comment there too, pointing at the PR.

An explicit "bugfix and PR" request from the user is the go to post the PR and the technical issue comment; outreach-style posts still need per-piece approval.

## Diagnosing a misleading upstream error

When the surfaced error is a generic hint (e.g. Chrome's "try --no-sandbox"), test the hinted cause directly before believing it: run the binary standalone with and without the hinted flag. If both work, the hint is noise; look for stale state the tool reuses (daemons, sockets, pid files: compare their start times with `ps -o lstart` against the current attempt). Kill only the specific stale PID, never `pkill -f <pattern>` that also matches your own shell's command line.

An attach flow (connect the tool to a process it did not start) has its own trap: a state-query command run before the attach command can make the tool lazily spawn its own instance on a default location, and that spawn is what fails or pollutes state. Order the fix so the attach command runs first, and verify before returning success that the tool's reported endpoint matches the requested target (port, path); on mismatch, close the session and return the real error. When testing shows a failure mode the existing fix PR does not cover, post the reproduction as a comment on that PR with the mechanism and the concrete completion steps, and answer "what would it take" with a numbered step list, not prose.

## Vulnerabilities in systems the user does not own

When asked to find, confirm, or act on vulnerabilities in a site or service the user does not administer, the deliverable is a disclosure advisory, never a test. Active probing of an unowned system is unauthorized whatever the intent, and a scan meant to help is identical traffic to the receiving side.

1. **Decline the test in one sentence and name the legitimate path.** Do not lecture; move straight to the work that helps.
2. **Passive observation only.** A HEAD request plus a GET on `/.well-known/security.txt` yields the platform, the web server, and whether the owner has a disclosure route. Never fuzz inputs, never send the payload the advisory warns about, never attempt the exploit "to confirm". Confirming is the boundary being crossed.
3. **Verify the vulnerability before writing anything.** A named CVE is checkable: read the vendor advisory and at least one independent writeup, and record the fixed versions and the mechanism. An unverified claim sent to a site owner is worse than silence.
4. **Report the user's own exposure first.** The same advisory applied to machines they are responsible for is work they can act on immediately, and it usually delivers more value than the third party ever will. Say what was checked and how.
5. **Write the advisory a non-specialist can act on.** Include the CVE IDs and severity, the fixed versions, the one command that says whether they are affected, a paragraph of mechanism in plain language, what to do if patching must wait, and links to the vendor and national CERT advisories. Omit exploit detail: it changes nothing about the fix.
6. **Give the report a route in.** If there is no `security.txt`, say so and offer to draft one. That gap is why nobody has been able to tell them things like this.

## Pitfalls

- **"I want to help" and "I want to attack" are the same request to a server you do not own.** Good intent does not supply authorization. Get permission in writing from the owner before any active testing, and scope what it covers.
- Never present an unverified CVE as confirmed. Vendor advisory plus one independent writeup before the claim enters a draft.
- Never claim "not reported" after a single title search. Absence of evidence from one query is the usual cause of duplicate issues.
- Never present a fix path you only read in code as tested. Label it "verified by code reading" in both the draft and the reply to the user.
