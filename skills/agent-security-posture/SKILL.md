---
name: agent-security-posture
description: Use when agents run with real keys or untrusted input.
version: 1.0.0
author: Karl Sundström
license: MIT
metadata:
  hermes:
    tags: [security, agents, prompt-injection, isolation, credentials, secrets]
    related_skills: [backup-and-recovery, agent-skill-tooling]
---
Keep untrusted input away from anything a compromised session could reach. Isolation is the control; avoidance is not a policy.

## When to Use

- Testing, pasting, or evaluating an external prompt, script, repository, or document.
- Hardening a machine that holds live credentials and runs agents with tool access.
- After any suspected injection, exfiltration attempt, or unexpected model behaviour.
- Deciding where a new untrusted workflow should run.

Do not use for routine work against trusted, self-authored sources on an already-isolated machine.

## Always-on gates (every instance)

1. **Untrusted input never runs in a privileged session.** Not "never touch untrusted input." Untrusted material will keep arriving through messages, repositories, files, and pages; an avoidance rule erodes on first contact and is then gone. The rule that survives is about the session, not the source.
2. **Judge the blast radius before the task.** Ask what the session can reach: credential files, SSH keys, API tokens, spend or approval authority, cloud sessions, internal network routes. If any of those are reachable, this is not the session for untrusted work.
3. **Contain the incident, do not exceed it.** The instinct after a compromise is to destroy everything. That is usually a larger loss than the attack. Isolate first, rotate the credentials that were exposed, preserve the rest, and reconstruct from a known point only when the exposure is proven to have reached it.
4. **Treat a refusal or an oddity in the model's own reasoning as a signal worth inspecting.** Attacks are aimed at behaviour, not at the visible reply, so the trace is where steering shows up first.

## Procedure

1. **Inventory what the session can reach.** List credential locations, tokens, approval and spend authority, and network reach. Note which are one command away versus genuinely unavailable.
2. **Create an isolation profile for untrusted work.** No API keys, no vault, no wallet, no spend approval, no terminal path to secret directories, no route to internal hosts. Everything untrusted goes there.
3. **Route work by trust, not by convenience.** A decision that needs privileged access is not the same task as one that inspects an unknown artifact. Split them rather than hoping the artifact is benign.
4. **After any suspicion: rotate first, analyse second.** Change the credentials the session could reach before spending time on forensics. Rotation is cheap; a slow analysis is not.
5. **Keep an incident record.** What arrived, what it attempted, what it could have reached, what was rotated, what was preserved.

## Pitfalls

- **Permissions do not stop an agent that has been told to read.** A secret file locked to its owner is still one file read away from a session running as that owner. Only session separation shrinks the blast radius.
- **chmod on a directory does not touch the files inside it.** `chmod 600 <dir>` strips the directory's execute bit and locks even the owner out of every file within; a secrets directory is 700 and the files in it are 600. Fix both levels and say in one line which level the permission belongs to.
- **Inventorying secrets must not read their values.** A `grep | sed 's/=.*/=<redacted>/'` pipeline is not redaction: any line that misses the pattern prints in full, and tool transcripts capture stdout. Check existence only (`[ -f ]`, `[ -n "$VAR" ]`, vault list without values) and pass values via env or vault tools so they never enter captured output. A value that did reach captured output is exposed and gets rotated per procedure step 4.
- **Attack objectives cluster into two moves: exfiltrate, then transact.** Credentials and approval or spend authority are almost always the pair. Defend both; a posture that guards secrets while leaving approval automatic has only closed half of it.
- **Payloads hide where nobody reads.** Reasoning traces, alternate languages, and long plausible passages are used to carry steering past a casual glance. Inspect the trace when behaviour shifts, not just the final answer.
- **Financial pressure degrades vetting.** When revenue is urgent, an untrusted artifact promising efficiency reads as a shortcut, so it gets pasted in without inspection. The pressure is the vulnerability; the artifact is just the trigger.
- **A fetch tool exposed to agents is an SSRF surface.** A page or prompt can steer the agent to fetch `localhost`, RFC 1918, link-local (the cloud metadata address 169.254.169.254) or unique-local IPv6. Refuse those by default with an explicit opt-in flag, check every address the host resolves to (obfuscated forms like `0x7f.1` and `2130706433` resolve to loopback), and re-check on every redirect hop by following redirects manually. A real browser follows redirects the guard never sees, so disable or cap browser-based fetching while the guard is on. Keep proxy URLs and passwords out of tool output and exception text, since HTTP client errors embed the proxy URL.
- **A rule that says "I will never do X again" is a rule that will be broken the first time it is inconvenient.** Write the rule as a boundary on where something may happen, not as an oath about whether it will.

## References

- `references/quarantine-profile-setup.md` — how to stand up and use an isolated profile for untrusted work.
