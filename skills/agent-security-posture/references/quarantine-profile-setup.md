# Quarantine profile setup

A quarantine profile is an isolated agent environment with no secrets and no authority.
Everything untrusted runs there. It exists so the answer to "can I look at this?" is
always yes, without the blast radius.

## What it must not contain

- API keys, provider tokens, OAuth sessions
- Credential vault or saved logins
- Wallet, billing, or spend-approval settings
- SSH keys or cloud credentials
- Terminal reach to secret directories or internal hosts
- Auto-approve or auto-confirm settings of any kind

If an untrusted task genuinely needs one of these, that is the signal that it cannot run
in quarantine and must be redesigned or refused.

## How to stand one up

Hermes isolates profiles under `~/.hermes/profiles/<name>/`, each with its own config,
sessions, skills, and memories. Create the profile, then strip it down:

1. Create the profile (via the CLI or dashboard profile builder).
2. Confirm its config carries no provider keys and no vault.
3. Confirm approval modes are set to prompt, never auto-approve. A subagent hitting a
   dangerous-command prompt must auto-deny, not auto-approve.
4. Confirm its working directory is a scratch area, not a repository with history or
   credentials.
5. Keep it out of any trusted-workspace list.

Verify by trying to read a secret from inside the profile. If it succeeds, the profile is
not quarantined.

## Rules of use

- Any external prompt, script, repository, or document goes here first.
- Nothing produced in quarantine is copied back to a privileged workspace without a
  human reading it first.
- The profile's own memory and skills stay separate, so untrusted content cannot ride
  into later sessions as trusted context.
- If the profile is used for anything with side effects, the side effects must be
  reversible and confined to its own sandbox.

## Complementary controls

Quarantine is the isolation layer, not the whole posture.

- **Secrets:** keep them in a single restricted directory and out of environment files
  that any session inherits. File mode 0600 protects against other users, not against
  the agent running as you.
- **Approval:** spend and payment actions always require an explicit, per-action human
  confirmation. Never configure automatic approval for anything that moves money or
  grants access.
- **Sudo:** when a passwordless sudo rule is required, scope it to the exact command needed.
  Understand that a scoped rule does not permit the probes around it, so either grant
  those separately or drop the probe.
- **Blast-radius review after any change:** anything new that a session can reach is new
  exposure. Re-run the inventory.
