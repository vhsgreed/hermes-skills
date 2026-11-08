# Dashboard auth (username/password) for remote-gateway access

## Config surface

`~/.hermes/config.yaml` (set via `hermes config set`):

- `dashboard.public_url: https://<host>.tailN.ts.net`
- `dashboard.basic_auth.username: <user>`
- `dashboard.basic_auth.password_hash: scrypt$...`: alternative to plaintext; unrecoverable by design, rotate when lost, do not hunt for the old value.

`$HERMES_HOME/.env` (env variants):

- `HERMES_DASHBOARD_BASIC_AUTH_USERNAME`
- `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`: plaintext alternative to `password_hash`. Do not set both mechanisms at once; precedence is not documented.
- `HERMES_DASHBOARD_BASIC_AUTH_SECRET`: keeps signed session cookies valid across restarts; set once.

## Generate and store a password (never echo it)

```bash
cd ~/.hermes && umask 077
PW=$(openssl rand -hex 12)   # hex stays easy to type on another machine
printf 'Hermes dashboard sign-in\nusername: karl\npassword: %s\n' "$PW" > dashboard-login.txt
chmod 600 dashboard-login.txt
```

Hash it from the file (stdlib scrypt via the plugin; the hermes-agent checkout must be on `sys.path`):

```bash
HASH=$(python3 -c "import sys,pathlib;sys.path.insert(0,'$HOME/.hermes/hermes-agent');\
from plugins.dashboard_auth.basic import hash_password;\
pw=pathlib.Path('$HOME/.hermes/dashboard-login.txt').read_text().split('password: ')[1].strip();\
print(hash_password(pw))")
hermes config set dashboard.basic_auth.password_hash "$HASH"
```

Then verify with a real login before reporting success:

```bash
BODY=$(python3 -c "import json,pathlib;pw=pathlib.Path('$HOME/.hermes/dashboard-login.txt').read_text().split('password: ')[1].strip();\
print(json.dumps({'provider':'basic','username':'karl','password':pw}))")
curl -s -o /dev/null -w '%{http_code}\n' -X POST https://<host>.tailN.ts.net/auth/password-login \
  -H 'Content-Type: application/json' -d "$BODY"
```

200 = working. 401 with credentials read back from the same file means the running serve has not picked up the new hash; restarting `hermes serve` reloads config but briefly drops the desktop connection (the app reconnects). 429 = per-IP login rate limit, wait it out.

## Login route (from `hermes_cli/dashboard_auth/routes.py`)

`POST <remote-url>/auth/password-login`, JSON body:

```json
{"provider": "basic", "username": "...", "password": "...", "next": ""}
```

`provider` is required and must match an entry in `/api/status`'s `auth_providers`. Failure codes: 404 unknown provider, 401 bad credentials, 429 rate limited, 503 provider store unreachable. Success: `{"ok": true, "next": ...}` plus session cookies (or a loopback redirect for native sign-in). The desktop uses these same flows; `auth_flows: ["cookie", "native_pkce"]` in `/api/status` tells you which.