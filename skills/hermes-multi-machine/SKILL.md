---
name: hermes-multi-machine
description: Use when linking machines to one Hermes brain or state sync.
version: 0.1.0
author: Karl Sundström, Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [hermes, multi-machine, tailscale, remote-gateway, sync]
    related_skills: [hermes-agent, backup-and-recovery]
---

# Hermes multi-machine: one brain, two windows

Run exactly ONE Hermes brain per user. Extra machines connect to it as remote gateways; they never replicate its state. When the user reports "syncing trouble" between machines, this architecture is the fix, not file sync.

## When to Use

- User wants Hermes on two machines to show the same sessions, memory, or skills
- Setting up or troubleshooting a remote-gateway connection (desktop app, SSH tunnel, Tailscale)
- Deciding whether a file may be synced or copied between Hermes installs
- Dashboard access over Tailscale is needed on a second machine

Don't use for: single-machine Hermes usage questions (see `hermes-agent`), backup jobs of `~/.hermes` (see `backup-and-recovery`), or bot/profile setup.

## Hard rules (every instance)

- Never two-way sync live SQLite state between machines. Never sync `state.db`, `sessions/`, `kanban.db`, `auth.json`, or `.env` via git/rsync/Syncthing: they are single-writer and credential-bearing; two writers produce conflict copies and corrupt the FTS index. `sessions optimize` refusing while any process holds `state.db` is that contract surfacing.
- Only markdown may be replicated: `memories/`, `skills/`, `SOUL.md` (git or rsync). Credentials and session state stay on the brain machine.
- Never run two `hermes serve` processes over one `~/.hermes`: each runs its own cron scheduler and routines double-fire (outreach batches, follow-up mail). If port binding is the goal, rebind the one existing serve, do not add a second.
- Never print, type, or accept a password in chat. Generate secrets in-shell, write them to a `chmod 600` local file, and point the user at the file to read locally on the machine where it is needed.
- Keep the backend bound to loopback and front it with Tailscale Serve for remote access. Do not bind `0.0.0.0`: it exposes the dashboard to the whole LAN and makes the auth gate the only barrier.

## Procedure (brain machine)

1. Recon before changing anything:
   - `tailscale serve status`: is a tailnet proxy already up? Expected shape: `https://<host>.tailN.ts.net (tailnet only)` with `/ proxy http://127.0.0.1:9119`. Done when you know the proxy URL and whether it exists.
   - `curl -s https://<host>.tailN.ts.net/api/status` (reachable unauthenticated): read `auth_required`, `auth_providers`, `auth_flows`, `gateway_running`, `version`. `auth_providers: ["basic"]` means client apps show a Sign in button; an empty list means they ask for a session token instead and the fix is enabling the basic provider (username + password or hash), not the connection mode. Done when you know which sign-in flow clients will get.
   - `ls ~/.hermes/` and grep `config.yaml` for `dashboard`/`gateway`/`bind`/`auth`: see what already exists before provisioning anything. Done when the existing config surface is known.
2. If password auth is missing or the password is lost (config stores only a scrypt `password_hash`, unrecoverable), provision a fresh one per `references/dashboard-auth.md`. Done when a password exists in a chmod 600 file and its hash is in config.
3. Verify end to end with a real login POST over the remote URL (same reference) BEFORE telling the user it works. A config write is not a working login. Done when the POST returns 200.
4. Hand the user the client-side steps: Desktop -> Settings -> Gateways -> Connection mode **Remote gateway** -> remote URL -> Sign in -> **Save and reconnect** -> click Test until "Reachable". Give the username and the path of the file holding the password. Done when the user reports the connection tests reachable.

## Fleet Tailscale updates (security advisories)

1. Inventory in one call: local `tailscale version`, `ssh <server> 'tailscale version; tailscale debug prefs | grep -i RunSSH'`, and peers via `tailscale status --json` (print `HostName`, `OS`, `Online`, `LastSeen` per Peer). Read the advisory for the fixed version and which features are affected (Tailscale SSH, Serve) before ranking machines: a node running the affected feature goes first.
2. Update the server non-interactively by piping a sudo secret from the environment, never typing it: `printf '%s\n' "$SERVER_SUDO_PASSWORD" | ssh <server> 'sudo -S -p "" sh -c "apt-get update -qq -o Dir::Etc::sourcelist=/etc/apt/sources.list.d/tailscale.list -o Dir::Etc::sourceparts=- -o APT::Get::List-Cleanup=0 && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --only-upgrade tailscale"'` (refreshes only the Tailscale repo). The same pipe is how to run `tailscale serve` changes on the server, which need root.
3. Verify after the daemon restarts: version, `tailscale status`, `tailscale serve status`, a fresh `ssh <server>` and a curl through every Serve URL (e.g. SearXNG on :8443). Done only when all answer.
4. Offline peers (Windows laptop, iPhone) cannot be updated remotely: list them as a user TODO in `~/STATUS.md` Infra with the target version.

## Expectations to state up front (prevents false bug reports)

- The client machine keeps its own local sessions entry for offline scratch. That is by design, not a sync failure.
- Sessions, memory, and skills shown after connecting are the brain machine's. Live agent output streams into every window showing the same session.
- App and backend version skew can break the chat websocket; match versions first when a connection connects but chat stalls.

## References

- `references/dashboard-auth.md`: config keys, password generation/hashing, the login route schema, verification curl.
- `references/windows-node-ssh.md`: SSH key setup, running scripts, launching GUI apps on the visible desktop, and cleanup on Karl's Windows laptop node.